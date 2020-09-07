from django.urls import include, path
from . import views

app_name = 'actions'

urlpatterns = [
    path('event/hook/', views.event_hook, name='event_hook'),
    ]