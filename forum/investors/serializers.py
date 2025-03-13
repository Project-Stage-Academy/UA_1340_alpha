from rest_framework import serializers
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
        read_only_fields = ('id', )


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
        read_only_fields = ('id', )


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
        read_only_fields = ('id', )

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

        read_only_fields = ('id', )
