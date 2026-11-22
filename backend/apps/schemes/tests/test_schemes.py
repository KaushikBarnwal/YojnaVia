import datetime
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db.utils import IntegrityError
from django.test import TestCase
from apps.schemes.models import Scheme, RequiredDocument, EligibilityRule
from apps.citizens.models import VerificationLog

class SchemeModelConstraintTestCase(TestCase):
    def test_sample_cannot_be_verified(self):
        """A sample scheme must never have verification_status='VERIFIED'."""
        scheme = Scheme(
            code="TEST-SAMPLE-FAIL",
            name="Sample Scheme",
            statutory_gr="GR-123",
            benefit_type="TUITION_FEE_WAIVER",
            benefit_amount_text="100%",
            brief_description="Desc",
            is_sample=True,
            verification_status="VERIFIED",
            official_source_url="https://gov.in",
            last_verified_on=datetime.date.today()
        )
        with self.assertRaises((ValidationError, IntegrityError)):
            scheme.full_clean()
            scheme.save()

    def test_verified_needs_source_url_and_date(self):
        """A verified scheme must have an official_source_url and last_verified_on."""
        # Missing source url
        scheme = Scheme(
            code="TEST-VERIFIED-NO-URL",
            name="Verified Scheme",
            statutory_gr="GR-123",
            benefit_type="TUITION_FEE_WAIVER",
            benefit_amount_text="100%",
            brief_description="Desc",
            is_sample=False,
            verification_status="VERIFIED",
            last_verified_on=datetime.date.today(),
            official_source_url=""
        )
        with self.assertRaises((ValidationError, IntegrityError)):
            scheme.full_clean()
            scheme.save()

    def test_valid_verified_scheme(self):
        """A properly documented non-sample scheme saves as VERIFIED cleanly."""
        scheme = Scheme.objects.create(
            code="TEST-VERIFIED-OK",
            name="Official Valid Scheme",
            statutory_gr="GR-2024-OFFICIAL",
            benefit_type="TUITION_FEE_WAIVER",
            benefit_amount_text="Full waiver",
            brief_description="Official Government Scheme",
            is_sample=False,
            verification_status="VERIFIED",
            official_source_url="https://maharashtra.gov.in/gr/123",
            last_verified_on=datetime.date.today()
        )
        self.assertEqual(scheme.verification_status, "VERIFIED")

    def test_eligibility_rule_validation(self):
        """Test rule operator validation."""
        scheme = Scheme.objects.create(
            code="TEST-RULES-SCHEME",
            name="Rule Test Scheme",
            statutory_gr="GR-1",
            benefit_type="MAINTENANCE_STIPEND",
            benefit_amount_text="₹1,000",
            brief_description="Desc"
        )

        # In operator requires a list
        bad_rule = EligibilityRule(
            scheme=scheme,
            code="R1",
            field="category",
            operator="in",
            value="NOT_A_LIST",
            description="Must fail"
        )
        with self.assertRaises(ValidationError):
            bad_rule.clean()

        # Numeric operator requires numeric value
        bad_numeric = EligibilityRule(
            scheme=scheme,
            code="R2",
            field="age",
            operator="gte",
            value="twenty",
            description="Must fail"
        )
        with self.assertRaises(ValidationError):
            bad_numeric.clean()

    def test_seed_ps5_samples_command(self):
        """Test seed_ps5_samples management command."""
        call_command('seed_ps5_samples')
        samples = Scheme.objects.filter(is_sample=True)
        self.assertGreaterEqual(samples.count(), 10)
        
        first = samples.first()
        self.assertTrue(first.code.startswith("SAMPLE-"))
        self.assertEqual(first.verification_status, "UNVERIFIED")
        self.assertGreater(first.required_documents.count(), 0)
        self.assertGreater(first.eligibility_rules.count(), 0)
