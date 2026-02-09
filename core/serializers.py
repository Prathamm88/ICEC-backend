from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EmissionFactor, ConsumptionRecord

Institute = get_user_model()


class InstituteSerializer(serializers.ModelSerializer):
    """Serializer for Institute registration and profile."""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = Institute
        fields = ['id', 'username', 'email', 'password', 'institute_name', 'address', 'city', 'state']
        extra_kwargs = {
            'email': {'required': True},
            'institute_name': {'required': True},
        }
    
    def create(self, validated_data):
        user = Institute.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            institute_name=validated_data.get('institute_name', ''),
            address=validated_data.get('address', ''),
            city=validated_data.get('city', ''),
            state=validated_data.get('state', ''),
        )
        return user


class InstituteProfileSerializer(serializers.ModelSerializer):
    """Read-only profile serializer."""
    class Meta:
        model = Institute
        fields = ['id', 'username', 'email', 'institute_name', 'address', 'city', 'state', 'created_at']
        read_only_fields = fields


class EmissionFactorSerializer(serializers.ModelSerializer):
    """Serializer for EmissionFactor."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    sub_category_display = serializers.CharField(source='get_sub_category_display', read_only=True)
    
    class Meta:
        model = EmissionFactor
        fields = ['id', 'category', 'category_display', 'sub_category', 'sub_category_display', 
                  'factor', 'unit', 'description', 'source']


class ConsumptionRecordSerializer(serializers.ModelSerializer):
    """Serializer for ConsumptionRecord."""
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    
    class Meta:
        model = ConsumptionRecord
        fields = [
            'id', 'department', 'department_display', 'date',
            'electricity_kwh', 'diesel_liters', 'petrol_liters', 'lpg_kg',
            'water_kl', 'waste_kg',
            'electricity_emissions', 'fuel_emissions', 'water_emissions', 'waste_emissions',
            'total_emissions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['electricity_emissions', 'fuel_emissions', 'water_emissions', 
                           'waste_emissions', 'total_emissions', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['institute'] = self.context['request'].user
        return super().create(validated_data)


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    total_emissions = serializers.FloatField()
    electricity_emissions = serializers.FloatField()
    fuel_emissions = serializers.FloatField()
    water_emissions = serializers.FloatField()
    waste_emissions = serializers.FloatField()
    department_breakdown = serializers.DictField()
    monthly_trend = serializers.ListField()
    record_count = serializers.IntegerField()


class MonthlyTrendSerializer(serializers.Serializer):
    """Serializer for monthly trend data."""
    month = serializers.CharField()
    total_emissions = serializers.FloatField()
    electricity_emissions = serializers.FloatField()
    fuel_emissions = serializers.FloatField()
    water_emissions = serializers.FloatField()
    waste_emissions = serializers.FloatField()
