from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email_address = models.EmailField(unique=True) 

    # Add custom related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='authentication_user_groups',  # Custom related_name
        related_query_name='authentication_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='authentication_user_permissions',  # Custom related_name
        related_query_name='authentication_user',
    )

    def __str__(self):
        return self.username
    
