from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import slack

from .models import SlackPost, AnswersDatabase



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
            #Make sure the post is not coming from the bot itself
            if(user != 'U01ACS227RS'):
                message_timestamp = event_msg['ts']
                channel = event_msg['channel']
                text = event_msg['text'].lower().strip()
                words = text.split(" ")
                answer_msg = []
                for each_word in words:
                    try:
                        print(each_word)
                        helpful_links = AnswersDatabase.objects.get(keywords__icontains=each_word)
                        answer_msg.append(helpful_links.resource)
                    except:
                        print("no value found")
                
                #message receipt and logging
                obj, created = SlackPost.objects.get_or_create(user_request= text)
                if(created):
                    response_msg = "I added this request to the request database"
                else:
                    response_msg = "Already part of the database"
                client.chat_postMessage(channel=channel, thread_ts= message_timestamp, text=response_msg)

                # answer given by bot
                if len(answer_msg) != 0:
                    client.chat_postMessage(channel=channel, thread_ts= message_timestamp, text=answer_msg)
                else:
                    answer_msg = "We didn't find a helpful link for your query, sorry"
                    client.chat_postMessage(channel=channel, thread_ts= message_timestamp, text=answer_msg)
                return HttpResponse(status=200)
    return HttpResponse(status=200)