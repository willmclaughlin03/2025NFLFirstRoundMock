from django.urls import path, include
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter
from .views import (
    PlayerViewSet,
    DraftViewSet,
    draft_home,
    draft_detail,
    draft_results,
)

# API Router
router = DefaultRouter()
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'drafts', DraftViewSet, basename='draft')

urlpatterns = [
    # API Endpoints (DRF Viewsets)
    path('api/', include(router.urls)),
    
    # HTML Views (Django Template Views)
    path('', draft_home, name='draft_home'),
    path('drafts/new/', login_required(draft_detail), {'draft_id': 'new'}, name='new_draft'),
    path('drafts/<int:draft_id>/', login_required(draft_detail), name='draft_detail'),
    path('drafts/<int:draft_id>/results/', login_required(draft_results), name='draft_results'),
    
    # Additional API endpoints
    path('api/drafts/<int:pk>/add_pick/', 
        DraftViewSet.as_view({'post': 'add_pick'}), 
        name='draft-add-pick'),
    path('api/drafts/<int:pk>/complete/', 
        DraftViewSet.as_view({'post': 'complete_draft'}), 
        name='draft-complete'),
    path('api/drafts/<int:pk>/status/', 
        DraftViewSet.as_view({'get': 'status'}), 
        name='draft-status'),
    path('api/drafts/<int:pk>/available_players/', 
        DraftViewSet.as_view({'get': 'available_players'}), 
        name='draft-available-players'),
] 