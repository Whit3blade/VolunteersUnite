"""volunteer URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.schemas import get_schema_view
from  django.views.generic import TemplateView

urlpatterns = [
    path('', include('volunteeringapp.urls')),
    path('admin/', admin.site.urls),
]
