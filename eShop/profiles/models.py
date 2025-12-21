from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_TYPES_CHOICES = [
        ('admin', 'Admin'),
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=6, choices=USER_TYPES_CHOICES)

    def __str__(self):
        return f'{self.user.username} {self.user_type}'