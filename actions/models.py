from django.db import models

# Create your models here.

class SlackPost(models.Model):
    time_stamp = models.TextField()
    user_request = models.TextField()
    user = models.TextField()
    def __str__(self):
        return str(self.time_stamp)
    