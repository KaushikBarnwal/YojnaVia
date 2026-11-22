import uuid
from django.db import models
from apps.schemes.models import Scheme

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    name_marathi = models.CharField(max_length=255, blank=True)
    issuing_authority = models.CharField(max_length=255)
    procurement_portal = models.CharField(max_length=255, default='aaplesarkar.mahaonline.gov.in')
    estimated_sla_days = models.IntegerField(default=15, help_text="Official citizen service delivery SLA in working days")
    validity_duration = models.CharField(max_length=100, default='1 Financial Year')
    
    # Prerequisite civil documents needed to apply for this document
    prerequisite_documents = models.JSONField(default=list, blank=True)
    how_to_obtain_steps = models.JSONField(default=list, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class SchemeDocumentRequirement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, related_name='document_requirements', on_delete=models.CASCADE)
    document = models.ForeignKey(Document, related_name='scheme_usages', on_delete=models.CASCADE)
    is_mandatory = models.BooleanField(default=True)
    specific_purpose = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('scheme', 'document')

    def __str__(self):
        return f"{self.scheme.code} -> {self.document.code}"
