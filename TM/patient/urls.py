"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

# views
from .views import *    


urlpatterns = [
    path('test', test_home, name='test'),
    path('', HomePageView.as_view(), name='patient-home'),
    path('all-patient', PatientListView.as_view(), name='patient-list-view'),
    path('upload/<int:pk>', DocumentUploadView.as_view(), name='upload-pdf'),
    path('docudetail/<int:pk>', GeneratedReportView.as_view(), name='patient-final-report'),
    path('dr/<int:patient_id>/<int:document_id>/', DiaplayResponseView.as_view(), name='display-response'),
    path('update/<int:pk>', TestResultUpdateView.as_view(), name='update-test-result'),
    path('create/<int:patient_id>/<int:document_id>/', TestResultCreateView.as_view(), name='create-test-result'),
    path('aak/', AlternateLabelCreateView.as_view(), name='create-alternate-label'),
    path('addpatient/', PatientCreateView.as_view(), name='patient-add'),
    path('patientprofile/<int:pk>', PatientProfileView.as_view(), name='patient-profile' ),
    path('patientupdate/<int:pk>', PatientUpdateView.as_view(), name='patient-update' ),
    path('patientsearch/', PatientSearchView.as_view(), name='patient-search' ),
    # url(r'^save/(?P<patient_id>[0-9]+)/(?P<doc1_id>[0-9]+)/(?P<doc2_id>[0-9]+)/(?P<table>.*)$', GeneratedReportSaveView.as_view(), name='save'),
    path('tesseractdata/<int:doc_id>',ShowReadDataView.as_view(),name='tesseract-data'),    
    path('deletepatient/<int:pk>', PatientDeleteView.as_view(), name='patient-delete'),
    path('saves/<int:pk>', GeneratedReportSaveView.as_view(), name='save2'),
    path('showall/<int:pk>', ShowAllReportView.as_view(), name='show-all-report'),
    path('showsavedreport/<int:pk>/<int:patient_id>', ShowSavedGeneratedReportView.as_view(), name='show-saved-report'),
    path('showpdf/<int:pk>', ViewPdfView.as_view(), name='show-pdf'),
    path('createlabel/',CreateLabelView.as_view(),name='create-labels'),
    #path('save/<int:patient_id>/<int:doc1_id>/<int:doc2_id>/<str:table>/', GeneratedReportSaveView.as_view(), name='save'),
    path('deletedocument/<int:pk>', DocumentDeleteView.as_view(), name='document-delete'),
    path('deletefinalgeneratedreport/<int:pk>', FinalGeneratedReportDeleteView.as_view(), name='final-generated-report-delete'),
]
