from django.db.models.query_utils import PathInfo
from patient.views import PatientCreateView
import patient
from django.test import TestCase
from django.test import Client
from .models import Document, Patient
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

# Create your tests here.
class LoginTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@test.com',
            username='test',
            first_name='test_fname',
            last_name='test_lname',
            password='passaman'
        )
        self.islogin = self.client.login(
            email='test@test.com',
            password='passaman'
        )

    def test_user_login(self):
        self.assertTrue(self.islogin)
        response = self.client.get(reverse('patient-home'))
        self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        self.client.logout()
        response = self.client.get(reverse('patient-home'))
        self.assertEqual(response.status_code, 302)

class HomePageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@test.com',
            username='test',
            first_name='test_fname',
            last_name='test_lname',
            password='passaman'
        )
        self.islogin = self.client.login(
            email='test@test.com',
            password='passaman'
        )

    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)



class PatientTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.patiet = Patient.objects.create(
            first_name = 'fname',
            last_name = 'lname',
            email = 'fname@lname.com',
            address = 'address',
            postal_zip = 12345,
            city ='city',
            country = 'country',
            phone_number = 123456789, # mobile
            alternate_number = 123456789,
        )
    
    def test_patient_created(self):
        patient = Patient.objects.get(
            first_name = 'fname',
            last_name = 'lname',
            email = 'fname@lname.com',
            address = 'address',
            postal_zip = 12345,
            city ='city',
            country = 'country',
            phone_number = 123456789, # mobile
            alternate_number = 123456789,
        )
        self.assertEqual(patient.first_name, 'fname')
        self.assertTrue(patient.last_name == 'lname')
        self.assertTrue(patient.email == 'fname@lname.com')
        self.assertTrue(patient.address == 'address')
        self.assertTrue(patient.postal_zip == 12345)
        self.assertTrue(patient.city =='city')
        self.assertTrue(patient.country == 'country')
        self.assertTrue(patient.phone_number == 123456789), # mobile
        self.assertTrue(patient.alternate_number == 123456789)


class PatientCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@test.com',
            username='test',
            first_name='test_fname',
            last_name='test_lname',
            password='passaman'
        )

    def test_veiw_url_by_name(self):
        self.client.login(email='test@test.com', password='passaman')
        response = self.client.get(reverse('patient-add'))
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        self.client.login(email='test@test.com', password='passaman')
        response = self.client.get(reverse('patient-add'))
        self.assertTemplateUsed(response, 'patient/patient_create_view.html')

    def test_view_require_login(self):
        response = self.client.get(reverse('patient-add'))
        self.assertEqual(response.status_code, 302)

    def test_create_new_patient(self):
        self.client.login(email='test@test.com', password='passaman')
        self.client.post(
            reverse('patient-add'),
            {
            'first_name' : 'fname',
            'last_name' : 'lname',
            'email' : 'fname@lname.com',
            'address' : 'address',
            'postal_zip' : 12345,
            'city' :'city',
            'country' : 'country',
            'phone_number' : 123456789, 
            'alternate_number' : 123456789,
            }
        )
        patient = Patient.objects.first()
        self.assertEqual(patient.first_name, 'fname')
        self.assertTrue(patient.last_name == 'lname')
        self.assertTrue(patient.email == 'fname@lname.com')
        self.assertTrue(patient.address == 'address')
        self.assertTrue(patient.postal_zip == 12345)
        self.assertTrue(patient.city =='city')
        self.assertTrue(patient.country == 'country')
        self.assertTrue(patient.phone_number == 123456789), # mobile
        self.assertTrue(patient.alternate_number == 123456789)


class PatientUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@test.com',
            username='test',
            first_name='test_fname',
            last_name='test_lname',
            password='passaman'
        )
        self.patient = Patient.objects.create(
            first_name = 'fname',
            last_name = 'lname',
            email = 'fname@lname.com',
            address = 'address',
            postal_zip = 12345,
            city ='city',
            country = 'country',
            phone_number = 123456789, # mobile
            alternate_number = 123456789,
        )

    def test_view_require_login(self):
        response = self.client.get(
            reverse('patient-update',kwargs={'pk': self.patient.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_page_login(self):
        self.islogin = self.client.login(
            email='test@test.com',
            password='passaman'
        )
        self.assertTrue(self.islogin)


    def test_veiw_url_by_name(self):
        self.client.login(email='test@test.com', password='passaman')
        response = self.client.get(reverse('patient-update', kwargs={'pk':self.patient.pk}))
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        self.client.login(email='test@test.com', password='passaman')
        response = self.client.get(reverse('patient-update', kwargs={'pk':self.patient.pk}))
        self.assertTemplateUsed(response, 'patient/patient_create_view.html')

    def test_update_patient(self):
        self.client.login(email='test@test.com', password='passaman')
        self.client.post(
            reverse('patient-update', kwargs={'pk':self.patient.pk} ),
            {
            'first_name' : 'new name',
            'last_name' : 'new lname',
            'email' : 'new_fname@lname.com',
            'address' : 'new address',
            'postal_zip' : 712345,
            'city' :'city home',
            'country' : 'country in',
            'phone_number' : 123, 
            'alternate_number' : 123,
            }
        )
        patient = Patient.objects.get(pk=self.patient.pk)
        self.assertTrue(patient.first_name== 'new name')
        self.assertTrue(patient.last_name == 'new lname')
        self.assertTrue(patient.email == 'new_fname@lname.com')
        self.assertTrue(patient.address == 'new address')
        self.assertTrue(patient.postal_zip == 712345)
        self.assertTrue(patient.city =='city home')
        self.assertTrue(patient.country == 'country in')
        self.assertTrue(patient.phone_number == 123), # mobile
        self.assertTrue(patient.alternate_number == 123)

# class DocumentTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(
#             email='test@test.com',
#             username='test',
#             first_name='test_fname',
#             last_name='test_lname',
#             password='passaman'
#         )
#         self.patient = Patient.objects.create(
#             first_name = 'fname',
#             last_name = 'lname',
#             email = 'fname@lname.com',
#             address = 'address',
#             postal_zip = 12345,
#             city ='city',
#             country = 'country',
#             phone_number = 123456789, # mobile
#             alternate_number = 123456789,
#         )
