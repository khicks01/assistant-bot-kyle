from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.http import HttpResponse, JsonResponse
import slack
@csrf_exempt
def event_hook(request):
    client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
    json_dict = json.loads(request.body.decode('utf-8'))
    if json_dict['token'] != settings.VERIFICATION_TOKEN:
        return HttpResponse(status=403)

    if 'type' in json_dict:
        if json_dict['type'] == 'url_verification':
            response_dict = {"challenge": json_dict['challenge']}
            return JsonResponse(response_dict, safe=False)
    
    if 'bot_id' in json_dict:
        return HttpResponse(status=200)

    if 'event' in json_dict:
        event_msg = json_dict['event']
        print(event_msg)

        if event_msg['type'] == 'message':
            user = event_msg['user']
            if(user != U01ACS227RS):
                channel = event_msg['channel']
                response_msg = "payload: <@%s>" % event_msg
                client.chat_postMessage(channel=channel, text=response_msg)
                return HttpResponse(status=200)

    return HttpResponse(status=200)