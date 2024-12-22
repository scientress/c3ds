from django.apps import AppConfig

from c3ds.utils.filesystem import check_directory


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'c3ds.core'

    def ready(self):
        from django.conf import settings
        for setting in ('DATA_DIR', 'MEDIA_ROOT', 'STATIC_ROOT'):
            directory = getattr(settings, setting)
            check_directory(directory)

        import c3ds.core.signals  # NoQa
        import c3ds.core.metrics  # NoQa
