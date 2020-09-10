from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core import exceptions
import json
import slack

from .models import SlackPost, AnswersDatabase, Topics

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
                #log the user question
                SlackPost.objects.get_or_create(user_request= text.strip())
                #look for topic nouns
                found_topics = find_topics(words)
                if len(found_topics) > 0:
                    #build array of helpful links based on the key word
                    answer_msg = find_helpful_links(found_topics, words)
                    # answer given by bot
                    if len(answer_msg) > 0:
                        respond_from_bot(answer_msg, str(found_topics), client, channel, message_timestamp)
    return HttpResponse(status=200)

def respond_to_subscription_challenge(json_dict, request):
    json_dict = json.loads(request.body.decode('utf-8'))
    if json_dict['token'] != settings.VERIFICATION_TOKEN:
        return HttpResponse(status=403)
    if 'type' in json_dict:
        if json_dict['type'] == 'url_verification':
            response_dict = {"challenge": json_dict['challenge']}
            return JsonResponse(response_dict, safe=False)
def find_helpful_links(found_topics, user_request_array):
    #TODO - exclude single letter searches, and catch MultipleObjectsReturned
    answer_list = []
    for each_topic in found_topics:
        for each_word in user_request_array:
            if len(each_word) >1 :
                try:
                    print(each_word)
                    answer_querySet = AnswersDatabase.objects.filter(context__icontains=each_topic.strip()).filter(keywords__icontains=each_word.strip())
                    print(answer_querySet)
                    if len(answer_querySet) > 0:
                        for answer in answer_querySet:
                            if answer.resource not in answer_list:
                                answer_list.append(answer.resource)
                except AnswersDatabase.DoesNotExist:
                    print("no value found")
    return answer_list
def respond_from_bot(bot_answer, topic, slack_client, slack_channel, time_stamp):
    if len(bot_answer) != 0:
        slack_client.chat_postMessage(channel=slack_channel, thread_ts= time_stamp, text="Context recognized: "+ topic.replace("'", "").strip("[ ]"))
        slack_client.chat_postMessage(channel=slack_channel, thread_ts= time_stamp, text=bot_answer.replace('"', "").strip("[ ]"))
    else:
        answer_msg = "We didn't find a helpful link for your question regarding "+ topic + " sorry."
        slack_client.chat_postMessage(channel=slack_channel, thread_ts= time_stamp, text=answer_msg)
    return HttpResponse(status=200)
def gather_message_data(message_json):
    message_timestamp = message_json['ts']
    channel = message_json['channel']
    text = message_json['text'].lower().strip()
    return message_timestamp, channel, text
def find_topics(post_text_array):
    found_topics = []
    for word in post_text_array:
        try:
            if len(word) > 1:
                topic_querySet = Topics.objects.filter(aliases__icontains=word.strip())
                if len(topic_querySet) > 0:
                    for each_topic in topic_querySet:
                        if each_topic.context not in found_topics:
                            found_topics.append(each_topic.context)
            print(found_topics)
        except Topics.DoesNotExist:
            print("no topic found")
    return found_topics
