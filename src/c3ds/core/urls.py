from django.urls import path

from c3ds.core.views import GenericView, TestView

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('views/<int:pk>/', GenericView.as_view(), name='view_by_pk'),
    path('views/<slug:slug>/', GenericView.as_view(), name='view_by_slug'),
]
