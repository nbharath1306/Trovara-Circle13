from rest_framework import serializers
from .models import ResearchTask


class ResearchTaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the list view."""

    class Meta:
        model = ResearchTask
        fields = ["id", "topic", "status", "created_at"]


class ResearchTaskDetailSerializer(serializers.ModelSerializer):
    """Full serializer with all agent output fields."""

    class Meta:
        model = ResearchTask
        fields = [
            "id", "topic", "status",
            "created_at", "updated_at",
            "search_results", "summaries",
            "report", "error",
        ]
        read_only_fields = [
            "status", "created_at", "updated_at",
            "search_results", "summaries", "report", "error",
        ]
