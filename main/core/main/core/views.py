from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Draft, Player
from .views import DraftViewSet

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