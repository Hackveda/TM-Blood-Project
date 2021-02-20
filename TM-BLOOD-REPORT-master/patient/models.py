from django.db import models
from django.utils import timezone
from django.conf import settings
import os
"""
database story
One patient can have multiple documents, One document can have only one Patient
One Label can have multiple Alternate label, One Alternate Label can have only one Label
TestResult can have only One ->(Label, Value, Unit, Document, Patient)
"""

class Report(models.Model):
    name = models.CharField(max_length=55,blank=False,null=False,unique=True)

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"{self.name}"


# Create your models here.
class Patient(models.Model):
    # required fields
    first_name = models.CharField(max_length=55, blank=False, null=False)
    last_name = models.CharField(max_length=55, blank=False, null=False)
    email = models.EmailField(max_length=255, blank=False, null=False, unique=True)


    # not required fields
    address = models.TextField(max_length=255, blank=True, null=True)
    postal_zip = models.IntegerField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.IntegerField(max_length=17, blank=True, null=True) # mobile
    alternate_number = models.IntegerField(max_length=17, blank=True, null=True) # alternate

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        super(Patient, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for i in FinalGeneratedReport.objects.filter(patient=self):
            os.remove(settings.MEDIA_ROOT.replace('/','//')+"//Generated_reports//"+str(i.id)+".pdf")
        super(Patient, self).delete(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Document(models.Model):
    name = models.CharField(max_length=15, blank=True)
    report = models.ForeignKey(to = Report,on_delete=models.SET_NULL,null=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE, unique=False)

    class Meta:
        unique_together = ('name', 'document', 'patient')

    # many document can have same patient

    def __str__(self) -> str:
        return f'{self.name}'

    def __repr__(self) -> str:
        return f'{self.name}'


class Label(models.Model):
    name = models.CharField(max_length=55, blank=True, unique=True)
    lower_range = models.FloatField(null=True, blank=True)
    upper_range = models.FloatField(null=True, blank=True)
    primary_unit = models.CharField(max_length=55)
    category = models.ForeignKey('Category', default=1, on_delete=models.SET_NULL, null=True)


    def save(self, *args, **kwargs):
        obj, created = Category.objects.get_or_create(name='Other', priority=0)
        if created:
            self.category = obj
        super(Label, self).save(*args, **kwargs)


    # value = models.CharField(max_length=55, blank=True)
    # unit = models.CharField(max_length=55, blank=True)
    # patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    # document = models.ForeignKey(to=Document, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"{self.name}"




class AlternateLabel(models.Model):
    name = models.CharField(max_length=55, blank=False, unique = False)
    label = models.ForeignKey(to=Label, on_delete=models.CASCADE)
    report = models.ForeignKey(to=Report, on_delete=models.SET_NULL,null=True)
    class Meta:
        unique_together  =('name', 'report')

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"{self.name}"

class TestResult(models.Model):
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE, unique=False)
    label = models.ForeignKey(to=Label, on_delete=models.CASCADE)
    value = models.CharField(max_length=10, blank=True)
    unit = models.CharField(max_length=55, blank=True)
    document = models.ForeignKey(to=Document, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('patient', 'document', 'label')
        ordering = ['label', 'document','patient']

    def __str__(self) -> str:
        return f"{self.label}-{self.patient}-{self.document}"

class FinalGeneratedReport(models.Model):
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    doc1 = models.ForeignKey(to=Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='generatedreport_doc1')
    doc2 = models.ForeignKey(to=Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='generatedreport_doc2')
    doc3 = models.ForeignKey(to=Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='generatedreport_doc3')
    doc4 = models.ForeignKey(to=Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='generatedreport_doc4')
    doc5 = models.ForeignKey(to=Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='generatedreport_doc5')

    sectiondtext = models.TextField(max_length=255, null=True, blank=True)


    created_time = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.patient}  "


class GeneratedReportTestResult(models.Model):
    final_report = models.ForeignKey(to=FinalGeneratedReport, on_delete=models.CASCADE, null=True)
    label = models.ForeignKey(to=Label, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(to='Category', on_delete=models.SET_NULL, null=True)


    value1 = models.CharField(max_length=10, blank=True, null=True)
    value2 = models.CharField(max_length=10, blank=True, null=True)
    value3 = models.CharField(max_length=10, blank=True, null=True)
    value4 = models.CharField(max_length=10, blank=True, null=True)
    value5 = models.CharField(max_length=10, blank=True, null=True)
    remark = models.CharField(max_length=255,null=True, blank=True)

    color1 = models.CharField(max_length=255, blank=True, null=True)
    color2 = models.CharField(max_length=255, blank=True, null=True)
    color3 = models.CharField(max_length=255, blank=True, null=True)
    color4 = models.CharField(max_length=255, blank=True, null=True)
    color5 = models.CharField(max_length=255, blank=True, null=True)

    remark_color = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"Report for  of report : {self.final_report}"

    def __repr__(self) -> str:
        return f"Report for  of report : {self.final_report}"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True)
    priority = models.IntegerField(blank=False, null=False, default=0)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class Conversion(models.Model):
    from_unit = models.CharField(max_length=55)
    to_unit = models.CharField(max_length=55)
    multiplier = models.FloatField(blank=True,null=True)
    adder = models.FloatField(blank=True,null=True)



    def __str__(self) -> str:
        return self.from_unit + " - " + self.to_unit

    def __repr__(self) -> str:
        return self.from_unit + " - " + self.to_unit
