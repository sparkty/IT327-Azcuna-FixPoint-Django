from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from fixpoint_backend.delete_requests.models import DeleteRequest

from .forms import RegisterForm, LoginForm, IssueForm

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

    if request.user.is_superuser:
        issues = Issue.objects.all().select_related('user').order_by('-createdAt')
    else:
        issues = Issue.objects.filter(user=request.user).order_by('-createdAt')

    my_issues = Issue.objects.filter(user=request.user).order_by('-createdAt')

    stats = {
        'total': issues.count(),
        'open': issues.filter(status='open').count(),
        'in_progress': issues.filter(status='in_progress').count(),
        'resolved': issues.filter(status__in=['resolved', 'closed']).count(),
    }

    users_with_issues = []
    pending_deletion_requests = []
    if request.user.is_superuser:
        users_with_issues = (
            User.objects
            .prefetch_related('issues')
            .order_by('first_name', 'last_name')
        )
        pending_deletion_requests = (
            DeleteRequest.objects
            .filter(status='pending')
            .select_related('issue', 'requested_by')
            .order_by('-created_at')
        )

    return render(request, 'pages/dashboard.html', {
        'issues': issues,
        'my_issues': my_issues,
        'stats': stats,
        'users_with_issues': users_with_issues,
        'pending_deletion_requests': pending_deletion_requests,
    })


@login_required(login_url='/')
def create_issue(request):
    from fixpoint_backend.issues.models import Issue
    from fixpoint_backend.attachments.models import Attachment

    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user
            issue.save()

            # JS sends files as attachment_0, attachment_1, attachment_2, ...
            for key, uploaded_file in request.FILES.items():
                if key.startswith('attachment_'):
                    Attachment.objects.create(
                        issue=issue,
                        file=uploaded_file,
                        fileName=uploaded_file.name,
                        fileType=uploaded_file.content_type or '',
                        fileSize=uploaded_file.size,
                    )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Issue created successfully!',
                    'issue_id': issue.issueID,
                })

            messages.success(request, 'Issue created successfully!')
            return redirect('issue_detail', issue_id=issue.issueID)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)

    else:
        form = IssueForm()

    return render(request, 'pages/create_issue.html', {
        'form': form,
        'user': request.user,
    })


@login_required(login_url='/')
def issue_detail(request, issue_id):
    from fixpoint_backend.issues.models import Issue

    issue = get_object_or_404(Issue, issueID=issue_id)  # ✅ Using issueID, not id

    # Check permissions
    if not request.user.is_superuser and issue.user != request.user:
        messages.error(request, 'You do not have permission to view this issue.')
        return redirect('dashboard')

    return render(request, 'pages/issue_detail.html', {
        'issue': issue,
    })


@login_required(login_url='/')
def add_comment(request, issue_id):
    from fixpoint_backend.issues.models import Issue
    from fixpoint_backend.comments.models import Comment

    issue = get_object_or_404(Issue, issueID=issue_id)

    # Check permissions
    if not request.user.is_superuser and issue.user != request.user:
        messages.error(request, 'You do not have permission to comment on this issue.')
        return redirect('dashboard')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment = Comment.objects.create(
                issue=issue,
                user=request.user,
                content=content
            )
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty.')

    return redirect('issue_detail', issue_id=issue_id)


@login_required(login_url='/')
def update_status(request, issue_id):
    from fixpoint_backend.issues.models import Issue

    if not request.user.is_superuser:
        messages.error(request, 'Only admins can update status.')
        return redirect('issue_detail', issue_id=issue_id)

    issue = get_object_or_404(Issue, issueID=issue_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['open', 'in_progress', 'resolved', 'closed']:
            issue.status = new_status
            issue.save()
            messages.success(request, f'Status updated to {issue.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')

    return redirect('issue_detail', issue_id=issue_id)


@login_required(login_url='/')
def request_deletion(request, issue_id):
    from fixpoint_backend.issues.models import Issue
    from fixpoint_backend.delete_requests.models import DeleteRequest  # If you have this model

    issue = get_object_or_404(Issue, issueID=issue_id)

    # Only the issue owner can request deletion
    if issue.user != request.user:
        messages.error(request, 'You do not have permission to request deletion of this issue.')
        return redirect('issue_detail', issue_id=issue_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if reason:
            # Check if a delete request already exists
            existing = DeleteRequest.objects.filter(issue=issue, status='pending').first()
            if existing:
                messages.error(request, 'A deletion request is already pending for this issue.')
            else:
                DeleteRequest.objects.create(
                    issue=issue,
                    requested_by=request.user,
                    reason=reason,
                    status='pending'
                )
                messages.success(request, 'Deletion request submitted successfully! An admin will review it shortly.')
        else:
            messages.error(request, 'Please provide a reason for deletion.')

    return redirect('issue_detail', issue_id=issue_id)

@login_required(login_url='/')
def accept_deletion_request(request, delete_request_id):
    if not request.user.is_superuser:
        messages.error(request, 'Only admins can approve deletion requests.')
        return redirect('dashboard')

    delete_request = get_object_or_404(DeleteRequest, deleteRequestID=delete_request_id)

    if request.method == 'POST':
        issue = delete_request.issue
        delete_request.status = 'approved'
        delete_request.save()
        issue.delete()
        messages.success(request, 'Issue deleted and request approved.')

    return redirect('dashboard')


@login_required(login_url='/')
def cancel_deletion_request(request, delete_request_id):
    if not request.user.is_superuser:
        messages.error(request, 'Only admins can cancel deletion requests.')
        return redirect('dashboard')

    delete_request = get_object_or_404(DeleteRequest, deleteRequestID=delete_request_id)

    if request.method == 'POST':
        delete_request.status = 'rejected'
        delete_request.save()
        messages.success(request, 'Deletion request cancelled.')

    return redirect('dashboard')


def logout_view(request):
    logout(request)
    return redirect('/')