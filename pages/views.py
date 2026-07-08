from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm

User = get_user_model()


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
                    department=data.get('department', ''),
                    role=data.get('role'),
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

                user = authenticate(
                    request,
                    username=email,
                    password=password
                )

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
    from fixpoint_backend.issues.models import Issue

    # Regular users see only their own issues; admins see all
    if request.user.is_staff:
        issues = Issue.objects.all().select_related('user').order_by('-createdAt')
    else:
        issues = Issue.objects.filter(user=request.user).order_by('-createdAt')

    stats = {
        'total': issues.count(),
        'open': issues.filter(status='open').count(),
        'in_progress': issues.filter(status='in_progress').count(),
        'resolved': issues.filter(status__in=['resolved', 'closed']).count(),
    }

    users_with_issues = []
    if request.user.is_staff:
        users_with_issues = (
            User.objects
                .prefetch_related('issues')
                .order_by('first_name', 'last_name')
        )

    return render(request, 'pages/dashboard.html', {
        'issues': issues,
        'stats': stats,
        'users_with_issues': users_with_issues,
    })


def logout_view(request):
    logout(request)
    return redirect('/')