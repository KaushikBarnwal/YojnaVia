import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentProfile
from .serializers import StudentProfileSerializer

DEMO_PERSONAS = {
    "rohan_obc": {
        "name": "Rohan Gaikwad (OBC Engineering Student)",
        "age": 20,
        "gender": "MALE",
        "state": "Maharashtra",
        "district": "Sangli",
        "is_maharashtra_domicile": True,
        "caste_category": "OBC",
        "caste_name": "Kunbi",
        "annual_family_income": 110000.00,
        "current_course_level": "PROFESSIONAL_DEGREE",
        "course_name": "B.Tech Mechanical Engineering (Pune)",
        "admission_quota": "CAP_ROUND",
        "previous_year_percentage": 78.50,
        "accommodation_type": "PRIVATE_RENTAL_PG",
        "parent_is_farmer": True,
        "parent_land_acres": 2.20,
        "has_aadhaar_seeded_bank": True,
        "is_confirmed": True
    },
    "sneha_ebc": {
        "name": "Sneha Kulkarni (General/Open EBC Pharmacy)",
        "age": 19,
        "gender": "FEMALE",
        "state": "Maharashtra",
        "district": "Nashik",
        "is_maharashtra_domicile": True,
        "caste_category": "OPEN",
        "caste_name": "Maratha",
        "annual_family_income": 320000.00,
        "current_course_level": "PROFESSIONAL_DEGREE",
        "course_name": "Bachelor of Pharmacy (B.Pharm)",
        "admission_quota": "CAP_ROUND",
        "previous_year_percentage": 82.00,
        "accommodation_type": "DAY_SCHOLAR",
        "parent_is_farmer": False,
        "parent_land_acres": 0.00,
        "has_aadhaar_seeded_bank": True,
        "is_confirmed": True
    },
    "vikas_sc": {
        "name": "Vikas Kamble (SC Polytechnic Student)",
        "age": 18,
        "gender": "MALE",
        "state": "Maharashtra",
        "district": "Solapur",
        "is_maharashtra_domicile": True,
        "caste_category": "SC",
        "caste_name": "Navboudha",
        "annual_family_income": 65000.00,
        "current_course_level": "DIPLOMA",
        "course_name": "Diploma in Civil Engineering",
        "admission_quota": "CAP_ROUND",
        "previous_year_percentage": 68.00,
        "accommodation_type": "PRIVATE_RENTAL_PG",
        "parent_is_farmer": False,
        "parent_land_acres": 0.00,
        "has_aadhaar_seeded_bank": True,
        "is_confirmed": True
    },
    "pooja_borderline": {
        "name": "Pooja Patil (Borderline Income Case)",
        "age": 21,
        "gender": "FEMALE",
        "state": "Maharashtra",
        "district": "Kolhapur",
        "is_maharashtra_domicile": True,
        "caste_category": "OBC",
        "caste_name": "Mali",
        "annual_family_income": 165000.00,  # Exceeds 1.5L cutoff by 15k
        "current_course_level": "POSTGRADUATE",
        "course_name": "M.Sc Biotechnology",
        "admission_quota": "CAP_ROUND",
        "previous_year_percentage": 74.00,
        "accommodation_type": "DAY_SCHOLAR",
        "parent_is_farmer": False,
        "parent_land_acres": 0.00,
        "has_aadhaar_seeded_bank": True,
        "is_confirmed": True
    }
}

class ProfileMeView(APIView):
    def get(self, request):
        session_token = request.query_params.get('session_token')
        if not session_token:
            session_token = str(uuid.uuid4())

        profile, created = StudentProfile.objects.get_or_create(
            session_token=session_token,
            defaults={"name": "New Student"}
        )
        serializer = StudentProfileSerializer(profile)
        return Response({
            "session_token": session_token,
            "is_new": created,
            "profile": serializer.data
        })

    def put(self, request):
        session_token = request.data.get('session_token')
        if not session_token:
            return Response({"error": "session_token required"}, status=status.HTTP_400_BAD_REQUEST)

        profile, _ = StudentProfile.objects.get_or_create(session_token=session_token)
        serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Synchronize confirmed edits to IntakeConversation state if present
            try:
                from apps.ai_assistant.models import IntakeConversation
                conv = IntakeConversation.objects.filter(session_token=session_token).first()
                if conv:
                    updated_fields = dict(conv.fields or {})
                    if 'age' in request.data:
                        updated_fields['age'] = {"value": profile.age, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "user_edit"}
                    if 'district' in request.data:
                        updated_fields['district'] = {"value": profile.district, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "user_edit"}
                    if 'caste_category' in request.data:
                        caste_str = "general" if profile.caste_category in ("OPEN", "GENERAL") else str(profile.caste_category).lower()
                        updated_fields['social_category'] = {"value": caste_str, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "user_edit"}
                    if 'annual_family_income' in request.data:
                        inc = float(profile.annual_family_income)
                        band = "below_1_lakh" if inc < 100000 else ("1_to_2_5_lakh" if inc <= 250000 else ("2_5_to_5_lakh" if inc <= 500000 else ("5_to_8_lakh" if inc <= 800000 else "above_8_lakh")))
                        updated_fields['income_band'] = {"value": band, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "user_edit"}
                    conv.fields = updated_fields
                    conv.save()
            except Exception:
                pass

            return Response({"status": "UPDATED", "profile": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    post = put

class LoadPersonaView(APIView):
    def post(self, request):
        persona_key = request.data.get('persona_key', 'rohan_obc')
        session_token = request.data.get('session_token', str(uuid.uuid4()))

        if persona_key not in DEMO_PERSONAS:
            return Response({"error": f"Invalid persona key. Options: {list(DEMO_PERSONAS.keys())}"}, status=status.HTTP_400_BAD_REQUEST)

        persona_data = DEMO_PERSONAS[persona_key]
        profile, _ = StudentProfile.objects.update_or_create(
            session_token=session_token,
            defaults=persona_data
        )

        # Synchronize persona attributes to AI Intake conversation state
        try:
            from apps.ai_assistant.models import IntakeConversation
            conv, _ = IntakeConversation.objects.get_or_create(session_token=session_token)
            income_val = float(profile.annual_family_income)
            income_band = "below_1_lakh" if income_val < 100000 else ("1_to_2_5_lakh" if income_val <= 250000 else ("2_5_to_5_lakh" if income_val <= 500000 else ("5_to_8_lakh" if income_val <= 800000 else "above_8_lakh")))
            edu_map = {
                "PROFESSIONAL_DEGREE": "undergraduate",
                "UNDERGRADUATE": "undergraduate",
                "POSTGRADUATE": "postgraduate",
                "DIPLOMA": "diploma",
                "11TH_12TH": "12th_pass"
            }
            caste_val = "general" if profile.caste_category in ("OPEN", "GENERAL") else str(profile.caste_category).lower()
            conv.fields = {
                "age": {"value": profile.age, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "persona_load"},
                "state": {"value": profile.state, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "persona_load"},
                "district": {"value": profile.district, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "persona_load"},
                "occupation": {"value": "Student", "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "persona_load"},
                "education_level": {"value": edu_map.get(profile.current_course_level, "undergraduate"), "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "persona_load"},
                "income_band": {"value": income_band, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "persona_load"},
                "social_category": {"value": caste_val, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "persona_load"},
                "disability_status": {"value": profile.has_disability, "status": "known", "confidence": 1.0, "user_confirmed": True, "source": "persona_load"},
            }
            conv.history = [
                {"role": "assistant", "text": f"Loaded demo persona '{persona_data['name']}'. Profile parameters and verified facts are now loaded into your session."}
            ]
            conv.save()
        except Exception:
            pass

        serializer = StudentProfileSerializer(profile)
        return Response({
            "message": f"Loaded demo persona '{persona_data['name']}'",
            "session_token": session_token,
            "profile": serializer.data
        })

class PersonasListAPIView(APIView):
    def get(self, request):
        return Response({
            "personas": [
                {
                    "key": "rohan_obc",
                    "name": "Rohan Gaikwad (OBC Engineering)",
                    "tag": "Max Bundle: Tuition + Hostel",
                    "details": "20yo Male, Sangli, B.Tech Mech, ₹1.1L income, Rental room in Pune, Farmer parents (2.2 acres)"
                },
                {
                    "key": "sneha_ebc",
                    "name": "Sneha Kulkarni (General/Open EBC Pharmacy)",
                    "tag": "EBC 50% Tuition Fee Reimbursement",
                    "details": "19yo Female, Nashik, B.Pharm, ₹3.2L income, General Category, Day Scholar"
                },
                {
                    "key": "vikas_sc",
                    "name": "Vikas Kamble (SC Polytechnic)",
                    "tag": "100% Free Tuition + Swadhar ₹51k",
                    "details": "18yo Male, Solapur, Civil Diploma, ₹65k income, SC category, Rented room (Hostel unavailable)"
                },
                {
                    "key": "pooja_borderline",
                    "name": "Pooja Patil (Borderline Income)",
                    "tag": "Near-Eligible Boundary Demonstration",
                    "details": "21yo Female, Kolhapur, M.Sc, ₹1.65L income (Exceeds ₹1.5L cutoff by ₹15k, routed to 50% Freeship)"
                }
            ]
        })
