from django.urls import path

from c3ds.core.views import DisplayView, GenericView, ShellView

urlpatterns = [
    path('views/<int:pk>/', GenericView.as_view(), name='view_by_pk'),
    path('views/<slug:slug>/', GenericView.as_view(), name='view_by_slug'),
    path('shell/<slug:slug>/', ShellView.as_view(), name='shell_by_slug'),
    path('display/<slug:slug>/', DisplayView.as_view(), name='display_by_slug_long'),
    path('d/<slug:slug>/', DisplayView.as_view(), name='display_by_slug'),
]
