from django.shortcuts import render, redirect, get_object_or_404, reverse, HttpResponse
from .forms import UserCreationForm, UserUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.contrib.auth.views import LoginView as _LoginView
from django.contrib.messages.views import SuccessMessageMixin

User = get_user_model()


def register(request):
    print(' in the register view')
    print(request.method)
    if request.method == 'POST':
        print('creating new user')
        form = UserCreationForm(request.POST)
        print('is form valid', form.is_valid())
        if form.is_valid():
            print('saving new user')
            form.save()
            a = reverse('users-login')
            print(f'redirecting')
            # print(redirect('patient-home'), reverse('patient-home'))
            print('redirecting', reverse('users-login'))
            return redirect('users-login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})


class LoginView(SuccessMessageMixin, _LoginView):
    success_message = 'welcome to your site'
    def get_success_url(self):
        return reverse('patient-home')