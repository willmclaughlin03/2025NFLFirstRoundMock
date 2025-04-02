from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet, DraftViewSet

router = DefaultRouter()
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'drafts', DraftViewSet, basename='draft')

urlpatterns = [
    path('', include(router.urls)),
]