from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for Ticket model with validation
    """
    class Meta:
        model = Ticket
        fields = [
            'id',
            'title',
            'description',
            'category',
            'priority',
            'status',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_title(self, value):
        """Ensure title is not empty after stripping whitespace"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()
    
    def validate_description(self, value):
        """Ensure description is not empty after stripping whitespace"""
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty")
        return value.strip()


class ClassificationRequestSerializer(serializers.Serializer):
    """
    Serializer for LLM classification request
    """
    description = serializers.CharField(required=True, allow_blank=False)
    
    def validate_description(self, value):
        """Ensure description is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty")
        return value.strip()


class ClassificationResponseSerializer(serializers.Serializer):
    """
    Serializer for LLM classification response
    """
    suggested_category = serializers.ChoiceField(
        choices=['billing', 'technical', 'account', 'general']
    )
    suggested_priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'critical']
    )
    classification_mode = serializers.ChoiceField(
        choices=['gemini', 'heuristic', 'hybrid'],
        required=False
    )
