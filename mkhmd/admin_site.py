"""
Custom admin site: a friendly dashboard with plain-English sections,
"needs attention" counters, quick actions and a setup checklist.
"""
from datetime import timedelta

from functools import partial, update_wrapper

from django.contrib.admin import AdminSite
from django.urls import NoReverseMatch, path, reverse
from django.utils import timezone


# Sections shown on the dashboard and in the sidebar, in this order.
# (app_label, ModelName, friendly name, short explanation)
ADMIN_SECTIONS = [
    {
        'title': 'Website content',
        'icon': 'globe',
        'description': 'What visitors see on mkhmd.uk.',
        'models': [
            ('website', 'Project', 'Projects', 'Projects shown on the homepage, Portfolio and Projects pages.'),
            ('website', 'TimeSlot', 'Weekly availability', 'The hours people can book a meeting with you.'),
        ],
    },
    {
        'title': 'Meetings',
        'icon': 'calendar',
        'description': 'Meeting requests from the Schedule page.',
        'models': [
            ('website', 'Booking', 'Meeting requests', 'Confirm, complete or cancel meeting requests.'),
        ],
    },
    {
        'title': 'Messages',
        'icon': 'chat',
        'description': 'Conversations with visitors and users.',
        'models': [
            ('website', 'ChatSession', 'Chat records', 'Raw chat list. Use the Chat inbox to read and reply.'),
            ('website', 'AIChat', 'AI chats', "Users' conversations with the AI assistant (read-only history)."),
        ],
    },
    {
        'title': 'People',
        'icon': 'users',
        'description': 'Accounts registered on the site.',
        'models': [
            ('accounts', 'User', 'Users', 'Accounts, passwords, admin access and Turnitin credits.'),
            ('accounts', 'UserProfile', 'User profiles', 'Extra details users filled in on their profile.'),
            ('accounts', 'Notification', 'Sent notifications', 'Every notification delivered to each user.'),
        ],
    },
    {
        'title': 'Turnitin',
        'icon': 'file',
        'description': 'Plagiarism-check service.',
        'models': [
            ('accounts', 'TurnitinSubmission', 'Submissions', 'Documents users submitted and their results.'),
        ],
    },
    {
        'title': 'Advanced',
        'icon': 'sliders',
        'description': 'Low-level records. You rarely need these.',
        'models': [
            ('website', 'ChatMessage', 'Individual chat messages', None),
            ('website', 'AIChatMessage', 'Individual AI messages', None),
            ('accounts', 'EmailVerification', 'Email verification codes', None),
            ('auth', 'Group', 'Permission groups', None),
        ],
    },
]


MODEL_ICONS = {
    'Project': 'folder', 'TimeSlot': 'clock', 'Booking': 'calendar',
    'ChatSession': 'chat', 'AIChat': 'sparkle', 'User': 'users', 'UserProfile': 'user',
    'Notification': 'bell', 'TurnitinSubmission': 'file',
}


def _url(name, *args, query=''):
    try:
        return reverse(name, args=args) + query
    except NoReverseMatch:
        return None


class MkhmdAdminSite(AdminSite):
    site_header = 'mkhmd.uk · Admin'
    site_title = 'mkhmd.uk admin'
    index_title = 'Dashboard'
    site_url = '/'

    def get_urls(self):
        from . import admin_views as v

        def view(func, cacheable=False):
            wrapped = self.admin_view(partial(func, self), cacheable=cacheable)
            return update_wrapper(wrapped, func)

        custom = [
            path('inbox/', view(v.inbox), name='mkhmd_inbox'),
            path('inbox/api/sessions/', view(v.inbox_sessions), name='mkhmd_inbox_sessions'),
            path('inbox/api/unread/', view(v.inbox_unread_count), name='mkhmd_inbox_unread'),
            path('inbox/api/<int:session_id>/', view(v.inbox_session), name='mkhmd_inbox_session'),
            path('inbox/api/<int:session_id>/send/', view(v.inbox_send), name='mkhmd_inbox_send'),
            path('inbox/api/<int:session_id>/toggle/', view(v.inbox_toggle), name='mkhmd_inbox_toggle'),
            path('notifications/', view(v.notifications), name='mkhmd_notifications'),
        ]
        return custom + super().get_urls()

    def each_context(self, request):
        context = super().each_context(request)
        if request.user.is_authenticated and request.user.is_staff:
            from website.models import ChatSession
            context['inbox_unread'] = ChatSession.objects.filter(
                messages__is_from_admin=False, messages__is_read=False).distinct().count()
        return context

    def get_app_list(self, request, app_label=None):
        # App-specific pages keep Django's default behaviour.
        if app_label:
            return super().get_app_list(request, app_label)

        app_dict = self._build_app_dict(request)
        available = {}
        for app in app_dict.values():
            for model in app['models']:
                available[(app['app_label'], model['object_name'])] = model

        sections = []
        used = set()
        for section in ADMIN_SECTIONS:
            models = []
            for app_label_, object_name, name, description in section['models']:
                model = available.get((app_label_, object_name))
                if not model:
                    continue
                used.add((app_label_, object_name))
                models.append(dict(model, name=name, description=description,
                                   icon=MODEL_ICONS.get(object_name, 'sliders')))
            if models:
                sections.append(self._section(section, models))

        # Anything not listed above still shows up, under "Other".
        leftovers = [m for key, m in available.items() if key not in used]
        if leftovers:
            sections.append(self._section(
                {'title': 'Other', 'icon': 'folder', 'description': ''},
                [dict(m, description=None, icon='folder') for m in leftovers],
            ))
        return sections

    @staticmethod
    def _section(section, models):
        return {
            'name': section['title'],
            'icon': section['icon'],
            'description': section['description'],
            'app_label': section['title'].lower().replace(' ', '_'),
            'app_url': models[0]['admin_url'],
            'has_module_perms': True,
            'models': models,
        }

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self._dashboard_context(request))
        return super().index(request, extra_context)

    def _dashboard_context(self, request):
        from accounts.models import TurnitinSubmission, User
        from website.models import Booking, ChatSession, Project, TimeSlot

        today = timezone.localdate()
        week_ago = timezone.now() - timedelta(days=7)

        pending_bookings = Booking.objects.filter(status='pending', date__gte=today)
        upcoming = Booking.objects.filter(
            status__in=['pending', 'confirmed'], date__gte=today, date__lte=today + timedelta(days=7)
        ).order_by('date', 'start_time')[:5]
        unread_chats = ChatSession.objects.filter(messages__is_from_admin=False, messages__is_read=False).distinct()
        ongoing_turnitin = TurnitinSubmission.objects.filter(submission_status=False)

        attention = [
            {
                'count': pending_bookings.count(),
                'label': 'meeting requests waiting for confirmation',
                'url': _url('admin:website_booking_changelist', query='?status__exact=pending'),
                'action': 'Review',
            },
            {
                'count': unread_chats.count(),
                'label': 'chats with unread messages',
                'url': _url('admin:mkhmd_inbox'),
                'action': 'Reply',
            },
            {
                'count': ongoing_turnitin.count(),
                'label': 'Turnitin checks still in progress',
                'url': _url('admin:accounts_turnitinsubmission_changelist', query='?submission_status__exact=0'),
                'action': 'View',
            },
        ]

        active_projects = Project.objects.filter(is_active=True)
        has_featured = active_projects.filter(is_featured=True).exists()
        has_slots = TimeSlot.objects.filter(is_active=True).exists()
        checklist = [
            {
                'done': active_projects.exists(),
                'label': 'Add at least one project',
                'help': 'Projects appear on the homepage, Portfolio and Projects pages.',
                'url': _url('admin:website_project_add'),
            },
            {
                'done': has_featured,
                'label': 'Choose a featured project',
                'help': 'Open a project and tick "Is featured". It becomes the big card on the homepage.',
                'url': _url('admin:website_project_changelist'),
            },
            {
                'done': has_slots,
                'label': 'Set your weekly availability',
                'help': 'Without it, the Schedule page shows a simple request form instead of a calendar.',
                'url': _url('admin:website_timeslot_add'),
            },
        ]

        stats = [
            {'value': User.objects.count(), 'label': 'Users',
             'sub': f'+{User.objects.filter(date_joined__gte=week_ago).count()} this week',
             'url': _url('admin:accounts_user_changelist')},
            {'value': active_projects.count(), 'label': 'Visible projects',
             'sub': f'{Project.objects.filter(is_active=False).count()} hidden',
             'url': _url('admin:website_project_changelist')},
            {'value': Booking.objects.filter(status='confirmed', date__gte=today).count(), 'label': 'Confirmed meetings',
             'sub': 'upcoming', 'url': _url('admin:website_booking_changelist', query='?status__exact=confirmed')},
            {'value': ChatSession.objects.filter(is_active=True).count(), 'label': 'Open chats',
             'sub': f'{ChatSession.objects.filter(created_at__gte=week_ago).count()} new this week',
             'url': _url('admin:website_chatsession_changelist')},
        ]

        quick_actions = [
            {'icon': 'plus', 'label': 'Add a project', 'url': _url('admin:website_project_add')},
            {'icon': 'clock', 'label': 'Add available hours', 'url': _url('admin:website_timeslot_add')},
            {'icon': 'chat', 'label': 'Open chat inbox', 'url': _url('admin:mkhmd_inbox')},
            {'icon': 'bell', 'label': 'Send a notification', 'url': _url('admin:mkhmd_notifications')},
            {'icon': 'calendar', 'label': 'All meeting requests', 'url': _url('admin:website_booking_changelist')},
            {'icon': 'key', 'label': 'Give Turnitin credits', 'url': _url('admin:accounts_user_changelist')},
            {'icon': 'globe', 'label': 'Open the website', 'url': '/'},
        ]

        from .admin_views import _session_dict, _sessions_queryset
        recent_chats = [_session_dict(s) for s in _sessions_queryset()[:4]]

        return {
            'recent_chats': recent_chats,
            'attention': attention,
            'attention_total': sum(item['count'] for item in attention),
            'upcoming_bookings': upcoming,
            'checklist': checklist,
            'checklist_done': all(item['done'] for item in checklist),
            'stats': stats,
            'quick_actions': [a for a in quick_actions if a['url']],
            'greeting_name': request.user.first_name or request.user.username,
        }


def friendly_name(model):
    """The plain-English name for a model, as listed in ADMIN_SECTIONS."""
    for section in ADMIN_SECTIONS:
        for app_label, object_name, name, _ in section['models']:
            if model._meta.app_label == app_label and model.__name__ == object_name:
                return name
    return model._meta.verbose_name_plural.capitalize()


class FriendlyAdminMixin:
    """Use the plain-English name as the title of list pages."""

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': friendly_name(self.model), **(extra_context or {})}
        return super().changelist_view(request, extra_context)
