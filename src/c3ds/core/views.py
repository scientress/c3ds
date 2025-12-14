from typing import Optional

from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView, TemplateView

from c3ds.core.models import BaseView, Display


class GenericView(DetailView):
    model = BaseView
    context_object_name = 'view'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return obj.get_specific()

    def get_template_names(self):
        return [self.object.get_template_name()]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'layout_mode': getattr(self.object, 'layout_mode', 'normal')
        })
        return ctx


class ShellView(DetailView):
    model = Display
    context_object_name = 'shell'

    template_name = "core/remote_shell_backend.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'slug': self.kwargs.get(self.slug_url_kwarg)
        })
        return ctx


class DisplayView(DetailView):
    model = Display
    context_object_name = 'display'
    is_unconfigured = False
    _view = None

    def get_queryset(self):
        return super().get_queryset().select_related('playlist', 'static_view')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            obj = super().get_object(queryset=queryset)
        except (queryset.model.DoesNotExist, Http404):
            obj = None
            self.is_unconfigured = True
        return obj

    def get_template_names(self):
        if self.is_unconfigured:
            return ['core/display_unconfigured_view.html']
        elif self.object.static_view is not None:
            return [self.get_view().get_template_name()]
        else:
            raise NotImplementedError('Playlist support not yet implemented')


    def get_view(self) -> Optional[BaseView]:
        if self.is_unconfigured or self.object is None:
            return None
        if self._view is None:
            self._view = self.object.static_view.get_specific()
        return self._view

    def get_layout_mode(self):
        return getattr(self.get_view(), 'layout_mode', 'normal') if self.get_view() is not None else 'normal'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'view': self.get_view(),
            'layout_mode': self.get_layout_mode(),
            'slug': self.kwargs.get(self.slug_url_kwarg)
        })
        return ctx
