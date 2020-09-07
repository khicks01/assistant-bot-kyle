from django.contrib import admin

from .models import SlackPost
# Register your models here.

class SlackPostAdmin(admin.ModelAdmin):
    list_display = ('time_stamp' , 'user_request' , 'user')

admin.site.register(SlackPost, SlackPostAdmin)
