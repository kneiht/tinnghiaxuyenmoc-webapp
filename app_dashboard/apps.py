from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_dashboard'
    def ready(self):
        import app_dashboard.models.signals  # Import signals when Django starts