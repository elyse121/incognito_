from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile

class ManageMember(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_memberships')
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='manage_members')
    status = models.BooleanField(default=True)  # True = active, False = banned
    joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, default='member')

    def __str__(self):
        return f"{self.member.username} ({'Active' if self.status else 'Banned'})"


# chat/blocked_conversations/models.py
from django.db import models
from django.contrib.auth.models import User

class BlockedConversation(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_user2")
    blocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # prevent duplicate bans


#Notifications table.    

class Notification(models.Model):
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    email = models.EmailField(max_length=255, null=True, blank=True)  # Make sure 'email' field exists if it's supposed to be there

    def __str__(self):
        return f'Notification from {self.sender.username}'


