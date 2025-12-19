import datetime

import channels.layers
from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib import admin
from django.core.cache import cache
from django.db import models
from django.db.models import functions
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from c3ds.core.models import (Display, DisplayQuerySet, HTMLView, IFrameView, ImageFile, ImageView, Schedule,
                              ScheduleView, VideoFile, VideoView)

class SlugLinkMixin():
    slug_view = 'view_by_slug'

    def link(self, obj):
        if not obj.slug:
            return ''
        url = reverse(self.slug_view, kwargs={'slug': obj.slug})
        return mark_safe(f'<a href="{url}" target="_blank">view</a>')


@admin.register(Display)
class DisplayAdmin(admin.ModelAdmin, SlugLinkMixin):
    list_display = ['name', 'slug', 'static_view', 'playlist', 'link', 'c3nav', 'heartbeat']
    if settings.REMOTE_SHELL:
        list_display.append('shell')
    list_display.append('last_changed')
    slug_view = 'display_by_slug'

    fields = ('name', 'slug', 'static_view', 'playlist', 'link', 'c3nav', 'last_seen', 'last_changed')
    readonly_fields = ('link', 'c3nav', 'last_seen', 'last_changed')
    actions = ('reload', )

    def c3nav(self, obj):
        return mark_safe(f'<a href="https://38c3.c3nav.de/l/{obj.slug.lower()}" target="_blank">map</a>')

    def shell(self, obj):
        if not settings.REMOTE_SHELL:
            return ''
        url = reverse('shell_by_slug', kwargs={'slug': obj.slug})
        return mark_safe(f'<a href="{url}" target="_blank">shell</a>')

    def heartbeat(self, obj: Display):
        last = cache.get(obj.get_heartbeat_cache_key())
        if last is None or not isinstance(last, datetime.datetime):
            return 'Unknown'
        else:
            if (datetime.datetime.now(tz=datetime.UTC) - last).total_seconds() < 60:
                return mark_safe('<span style="color: green;">Online</span>')
            else:
                return mark_safe('<span style="color: red;">Offline</span>')

    def last_seen(self, obj: Display):
        last = cache.get(obj.get_heartbeat_cache_key())
        if last is None or not isinstance(last, datetime.datetime):
            return 'Unknown'
        else:
            return last.strftime('%Y-%m-%d %H:%M')

    @admin.action(description=_('Reload Display(s)'))
    def reload(self, request: HttpRequest, queryset: DisplayQuerySet):
        queryset.reload()


class ViewAdmin(admin.ModelAdmin, SlugLinkMixin):
    actions = ('reload',)

    @admin.action(description=_('Reload Sssigned Display(s)'))
    def reload(self, request: HttpRequest, queryset):
        num_displays = queryset.annotate(num_displays = functions.Coalesce(models.Count('displays'), 0))\
            .aggregate(num_displays=models.Sum('num_displays', default=0))['num_displays']
        delayed = num_displays > settings.DELAYED_RELOAD_THRESHOLD
        for view in queryset.all():
            view.displays.reload(delayed)


@admin.register(HTMLView)
class HTMLViewAdmin(ViewAdmin):
    list_display = ('name', 'slug', 'title', 'link', 'last_changed')


@admin.register(IFrameView)
class IFrameViewAdmin(ViewAdmin):
    list_display = ('name', 'slug', 'title', 'layout_mode', 'url', 'link', 'last_changed')


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'filename', 'file', 'file_link', 'last_changed')

    def file_link(self, obj) -> str:
        return mark_safe(f'<a href="{obj.file.url}" target="_blank" alt="{obj.name}">View</a>')


@admin.register(ImageView)
class ImageViewAdmin(ViewAdmin):
    list_display = ('name', 'slug', 'title', 'layout_mode', 'image', 'link', 'last_changed')


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'filename', 'file', 'loop', 'file_link', 'last_changed')

    def file_link(self, obj) -> str:
        return mark_safe(f'<a href="{obj.file.url}" target="_blank" alt="{obj.name}">View</a>')


@admin.register(VideoView)
class VideoViewAdmin(ViewAdmin):
    list_display = ('name', 'slug', 'title', 'layout_mode', 'video', 'video_url', 'link', 'last_changed')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'last_changed')
    fields = ('name', 'url', 'uuid', 'version', 'etag', 'file', 'last_changed')
    readonly_fields = ('uuid', 'version', 'etag', 'file', 'last_changed')
    actions = ('update_schedule',)

    @admin.action(description=_('Update Schedule'))
    def update_schedule(self, request, queryset):
        for schedule in queryset:
            schedule.update_schedule()


@admin.register(ScheduleView)
class ScheduleViewAdmin(ViewAdmin):
    list_display = ('name', 'slug', 'title', 'layout_mode', 'schedule', 'room_filter', 'link', 'last_changed')
