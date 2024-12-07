from django.urls import path

from c3ds.core.views import TestView, ExampleVueView

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
]
