from rest_framework import serializers
from startups.serializers import StartupProfileSerializer

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    startup = StartupProfileSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'startup',
            'title',
            'description',
            'funding_goal',
            'funding_needed',
            'status',
            'status_display',
            'duration',
            'created_at',
            'updated_at',
            'business_plan',
            'media_files',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_display']

    def get_status_display(self, obj):
        return obj.get_status_display()


class CreateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'startup',
            'title',
            'description',
            'funding_goal',
            'funding_needed',
            'status',
            'duration',
            'business_plan',
            'media_files',
        ]

    def validate_funding_needed(self, value):
        if 'funding_goal' in self.initial_data:
            funding_goal = float(self.initial_data['funding_goal'])
            if value > funding_goal:
                raise serializers.ValidationError("Funding needed cannot exceed funding goal.")
        return value


class UpdateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'funding_goal',
            'funding_needed',
            'status',
            'duration',
            'business_plan',
            'media_files',
        ]

    def validate(self, data):
        funding_needed = data.get('funding_needed', None)
        funding_goal = data.get('funding_goal', None)

        if funding_needed is not None and funding_goal is not None and funding_needed > funding_goal:
            raise serializers.ValidationError("Funding needed cannot exceed funding goal.")
        return data
