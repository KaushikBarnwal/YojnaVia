import uuid
from django.db import models
from apps.profiles.models import StudentProfile
from apps.schemes.models import Scheme

class EligibilityAssessment(models.Model):
    STATUS_CHOICES = [
        ('LIKELY_ELIGIBLE', 'Likely Eligible'),
        ('NEAR_ELIGIBLE', 'Near-Eligible (Boundary Condition)'),
        ('NEEDS_CONFIRMATION', 'Needs Confirmation'),
        ('INELIGIBLE', 'Ineligible'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(StudentProfile, related_name='assessments', on_delete=models.CASCADE)
    scheme = models.ForeignKey(Scheme, related_name='assessments', on_delete=models.CASCADE)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    evaluation_matrix = models.JSONField(default=dict, help_text="Detailed passed, failed, near_eligible and missing criteria log")
    estimated_benefit_amount = models.IntegerField(default=0)
    
    assessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('profile', 'scheme')

    def __str__(self):
        return f"{self.profile.name} -> {self.scheme.code}: {self.status}"
