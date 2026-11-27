from django.contrib.admin.apps import AdminConfig


class MkhmdAdminConfig(AdminConfig):
    """Use the friendly dashboard admin site as the default admin."""
    default_site = 'mkhmd.admin_site.MkhmdAdminSite'
