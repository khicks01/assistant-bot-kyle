from django.db import models

# Create your models here.

class SlackPost(models.Model):
    user_request = models.TextField()
    def __str__(self):
        return str(self.user_request)

class AnswersDatabase(models.Model):
    context = models.TextField()
    keywords = models.TextField()
    resource = models.TextField()
    def __str__(self):
        return str(self.context)

class Topics(models.Model):
    context = models.TextField()
    aliases = models.TextField()
    def __str__(self):
        return str(self.context)

    