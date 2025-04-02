from django.contrib import admin
from .models import Player, CombineStats, Draft, DraftPick
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Player)
admin.site.register(CombineStats)
admin.site.register(Draft)
admin.site.register(DraftPick)
