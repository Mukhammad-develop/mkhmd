from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
import json

from .models import User, EmailVerification, UserProfile
from .forms import SignUpForm, EmailVerificationForm, ProfileForm, UserUpdateForm

def signup_view(request):
    """Handle user signup with email verification"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            username = email.split('@')[0]  # Use email prefix as username
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists.')
                return render(request, 'accounts/signup.html', {'form': form})
            
            # Create user but don't activate yet
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False  # User inactive until email verified
            )
            
            # Profile is automatically created by signal
            
            # Send verification email
            verification = EmailVerification.objects.create(
                user=user,
                email=email
            )
            
            send_verification_email(email, verification.code)
            
            # Store user ID in session for verification step
            request.session['pending_user_id'] = user.id
            
            messages.success(request, f'Verification code sent to {email}. Please check your email.')
            return redirect('accounts:verify_email')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def verify_email_view(request):
    """Handle email verification with one-time code"""
    if 'pending_user_id' not in request.session:
        messages.error(request, 'No pending verification found.')
        return redirect('accounts:signup')
    
    user_id = request.session['pending_user_id']
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            try:
                verification = EmailVerification.objects.get(
                    user=user,
                    code=code,
                    is_used=False
                )
                
                if verification.is_expired():
                    messages.error(request, 'Verification code has expired. Please request a new one.')
                    return render(request, 'accounts/verify_email.html', {
                        'form': form,
                        'user_email': user.email
                    })
                
                # Activate user and mark verification as used
                with transaction.atomic():
                    user.is_active = True
                    user.is_email_verified = True
                    user.save()
                    
                    verification.is_used = True
                    verification.save()
                
                # Auto-login user
                user.backend = 'accounts.backends.EmailBackend'
                login(request, user)
                
                # Clear session
                del request.session['pending_user_id']
                
                messages.success(request, 'Email verified successfully! Welcome to MKHMD.')
                return redirect('website:home')
                
            except EmailVerification.DoesNotExist:
                messages.error(request, 'Invalid verification code.')
    else:
        form = EmailVerificationForm()
    
    return render(request, 'accounts/verify_email.html', {
        'form': form,
        'user_email': user.email
    })

def resend_verification_view(request):
    """Resend verification code"""
    if 'pending_user_id' not in request.session:
        return JsonResponse({'error': 'No pending verification found.'}, status=400)
    
    user_id = request.session['pending_user_id']
    user = get_object_or_404(User, id=user_id)
    
    # Mark old verifications as used
    EmailVerification.objects.filter(user=user, is_used=False).update(is_used=True)
    
    # Create new verification
    verification = EmailVerification.objects.create(
        user=user,
        email=user.email
    )
    
    send_verification_email(user.email, verification.code)
    
    return JsonResponse({'message': 'Verification code sent successfully.'})

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Django uses 'username' field
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=email, password=password)
            if user is not None:
                if not user.is_email_verified:
                    messages.error(request, 'Please verify your email before logging in.')
                    return redirect('accounts:signup')
                
                login(request, user)
                next_url = request.GET.get('next', 'website:home')
                messages.success(request, f'Welcome back, {user.get_short_name()}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('website:home')

@login_required
def profile_view(request):
    """Display user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def delete_account_view(request):
    """Delete user account"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('website:home')
    
    return render(request, 'accounts/delete_account.html')

# Helper functions
def send_verification_email(email, code):
    """Send the sign-up / login verification code."""
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import escape

    subject = f'Your mkhmd.uk verification code: {code}'
    text = (
        f"Hello!\n\n"
        f"Your verification code for mkhmd.uk is: {code}\n\n"
        f"It expires in 10 minutes. If you didn't request it, you can ignore this email.\n\n"
        f"Abdurohman\nhttps://mkhmd.uk\n"
    )
    html = f"""<!DOCTYPE html><html><body style="margin:0;background:#f4f4f7;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;">
<table role="presentation" width="100%" style="padding:32px 0;"><tr><td align="center">
<table role="presentation" width="480" style="max-width:100%;background:#fff;border-radius:14px;overflow:hidden;">
<tr><td style="background:linear-gradient(135deg,#7c3aed,#5b21b6);padding:24px 32px;color:#fff;font-family:monospace;font-size:15px;">&lt;abdurohman/&gt;</td></tr>
<tr><td style="padding:32px;color:#1f2937;font-size:15px;line-height:1.6;">
<h1 style="margin:0 0 12px;font-size:20px;">Your verification code</h1>
<p style="margin:0 0 20px;">Enter this code on mkhmd.uk to continue:</p>
<div style="font-size:34px;font-weight:700;letter-spacing:10px;background:#f3f0ff;color:#5b21b6;border-radius:12px;padding:18px;text-align:center;font-family:monospace;">{escape(code)}</div>
<p style="margin:20px 0 0;color:#6b7280;font-size:13px;">It expires in 10 minutes. If you didn't request it, you can safely ignore this email.</p>
</td></tr>
<tr><td style="padding:16px 32px;background:#fafafa;color:#9ca3af;font-size:12px;">Sent by mkhmd.uk</td></tr>
</table></td></tr></table></body></html>"""

    try:
        mail = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [email])
        mail.attach_alternative(html, 'text/html')
        mail.send(fail_silently=False)
        return True
    except Exception as e:
        import sys
        print(f"Failed to send verification email to {email}: {e!r}", file=sys.stderr)
        return False

# API Views for AJAX requests
@csrf_exempt
def check_email_availability(request):
    """Check if email is available"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'available': False})
        return JsonResponse({'available': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ---------------------------------------------------------------------------
# Notifications (bell icon)
# ---------------------------------------------------------------------------
from django.views.decorators.http import require_POST
from django.utils.timesince import timesince


def _notification_dict(n):
    return {
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'link': n.link,
        'level': n.level,
        'is_read': n.is_read,
        'when': timesince(n.created_at).split(',')[0] + ' ago',
    }


@login_required
def notifications_page(request):
    items = list(request.user.notifications.all()[:100])
    unread_ids = [n.id for n in items if not n.is_read]
    response = render(request, 'accounts/notifications.html', {
        'title': 'Notifications',
        'name': 'Abdurohman',
        'items': items,
        'unread_ids': unread_ids,
    })
    if unread_ids:
        request.user.notifications.filter(id__in=unread_ids).update(is_read=True)
    return response


@login_required
def notifications_api(request):
    qs = request.user.notifications.all()
    return JsonResponse({
        'unread': qs.filter(is_read=False).count(),
        'items': [_notification_dict(n) for n in qs[:8]],
    })


@login_required
@require_POST
def notifications_mark_read(request):
    try:
        data = json.loads(request.body or '{}')
    except ValueError:
        data = {}
    qs = request.user.notifications.filter(is_read=False)
    if data.get('id'):
        qs = qs.filter(id=data['id'])
    qs.update(is_read=True)
    return JsonResponse({'success': True, 'unread': request.user.notifications.filter(is_read=False).count()})
