"""
Extra admin pages: the chat inbox and the notification composer.
They are wired into the admin in MkhmdAdminSite.get_urls().
"""
import json

from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Count, Max, Q
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import escape, linebreaks


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _visitor_name(session):
    if session.user:
        return session.user.get_full_name() or session.user.username
    if session.visitor_name:
        return session.visitor_name
    return f"Visitor #{session.session_id.hex[:6]}"


def _visitor_contact(session):
    if session.user:
        return session.user.email
    return session.visitor_email or ''


def _initials(name):
    parts = [p for p in name.replace('#', ' ').split() if p]
    return ''.join(p[0] for p in parts[:2]).upper() or '?'


def _when(dt):
    now = timezone.now()
    local = timezone.localtime(dt)
    if local.date() == timezone.localdate():
        return local.strftime('%H:%M')
    if (now - dt).days < 7:
        return local.strftime('%a')
    return local.strftime('%d %b')


def _session_dict(s):
    name = _visitor_name(s)
    last = s.messages.order_by('-created_at').first()
    return {
        'id': s.id,
        'name': name,
        'initials': _initials(name),
        'contact': _visitor_contact(s),
        'is_user': bool(s.user_id),
        'is_active': s.is_active,
        'unread': s.unread_count,
        'last_message': (('You: ' if last.is_from_admin else '') + last.message[:90]) if last else 'No messages yet',
        'last_at': _when(last.created_at) if last else _when(s.created_at),
    }


def _message_dict(m):
    local = timezone.localtime(m.created_at)
    return {
        'id': m.id,
        'text': m.message,
        'mine': m.is_from_admin,
        'time': local.strftime('%H:%M'),
        'day': local.strftime('%A, %d %B %Y'),
    }


def _sessions_queryset(q='', only_unread=False):
    from website.models import ChatSession
    qs = ChatSession.objects.select_related('user').annotate(
        unread_count=Count('messages', filter=Q(messages__is_from_admin=False, messages__is_read=False)),
        last_activity=Max('messages__created_at'),
    ).filter(messages__isnull=False).distinct()
    if q:
        qs = qs.filter(
            Q(visitor_name__icontains=q) | Q(visitor_email__icontains=q) |
            Q(user__username__icontains=q) | Q(user__email__icontains=q) |
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) |
            Q(messages__message__icontains=q)
        ).distinct()
    if only_unread:
        qs = qs.filter(unread_count__gt=0)
    return qs.order_by('-last_activity')


# ---------------------------------------------------------------------------
# Chat inbox
# ---------------------------------------------------------------------------

def inbox(site, request):
    context = {
        **site.each_context(request),
        'title': 'Chat inbox',
        'open_id': request.GET.get('chat', ''),
    }
    return TemplateResponse(request, 'admin/mkhmd/inbox.html', context)


def inbox_sessions(site, request):
    qs = _sessions_queryset(request.GET.get('q', '').strip(), request.GET.get('filter') == 'unread')
    sessions = [_session_dict(s) for s in qs[:100]]
    return JsonResponse({
        'sessions': sessions,
        'total_unread': sum(1 for s in sessions if s['unread']),
    })


def inbox_session(site, request, session_id):
    from website.models import ChatSession
    session = get_object_or_404(ChatSession.objects.select_related('user'), pk=session_id)
    after = int(request.GET.get('after', 0) or 0)
    msgs = session.messages.order_by('created_at')
    if after:
        msgs = msgs.filter(id__gt=after)
    data = [_message_dict(m) for m in msgs]

    # Opening a conversation marks the visitor's messages as read.
    updated = session.messages.filter(is_from_admin=False, is_read=False).update(is_read=True)
    if updated or not session.is_read_by_admin:
        type(session).objects.filter(pk=session.pk).update(is_read_by_admin=True)

    name = _visitor_name(session)
    return JsonResponse({
        'session': {
            'id': session.id,
            'name': name,
            'initials': _initials(name),
            'contact': _visitor_contact(session),
            'is_user': bool(session.user_id),
            'is_active': session.is_active,
            'started': timezone.localtime(session.created_at).strftime('%d %b %Y, %H:%M'),
            'admin_url': f'/admin/website/chatsession/{session.id}/change/',
        },
        'messages': data,
    })


def inbox_send(site, request, session_id):
    from website.models import ChatMessage, ChatSession
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    session = get_object_or_404(ChatSession.objects.select_related('user'), pk=session_id)
    try:
        data = json.loads(request.body or '{}')
    except ValueError:
        return HttpResponseBadRequest('Invalid JSON')
    text = (data.get('message') or '').strip()
    if not text:
        return JsonResponse({'success': False, 'error': 'Message is empty'}, status=400)

    msg = ChatMessage.objects.create(session=session, message=text, is_from_admin=True)
    session.is_read_by_admin = True
    session.is_active = True
    session.save()

    notified = emailed = False
    # Registered users get a bell notification so they see the reply next visit.
    if session.user_id:
        from accounts.notifications import notify
        notify([session.user], 'New reply from Abdurakhmon', text[:300],
               link='/support-chat/', level='info', sent_by=request.user,
               email=bool(data.get('email')))
        notified = True
        emailed = bool(data.get('email'))
    # Anonymous visitors can only be reached by email, if they left one.
    elif data.get('email') and session.visitor_email:
        try:
            body = (f"<p>Hi {escape(session.visitor_name or 'there')},</p>"
                    f"{linebreaks(escape(text))}"
                    f"<p>You can reply in the chat on <a href='https://mkhmd.uk/'>mkhmd.uk</a>.</p>"
                    f"<p>— Abdurakhmon</p>")
            mail = EmailMultiAlternatives('Reply from Abdurakhmon (mkhmd.uk)', text,
                                          settings.DEFAULT_FROM_EMAIL, [session.visitor_email])
            mail.attach_alternative(body, 'text/html')
            mail.send()
            emailed = True
        except Exception as exc:
            print(f"Chat reply email failed: {exc}")

    return JsonResponse({'success': True, 'message': _message_dict(msg),
                         'notified': notified, 'emailed': emailed})


def inbox_toggle(site, request, session_id):
    from website.models import ChatSession
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    session = get_object_or_404(ChatSession, pk=session_id)
    session.is_active = not session.is_active
    session.save(update_fields=['is_active', 'updated_at'])
    return JsonResponse({'success': True, 'is_active': session.is_active})


def inbox_unread_count(site, request):
    from website.models import ChatSession
    count = ChatSession.objects.filter(messages__is_from_admin=False, messages__is_read=False).distinct().count()
    return JsonResponse({'unread': count})


# ---------------------------------------------------------------------------
# Notifications composer
# ---------------------------------------------------------------------------

def notifications(site, request):
    from accounts.models import Notification, User
    from accounts.notifications import notify

    form = {'audience': 'all', 'title': '', 'message': '', 'link': '', 'level': 'info', 'email': False, 'users': []}

    if request.method == 'POST':
        form = {
            'audience': request.POST.get('audience', 'all'),
            'title': request.POST.get('title', '').strip(),
            'message': request.POST.get('message', '').strip(),
            'link': request.POST.get('link', '').strip(),
            'level': request.POST.get('level', 'info'),
            'email': request.POST.get('email') == 'on',
            'users': [int(u) for u in request.POST.getlist('users') if u.isdigit()],
        }
        errors = []
        if not form['title']:
            errors.append('Please write a title.')
        if form['level'] not in dict(Notification.LEVEL_CHOICES):
            form['level'] = 'info'
        if form['link'] and not (form['link'].startswith('/') or form['link'].startswith('http')):
            errors.append('The link must start with / (a page on your site) or http.')

        recipients = User.objects.filter(is_active=True)
        if form['audience'] == 'verified':
            recipients = recipients.filter(is_email_verified=True)
        elif form['audience'] == 'selected':
            recipients = recipients.filter(id__in=form['users'])
            if not form['users']:
                errors.append('Pick at least one person, or choose "Everyone".')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            created, emailed, _ = notify(recipients, form['title'], form['message'], form['link'],
                                         form['level'], sent_by=request.user, email=form['email'])
            note = f'Sent to {created} {"person" if created == 1 else "people"}.'
            if form['email']:
                note += f' {emailed} email{"" if emailed == 1 else "s"} delivered.'
            messages.success(request, note)
            return redirect('admin:mkhmd_notifications')

    # History: one row per batch.
    batches = (Notification.objects.exclude(batch=None)
               .values('batch', 'title', 'level', 'link')
               .annotate(sent_at=Max('created_at'), recipients=Count('id'),
                         read=Count('id', filter=Q(is_read=True)),
                         emailed=Count('id', filter=Q(emailed=True)))
               .order_by('-sent_at')[:25])
    history = []
    for b in batches:
        sample = Notification.objects.filter(batch=b['batch']).select_related('user').first()
        b['single'] = sample.user if b['recipients'] == 1 and sample else None
        history.append(b)

    users = User.objects.filter(is_active=True).order_by('first_name', 'username')
    context = {
        **site.each_context(request),
        'title': 'Send a notification',
        'form': form,
        'users': users,
        'user_count': users.count(),
        'verified_count': users.filter(is_email_verified=True).count(),
        'history': history,
        'levels': [('info', 'Info', '🔔'), ('success', 'Good news', '🎉'), ('warning', 'Important', '⚠️')],
    }
    return TemplateResponse(request, 'admin/mkhmd/notifications.html', context)


# ---------------------------------------------------------------------------
# GitHub repos shown on the website
# ---------------------------------------------------------------------------

def github_repos(site, request):
    from django.core.cache import cache
    from website.models import GitHubDisplaySettings, GitHubRepo
    from website.views import apply_repo_settings, fetch_github_projects

    username = 'mukhammad-develop'
    settings_obj = GitHubDisplaySettings.load()

    if request.method == 'POST':
        try:
            data = json.loads(request.body or '{}')
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON')
        action = data.get('action')

        if action == 'save':
            name = (data.get('name') or '').strip()
            if not name:
                return JsonResponse({'success': False, 'error': 'Missing repo name'}, status=400)
            repo, _ = GitHubRepo.objects.get_or_create(
                name=name, defaults={'visible': settings_obj.show_new_automatically})
            for field in ('visible', 'pinned'):
                if field in data:
                    setattr(repo, field, bool(data[field]))
            if 'order' in data:
                try:
                    repo.order = int(data['order'] or 0)
                except (TypeError, ValueError):
                    repo.order = 0
            if 'title' in data:
                repo.title = (data['title'] or '').strip()[:200]
            if 'description' in data:
                repo.description = (data['description'] or '').strip()
            repo.save()
            return JsonResponse({'success': True})

        if action == 'settings':
            if 'show_new_automatically' in data:
                settings_obj.show_new_automatically = bool(data['show_new_automatically'])
            if 'homepage_count' in data:
                try:
                    settings_obj.homepage_count = max(0, min(24, int(data['homepage_count'])))
                except (TypeError, ValueError):
                    pass
            settings_obj.save()
            return JsonResponse({'success': True, 'homepage_count': settings_obj.homepage_count})

        if action == 'bulk':
            visible = bool(data.get('visible'))
            for name in data.get('names', []):
                GitHubRepo.objects.update_or_create(name=name, defaults={'visible': visible})
            return JsonResponse({'success': True})

        if action == 'refresh':
            cache.delete(f'github_repos_{username}')
            cache.delete(f'github_profile_{username}')
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Unknown action'}, status=400)

    live = fetch_github_projects(username)
    choices = {r.name: r for r in GitHubRepo.objects.all()}
    shown, _ = apply_repo_settings(live)
    position = {r['name']: i + 1 for i, r in enumerate(shown)}

    rows = []
    for repo in live:
        choice = choices.get(repo['name'])
        rows.append({
            'name': repo['name'],
            'default_title': repo['name'].replace('-', ' ').replace('_', ' ').title(),
            'github_description': repo.get('description') or '',
            'url': repo.get('github_url'),
            'language': repo.get('language') or '',
            'stars': repo.get('stars', 0),
            'updated': repo.get('updated'),
            'visible': choice.visible if choice else settings_obj.show_new_automatically,
            'pinned': bool(choice and choice.pinned),
            'order': choice.order if choice else 0,
            'title': choice.title if choice else '',
            'description': choice.description if choice else '',
            'is_new': choice is None,
            'position': position.get(repo['name']),
        })
    rows.sort(key=lambda r: (r['position'] is None, r['position'] or 0))

    context = {
        **site.each_context(request),
        'title': 'GitHub repos on the website',
        'rows': rows,
        'settings': settings_obj,
        'shown_count': len(shown),
        'total_count': len(live),
        'loaded': bool(live),
    }
    return TemplateResponse(request, 'admin/mkhmd/github_repos.html', context)
