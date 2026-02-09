from django.db import models
from django.contrib.auth.models import AbstractUser


class Institute(AbstractUser):
    """Custom user model for institutes."""
    institute_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.institute_name or self.username


class EmissionFactor(models.Model):
    """Emission factors for different resource types."""
    
    CATEGORY_CHOICES = [
        ('ELECTRICITY', 'Electricity'),
        ('FUEL', 'Fuel'),
        ('WATER', 'Water'),
        ('WASTE', 'Waste'),
    ]
    
    SUB_CATEGORY_CHOICES = [
        ('GRID', 'Grid Electricity'),
        ('DIESEL', 'Diesel'),
        ('PETROL', 'Petrol'),
        ('LPG', 'LPG'),
        ('CNG', 'CNG'),
        ('MUNICIPAL_WATER', 'Municipal Water'),
        ('ORGANIC_WASTE', 'Organic Waste'),
        ('PLASTIC_WASTE', 'Plastic Waste'),
        ('E_WASTE', 'E-Waste'),
        ('GENERAL_WASTE', 'General Waste'),
    ]
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    sub_category = models.CharField(max_length=50, choices=SUB_CATEGORY_CHOICES)
    factor = models.FloatField(help_text="kg CO2e per unit")
    unit = models.CharField(max_length=50, help_text="e.g., kWh, liter, kg")
    description = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True, help_text="Data source reference")
    
    class Meta:
        unique_together = ['category', 'sub_category']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.get_sub_category_display()}: {self.factor} kg CO2e/{self.unit}"


class ConsumptionRecord(models.Model):
    """Records consumption data for each department."""
    
    DEPARTMENT_CHOICES = [
        ('HOSTEL', 'Hostel'),
        ('CANTEEN', 'Canteen'),
        ('ADMIN', 'Administration'),
        ('LABS', 'Laboratories'),
        ('TRANSPORT', 'Transport'),
    ]
    
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='consumption_records')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    date = models.DateField()
    
    # Consumption values
    electricity_kwh = models.FloatField(default=0, help_text="Electricity in kWh")
    diesel_liters = models.FloatField(default=0, help_text="Diesel consumption in liters")
    petrol_liters = models.FloatField(default=0, help_text="Petrol consumption in liters")
    lpg_kg = models.FloatField(default=0, help_text="LPG consumption in kg")
    water_kl = models.FloatField(default=0, help_text="Water consumption in kiloliters")
    waste_kg = models.FloatField(default=0, help_text="Waste generated in kg")
    
    # Calculated emissions (stored for historical accuracy)
    electricity_emissions = models.FloatField(default=0, help_text="kg CO2e from electricity")
    fuel_emissions = models.FloatField(default=0, help_text="kg CO2e from fuels")
    water_emissions = models.FloatField(default=0, help_text="kg CO2e from water")
    waste_emissions = models.FloatField(default=0, help_text="kg CO2e from waste")
    total_emissions = models.FloatField(default=0, help_text="Total kg CO2e")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['institute', 'department', 'date']
    
    def calculate_emissions(self):
        """Calculate emissions based on current emission factors."""
        factors = {ef.sub_category: ef.factor for ef in EmissionFactor.objects.all()}
        
        # Electricity emissions
        self.electricity_emissions = self.electricity_kwh * factors.get('GRID', 0.82)
        
        # Fuel emissions
        self.fuel_emissions = (
            self.diesel_liters * factors.get('DIESEL', 2.68) +
            self.petrol_liters * factors.get('PETROL', 2.31) +
            self.lpg_kg * factors.get('LPG', 2.98)
        )
        
        # Water emissions (typically low, but included)
        self.water_emissions = self.water_kl * factors.get('MUNICIPAL_WATER', 0.344)
        
        # Waste emissions
        self.waste_emissions = self.waste_kg * factors.get('GENERAL_WASTE', 0.58)
        
        # Total
        self.total_emissions = (
            self.electricity_emissions +
            self.fuel_emissions +
            self.water_emissions +
            self.waste_emissions
        )
        
        return self.total_emissions
    
    def save(self, *args, **kwargs):
        self.calculate_emissions()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.institute} - {self.department} - {self.date}"
