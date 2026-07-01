from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm


def login_register(request):
    register_form = RegisterForm()
    login_form = LoginForm()
    active_tab = request.GET.get('tab', 'login')

    if request.method == 'POST':
        if 'register_submit' in request.POST:
            register_form = RegisterForm(request.POST)
            active_tab = 'register'
            if register_form.is_valid():
                data = register_form.cleaned_data
                User.objects.create_user(
                    username=data['email'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    password=data['password'],
                )
                messages.success(request, "Account created! Please sign in.")
                return redirect('/?tab=login')

        elif 'login_submit' in request.POST:
            login_form = LoginForm(request.POST)
            active_tab = 'login'
            if login_form.is_valid():
                email = login_form.cleaned_data['email']
                password = login_form.cleaned_data['password']
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('dashboard')
                login_form.add_error(None, "Invalid email or password.")

    return render(request, 'pages/login_register.html', {
        'register_form': register_form,
        'login_form': login_form,
        'active_tab': active_tab,
    })


@login_required(login_url='/')
def dashboard(request):
    return render(request, 'pages/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('/')