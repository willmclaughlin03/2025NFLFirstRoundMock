from django.db import models

# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length = 30)
    last_name = models.CharField(max_length = 30)
    email_address = models.EmailField(max_length = 30)
    username = models.CharField(max_length = 30)
    password = models.CharField(max_length = 20)

    def __str__(self):
        return self.first_name
    
