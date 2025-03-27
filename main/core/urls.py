from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet, DraftViewSet

router = DefaultRouter()
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'drafts', DraftViewSet, basename='draft')

urlpatterns = [
    path('', include(router.urls)),
    # Optionally add login/logout views for session-based auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]