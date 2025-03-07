from django.db import models

# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length = 30)
    last_name = models.CharField(max_length = 30)
    email_address = models.EmailField(max_length = 30)
    username = models.CharField(max_length = 30)
    password = models.CharField(max_length = 20)

class combine_stats(models.Model):
    height =  models.FloatField(max_length=5, default= 'null')
    weight =  models.IntegerField(default= 'null')
    fourty_time = models.FloatField(max_length= 5, default= 'null')
    bench_press = models.IntegerField(default= 'null')
    cone_3 = models.FloatField(max_length = 4, default= 'null')
    broad_jump = models.FloatField(max_length = 6, default= 'null')
    vertical_jump = models.FloatField(max_length = 6, default= 'null')

class Player(models.Model):
    first_name = models.CharField(max_length = 20, default= 'null')
    last_name = models.CharField(max_length = 30, default= 'null')
    ranking = models.IntegerField(default= 2)
    position = models.CharField(max_length = 4, default= 'null')
    age = models.IntegerField(default = 20)
    college = models.CharField(max_length =  30, default= 'null')
    combine_stats = models.ForeignKey(combine_stats, on_delete = models.CASCADE, default= 'null')




