from django.db import models

# Create your models here.
# triage/models.py

class SupportCase(models.Model):
    CASE_TYPES = [
        ('FRAUD', 'Fraud'),
        ('LOCKOUT', 'Account Lockout'),
        ('DISPUTE', 'Transaction Dispute'),
        ('OTHER', 'Other'),
    ]
    
    case_id = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    predicted_case_type = models.CharField(max_length=50, choices=CASE_TYPES)
    confidence_score = models.FloatField()
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_outcome = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.case_id} - {self.predicted_case_type}"

class CaseInteraction(models.Model):
    case = models.ForeignKey(SupportCase, on_delete=models.CASCADE)
    interaction_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_user = models.BooleanField(default=False)