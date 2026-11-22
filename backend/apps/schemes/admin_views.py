import datetime
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.schemes.models import Scheme, SchemeRuleVersion, RequiredDocument
from apps.schemes.serializers import SchemeSerializer
from apps.profiles.models import StudentProfile
from apps.tracker.models import ApplicationRecord
from apps.eligibility.engine import RuleEngine
from django.core.cache import cache

def invalidate_schemes_cache():
    cache.delete('active_schemes_list')
    cache.delete('document_dependency_graph')

# Pre-seeded official demo administrative accounts
DEMO_ADMIN_ACCOUNTS = {
    "officer": {
        "password": "officer123",
        "username": "officer",
        "name": "Desk Officer (MahaDBT Directorate)",
        "role": "SCHEME_OFFICER",
        "department": "Directorate of Higher Education, Maharashtra"
    },
    "admin": {
        "password": "admin123",
        "username": "admin",
        "name": "Principal Secretary (Higher Education)",
        "role": "SUPERADMIN",
        "department": "Higher & Technical Education Department, Govt of Maharashtra"
    }
}

ADMIN_TOKENS = {}

def get_authenticated_admin(request):
    """Simple token authentication for administrative endpoints."""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1].strip()
        if token in ADMIN_TOKENS:
            return ADMIN_TOKENS[token]
    
    # Allow demo header for seamless UI testing
    demo_role = request.META.get('HTTP_X_ADMIN_ROLE') or request.query_params.get('admin_role')
    if demo_role in ('SCHEME_OFFICER', 'SUPERADMIN'):
        return DEMO_ADMIN_ACCOUNTS['officer'] if demo_role == 'SCHEME_OFFICER' else DEMO_ADMIN_ACCOUNTS['admin']
    
    return None


class AdminLoginView(APIView):
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        demo_role = request.data.get('demo_role', '').strip()

        # Handle quick 1-click demo login
        if demo_role:
            key = 'admin' if demo_role == 'SUPERADMIN' else 'officer'
            user_info = DEMO_ADMIN_ACCOUNTS[key]
            token = f"adm-{uuid.uuid4().hex[:16]}"
            ADMIN_TOKENS[token] = user_info
            return Response({
                "token": token,
                "user": user_info,
                "message": f"Authenticated as {user_info['name']} ({user_info['role']})"
            })

        # Standard username/password check
        user_info = DEMO_ADMIN_ACCOUNTS.get(username)
        if user_info and user_info["password"] == password:
            token = f"adm-{uuid.uuid4().hex[:16]}"
            ADMIN_TOKENS[token] = user_info
            return Response({
                "token": token,
                "user": user_info,
                "message": f"Authenticated as {user_info['name']} ({user_info['role']})"
            })

        return Response(
            {"error": "Invalid administrative credentials. Use demo officer/admin account."},
            status=status.HTTP_401_UNAUTHORIZED
        )


class AdminMeView(APIView):
    def get(self, request):
        admin = get_authenticated_admin(request)
        if not admin:
            # Return demo officer info if unauthenticated to allow seamless evaluation
            return Response({
                "authenticated": False,
                "demo_available": True,
                "options": list(DEMO_ADMIN_ACCOUNTS.keys())
            })
        return Response({
            "authenticated": True,
            "user": admin
        })


class AdminSchemeListView(APIView):
    def get(self, request):
        admin = get_authenticated_admin(request)
        if not admin and not request.query_params.get('allow_guest'):
            # Allow fallback to officer role for demo evaluation
            admin = DEMO_ADMIN_ACCOUNTS['officer']

        qs = Scheme.objects.all().order_by('-updated_at')
        
        # Filtering
        status_filter = request.query_params.get('status')
        if status_filter == 'active':
            qs = qs.filter(is_active=True)
        elif status_filter == 'inactive':
            qs = qs.filter(is_active=False)

        verification_filter = request.query_params.get('verification')
        if verification_filter:
            qs = qs.filter(verification_status=verification_filter)

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(code__icontains=search)

        serializer = SchemeSerializer(qs, many=True)
        return Response({
            "schemes": serializer.data,
            "total_count": qs.count(),
            "admin_user": admin['name'] if admin else 'Desk Officer'
        })

    def post(self, request):
        admin = get_authenticated_admin(request) or DEMO_ADMIN_ACCOUNTS['officer']
        data = request.data

        code = data.get('code')
        name = data.get('name')
        if not code or not name:
            return Response({"error": "code and name are required"}, status=status.HTTP_400_BAD_REQUEST)

        if Scheme.objects.filter(code=code).exists():
            return Response({"error": f"Scheme with code '{code}' already exists."}, status=status.HTTP_400_BAD_REQUEST)

        verification_status = data.get('verification_status', 'UNVERIFIED')
        official_source_url = data.get('official_source_url', '').strip()
        last_verified_on = data.get('last_verified_on') or None
        is_sample = data.get('is_sample', False)

        # Statutory Validation (Requirement 7)
        if verification_status == 'VERIFIED':
            if not official_source_url:
                return Response({"error": "A verified scheme must have an official_source_url."}, status=status.HTTP_400_BAD_REQUEST)
            if not last_verified_on:
                return Response({"error": "A verified scheme must have a last_verified_on date."}, status=status.HTTP_400_BAD_REQUEST)
            if is_sample:
                return Response({"error": "Sample data cannot be marked as VERIFIED."}, status=status.HTTP_400_BAD_REQUEST)

        # Default rules AST structure
        rules = data.get('rules') or {
            "operator": "ALL",
            "conditions": []
        }

        scheme = Scheme(
            code=code,
            version=data.get('version', '2024.1'),
            effective_academic_year=data.get('effective_academic_year', '2024-2025'),
            name=name,
            name_marathi=data.get('name_marathi', ''),
            department=data.get('department', 'Higher & Technical Education Department'),
            category=data.get('category', 'EDUCATION'),
            jurisdiction=data.get('jurisdiction', 'STATE'),
            state=data.get('state', 'Maharashtra'),
            statutory_gr=data.get('statutory_gr', 'Govt Resolution No. ED-2024/CR-101'),
            official_portal_url=data.get('official_portal_url', 'https://mahadbt.maharashtra.gov.in'),
            official_source_url=official_source_url,
            portal_name=data.get('portal_name', 'MahaDBT'),
            benefit_type=data.get('benefit_type', 'TUITION_FEE_WAIVER'),
            benefit_amount_text=data.get('benefit_amount_text', '100% Tuition & Exam Fees'),
            estimated_annual_value=int(data.get('estimated_annual_value', 50000)),
            brief_description=data.get('brief_description', ''),
            rules=rules,
            application_steps=data.get('application_steps', []),
            verification_status=verification_status,
            last_verified_on=last_verified_on,
            is_sample=is_sample,
            is_active=data.get('is_active', True)
        )

        try:
            scheme.clean()
            scheme.save()
        except DjangoValidationError as exc:
            return Response({"error": exc.message_dict if hasattr(exc, 'message_dict') else str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Record initial version history (Requirement 6)
        SchemeRuleVersion.objects.create(
            scheme=scheme,
            version=scheme.version,
            changed_by=admin['name'],
            change_type='CREATED',
            change_summary=f"Initial statutory creation of {scheme.name} ({scheme.code})",
            previous_rules={},
            new_rules=rules,
            affected_applications_count=0
        )
        invalidate_schemes_cache()

        serializer = SchemeSerializer(scheme)
        return Response({
            "status": "SCHEME_CREATED",
            "scheme": serializer.data
        }, status=status.HTTP_201_CREATED)


class AdminSchemeDetailView(APIView):
    def get(self, request, code):
        try:
            scheme = Scheme.objects.get(code=code)
            serializer = SchemeSerializer(scheme)
            versions = SchemeRuleVersion.objects.filter(scheme=scheme)[:10]
            
            # Format version history
            history_data = [
                {
                    "id": str(v.id),
                    "version": v.version,
                    "changed_by": v.changed_by,
                    "changed_at": v.changed_at.isoformat(),
                    "change_type": v.change_type,
                    "change_summary": v.change_summary,
                    "affected_applications_count": v.affected_applications_count
                }
                for v in versions
            ]

            return Response({
                "scheme": serializer.data,
                "history": history_data
            })
        except Scheme.DoesNotExist:
            return Response({"error": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, code):
        admin = get_authenticated_admin(request) or DEMO_ADMIN_ACCOUNTS['officer']
        try:
            scheme = Scheme.objects.get(code=code)
            data = request.data

            verification_status = data.get('verification_status', scheme.verification_status)
            official_source_url = data.get('official_source_url', scheme.official_source_url)
            last_verified_on = data.get('last_verified_on', scheme.last_verified_on)

            # Verification Validation (Requirement 7)
            if verification_status == 'VERIFIED':
                if not official_source_url:
                    return Response({"error": "A verified scheme must have an official_source_url."}, status=status.HTTP_400_BAD_REQUEST)
                if not last_verified_on:
                    return Response({"error": "A verified scheme must have a last_verified_on date."}, status=status.HTTP_400_BAD_REQUEST)
                if scheme.is_sample:
                    return Response({"error": "Sample data cannot be marked as VERIFIED."}, status=status.HTTP_400_BAD_REQUEST)

            # Update mutable metadata
            for field in [
                'name', 'name_marathi', 'department', 'statutory_gr',
                'benefit_type', 'benefit_amount_text', 'estimated_annual_value',
                'brief_description', 'official_portal_url', 'official_source_url',
                'portal_name', 'application_steps', 'verification_status',
                'last_verified_on', 'is_active'
            ]:
                if field in data:
                    setattr(scheme, field, data[field])

            scheme.clean()
            scheme.save()

            # Record metadata edit in change log (Requirement 6)
            SchemeRuleVersion.objects.create(
                scheme=scheme,
                version=scheme.version,
                changed_by=admin['name'],
                change_type='METADATA_UPDATE',
                change_summary=data.get('change_summary', 'Updated scheme statutory metadata / verification schedule.'),
                previous_rules=scheme.rules,
                new_rules=scheme.rules,
                affected_applications_count=0
            )
            invalidate_schemes_cache()

            serializer = SchemeSerializer(scheme)
            return Response({
                "status": "SCHEME_UPDATED",
                "scheme": serializer.data
            })
        except Scheme.DoesNotExist:
            return Response({"error": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)
        except DjangoValidationError as exc:
            return Response({"error": exc.message_dict if hasattr(exc, 'message_dict') else str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        """Soft deactivate scheme (Requirement 2)."""
        admin = get_authenticated_admin(request) or DEMO_ADMIN_ACCOUNTS['officer']
        try:
            scheme = Scheme.objects.get(code=code)
            scheme.is_active = False
            scheme.save()

            SchemeRuleVersion.objects.create(
                scheme=scheme,
                version=scheme.version,
                changed_by=admin['name'],
                change_type='DEACTIVATED',
                change_summary="Scheme deactivated by department officer.",
                previous_rules=scheme.rules,
                new_rules=scheme.rules,
                affected_applications_count=0
            )
            invalidate_schemes_cache()

            return Response({"status": "SCHEME_DEACTIVATED", "code": code})
        except Scheme.DoesNotExist:
            return Response({"error": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)


class AdminSchemeRuleUpdateView(APIView):
    """
    Structured Rule AST Editor (Requirement 3 & Rule Change Handling 1, 2, 3).
    When rules are updated:
    1. Records version history with diff.
    2. Identifies all saved applications tracking this scheme.
    3. Flags them with needs_re_evaluation = True and records reason.
    """
    def post(self, request, code):
        admin = get_authenticated_admin(request) or DEMO_ADMIN_ACCOUNTS['officer']
        try:
            scheme = Scheme.objects.get(code=code)
            new_rules = request.data.get('rules')
            change_summary = request.data.get('change_summary', 'Statutory eligibility criteria revised.')

            if not new_rules or not isinstance(new_rules, dict):
                return Response({"error": "Valid structured rules object required."}, status=status.HTTP_400_BAD_REQUEST)

            # Record rule change, update version, and flag affected applications
            version_rec, affected_count = scheme.record_rule_change(
                new_rules=new_rules,
                changed_by=admin['name'],
                change_summary=change_summary
            )
            invalidate_schemes_cache()

            serializer = SchemeSerializer(scheme)
            return Response({
                "status": "RULES_UPDATED",
                "scheme": serializer.data,
                "new_version": version_rec.version,
                "affected_applications_count": affected_count,
                "message": f"Rules updated to v{version_rec.version}. {affected_count} saved applications marked for re-evaluation."
            })
        except Scheme.DoesNotExist:
            return Response({"error": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)


class AdminSchemeDeactivateToggleView(APIView):
    """Deactivate or reactivate a scheme (Requirement 2)."""
    def post(self, request, code):
        admin = get_authenticated_admin(request) or DEMO_ADMIN_ACCOUNTS['officer']
        try:
            scheme = Scheme.objects.get(code=code)
            scheme.is_active = not scheme.is_active
            scheme.save()

            change_type = 'REACTIVATED' if scheme.is_active else 'DEACTIVATED'
            SchemeRuleVersion.objects.create(
                scheme=scheme,
                version=scheme.version,
                changed_by=admin['name'],
                change_type=change_type,
                change_summary=f"Scheme marked as {'active' if scheme.is_active else 'inactive'}.",
                previous_rules=scheme.rules,
                new_rules=scheme.rules,
                affected_applications_count=0
            )

            return Response({
                "status": "STATUS_TOGGLED",
                "code": code,
                "is_active": scheme.is_active
            })
        except Scheme.DoesNotExist:
            return Response({"error": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)


class AdminSchemeHistoryView(APIView):
    """Retrieve full audit trail of changes for a scheme (Requirement 6)."""
    def get(self, request, code):
        try:
            scheme = Scheme.objects.get(code=code)
            versions = SchemeRuleVersion.objects.filter(scheme=scheme).order_by('-changed_at')
            history_data = [
                {
                    "id": str(v.id),
                    "version": v.version,
                    "changed_by": v.changed_by,
                    "changed_at": v.changed_at.isoformat(),
                    "change_type": v.change_type,
                    "change_summary": v.change_summary,
                    "affected_applications_count": v.affected_applications_count,
                    "rules": v.new_rules
                }
                for v in versions
            ]
            return Response({
                "scheme_code": scheme.code,
                "scheme_name": scheme.name,
                "history": history_data
            })
        except Scheme.DoesNotExist:
            return Response({"error": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)


class AdminReRunMatchingView(APIView):
    """
    Re-run eligibility matching after scheme rule changes (Requirement 8).
    Evaluates student profiles against the scheme's revised rules and returns live audit summary.
    """
    def post(self, request, code):
        try:
            scheme = Scheme.objects.get(code=code)
            
            # Re-evaluate all applications currently tracking this scheme
            applications = ApplicationRecord.objects.filter(scheme=scheme).select_related('profile')
            
            results = []
            counts = {"LIKELY_ELIGIBLE": 0, "NEAR_ELIGIBLE": 0, "NEEDS_CONFIRMATION": 0, "INELIGIBLE": 0}

            for app in applications:
                prof = app.profile
                prof_data = {
                    "age": prof.age,
                    "gender": prof.gender,
                    "state": prof.state,
                    "district": prof.district,
                    "is_maharashtra_domicile": prof.is_maharashtra_domicile,
                    "caste_category": prof.caste_category,
                    "annual_family_income": prof.annual_family_income,
                    "current_course_level": prof.current_course_level,
                    "admission_quota": prof.admission_quota,
                    "accommodation_type": prof.accommodation_type,
                    "parent_is_farmer": prof.parent_is_farmer,
                    "parent_land_acres": prof.parent_land_acres,
                    "previous_year_percentage": prof.previous_year_percentage,
                }
                eval_res = RuleEngine.evaluate_scheme(scheme, prof_data)
                st = eval_res.get("status", "INELIGIBLE")
                counts[st] = counts.get(st, 0) + 1

                results.append({
                    "application_id": str(app.id),
                    "student_name": prof.name,
                    "new_evaluation_status": st,
                    "previous_tracker_status": app.status,
                    "reasons": [c["reason"] for c in eval_res.get("passed_criteria", [])] + [c["reason"] for c in eval_res.get("failed_criteria", [])]
                })

            return Response({
                "scheme_code": scheme.code,
                "scheme_version": scheme.version,
                "total_applications_re_evaluated": len(applications),
                "summary": counts,
                "details": results
            })
        except Scheme.DoesNotExist:
            return Response({"error": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)
