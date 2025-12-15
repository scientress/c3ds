import datetime
import logging
import uuid
from contextlib import suppress
from pathlib import Path
from typing import Optional, Self

import requests
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class Display(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('Display Name'))
    slug = models.SlugField(verbose_name=_('Display Slug'), unique=True)
    uuid = models.UUIDField(verbose_name=_('Display UUID'), default=uuid.uuid4, editable=False, unique=True)
    static_view = models.ForeignKey('BaseView', on_delete=models.PROTECT, verbose_name=_('Static View'), null=True, blank=True)
    playlist = models.ForeignKey('Playlist', on_delete=models.PROTECT, verbose_name=_('Playlist'), null=True, blank=True)
    last_changed = models.DateTimeField(verbose_name=_('Last Changed'), auto_now=True)
    created_at = models.DateTimeField(verbose_name=_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Display')
        verbose_name_plural = _('Displays')
        default_related_name = 'displays'
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=(Q(static_view__isnull=True) ^ Q(playlist__isnull=True)),
                name='static_view_or_playlist'
            ),
        ]

    def __str__(self):
        return self.name

    @staticmethod
    def heartbeat_cache_key_for_slug(slug: str) -> str:
        return f'{slug}-heartbeat'

    def get_heartbeat_cache_key(self):
        return self.heartbeat_cache_key_for_slug(self.slug)


class MediaFile(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    filename = models.CharField(max_length=128, verbose_name=_('Filename'))
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    last_changed = models.DateTimeField(verbose_name=_('Last Changed'), auto_now=True)
    created_at = models.DateTimeField(verbose_name=_('Created At'), auto_now_add=True)

    class Meta:
        abstract: True
        ordering = ["name"]

    def __str__(self):
        return self.name

class ImageFile(MediaFile):

    display_duration = models.PositiveIntegerField(verbose_name=_('Display Duration'), default=6,
                                                   help_text=_('Duration in seconds'))
    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')


class VideoFile(MediaFile):

    loop = models.BooleanField(default=False, verbose_name=_('Loop Video'))

    class Meta:
        verbose_name = _('Video')
        verbose_name_plural = _('Videos')


class Playlist(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(verbose_name=_('Slug'), unique=True)
    uuid = models.UUIDField(verbose_name=_('UUID'), default=uuid.uuid4, editable=False, unique=True)
    views = models.ManyToManyField('BaseView', verbose_name=_('Views'), related_name='playlists',
                                   through='PlaylistEntry')
    last_changed = models.DateTimeField(verbose_name=_('Last Changed'), auto_now=True)
    created_at = models.DateTimeField(verbose_name=_('Created At'), auto_now_add=True)

    class Meta:
        ordering = ["name"]


class PlaylistEntry(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, verbose_name=_('Playlist'), related_name='entries')
    view = models.ForeignKey('BaseView', on_delete=models.PROTECT, verbose_name=_('View'), related_name='+')
    order = models.PositiveIntegerField(verbose_name=_('Order'))
    display_duration = models.PositiveIntegerField(
        verbose_name=_('Display Duration'), blank=True, null=True,
        help_text=_('Overrides the display duration of an item. (seconds) \n'
                    'If the item is a video and it\'s not set to loop, this setting will be ignored.')
    )


class BaseView(models.Model):
    view = None
    template_name = None
    vue_module = None

    class LayoutModes(models.TextChoices):
        NORMAL = 'normal', _('Normal')
        COVER = 'cover', _('Cover')
        FULLSCREEN = 'fullscreen', _('Full Screen')

    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(verbose_name=_('Slug'), unique=True)
    uuid = models.UUIDField(verbose_name=_('UUID'), default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=128, verbose_name=_('Title'), blank=True)
    layout_mode = models.CharField(verbose_name=_('Layout Mode'), max_length=32, choices=LayoutModes,
                                   default=LayoutModes.NORMAL)
    last_changed = models.DateTimeField(verbose_name=_('Last Changed'), auto_now=True)
    created_at = models.DateTimeField(verbose_name=_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('View')
        verbose_name_plural = _('Views')
        default_related_name = 'views'
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_view(self):
        raise NotImplementedError()
        # ToDo: implement view loading

    def get_template_name(self):
        if self.template_name:
            return self.template_name
        raise ImproperlyConfigured('Subclasses of BaseView must provide a template_name or override get_template_name')

    def get_vue_module(self):
        if self.vue_module:
            return self.vue_module
        raise ImproperlyConfigured('Subclasses of BaseView must provide a vue_module or override get_vue_module')

    def get_specific(self) -> Optional[Self]:
        for field in self._meta.get_fields():
            if not isinstance(field, models.OneToOneRel) or not field.parent_link:
                continue
            with suppress(ObjectDoesNotExist):
                return getattr(self, field.accessor_name)
        return None

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("view_by_pk", kwargs={"pk": self.pk})


class HTMLView(BaseView):
    content = models.TextField(verbose_name=_('HTML Content'), blank=True)
    context = models.JSONField(verbose_name=_('context'), default=dict, blank=True, null=True,
                               help_text=_('Extra data passed to the context'))
    template_name_override = models.CharField(max_length=128, verbose_name=_('Template Name'), blank=True, null=True)
    vue_module_override = models.CharField(max_length=128, verbose_name=_('Vue Module'), blank=True, null=True)

    class Meta:
        verbose_name = _('HTML View')
        verbose_name_plural = _('HTML Views')
        default_related_name = 'html_views'
        ordering = ["name"]

    def get_template_name(self):
        return self.template_name_override or 'core/html_views/generic.html'

    def get_vue_module(self):
        return self.vue_module_override or 'HTMLViewGeneric'


class IFrameView(BaseView):
    template_name = 'core/iframe_view.html'
    vue_module = 'IFrameView'
    url = models.URLField(verbose_name=_('iframe URL'))

    class Meta:
        verbose_name = _('Iframe View')
        verbose_name_plural = _('Iframe Views')
        default_related_name = 'iframe_views'
        ordering = ["name"]


class ImageView(BaseView):
    template_name = 'core/image_view.html'
    vue_module = 'ImageView'
    image = models.ForeignKey(ImageFile, on_delete=models.PROTECT, verbose_name=_('Image'))

    class Meta:
        verbose_name = _('Image View')
        verbose_name_plural = _('Image Views')
        default_related_name = 'image_views'
        ordering = ["name"]


class VideoView(BaseView):
    template_name = 'core/video_view.html'
    vue_module = 'VideoView'
    video = models.ForeignKey(VideoFile, on_delete=models.PROTECT, verbose_name=_('Video'), blank=True, null=True)
    video_url = models.URLField(verbose_name=_('Video URL'), blank=True, null=True,
                                help_text=_('Can also be a hls or dash stream.'))

    class Meta:
        verbose_name = _('Video View')
        verbose_name_plural = _('Video Views')
        default_related_name = 'video_views'
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=(Q(video__isnull=True) ^ Q(video_url__isnull=True)),
                name='video_file_or_video_url'
            ),
        ]

    def get_video_src(self) -> str:
        return self.video_url or self.video.file.url

    def get_video_type(self):
        suffix = self.get_video_src().rsplit('.', 1)[-1]
        match suffix:
            case 'm3u8':
                return 'application/x-mpegURL'
            case 'mpd':
                return 'application/dash+xml'
            case _:
                return f'video/{suffix}'


class Schedule(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    uuid = models.UUIDField(verbose_name=_('UUID'), default=uuid.uuid4, editable=False, unique=True)
    url = models.URLField(verbose_name=_('URL'))
    version = models.CharField(max_length=256, verbose_name=_('Version'), editable=False, null=True, blank=True)
    etag = models.CharField(max_length=256, verbose_name='ETag', editable=False, null=True, blank=True)
    file = models.FileField(verbose_name=_('File'), upload_to='schedule/', null=True, blank=True)
    last_changed = models.DateTimeField(verbose_name=_('Last Changed'), auto_now=True)
    created_at = models.DateTimeField(verbose_name=_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')
        default_related_name = 'schedules'
        ordering = ["name"]

    def __str__(self):
        return self.name

    def update_schedule(self, force: bool = False):
        if self.pk is None:
            raise ValueError('Save model first')
        # start transaction and lock
        with transaction.atomic():
            obj = Schedule.objects.select_for_update().get(pk=self.pk)
            file_time = None
            if self.file:
                with suppress(FileNotFoundError):
                    file_time = datetime.datetime.fromtimestamp(Path(self.file.path).stat().st_mtime, datetime.UTC)\
                        .strftime('%a, %d %b %Y %H:%M:%S GMT')
            req = requests.get(self.url, headers={
                'Accept': 'application/json',
                'If-None-Match': self.etag,
                'If-Modified-Since': None if self.etag else file_time
            })
            if not force and req.status_code == 304:
                logger.info('Not updating schedule "%s" [%d], unchanged. (304)', self.name, self.pk)
                return
            req.raise_for_status()
            data = req.json()
            old_version = self.version
            new_version = data['schedule']['version']
            if not force and self.version and self.version == new_version:
                logger.info('Not updating schedule "%s" [%d], unchanged. (Version)', self.name, self.pk)
                return
            if not self.file.name:
                self.file.name = f'schedules/schedule-{self.uuid}.json'
            with self.file.open('wb') as fp:
                fp.write(req.content)
            self.etag = req.headers.get('ETag', None)
            self.version = new_version
            self.save()
            logger.info('Updated schedule "%s" [%d]: %s → %s', self.name, self.pk, old_version, new_version)

    @property
    def local_url(self):
        return self.file.url


class ScheduleView(BaseView):
    template_name = 'core/schedule_view.html'
    vue_module = 'ScheduleView'
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT, verbose_name=_('Schedule'))
    room_filter = models.CharField(max_length=256, verbose_name=_('Room Filter'), blank=True, null=True,
                                        help_text=_('Room filter for schedule as semicolon-separated list'))

    class Meta:
        verbose_name = _('Schedule View')
        verbose_name_plural = _('Schedule Views')
        default_related_name = 'schedule_views'
        ordering = ["name"]
