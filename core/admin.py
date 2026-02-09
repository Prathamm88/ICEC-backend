from django.contrib import admin
from .models import Institute, EmissionFactor, ConsumptionRecord


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ['username', 'institute_name', 'email', 'city', 'state', 'created_at']
    search_fields = ['username', 'institute_name', 'email']
    list_filter = ['state', 'created_at']


@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ['category', 'sub_category', 'factor', 'unit', 'source']
    list_filter = ['category']
    search_fields = ['sub_category', 'description']


@admin.register(ConsumptionRecord)
class ConsumptionRecordAdmin(admin.ModelAdmin):
    list_display = ['institute', 'department', 'date', 'total_emissions', 'created_at']
    list_filter = ['department', 'date', 'institute']
    search_fields = ['institute__username', 'institute__institute_name']
    date_hierarchy = 'date'
    readonly_fields = ['electricity_emissions', 'fuel_emissions', 'water_emissions', 
                       'waste_emissions', 'total_emissions']
