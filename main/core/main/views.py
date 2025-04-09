from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import (SessionAuthentication, 
                                         BasicAuthentication, 
                                         TokenAuthentication)
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Player, Draft, DraftPick
from .serializers import PlayerSerializer, DraftSerializer, DraftPickSerializer

# Template Views
@login_required
def draft_home(request):
    """Render the draft home page"""
    context = {}
    if request.user.is_authenticated:
        context['drafts'] = Draft.objects.filter(
            user=request.user
        ).order_by('-draft_date')[:3]
    # Add top prospects to context
    context['top_prospects'] = Player.objects.all().order_by('draft_ranking')[:10]
    return render(request, 'draft/draft_home.html', context)

@login_required
def draft_detail(request, draft_id):
    """Render the draft detail page"""
    if draft_id == 'new':
        # Create a new draft
        draft = Draft.objects.create(user=request.user)
        return redirect('draft_detail', draft_id=draft.id)
    
    draft = get_object_or_404(Draft, id=draft_id, user=request.user)
    context = {
        'draft': draft,
        'picks': draft.draftpicks.order_by('round_number', 'pick_number'),
    }
    
    if not draft.is_completed:
        # Add draft status for in-progress drafts
        status_data = DraftViewSet()._get_draft_status(draft)
        context.update({
            'current_pick': status_data['current_pick'],
            'current_team': status_data['team_name'],
            'available_players': Player.objects.exclude(
                id__in=draft.draftpicks.values_list('player__id', flat=True)
            ).order_by('draft_ranking')
        })
    
    return render(request, 'draft/draft_detail.html', context) 