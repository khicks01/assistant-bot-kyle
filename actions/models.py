from django.db import models

# Create your models here.

class SlackPost(models.Model):
    user_request = models.TextField()
    def __str__(self):
        return str(self.user_request)
    