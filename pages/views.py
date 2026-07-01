from django.shortcuts import render


def login_register(request):
    return render(request, 'pages/login_register.html')

def dashboard(request):
    return render(request, 'pages/dashboard.html')

def new_issue(request):
    return render(request, 'pages/new_issue.html')