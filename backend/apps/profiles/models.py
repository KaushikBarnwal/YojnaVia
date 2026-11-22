import uuid
from django.db import models

class StudentProfile(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    CASTE_CHOICES = [
        ('OPEN', 'Open / General'),
        ('OBC', 'Other Backward Class (OBC)'),
        ('SC', 'Scheduled Caste (SC)'),
        ('ST', 'Scheduled Tribe (ST)'),
        ('VJNT', 'Vimukta Jati & Nomadic Tribes (VJNT)'),
        ('SBC', 'Special Backward Class (SBC)'),
        ('EWS', 'Economically Weaker Section (EWS)'),
    ]

    COURSE_LEVEL_CHOICES = [
        ('11TH_12TH', '11th - 12th / Junior College'),
        ('DIPLOMA', 'Polytechnic Diploma'),
        ('UNDERGRADUATE', 'Undergraduate Degree (BA/B.Sc/B.Com)'),
        ('PROFESSIONAL_DEGREE', 'Professional Degree (Engineering, Medical, Pharmacy, MBA)'),
        ('POSTGRADUATE', 'Postgraduate (MA/M.Sc/M.Tech)'),
    ]

    ADMISSION_QUOTA_CHOICES = [
        ('CAP_ROUND', 'Centralized Admission Process (CAP / Merit Round)'),
        ('INSTITUTE_QUOTA', 'Institutional / Management Quota'),
        ('DIRECT_SECOND_YEAR', 'Direct Second Year (DSE) via CAP'),
    ]

    ACCOMMODATION_CHOICES = [
        ('DAY_SCHOLAR', 'Day Scholar (Living at home with parents)'),
        ('GOVT_HOSTEL', 'Government / University Hostel Resident'),
        ('PRIVATE_RENTAL_PG', 'Private Rented Room / Paying Guest / Non-Govt Hostel'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_token = models.CharField(max_length=128, db_index=True)
    name = models.CharField(max_length=100, default='Student')

    # Demographics
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='MALE')
    state = models.CharField(max_length=50, default='Maharashtra')
    district = models.CharField(max_length=50, default='Pune')
    is_maharashtra_domicile = models.BooleanField(default=True)

    # Social & Economic
    caste_category = models.CharField(max_length=10, choices=CASTE_CHOICES, default='OPEN')
    caste_name = models.CharField(max_length=100, blank=True)
    annual_family_income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    has_ration_card = models.BooleanField(default=True)
    ration_card_type = models.CharField(max_length=20, default='ORANGE_BPL')

    # Academic & Admission
    current_course_level = models.CharField(max_length=30, choices=COURSE_LEVEL_CHOICES, default='PROFESSIONAL_DEGREE')
    course_name = models.CharField(max_length=120, blank=True, default='Engineering / Technology')
    admission_quota = models.CharField(max_length=30, choices=ADMISSION_QUOTA_CHOICES, default='CAP_ROUND')
    previous_year_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Housing & Family Background
    accommodation_type = models.CharField(max_length=30, choices=ACCOMMODATION_CHOICES, default='DAY_SCHOLAR')
    parent_is_farmer = models.BooleanField(default=False)
    parent_land_acres = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    # Vulnerability & Readiness
    has_disability = models.BooleanField(default=False)
    disability_percentage = models.IntegerField(default=0)
    has_aadhaar_seeded_bank = models.BooleanField(default=True)

    # Human-in-the-Loop Confidence & Confirmation
    is_confirmed = models.BooleanField(default=False)
    field_confidence_scores = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.caste_category}, ₹{self.annual_family_income})"
