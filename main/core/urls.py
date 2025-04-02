from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required



urlpatterns = [
    # Main draft pages
    path('', views.draft_home, name='draft_home'),
    path('history/', login_required(views.draft_history), name='draft_history'),
    
    # Draft modes
    path('draft/', views.quick_draft, name='quick_draft'),

    
    # Draft results and details
    path('draft/<int:draft_id>/', login_required(views.draft_detail), name='draft_detail'),
    path('draft/<int:draft_id>/results/', login_required(views.draft_results), name='draft_results'),
]