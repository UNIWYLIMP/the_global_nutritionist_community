from django.contrib import admin
from .models import *

models = [Blog, BlogReply, CommunityTopicReply, CommunityTopic, CustomUser, SponsorRequest, ContactUs, ImageDump,
          FileDump, Resource, EventReply, Event, EventAttendance, ]

# Register your models here.
admin.site.register(models)