from django.core.management.base import BaseCommand
from core.models import EmissionFactor


class Command(BaseCommand):
    help = 'Seed the database with default emission factors'

    def handle(self, *args, **options):
        # Standard emission factors based on various sources
        # Sources: EPA, IPCC, India GHG Program
        
        emission_factors = [
            # Electricity (India Grid Average)
            {
                'category': 'ELECTRICITY',
                'sub_category': 'GRID',
                'factor': 0.82,
                'unit': 'kWh',
                'description': 'CO2 emissions from Indian grid electricity',
                'source': 'India GHG Program / CEA 2023',
            },
            
            # Fuels
            {
                'category': 'FUEL',
                'sub_category': 'DIESEL',
                'factor': 2.68,
                'unit': 'liter',
                'description': 'CO2 emissions from diesel combustion',
                'source': 'IPCC 2006 Guidelines',
            },
            {
                'category': 'FUEL',
                'sub_category': 'PETROL',
                'factor': 2.31,
                'unit': 'liter',
                'description': 'CO2 emissions from petrol/gasoline combustion',
                'source': 'IPCC 2006 Guidelines',
            },
            {
                'category': 'FUEL',
                'sub_category': 'LPG',
                'factor': 2.98,
                'unit': 'kg',
                'description': 'CO2 emissions from LPG combustion',
                'source': 'IPCC 2006 Guidelines',
            },
            {
                'category': 'FUEL',
                'sub_category': 'CNG',
                'factor': 2.75,
                'unit': 'kg',
                'description': 'CO2 emissions from CNG combustion',
                'source': 'IPCC 2006 Guidelines',
            },
            
            # Water
            {
                'category': 'WATER',
                'sub_category': 'MUNICIPAL_WATER',
                'factor': 0.344,
                'unit': 'kL',
                'description': 'CO2 emissions from water treatment and distribution',
                'source': 'Water Research Foundation',
            },
            
            # Waste
            {
                'category': 'WASTE',
                'sub_category': 'ORGANIC_WASTE',
                'factor': 0.58,
                'unit': 'kg',
                'description': 'CO2e emissions from organic waste decomposition',
                'source': 'EPA WARM Model',
            },
            {
                'category': 'WASTE',
                'sub_category': 'PLASTIC_WASTE',
                'factor': 6.0,
                'unit': 'kg',
                'description': 'CO2e emissions from plastic waste (lifecycle)',
                'source': 'EPA WARM Model',
            },
            {
                'category': 'WASTE',
                'sub_category': 'E_WASTE',
                'factor': 2.0,
                'unit': 'kg',
                'description': 'CO2e emissions from e-waste processing',
                'source': 'Estimated',
            },
            {
                'category': 'WASTE',
                'sub_category': 'GENERAL_WASTE',
                'factor': 0.58,
                'unit': 'kg',
                'description': 'CO2e emissions from general mixed waste',
                'source': 'EPA WARM Model',
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for ef_data in emission_factors:
            obj, created = EmissionFactor.objects.update_or_create(
                category=ef_data['category'],
                sub_category=ef_data['sub_category'],
                defaults={
                    'factor': ef_data['factor'],
                    'unit': ef_data['unit'],
                    'description': ef_data['description'],
                    'source': ef_data['source'],
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded emission factors: {created_count} created, {updated_count} updated'
            )
        )
