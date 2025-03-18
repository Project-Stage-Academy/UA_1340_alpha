from django.db.models import Sum
from rest_framework import serializers

from projects.models import Project
from .models import InvestorProfile, InvestorPreferredIndustry, InvestorSavedStartup, InvestorTrackedProject
from startups.serializers import StartupProfileSerializer, IndustrySerializer
from projects.serializers import ProjectSerializer
from users.serializers import UserSerializer


class InvestorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = InvestorProfile
        fields = [
            'id',
            'user',
            'company_name',
            'investment_focus',
            'contact_email',
            'investment_range',
            'created_at',
            'investor_logo',
        ]
        read_only_fields = ['id', 'created_at']


class CreateInvestorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorProfile
        fields = [
            'id',
            'user',
            'company_name',
            'investment_focus',
            'contact_email',
            'investment_range',
            'investor_logo',
        ]
        read_only_fields = ('id',)


class InvestorPreferredIndustrySerializer(serializers.ModelSerializer):
    investor = InvestorProfileSerializer(read_only=True)
    industry = IndustrySerializer(read_only=True)

    class Meta:
        model = InvestorPreferredIndustry
        fields = [
            'id',
            'investor',
            'industry',
        ]


class CreateInvestorPreferredIndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorPreferredIndustry
        fields = [
            'id',
            'investor',
            'industry',
        ]
        read_only_fields = ('id',)


class InvestorSavedStartupSerializer(serializers.ModelSerializer):
    investor = InvestorProfileSerializer(read_only=True)
    startup = StartupProfileSerializer(read_only=True)

    class Meta:
        model = InvestorSavedStartup
        fields = [
            'id',
            'investor',
            'startup',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class CreateInvestorSavedStartupSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorSavedStartup
        fields = [
            'id',
            'investor',
            'startup',
        ]
        read_only_fields = ('id',)


class InvestorTrackedProjectSerializer(serializers.ModelSerializer):
    investor = InvestorProfileSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = InvestorTrackedProject
        fields = [
            'id',
            'investor',
            'project',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class CreateInvestorTrackedProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorTrackedProject
        fields = [
            'id',
            'investor',
            'project',
        ]

        read_only_fields = ('id',)


class SubscriptionSerializer(serializers.ModelSerializer):
    investor = serializers.PrimaryKeyRelatedField(queryset=InvestorProfile.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    investment_share = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100,
        help_text="Investment share in percentage (0 - 100%)"
    )

    class Meta:
        model = InvestorTrackedProject
        fields = ['investor', 'project', 'investment_share', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        project = data['project']
        new_share = data['investment_share']

        # Get the total current investment for the project
        total_current_share = InvestorTrackedProject.objects.filter(project=project).aggregate(
            total_investment=Sum('investment_share')
        )['total_investment'] or 0

        # Ensure new subscription does not exceed 100% funding
        if total_current_share + new_share > 100:
            raise serializers.ValidationError(
                {"investment_share": "Project is fully funded. No further subscriptions allowed."}
            )

        return data

    def create(self, validated_data):
        return InvestorTrackedProject.objects.create(**validated_data)
