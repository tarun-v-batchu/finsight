from rest_framework import serializers

from .models import SupportCase, CaseInteraction


class SupportCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportCase
        fields = [
            "case_id",
            "description",
            "predicted_case_type",
            "confidence_score",
            "is_processed",
            "created_at",
            "resolved_at",
            "resolution_outcome",
        ]
        read_only_fields = [
            "case_id",
            "predicted_case_type",
            "confidence_score",
            "is_processed",
            "created_at",
            "resolved_at",
            "resolution_outcome",
        ]


class CaseInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseInteraction
        fields = ["id", "case", "interaction_text", "timestamp", "is_user"]
        read_only_fields = ["id", "timestamp"]
