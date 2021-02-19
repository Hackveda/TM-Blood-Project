from django.contrib import admin

# import model
from .models import Document, Patient, Label, AlternateLabel, TestResult, GeneratedReportTestResult, FinalGeneratedReport, Category ,Comparison ,Report
# Register your models here.

admin.site.register(Patient)
admin.site.register(Report)
admin.site.register(TestResult)
admin.site.register(GeneratedReportTestResult)
admin.site.register(FinalGeneratedReport)
admin.site.register(Category)
admin.site.register(Comparison)

admin.site.register(Label)

@admin.register(AlternateLabel)
class AlternateLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'label')
    list_filter = ('label',)
    search_fields = ['name']
    pass

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at', 'patient')
