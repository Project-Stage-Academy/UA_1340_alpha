from rest_framework import serializers
from .models import Industry, StartupProfile, StartupIndustry
from users.serializers import UserSerializer

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name']


class StartupProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    industries = IndustrySerializer(many=True, read_only=True)

    class Meta:
        model = StartupProfile
        fields = [
            'id',
            'user',
            'company_name',
            'description',
            'website',
            'contact_email',
            'created_at',
            'startup_logo',
            'industries',
        ]
        read_only_fields = ['id', 'created_at']


class CreateStartupProfileSerializer(serializers.ModelSerializer):
    industries = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Industry.objects.all()
    )

    class Meta:
        model = StartupProfile
        fields = [
            'id',
            'user',
            'company_name',
            'description',
            'website',
            'contact_email',
            'startup_logo',
            'industries',
        ]
        read_only_fields = ('id', )

    def validate_industries(self, value):
        if not value:
            raise serializers.ValidationError("At least one industry must be selected.")
        return value


class StartupIndustrySerializer(serializers.ModelSerializer):
    startup = serializers.StringRelatedField()
    industry = serializers.StringRelatedField()

    class Meta:
        model = StartupIndustry
        fields = ['id', 'startup', 'industry']
