from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
from django.db.models import Prefetch, Q
from fixpoint_backend.delete_requests.models import DeleteRequest
from fixpoint_backend.notifications.models import Notification

from .forms import RegisterForm, LoginForm, IssueForm

User = get_user_model()


def notification_context(request):
    if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
        return {}
    return {
        'unread_notifications_count': request.user.notifications.filter(isRead=False).count()
    }


def display_name(user):
    return user.get_full_name() or user.email or user.username


def notify_users(users, issue, message, exclude_user=None):
    seen_user_ids = set()
    for user in users:
        if not user or not user.is_active:
            continue
        if exclude_user and user.pk == exclude_user.pk:
            continue
        if user.pk in seen_user_ids:
            continue
        seen_user_ids.add(user.pk)
        Notification.objects.create(
            user=user,
            issue=issue,
            message=message,
        )


def admin_users():
    return User.objects.filter(is_superuser=True, is_active=True)


def number_user_issues(issues):
    ordered = sorted(issues, key=lambda issue: (issue.createdAt, issue.issueID))
    for number, issue in enumerate(ordered, start=1):
        issue.user_issue_number = number
    return issues


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

    my_issues = list(Issue.objects.filter(user=request.user).order_by('-createdAt', '-issueID'))
    number_user_issues(my_issues)

    stats = {
        'total': issues.count(),
        'open': issues.filter(status='PENDING').count(),
        'in_progress': issues.filter(status='IN_PROGRESS').count(),
        'resolved': issues.filter(status__in=['RESOLVED', 'CLOSED']).count(),
    }

    users_with_issues = []
    pending_deletion_requests = []
    if request.user.is_superuser:
        users_with_issues = (
            User.objects
            .prefetch_related(
                Prefetch(
                    'issues',
                    queryset=Issue.objects.order_by('-createdAt', '-issueID'),
                    to_attr='dashboard_issues',
                )
            )
            .order_by('first_name', 'last_name')
        )
        users_with_issues = list(users_with_issues)
        for user_obj in users_with_issues:
            number_user_issues(user_obj.dashboard_issues)
        pending_deletion_requests = (
            DeleteRequest.objects
            .filter(status='pending')
            .select_related('issue', 'requested_by')
            .order_by('-created_at')
        )

    context = {
        'issues': issues,
        'my_issues': my_issues,
        'stats': stats,
        'users_with_issues': users_with_issues,
        'pending_deletion_requests': pending_deletion_requests,
    }
    context.update(notification_context(request))
    return render(request, 'pages/dashboard.html', context)


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

            notify_users(
                admin_users(),
                issue,
                f"New issue #{issue.issueID} submitted by {display_name(request.user)}: {issue.title}",
                exclude_user=request.user,
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

    context = {
        'form': form,
        'user': request.user,
    }
    context.update(notification_context(request))
    return render(request, 'pages/create_issue.html', context)


@login_required(login_url='/')
def notifications(request):
    from fixpoint_backend.issues.models import Issue

    user_notifications = (
        Notification.objects
        .filter(user=request.user)
        .select_related('issue')
        .order_by('-createdAt')
    )
    user_notifications = list(user_notifications)
    if request.user.is_superuser:
        for notification in user_notifications:
            if notification.issue:
                notification.display_issue_number = notification.issue.issueID
    else:
        numbered_issues = list(Issue.objects.filter(user=request.user))
        number_user_issues(numbered_issues)
        issue_numbers = {
            issue.issueID: issue.user_issue_number
            for issue in numbered_issues
        }
        for notification in user_notifications:
            if notification.issue:
                notification.display_issue_number = issue_numbers.get(
                    notification.issue.issueID,
                    notification.issue.issueID,
                )
    unread_count = sum(1 for notification in user_notifications if not notification.isRead)
    read_count = sum(1 for notification in user_notifications if notification.isRead)

    return render(request, 'pages/notifications.html', {
        'notifications': user_notifications,
        'total_notifications_count': len(user_notifications),
        'unread_notifications_count': unread_count,
        'read_notifications_count': read_count,
    })


@login_required(login_url='/')
@require_POST
def open_notification(request, notification_id):
    notification = get_object_or_404(
        Notification.objects.select_related('issue'),
        notificationID=notification_id,
        user=request.user,
    )
    if not notification.isRead:
        notification.isRead = True
        notification.save(update_fields=['isRead'])

    issue = notification.issue
    if issue and (request.user.is_superuser or issue.user_id == request.user.pk):
        return redirect('issue_detail', issue_id=issue.issueID)
    return redirect('notifications')


@login_required(login_url='/')
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, isRead=False).update(isRead=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')


@login_required(login_url='/')
@require_POST
def delete_read_notifications(request):
    deleted_count, _ = Notification.objects.filter(user=request.user, isRead=True).delete()
    if deleted_count:
        messages.success(request, 'Read notifications deleted.')
    else:
        messages.error(request, 'There are no read notifications to delete.')
    return redirect('notifications')


@login_required(login_url='/')
def issue_detail(request, issue_id):
    from fixpoint_backend.issues.models import Issue

    issue = get_object_or_404(Issue, issueID=issue_id)  # ✅ Using issueID, not id

    # Check permissions
    if not request.user.is_superuser and issue.user != request.user:
        messages.error(request, 'You do not have permission to view this issue.')
        return redirect('dashboard')

    user_issue_number = Issue.objects.filter(
        user=issue.user
    ).filter(
        Q(createdAt__lt=issue.createdAt) |
        Q(createdAt=issue.createdAt, issueID__lte=issue.issueID)
    ).count()

    context = {
        'issue': issue,
        'display_issue_number': issue.issueID if request.user.is_superuser else user_issue_number,
    }
    context.update(notification_context(request))
    return render(request, 'pages/issue_detail.html', context)


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
            if request.user.is_superuser:
                recipients = [issue.user]
            else:
                recipients = admin_users()
            notify_users(
                recipients,
                issue,
                f"{display_name(request.user)} commented on issue #{issue.issueID}: {issue.title}",
                exclude_user=request.user,
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
        if new_status in ['PENDING', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']:
            issue.status = new_status
            issue.save()
            notify_users(
                [issue.user],
                issue,
                f"Issue #{issue.issueID} status changed to {issue.get_status_display()}: {issue.title}",
                exclude_user=request.user,
            )
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
                issue.status = 'PENDING_DELETION'
                issue.save(update_fields=['status', 'updatedAt'])
                notify_users(
                    admin_users(),
                    issue,
                    f"Deletion requested for issue #{issue.issueID} by {display_name(request.user)}: {issue.title}",
                    exclude_user=request.user,
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
        issue = delete_request.issue
        if issue.status == 'PENDING_DELETION':
            issue.status = 'PENDING'
            issue.save(update_fields=['status', 'updatedAt'])
        notify_users(
            [issue.user],
            issue,
            f"Deletion request cancelled for issue #{issue.issueID}: {issue.title}",
            exclude_user=request.user,
        )
        messages.success(request, 'Deletion request cancelled.')

    return redirect('dashboard')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required(login_url='/')
def profile(request):
    context = {}
    context.update(notification_context(request))
    return render(request, 'pages/profile.html', context)


@login_required(login_url='/')
@require_POST
def profile_change_password(request):
    current_password = request.POST.get('current_password', '').strip()
    new_password = request.POST.get('new_password', '').strip()
    confirm_password = request.POST.get('confirm_password', '').strip()

    if not current_password or not new_password or not confirm_password:
        messages.error(request, 'All password fields are required.')
        return redirect('profile')

    if not request.user.check_password(current_password):
        messages.error(request, 'Current password is incorrect.')
        return redirect('profile')

    if len(new_password) < 8:
        messages.error(request, 'New password must be at least 8 characters.')
        return redirect('profile')

    if new_password != confirm_password:
        messages.error(request, 'New passwords do not match.')
        return redirect('profile')

    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)
    messages.success(request, 'Password updated successfully.')
    return redirect('profile')


@require_POST
def forgot_password(request):
    email = request.POST.get('email', '').strip().lower()
    if not email:
        messages.error(request, 'Email is required.')
        return redirect('/?tab=login')

    user = User.objects.filter(email=email, is_active=True).first()
    if not user:
        messages.error(request, 'No account found with that email address.')
        return redirect('/?tab=login')

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_token = f"{uid}.{token}"

    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"[FixPoint] Password reset token for {email}: {reset_token}")
    print(f"\n[FixPoint] Password reset token for {email}:\n  {reset_token}\n")

    return redirect(f'/?resetToken={reset_token}')


@require_POST
def reset_password(request):
    raw_token = request.POST.get('token', '').strip()
    new_password = request.POST.get('password', '').strip()

    if not raw_token or not new_password:
        messages.error(request, 'Invalid request. Please try again.')
        return redirect('/?tab=login')

    try:
        uid_b64, token = raw_token.rsplit('.', 1)
        uid = force_str(urlsafe_base64_decode(uid_b64))
        user = User.objects.get(pk=uid)
    except (ValueError, User.DoesNotExist, Exception):
        messages.error(request, 'Reset link is invalid or expired. Please request a new one.')
        return redirect('/?tab=login')

    if not default_token_generator.check_token(user, token):
        messages.error(request, 'Reset link is invalid or expired. Please request a new one.')
        return redirect('/?tab=login')

    user.set_password(new_password)
    user.save()
    messages.success(request, 'Password reset successfully. You can now sign in.')
    return redirect('/?tab=login')
