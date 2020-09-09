from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core import exceptions
import json
import slack

from .models import SlackPost, AnswersDatabase



@csrf_exempt
def event_hook(request):
    client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
    json_dict = json.loads(request.body.decode('utf-8'))
    #check if this is a verification challenge
    respond_to_subscription_challenge(json_dict, request)
    #if this is a normal event which the bot is subscribed to
    if 'event' in json_dict:
        event_msg = json_dict['event']
        if event_msg['type'] == 'message':
            user = event_msg['user']
            #Make sure the post is not coming from the bot itself
            if(user != 'U01ACS227RS'):
                message_timestamp, channel, text = gather_message_data(event_msg)
                words = text.split(" ")
                answer_msg = []
                #build array of helpful links based on the key word
                answer_msg = find_helpful_links(words, answer_msg)
                #log the user question
                SlackPost.objects.get_or_create(user_request= text)
                # answer given by bot
                respond_from_bot(answer_msg, client, channel, message_timestamp)
    return HttpResponse(status=200)
def respond_to_subscription_challenge(json_dict, request):
    json_dict = json.loads(request.body.decode('utf-8'))
    if json_dict['token'] != settings.VERIFICATION_TOKEN:
        return HttpResponse(status=403)
    if 'type' in json_dict:
        if json_dict['type'] == 'url_verification':
            response_dict = {"challenge": json_dict['challenge']}
            return JsonResponse(response_dict, safe=False)
def find_helpful_links(user_request_keyword_array, answer_list):
    #TODO - exclude single letter searches, and catch MultipleObjectsReturned
    for each_word in user_request_keyword_array:
        try:
            print(each_word)
            helpful_links = AnswersDatabase.objects.get(keywords__icontains=each_word)
            print(helpful_links)
            if helpful_links.resource not in answer_list:
                answer_list.append(helpful_links.resource)
        except AnswersDatabase.DoesNotExist:
            print("no value found")
    return answer_list
def respond_from_bot(bot_answer, slack_client, slack_channel, time_stamp):
    if len(bot_answer) != 0:
        slack_client.chat_postMessage(channel=slack_channel, thread_ts= time_stamp, text=bot_answer)
    else:
        answer_msg = "We didn't find a helpful link for your query, sorry"
        slack_client.chat_postMessage(channel=slack_channel, thread_ts= time_stamp, text=answer_msg)
    return HttpResponse(status=200)
def gather_message_data(message_json):
    message_timestamp = message_json['ts']
    channel = message_json['channel']
    text = message_json['text'].lower().strip()
    return message_timestamp, channel, text


