from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('donate', views.donate, name='donate'),
    path('sponsor', views.sponsor_request, name='sponsor'),
    path('resources', views.resources, name='resources'),
    path('resources_download', views.resources_download, name='resources_download'),
    path('admin-resources', views.admin_resources, name='admin_resources'),
    path('upload_resource', views.upload_resource, name='upload_resource'),
    path("delete_resource/<str:pk>", views.delete_resource, name="delete_resources"),
    path('single_resource/<str:pk>', views.single_resource, name='single_resources'),
    path('events', views.events, name='events'),
    path('admin_events', views.admin_events, name='admin_events'),
    path('upload_event', views.create_event, name='upload_event'),
    path('community_offline', views.community_offline, name='community_offline'),
    path('community', views.community, name='community'),
    path('all_members', views.member_directory, name='all_members'),
    path('create_topic', views.create_topic, name='create_topic'),
    path('delete_post/<str:pk>', views.delete_topic, name='delete_post'),
    path('delete_event/<str:pk>', views.delete_event, name='delete_event'),
    path('featured_event/<str:pk>', views.featured_event, name='featured_event'),
    path('single_event/<str:pk>', views.get_event, name='single_event'),
]
