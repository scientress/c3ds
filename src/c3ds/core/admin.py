from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from c3ds.core.models import (Display, HTMLView, IFrameView, ImageFile, ImageView, Schedule, ScheduleView, VideoFile,
                              VideoView)


@admin.register(Display)
class DisplayAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'static_view', 'playlist', 'last_changed')


@admin.register(HTMLView)
class HTMLViewAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'title', 'last_changed')

@admin.register(IFrameView)
class IFrameViewAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'title', 'layout_mode', 'url', 'last_changed')


@admin.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'filename', 'file', 'file_link', 'last_changed')

    def file_link(self, obj) -> str:
        return mark_safe(f'<a href="{obj.file.url}" target="_blank" alt="{obj.name}">View</a>')


@admin.register(ImageView)
class ImageViewAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'title', 'layout_mode', 'image', 'last_changed')


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'filename', 'file', 'loop', 'file_link', 'last_changed')

    def file_link(self, obj) -> str:
        return mark_safe(f'<a href="{obj.file.url}" target="_blank" alt="{obj.name}">View</a>')


@admin.register(VideoView)
class VideoViewAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'title', 'layout_mode', 'video', 'video_url', 'last_changed')


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
class ScheduleViewAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'title', 'layout_mode', 'schedule', 'room_filter', 'last_changed')
