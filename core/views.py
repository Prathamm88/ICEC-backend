from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

from .models import EmissionFactor, ConsumptionRecord
from .serializers import (
    InstituteSerializer, InstituteProfileSerializer,
    EmissionFactorSerializer, ConsumptionRecordSerializer
)

Institute = get_user_model()


class RegisterView(generics.CreateAPIView):
    """API endpoint for institute registration."""
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveAPIView):
    """API endpoint to get current user profile."""
    serializer_class = InstituteProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class EmissionFactorListView(generics.ListAPIView):
    """API endpoint to list all emission factors."""
    queryset = EmissionFactor.objects.all()
    serializer_class = EmissionFactorSerializer
    permission_classes = [permissions.IsAuthenticated]


class ConsumptionRecordListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create consumption records."""
    serializer_class = ConsumptionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ConsumptionRecord.objects.filter(institute=self.request.user)


class ConsumptionRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update, or delete a consumption record."""
    serializer_class = ConsumptionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ConsumptionRecord.objects.filter(institute=self.request.user)


class DashboardStatsView(APIView):
    """API endpoint for dashboard statistics."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        records = ConsumptionRecord.objects.filter(institute=request.user)
        
        # Get date filter from query params
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if year:
            records = records.filter(date__year=int(year))
        if month:
            records = records.filter(date__month=int(month))
        
        # Aggregate totals
        totals = records.aggregate(
            total_emissions=Sum('total_emissions'),
            electricity_emissions=Sum('electricity_emissions'),
            fuel_emissions=Sum('fuel_emissions'),
            water_emissions=Sum('water_emissions'),
            waste_emissions=Sum('waste_emissions'),
        )
        
        # Department breakdown
        department_data = records.values('department').annotate(
            total=Sum('total_emissions')
        ).order_by('department')
        
        department_breakdown = {
            item['department']: round(item['total'] or 0, 2) 
            for item in department_data
        }
        
        # Monthly trend (last 12 months)
        twelve_months_ago = timezone.now().date() - timedelta(days=365)
        monthly_data = (
            ConsumptionRecord.objects
            .filter(institute=request.user, date__gte=twelve_months_ago)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(
                total_emissions=Sum('total_emissions'),
                electricity_emissions=Sum('electricity_emissions'),
                fuel_emissions=Sum('fuel_emissions'),
                water_emissions=Sum('water_emissions'),
                waste_emissions=Sum('waste_emissions'),
            )
            .order_by('month')
        )
        
        monthly_trend = [
            {
                'month': item['month'].strftime('%Y-%m') if item['month'] else '',
                'total_emissions': round(item['total_emissions'] or 0, 2),
                'electricity_emissions': round(item['electricity_emissions'] or 0, 2),
                'fuel_emissions': round(item['fuel_emissions'] or 0, 2),
                'water_emissions': round(item['water_emissions'] or 0, 2),
                'waste_emissions': round(item['waste_emissions'] or 0, 2),
            }
            for item in monthly_data
        ]
        
        return Response({
            'total_emissions': round(totals['total_emissions'] or 0, 2),
            'electricity_emissions': round(totals['electricity_emissions'] or 0, 2),
            'fuel_emissions': round(totals['fuel_emissions'] or 0, 2),
            'water_emissions': round(totals['water_emissions'] or 0, 2),
            'waste_emissions': round(totals['waste_emissions'] or 0, 2),
            'department_breakdown': department_breakdown,
            'monthly_trend': monthly_trend,
            'record_count': records.count(),
        })


class ComparisonView(APIView):
    """API endpoint for department comparison."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        records = ConsumptionRecord.objects.filter(institute=request.user)
        
        # Get comparison data by department
        comparison = records.values('department').annotate(
            total_emissions=Sum('total_emissions'),
            electricity_emissions=Sum('electricity_emissions'),
            fuel_emissions=Sum('fuel_emissions'),
            water_emissions=Sum('water_emissions'),
            waste_emissions=Sum('waste_emissions'),
            electricity_kwh=Sum('electricity_kwh'),
            diesel_liters=Sum('diesel_liters'),
            petrol_liters=Sum('petrol_liters'),
            lpg_kg=Sum('lpg_kg'),
            water_kl=Sum('water_kl'),
            waste_kg=Sum('waste_kg'),
        ).order_by('department')
        
        result = []
        dept_names = dict(ConsumptionRecord.DEPARTMENT_CHOICES)
        
        for item in comparison:
            result.append({
                'department': item['department'],
                'department_name': dept_names.get(item['department'], item['department']),
                'total_emissions': round(item['total_emissions'] or 0, 2),
                'electricity_emissions': round(item['electricity_emissions'] or 0, 2),
                'fuel_emissions': round(item['fuel_emissions'] or 0, 2),
                'water_emissions': round(item['water_emissions'] or 0, 2),
                'waste_emissions': round(item['waste_emissions'] or 0, 2),
                'consumption': {
                    'electricity_kwh': round(item['electricity_kwh'] or 0, 2),
                    'diesel_liters': round(item['diesel_liters'] or 0, 2),
                    'petrol_liters': round(item['petrol_liters'] or 0, 2),
                    'lpg_kg': round(item['lpg_kg'] or 0, 2),
                    'water_kl': round(item['water_kl'] or 0, 2),
                    'waste_kg': round(item['waste_kg'] or 0, 2),
                }
            })
        
        return Response(result)


class GenerateReportView(APIView):
    """API endpoint to generate PDF reports."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        institute = request.user
        records = ConsumptionRecord.objects.filter(institute=institute)
        
        # Get date filters
        year = request.query_params.get('year')
        if year:
            records = records.filter(date__year=int(year))
        
        # Aggregate data
        totals = records.aggregate(
            total_emissions=Sum('total_emissions'),
            electricity_emissions=Sum('electricity_emissions'),
            fuel_emissions=Sum('fuel_emissions'),
            water_emissions=Sum('water_emissions'),
            waste_emissions=Sum('waste_emissions'),
        )
        
        department_data = records.values('department').annotate(
            total=Sum('total_emissions')
        ).order_by('department')
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a365d'),
            alignment=1,
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2b6cb0'),
        )
        
        story = []
        
        # Title
        story.append(Paragraph("Carbon Emissions Report", title_style))
        story.append(Paragraph(f"<b>Institute:</b> {institute.institute_name or institute.username}", styles['Normal']))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        if year:
            story.append(Paragraph(f"<b>Period:</b> Year {year}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary Section
        story.append(Paragraph("Executive Summary", heading_style))
        
        summary_data = [
            ['Emission Category', 'Value (kg CO2e)'],
            ['Total Emissions', f"{totals['total_emissions'] or 0:,.2f}"],
            ['Electricity', f"{totals['electricity_emissions'] or 0:,.2f}"],
            ['Fuel', f"{totals['fuel_emissions'] or 0:,.2f}"],
            ['Water', f"{totals['water_emissions'] or 0:,.2f}"],
            ['Waste', f"{totals['waste_emissions'] or 0:,.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ebf8ff')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bee3f8')),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Department Breakdown
        story.append(Paragraph("Department-wise Breakdown", heading_style))
        
        dept_names = dict(ConsumptionRecord.DEPARTMENT_CHOICES)
        dept_data = [['Department', 'Emissions (kg CO2e)']]
        for item in department_data:
            dept_data.append([
                dept_names.get(item['department'], item['department']),
                f"{item['total'] or 0:,.2f}"
            ])
        
        if len(dept_data) > 1:
            dept_table = Table(dept_data, colWidths=[3*inch, 2*inch])
            dept_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38a169')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fff4')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#9ae6b4')),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            story.append(dept_table)
        else:
            story.append(Paragraph("No department data available.", styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Recommendations
        story.append(Paragraph("Recommendations", heading_style))
        
        recommendations = [
            "• Switch to LED lighting in high-consumption areas to reduce electricity usage.",
            "• Implement rainwater harvesting to reduce municipal water dependency.",
            "• Set up composting facilities for organic waste management.",
            "• Consider solar panels for renewable energy generation.",
            "• Promote public transport and carpooling among staff and students.",
        ]
        
        for rec in recommendations:
            story.append(Paragraph(rec, styles['Normal']))
            story.append(Spacer(1, 5))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Create response
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"carbon_report_{institute.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
