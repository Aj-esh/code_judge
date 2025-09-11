from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommender_profile')
    last_5_solved_pids = models.JSONField(default=list) # Stores a list of problem IDs

    def __str__(self):
        return f"Profile for {self.user.username}"
