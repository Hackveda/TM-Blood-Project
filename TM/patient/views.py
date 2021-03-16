# TODO: work on saved reports view. | DONE

from io import RawIOBase
from os import pathconf, removexattr,getcwd
from pydoc import doc
from typing import Counter
from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic.edit import ModelFormMixin, UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from .forms import PatientSearchForm , LabelForm
from django.db.models import Q
from django.utils.timezone import make_aware
from django.core import serializers
from .create_pdf import run as create_PDF
from django.core.paginator import Paginator
from django.contrib import messages

# app import
from .models import *
from .forms import DocumentForm, GeneratedReportForm, TestResultForm , LabelCreationForm

# utility import
from .process import main as process_main

# general imports
import json
#import requests
from collections import defaultdict, Counter
import datetime

#  import
from patient.models import Patient


# GLOBAL VARS
remark_color = {
            'White'         :'#ffffff',
            'Yellow'        :'#FFFF00',
            'Pale_Yellow'   :'#FE2E2E',
            'Green'         :'#31B404',
            'Pale_Green'    :'#82FA58',
            'Red'           :'#FF0000',
            'Maroon'        :'#800000'
        }

def log(msg):
    with open('log_custom.txt', 'a+') as wf:
        wf.writelines(msg)
        wf.write('\n')

def test_home(requests):
    template_name = 'patient/test.html'
    return render(requests, template_name)


class HomePageView(LoginRequiredMixin, View):
    """
    This is a view for home page
    """
    def get(self, request):
        template_name = 'patient/home_page.html'
        return render(request, template_name)

class PatientDeleteView(LoginRequiredMixin, DeleteView):
    model = Patient
    template_name = 'patient/delete_patient.html'
    fields = ('__all__')

    def get_success_url(self):
        return reverse('patient-home')

class DocumentUploadView(LoginRequiredMixin, View):
    """
    on document submission, redirect to 'display-response' with `patient` and `document`
    kwargs
    """
    template_name = 'patient/upload_pdf.html'

    def get(self, request, pk=None):
        """
        render upload document on get request
        """
        form = DocumentForm()
        try:
            patient = Patient.objects.get(pk=pk)
        except :
            patient = pk
        context = {
            'form':form,
            'patient':patient
        }
        return render(request, self.template_name, context)

    def post(self, request, pk=None):
        """
        on post request, document and patient details are sent to process.main()
        name, Value and unit are fetched for each item in the response. Name is
        searched in database for altername keyword, label associated with that alternate
        keyword is used in create TestResult object. All TestResult object is then saved in the
        database, redirected to display response page.
        """
        patient = Patient.objects.get(pk=pk)
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            #log('this is test')
            # getting DocumentForm object, adding patient object to it
            # then saving it
            document_object = form.save(commit=False)
            document_object.patient = patient
            document_object.save()

            # reading and processing uploaded document
            try:
                path = document_object.document.path
                # sending respone to process.py and parsing it to object
                res = process_main(path,document_object.report)
                # res = eval(res) # evaluating response'
                print("res ",res)
                for response in res:
                    name = response['name']
                    value = response['Value']
                    unit = response['Unit']
                    range1 = response['Range']
                    # upper_range = response['upper_range']
                    # lower_range = response['lower_range']
                    lower_range=range1[0]
                    upper_range = range1[1]
                    print(name,value,unit,range1)
                    try:
                        #log('got name value unit')
                        alternate_label= AlternateLabel.objects.filter(name=name,report=document_object.report).first()
                        print(alternate_label)
                        test_result = TestResult.objects.create(
                            patient = patient,
                            label = alternate_label.label,
                            value = value,
                            unit = unit,
                            document = document_object,
                            lower_range= lower_range,
                            upper_range = upper_range,
                        )
                        #log('saving label')
                        test_result.save()
                    except Exception as e:
                        #log(f'DocumentUploadView, post 1 {e}')
                        #log(f'{e}')
                        print('error1',e)

            except Exception as e:
                print('error2',e)
                #log(f'{e}')

            return redirect(reverse('display-response', kwargs={'patient_id':patient.id, 'document_id':document_object.id}))
        else:
            print('--none--'*10)
            print(form.errors)
            return redirect(reverse('upload-pdf', kwargs={'pk':pk}))

class DiaplayResponseView(LoginRequiredMixin,View):
    template_name = 'patient/display_response.html'

    def get(self, request, patient_id, document_id):
        patient = Patient.objects.get(id=patient_id)
        document = Document.objects.get(id=document_id)
        test_results = TestResult.objects.filter(patient=patient, document=document)
        context={
            'data':test_results,
            'document_url':document.document.url,
            'document':document,
            'patient':patient
        }
        return render(request, self.template_name, context )


class TestResultUpdateView(LoginRequiredMixin, View):
    template_name = 'patient/test_result_update_form.html'

    def get(self, request,pk, *args, **kwargs):
        form = TestResultForm()
        obj=TestResult.objects.filter(id=pk)[0]
        context = {
            'form':form,
            'obj':obj,
        }
        return render(request, self.template_name, context)

    def post(self, request,pk, *args, **kwargs):
        form = TestResultForm(request.POST)
        testresult=TestResult.objects.get(id=pk)
        if form.is_valid():
            unit=form.cleaned_data['unit']
            label=testresult.label
            value=float(form.cleaned_data['value'])
            testresult.upper_range = form.cleaned_data['upper_range'] if form.cleaned_data['upper_range']!="" else None
            testresult.lower_range = form.cleaned_data['lower_range'] if form.cleaned_data['lower_range']!="" else None
            testresult.unit=unit
            testresult.value=value
            testresult.label=label
            testresult.save()
            return redirect(reverse('display-response', kwargs={'patient_id':testresult.patient.id, 'document_id':testresult.document.id}))


class TestResultCreateView(LoginRequiredMixin, View):
    template_name = 'patient/test_result_create_form.html'

    def get(self, request,  patient_id=None, document_id=None):
        """
        render new test result on get request
        """
        form = LabelForm()
        try:
            patient = Patient.objects.get(pk=patient_id)
            document = Document.objects.get(pk=document_id)
        except Exception as e :
            print(e)
            patient = pk

        context = {
            'form':form,
            'patient':patient,
            'document':document
        }
        return render(request, self.template_name, context)

    def post(self, request,  patient_id=None, document_id=None):
        patient = Patient.objects.get(pk=patient_id)
        document = Document.objects.get(pk=document_id)
        form = LabelForm(request.POST, request.FILES)
        if form.is_valid():
            document_object = form.save(commit=False)
            document_object.patient = patient
            document_object.document = document
            if TestResult.objects.filter(label=document_object.label, document=document_object.document):
                pass
            else:
                document_object.save()
            return redirect(reverse('display-response', kwargs={'patient_id':patient.id, 'document_id':document.id}))

        else:
            print('--none--'*10)
            print(form.errors)
            return redirect(reverse('display-response', kwargs={'patient_id':patient.id, 'document_id':document.id}))


class AlternateLabelCreateView(LoginRequiredMixin, CreateView):
    model = AlternateLabel
    fields = ['label', 'name' , 'report']
    template_name = 'patient/add_alternate_keyword.html'

    def get_success_url(self) -> str:
        return reverse('create-alternate-label')

class GeneratedReportSaveView(LoginRequiredMixin, View):

    def get(self,request, *args, **kwargs):
        """
        saves table data from generated report page
        expected kwargs:
            patient_id, doc1_id, doc2_id, table
        """
        print('is save generated report view'* 100)

        pk = kwargs.get('pk', None)
        patient_obj=Patient.objects.get(pk=pk)

        table = self.request.session['table']
        if table == None:
            return redirect(reverse('patient-profile', kwargs={'pk':pk}))
        table_document = table.pop('documents')
        print('table_document', table_document)
        try:
            doc5 = Document.objects.get(pk = table_document.get('5', {}).get('pk', None))
        except :
            doc5 = None

        try:
            doc4 = Document.objects.get(pk = table_document.get('4', {}).get('pk', None))
        except :
            doc4 = None
        try:
            doc3 = Document.objects.get(pk = table_document.get('3', {}).get('pk', None))
        except :
            doc3 = None
        try:
            doc2 = Document.objects.get(pk = table_document.get('2', {}).get('pk', None))
        except :
            doc2 = None
        try:
            doc1 = Document.objects.get(pk = table_document.get('1', {}).get('pk', None))
        except :
            doc1 = None
        print(
        f"""
        these are values, save view
        {doc1}, {doc2}, {doc3}, {doc4},  {doc5}
            """
        )


        print(
        f"""
        this is table_doc, {table_document}
        """
        )
        # doc1_id = table.pop('doc1_id')
        # doc2_id = table.pop('doc2_id')

        # doc1_obj = Document.objects.get(pk=doc1_id)
        # doc2_obj = Document.objects.get(pk=doc2_id)

        sectiondtext = table_document.get('text', '')

        final_report = FinalGeneratedReport(
            patient= patient_obj,    #Patient.objects.filter(pk=pk).first(),
            sectiondtext = sectiondtext,
            doc1 = doc1,
            doc2 =doc2,
            doc3 = doc3,
            doc4 = doc4,
            doc5 = doc5,

        )
        final_report.save()

        # saving sectiond values


        # saving sectiona values
        # for val in table.get('sectiona',[]):
            # SectionAText.objects.create(text=val, final_generated_report=final_report)

        # saving sectionb values
        # for val in table.get('sectionb',[]):
            # SectionBText.objects.create(text=val, final_generated_report=final_report)

        # saving sectionc values
        # for val in table.get('sectionc',[]):
            # SectionCText.objects.create(text=val, final_generated_report=final_report)


        # SectionDText.objects.create(text=text, final_generated_report=final_report)

        # saving sectiond values
        # for val in table.get('all_category',[]):
            # AllCategory.objects.create(text=val, final_generated_report=final_report)


        print(final_report)

        print('---------------------'*100)
        print(table, len(table))
        print('this is len_table', len(table))

        try: # if error occurs during saving results then delete report as well.
            for item, val in table.items():
                print(item, val)
                print('this is label', item, type(item), val)

                # since sectiond has no attributes, do nothing
                if item=='documents':
                    continue

                # if doc1 object doesn't exists then graph unit from doc2
                # try:
                    # unit = table[item]['doc1']['unit']
                # except:
                    # unit = table[item]['doc2']['unit']
                    # print('error as unit' )
                # print('unit', unit)

                # trying to fetch value, try except because it is possible
                # that either 'doc1' or 'doc2' are None
                try:
                    value5 = val.get('5', {}).get('value', None)
                    value4 = val.get('4', {}).get('value', None)
                    value3 = val.get('3', {}).get('value', None)
                    value2 = val.get('2', {}).get('value', None)
                    value1 = val.get('1', {}).get('value', None)
                except:
                    print('error as value' )


                print(
                f"""
                these are values, save view
                {value1}, {value2}, {value3}, {value4},  {value5}
                 """
                )

                try:
                    color5 = val.get('5', {}).get('remark_color', None)
                    color4 = val.get('4', {}).get('remark_color', None)
                    color3 = val.get('3', {}).get('remark_color', None)
                    color2 = val.get('2', {}).get('remark_color', None)
                    color1 = val.get('1', {}).get('remark_color', None)
                except:
                    print('error as value' )


                try:
                    remark = val.get('5', {}).get('remark', '')
                except:
                    remark = ''
                    print('error at remark')
                print('remark', remark)

                try:
                    remark_color = val.get('5', {}).get('remark_color', '')
                except:
                    remark_color = ''
                    print('error at remark color')

                try:
                    category = val.get('5', {}).get('category', '')
                except:
                    pass


                try:
                    print('saving generated report')
                    GeneratedReportTestResult.objects.create(
                        final_report = final_report,
                        label = Label.objects.get(name= item),
                        category = Category.objects.get(name=category),


                        value1 = value1,
                        value2 = value2,
                        value3 = value3,
                        value4 = value4,
                        value5 = value5,

                        color1=color1,
                        color2=color2,
                        color3 = color3,
                        color4 = color4,
                        color5 = color5,

                        remark = remark,
                        remark_color = remark_color
                    )
                    print('saved generated report',final_report.id)
                except Exception as e:
                    print("ERROR", e)
        except Exception as e:
            print('this is main error', e)
        print(request.session['table_for_pdf']['documents'])
        row_wise_table=request.session['table_for_pdf']
        #range=0
        patient_dict = {'id':patient_obj.id,'name':patient_obj.first_name,'contact':patient_obj.phone_number}
        create_PDF(row_wise_table,final_report.id,patient_dict)
        #return redirect('patient-home')
        return redirect(reverse('patient-profile', kwargs={'pk':pk}))

class FinalGeneratedReportDetailView(LoginRequiredMixin, DetailView):
    model = FinalGeneratedReport
    template_name = 'patient/show_saved_generated_report.html'
    context_object_name = 'report'

class ShowSavedGeneratedReportView(View):
    """
    this is a view to show all `GeneratedReportTestResult` of `FinalGeneratedReport`
    """
    template_name = 'patient/show_saved_generated_report.html'

    def get(self, request, pk, patient_id):
        """
        pk : pk of `FinalGeneratedReport`
        """
        patient = Patient.objects.get(pk=patient_id)
        final_generated_report_obj = FinalGeneratedReport.objects.get(pk=pk)
        all_testresult = final_generated_report_obj.generatedreporttestresult_set.all()
        #patient = Patient.objects.get(pk=pk)
        #patient_obj = Patient.objects.get(pk=pk)
        # getting all categories
        all_categories = sorted(
            list(set(item.category for item in all_testresult)),
            key = lambda x : x.priority
        )
        all_categories = list(map(lambda x: x.name, all_categories))
        print(
            f"""
            this is save_all_category
            {all_categories}
            """
        )
        # print(getcwd())
        pdf_url = "/media/Generated_reports/"+str(final_generated_report_obj.id)+".pdf"
        context = {
            'patient':patient,
            'all_testresult':all_testresult,
            'final_generated_report':final_generated_report_obj,
            'all_categories':all_categories,
            'remark_color':remark_color,
            'pdf_url':pdf_url
        }
        return render(request, template_name=self.template_name, context=context)


class ShowAllReportView(LoginRequiredMixin, View):
    template_name = 'patient/show_all_report.html'

    def get(self, request, pk):
        patient = Patient.objects.get(pk=pk)
        gen_rep = FinalGeneratedReport.objects.filter(patient__pk=pk).order_by('-pk')
        report1 = patient.document_set.all().order_by('-pk')
        paginator1 = Paginator(gen_rep, 5)
        paginator2 = Paginator(report1, 5)
        page_number = request.GET.get('page')
        page_obj1 = paginator1.get_page(page_number)
        page_obj2 = paginator2.get_page(page_number)
        context = {
            'patient':patient,
            'generated_reports':FinalGeneratedReport.objects.filter(patient__pk=pk).order_by('-pk'),
            'reports': patient.document_set.all().order_by('-pk'),
            'page_obj1':page_obj1,
            'page_obj2':page_obj2
        }
        return render(request, self.template_name, context)

class GeneratedReportView(LoginRequiredMixin, View):
    """
    View to display all details about a single patient

    @param:
    is_single_document: bool, if true it means only single document exist for patient
                        and to display only one col in html page
    doc2 is latest report
    doc1 is old report
    """

    model = Patient
    template_name = 'patient/patient_generated_report.html'
    context_object_name = 'object'
    form = GeneratedReportForm()
    remark_color = {
            'White'         :'#ffffff',
            'Yellow'        :'#FFFF00',
            'Pale_Yellow'   :'#FE2E2E',
            'Green'         :'#31B404',
            'Pale_Green'    :'#82FA58',
            'Red'           :'#FF0000',
            'Maroon'        :'#800000'
        }

    def get_all_labels(self, doc1_obj: Document = None, doc2_obj: Document = None, doc3_obj: Document = None, doc4_obj: Document = None, doc5_obj: Document = None ):
        """
        returns the common labels between passed documents
        """
        # getting doc1 labels
        if doc1_obj is not None:
            testresult1 = TestResult.objects.filter(document=doc1_obj)
            result1_labels = {result.label: {'value':float(result.value), 'unit':result.unit} for result in testresult1}
            # result1_labels = {result.label : {'result_id':result.id,'value':float(result.value), 'unit':result.unit, 'upper_range':float(result.upper_range) if result.upper_range!="" else None, 'lower_range':float(result.lower_range) if result.lower_range!="" else None} for result in testresult1}
        else:
            result1_labels = {}

        # getting doc2 labels
        if doc2_obj is not None:
            testresult2 = TestResult.objects.filter(document=doc2_obj)
            result2_labels = {result.label : {'value':float(result.value), 'unit':result.unit} for result in testresult2}
            # result2_labels = {result.label : {'result_id':result.id,'value':float(result.value), 'unit':result.unit, 'upper_range':float(result.upper_range) if result.upper_range!="" else None, 'lower_range':float(result.lower_range) if result.lower_range!="" else None} for result in testresult2}
        else:
            result2_labels = {}

        # getting doc3 labels
        if doc3_obj is not None:
            testresult3 = TestResult.objects.filter(document=doc3_obj)
            result3_labels = {result.label : {'value':float(result.value), 'unit':result.unit} for result in testresult3}
        else:
            result3_labels = {}

        # getting doc4 labels
        if doc4_obj is not None:
            testresult4 = TestResult.objects.filter(document=doc4_obj)
            result4_labels = {result.label : {'value':float(result.value), 'unit':result.unit} for result in testresult4}
        else:
            result4_labels = {}

        # getting doc5 labels
        if doc5_obj is not None:
            testresult5 = TestResult.objects.filter(document=doc5_obj)
            result5_labels = {result.label : {'value':float(result.value), 'unit':result.unit} for result in testresult5}
        else:
            result5_labels = {}


        # getting union of labels present in both docs
        all_labels = list(set(
            result1_labels.keys())|set(result2_labels.keys()|result3_labels.keys()|result4_labels.keys()|result5_labels.keys()
        ))
        print(all_labels)
        # getting unique categories of all_labels
        all_categories = [category.name for category in Category.objects.all().order_by('-priority')] # categories present in backend in highest to lowest order
        print("htis is all_categories", all_categories, type(all_categories[0]))
        print("############################################################################################")
        for i in all_labels:
            print("htis is all_labels",i, type(i))
            print(i.category)
            print(i.category.name)
        present_category = list(set(label.category.name for label in all_labels)) # all common categories in 5 documents
        all_category = [category for category in all_categories if category in present_category] # categories present in 5 documents in priority order


        print('this is all_labels_unions', all_labels)
        return all_labels, all_category


    def create_comparision(self, prev_report: Document, present_report: Document, all_labels: list):
        """
        this function create the comparison of two reports

        @params:
            prev_report, present_report : present and previous reprot document object
            all_labels : contains all test labels that needs to be present in the final report
                         based on all documents [list of Label object]
        @algo
            given two reports, compare the values of the test labels, and return the column
            containing labels values and color remarks that should be present in present report

        @return : dict, containt column wise data for present report with color combination
        """
        print('create_comp input')
        print(present_report, prev_report, all_labels)
        doc2_obj = present_report
        doc1_obj = prev_report
        remark_color = {
            'White'         :'#ffffff',
            'Yellow'        :'#FFFF00',
            'Pale Yellow'   :'#FE2E2E',
            'Green'         :'#31B404',
            'Pale Green'    :'#82FA58',
            'Red'           :'#FF0000',
            'Maroon'        :'#800000',
            'Purple'        :'',
        }
        # table template to return
        #table = {
        #    'label':{
        #       'value': '',
        #        'color': '',
        #        'remark': '',
        #        'category': '',
        #    },
        #    'document': {'doc_index':'contains docs index',
        #                'all_category': 'contains all category',
        #                'sectiond_text': 'contains section d text'},
        #
        #}

        # if there is only one document
        is_single_document = False
        if (prev_report is None) and (present_report is not None): # if there is not prev reprot
            is_single_document=True

        print('is_single', is_single_document)
        # getting all testresult associated with both document
        # storing all values in dict in {label: {value, unit}} format
        if doc1_obj is not None:
            testresult1 = TestResult.objects.filter(document=doc1_obj)
            # result1_labels = {result.label : {'result_id':result.id,'value':float(result.value), 'unit':result.unit, 'upper_range':float(result.upper_range) if result.upper_range!="" else None, 'lower_range':float(result.lower_range)} for result in testresult1}
            result1_labels = {result.label : {'result_id':result.id,'value':float(result.value), 'unit':result.unit, 'upper_range':float(result.upper_range) if result.upper_range!="" else None, 'lower_range':float(result.lower_range) if result.lower_range!="" else None} for result in testresult1}
        else:
            result1_labels = {}

        if doc2_obj is not None:
            testresult2 = TestResult.objects.filter(document=doc2_obj)
            # result2_labels = {result.label : {'result_id':result.id,'value':float(result.value), 'unit':result.unit, 'upper_range':float(result.upper_range) if result.upper_range!="" else None, 'lower_range':float(result.lower_range)} for result in testresult2}
            result2_labels = {result.label : {'result_id':result.id,'value':float(result.value), 'unit':result.unit, 'upper_range':float(result.upper_range) if result.upper_range!="" else None, 'lower_range':float(result.lower_range) if result.lower_range!="" else None} for result in testresult2}
        else:
            result2_labels = {}

        table = defaultdict(dict)
        for label in all_labels:        # label is Label object
            label_name = label.name
            category = label.category.name
            doc1 = result1_labels.get(label, None)
            doc2 = result2_labels.get(label, None)

            if doc1 is not None:
                doc1_value = doc1.get('value', 0)
            else:
                doc1_value = ''
            if doc2 is not None:
                doc2_value = doc2.get('value', 0)
            else:
                doc2_value = ''

            # finding remark value doc2_value - doc1_value
            # remark is Increase or decrease if seconds report values increases or decreases
            # if only single report contains that value then, it is empty

            lower_range1 = None
            lower_range2 = None
            upper_range1 = None
            upper_range2 = None
            if doc1:
                lower_range1 = doc1.get('lower_range',0)
                upper_range1 = doc1.get('upper_range',0)
            if doc2:
                lower_range2 = doc2.get('lower_range',0)
                upper_range2 = doc2.get('upper_range',0)
                table[label_name]['result_id'] = doc2.get('result_id',0)
            else:
                table[label_name]['result_id'] = 0

            table[label_name]['value'] = doc2_value
            table[label_name]['category'] = category
            table[label_name]['upper_range'] = upper_range2
            table[label_name]['lower_range'] = lower_range2
            if is_single_document or ((doc1 is None) and (doc2 is not None)):
                try:
                    if upper_range2==None:
                        table[label_name]['remark'] = 'different unit/range'
                        table[label_name]['remark_color'] = remark_color['Purple']
                    elif doc2_value < lower_range2:
                        table[label_name]['remark'] = 'Low'
                        table[label_name]['remark_color'] = remark_color['Yellow']
                        print('this is single lower remark color', table[label_name]['remark_color'])
                    elif lower_range2<= doc2_value <= upper_range2:
                        table[label_name]['remark'] = 'Normal'
                        table[label_name]['remark_color'] = remark_color['Green']
                        print('this is single normal remark color', table[label_name]['remark_color'])
                    else:
                        table[label_name]['remark'] = 'High'
                        table[label_name]['remark_color'] = remark_color['Red']
                        print('this is single high remark color', table[label_name]['remark_color'])
                except Exception as e:
                    table[label_name]['remark'] = '-'
                    print('lower_range, upper_range error', e)

            # if label exist for both docs
            elif (doc1 is not None) and (doc2 is not None):
                doc2_value = doc2.get('value', 0)
                doc1_value = doc1.get('value', 0)
                doc2_unit = doc2.get('unit',0)
                doc1_unit = doc1.get('unit',0)
                if(doc2_unit==doc1_unit):
                    try:
                       value_change = abs(doc2_value - (upper_range2+lower_range2)/2) - abs(doc1_value - (upper_range1+lower_range1)/2)
                    except:
                       value_change = None
                else:
                    value_change = None

                try:
                    # previos value was low
                    if upper_range1==None or value_change==None:
                        if upper_range2==None:
                            table[label_name]['remark'] = 'different unit/range'
                            table[label_name]['remark_color'] = remark_color['Purple']
                        elif doc2_value < lower_range2:
                            table[label_name]['remark'] = 'Low'
                            table[label_name]['remark_color'] = remark_color['Yellow']
                            print('this is single lower remark color', table[label_name]['remark_color'])
                        elif doc2_value <= upper_range2:
                            table[label_name]['remark'] = 'Normal'
                            table[label_name]['remark_color'] = remark_color['Green']
                            print('this is single normal remark color', table[label_name]['remark_color'])
                        else:
                            table[label_name]['remark'] = 'High'
                            table[label_name]['remark_color'] = remark_color['Red']
                            print('this is single high remark color', table[label_name]['remark_color'])

                    elif doc1_value < lower_range1:
                        if upper_range2==None:
                            table[label_name]['remark'] = 'different range/unit'
                            table[label_name]['remark_color'] = remark_color['Purple']
                        elif doc2_value <lower_range2:
                            if value_change==None:
                                table[label_name]['remark'] = 'different range/unit'
                                table[label_name]['remark_color'] = remark_color['Purple']
                            elif value_change<0:                                              # value has gone lower (a)
                                table[label_name]['remark'] = 'Improved but still out of range'
                                table[label_name]['remark_color'] = remark_color['Pale Yellow']
                            elif value_change>=0:                                           # value is same (b)
                                table[label_name]['remark'] = 'Low'
                                table[label_name]['remark_color'] = remark_color['Yellow']
                        elif doc2_value <=upper_range2:
                            table[label_name]['remark'] = 'Improved'
                            table[label_name]['remark_color'] = remark_color['Pale Green']
                        else:
                            table[label_name]['remark'] = 'High'
                            table[label_name]['remark_color'] = remark_color['Red']


                    # if value was normal
                    elif doc1_value<=upper_range1:
                        if upper_range2==None:
                            table[label_name]['remark'] = 'different range/unit'
                            table[label_name]['remark_color'] = remark_color['Purple']
                        elif doc2_value <lower_range2:
                            table[label_name]['remark'] = 'Low'
                            table[label_name]['remark_color'] = remark_color['Yellow']

                        elif doc2_value <=upper_range2:
                            if value_change==None:
                                table[label_name]['remark'] = 'different range/unit'
                                table[label_name]['remark_color'] = remark_color['Purple']
                            elif value_change<0:                                              # value has gone lower (a)
                                table[label_name]['remark'] = 'Improved'
                                table[label_name]['remark_color'] = remark_color['Pale Green']
                            elif value_change>=0:                                           # value is same (b)
                                table[label_name]['remark'] = 'Normal'
                                table[label_name]['remark_color'] = remark_color['Green']
                        else:
                            table[label_name]['remark'] = 'High'
                            table[label_name]['remark_color'] = remark_color['Red']

                    # if value was high
                    else:
                        if upper_range2==None:
                            table[label_name]['remark'] = 'different range/unit'
                            table[label_name]['remark_color'] = remark_color['Purple']

                        elif doc2_value <lower_range2:
                            table[label_name]['remark'] = 'Low'
                            table[label_name]['remark_color'] = remark_color['Yellow']

                        elif doc2_value <=upper_range2:
                            table[label_name]['remark'] = 'improved'
                            table[label_name]['remark_color'] = remark_color['Pale Green']

                        else:
                            if value_change==None:
                                table[label_name]['remark'] = 'different range/unit'
                                table[label_name]['remark_color'] = remark_color['Purple']
                            elif value_change<0:                                              # value has gone lower (a)
                                table[label_name]['remark'] = 'Improved but still oy of range'
                                table[label_name]['remark_color'] = remark_color['Pale Yellow']
                            elif value_change>=0:                                           # value is same (b)
                                table[label_name]['remark'] = 'high'
                                table[label_name]['remark_color'] = remark_color['Red']

                    print(label_name,table[label_name]['remark_color'],"1"*80)

                except Exception as e:
                    table[label_name]['remark'] = '-'
                    print('No lower upper range error',  label_name, e)

            else: # when label exist for only one doc
                table[label_name]['remark'] = '-'
                table[label_name]['remark_color'] = ''
        # table data type from defaultdict to dict
        table = dict(table)
        return table, is_single_document

    # helper function
    def create_final_report(self, doc1_obj: Document, doc2_obj: Document = None, doc3_obj=None,doc4_obj=None,doc5_obj=None, is_single_document: bool = False) :
        """
        @param:
            doc2_obj :  latest report
            doc1_obj : second report
            doc3_obj : third report
            doc4_obj : fourth report
            doc5_obj : fifth report
        """


        # getting common labels among all 5 documents
        labels, all_category = self.get_all_labels(doc1_obj, doc2_obj, doc3_obj, doc4_obj, doc5_obj)

        # list of all documents from oldest to latest
        all_docs = [None, doc5_obj, doc4_obj, doc3_obj, doc1_obj, doc2_obj]
        print('all_docs', all_docs)

        # creating comparison of two consicutive documents one by one, and saving the comparison result
        # in `table_new`
        table_new = dict()
        for index, present_doc in enumerate(all_docs):
            if present_doc is None: # skip if present document is None
                continue
            previous_doc = all_docs[index-1]
            col, is_single_document = self.create_comparision(previous_doc, present_doc, labels)
            table_new[index] = {
                'name': present_doc,
                'col' : col
            }
            print('doc_detail', present_doc, len(col), is_single_document)
            # print('this is pres_col', present_doc, is_single_document)
            # print(col)

        # converting col wise data to row wise
        row_wise_table = dict()
        # print((table_new))
        # print('table_new_keys')
        # print(table_new.keys())
        for index in table_new.keys():
            print(index)
        for label in labels:
            row_wise_table[label.name] = {
                index : {
                    'value' : table_new[index]['col'][label.name].get('value', ''),
                    'remark': table_new[index]['col'][label.name].get('remark', ''),
                    'remark_color': table_new[index]['col'][label.name].get('remark_color', ''),
                    'category': table_new[index]['col'][label.name].get('category', ''),
                    'upper_range': table_new[index]['col'][label.name].get('upper_range', ''),
                    'lower_range': table_new[index]['col'][label.name].get('lower_range', ''),
                    'result_id': table_new[index]['col'][label.name].get('result_id', 0),
                } for index in table_new.keys()
            }
        row_wise_table['documents'] = {}
        for doc_index in table_new.keys():

            # converting doc_obj to dict obj
            doc_obj = table_new[doc_index]['name']
            fields = {'uploaded_at':str(doc_obj.uploaded_at), 'pk':doc_obj.pk}
            # fields = eval(serializers.serialize('json', [doc_obj, ]))[0]['fields']

            row_wise_table['documents'][doc_index] = fields
        row_wise_table['documents']['all_category'] = all_category

        print('this is row_wise')
        print(row_wise_table)

        # getting color count, to display comment at the last of page
        red_count, green_count, yellow_count = 0, 0, 0
        print("""
        this is color data

        """)
        for label, val in row_wise_table.items():
            try:
                color = val.get(5, {}).get('remark_color', None)
                print(color)
                if color == self.remark_color['Red'] or color == self.remark_color['Maroon']:
                    red_count+=1
                elif color == self.remark_color['Yellow'] or color == self.remark_color['Pale_Yellow']:
                    yellow_count+=1
                elif color == self.remark_color['Green'] or color == self.remark_color['Pale_Green']:
                    green_count+=1
            except:
                pass
        print(green_count, yellow_count, red_count)
        sectiond_text = ""
        if green_count>red_count and green_count>yellow_count:
            sectiond_text = 'Overall, Very Good Job'
        if green_count<=yellow_count:
            sectiond_text = 'Overall, Things are looking better, Just needs more process and sacrifice'
        if green_count<red_count:
            sectiond_text = 'Things are not looking great. Please get back to process and begin to sacrifice to fix your physiology'
        row_wise_table['documents']['text'] = sectiond_text
        return row_wise_table

    def get(self, request, pk):
        request.session['aman'] = 'aman'
        # instantiating form for selected particular user
        form = GeneratedReportForm(pk=pk)
        patient_obj = Patient.objects.get(pk=pk)
        # retrieving all document of patient.pk = pk from latest to oldest
        documents = Document.objects.filter(patient__id=pk).order_by('-uploaded_at')
        table, is_single_document, row_wise_table = None, None, None
        doc1_obj, doc2_obj = None, None
        doc3_obj, doc4_obj, doc5_obj = None, None, None
        try:
            doc2_obj = documents[0]  # most recent report
            print(doc2_obj, '2nd')
            doc1_obj = documents[1]  # second most recent report
            print(doc1_obj, '1st')
            doc3_obj = documents[2]
            print(doc3_obj, '3rd')
            doc4_obj = documents[3]
            print(doc4_obj, '4th')
            doc5_obj = documents[4]
            print(doc5_obj, '5th')
        except Exception as e:
            print('ERROR while getting doc2, doc2 obj', e)

        if doc2_obj is not None:
            # table, is_single_document = self.create_final_report(doc2_obj, doc1_obj)
            print('these are docs', doc1_obj, doc2_obj, doc3_obj, doc4_obj, doc5_obj)
            row_wise_table = self.create_final_report(doc1_obj, doc2_obj, doc3_obj, doc4_obj, doc5_obj)


        request.session['table'] = row_wise_table
        context = {
        'patient_obj':patient_obj,
        'row_wise_table': row_wise_table,
        'form':form ,
        'remark_color': self.remark_color,
        }
        request.session['table_for_pdf'] = row_wise_table
        return render(request, self.template_name, context)

    def post(self, request, pk):
        # instantiating form for selected user
        form = GeneratedReportForm(request.POST, pk=pk)
        patient_obj = Patient.objects.get(pk=pk)

        if form.is_valid():
            # retrieveing doc1 and doc2 from form
            doc1_obj  = form.cleaned_data['document1']
            doc2_obj = form.cleaned_data['document2']
            row_wise_table = self.create_final_report(doc1_obj, doc2_obj)


            print(f"""
            this is post request row_wise_table,
            {row_wise_table}

            """)
            request.session['table'] = row_wise_table
            context = {
            'patient_obj':patient_obj,
            'row_wise_table': row_wise_table,
            'form':form ,
            'remark_color': self.remark_color,
            }
            request.session['table_for_pdf'] = row_wise_table
            return render(request,self.template_name, context )
        return render(request, self.template_name, context)

class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'patient/patient_list_view.html'
    paginate_by = 5
    context_object_name = 'patient_list'

class PatientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Patient
    fields = '__all__'
    template_name = 'patient/patient_create_view.html'
    success_message = "Patient was added successfully"

    def get_success_url(self):
        return reverse('patient-profile', kwargs = {'pk': self.object.id})

class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    template_name = 'patient/patient_update_view.html'
    fields = "__all__"

    def get_success_url(self):
        return reverse('patient-profile', kwargs = {'pk': self.object.id})

class PatientProfileView(LoginRequiredMixin, DetailView):
    """
    Detail view to handle paitent profile page of particular patient
    """
    model = Patient
    template_name = 'patient/patient_profile_view.html'
    context_object_name = 'patient'


class PatientSearchView(LoginRequiredMixin, ListView):
    form_class = PatientSearchForm
    form = PatientSearchForm()
    template_name = 'patient/patient_search_form.html'

    def get(self, request, *args, **kwargs):
        patient_list2 = Patient.objects.all()
        paginator = Paginator(patient_list2, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'form':self.form,
            #'patient_list': Patient.objects.all().order_by('-pk'),
            #'patient_list2': Patient.objects.all(),
            'page_obj': page_obj
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        form = PatientSearchForm(request.POST)
        print('-'*100)
        print('IN the search post view')
        try:
            if form.is_valid():
                print('form in valid')
                search_key = form.cleaned_data['name']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']

                query = Patient.objects.filter(
                    Q(first_name__icontains=search_key)         |
                    Q(last_name__icontains=search_key)          |
                    Q(email__icontains=search_key)              |
                    Q(city__icontains=search_key)               |
                    Q(phone_number__icontains=search_key)       |
                    Q(alternate_number__icontains=search_key)   |
                    Q(country__icontains=search_key)
                )


                # converting start_date, end_date to timezone aware datetime.datetime objects
                try:
                    if start_date is not None:
                        start_date = make_aware(
                            datetime.datetime(start_date.year, start_date.month, start_date.day)
                        )
                    if end_date is not None:
                        end_date = make_aware(
                            datetime.datetime(end_date.year, end_date.month, end_date.day+1) # adding 1 day offset to enddate
                        )
                except Exception as e:
                    print('ERROR at PatientSerchView, post:',e)

                # restricing query to date range

                # no date exist
                if (start_date is None) and (end_date is None):
                    pass # do not change query

                # both date exist
                elif (start_date is not None) and (end_date is not None):
                    query = Patient.objects.filter(
                        document__uploaded_at__range=[start_date, end_date]
                    ).intersection(query).distinct()

                # end date exist
                elif start_date is None:
                    query = Patient.objects.filter(
                        document__uploaded_at__lte=end_date
                    ).intersection(query).distinct()

                # start date exist
                elif end_date is None:
                    query = Patient.objects.filter(
                        document__uploaded_at__gte=start_date
                    ).intersection(query).distinct()

                context = {
                    'form':form,
                    'page_obj':query
                }
                return render(request, self.template_name, context)

            print(' form errors ' * 10)
            print(form.errors)
            context = {
                'form':form
            }

            return render(request, self.template_name, context)
        except Exception as e:
            print(e)

class ViewPdfView(LoginRequiredMixin, View):
    template_name = 'patient/view_pdf.html'
    def get(self, request, pk):
        context = { 'doc_obj':  Document.objects.get(pk=pk)}
        return render(request, self.template_name, context)



class CreateLabelView(LoginRequiredMixin,View):
    template_name = 'patient/create_label.html'

    def get(self, request):
        form = LabelCreationForm()
        context = {
            'form':form,
        }
        return render(request, self.template_name, context=context)


    def post(self, request):

        form = LabelCreationForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data['name']
            category=form.cleaned_data['category']
            try:
                label_obj = Label.objects.filter(name=name)[0]
            except:
                label_obj = Label.objects.create(name=name,category=category)

            label_obj.save()

        return redirect('create-labels')
