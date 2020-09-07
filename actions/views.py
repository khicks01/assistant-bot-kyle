from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import slack

from .models import SlackPost



@csrf_exempt
def event_hook(request):
    client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
    json_dict = json.loads(request.body.decode('utf-8'))
    #check if this is a verification challenge
    if json_dict['token'] != settings.VERIFICATION_TOKEN:
        return HttpResponse(status=403)
    if 'type' in json_dict:
        if json_dict['type'] == 'url_verification':
            response_dict = {"challenge": json_dict['challenge']}
            return JsonResponse(response_dict, safe=False)
    #if this is a normal event which the bot is subscribed to
    if 'event' in json_dict:
        event_msg = json_dict['event']
        if event_msg['type'] == 'message':
            user = event_msg['user']
            message_timestamp = event_msg['ts']
            #Make sure the post is not coming from the bot itself
            if(user != 'U01ACS227RS'):
                channel = event_msg['channel']
                new_db_entry = SlackPost()
                new_db_entry.user = user
                new_db_entry.user_request = event_msg['text']
                new_db_entry.save()
                response_msg = "I added this request to the database"
                client.chat_postMessage(channel=channel, thread_ts= message_timestamp, text=response_msg)
                return HttpResponse(status=200)
    return HttpResponse(status=200)