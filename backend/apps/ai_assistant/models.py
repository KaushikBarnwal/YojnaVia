from django.db import models

class IntakeConversation(models.Model):
    """Server-side Phase 3 intake state, keyed by the client session token."""
    session_token = models.CharField(max_length=128, unique=True, db_index=True)
    fields = models.JSONField(default=dict, blank=True)  # {field_name: {"value": ..., "status": "known"|"unknown", "confidence": float|None, "user_confirmed": bool, "source": str|None}}
    history = models.JSONField(default=list, blank=True)  # last 20 turns: [{"role": "user"|"assistant", "text": str}]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session_token
