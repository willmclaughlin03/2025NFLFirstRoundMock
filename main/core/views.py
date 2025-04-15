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

class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(position=position)
        return queryset

class DraftViewSet(viewsets.ModelViewSet):
    serializer_class = DraftSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [IsAuthenticated]


    # filters players by their position if specified
    def get_queryset(self):
        return Draft.objects.filter(user=self.request.user)

    # assigns the current user to the new drafts taking place
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # uses get method to get the current status of draft and the next picks
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
    
        draft = self.get_object()
        return Response(self._get_draft_status(draft))
    
    # Lists the undrafted players
    @action(detail=True, methods=['get'])
    def available_players(self, request, pk=None):

        draft = self.get_object()
        available_players = Player.objects.exclude(
            id__in=draft.draftpicks.values_list('player__id', flat=True)
        ).order_by('draft_ranking')
        
        return Response({
            'count': available_players.count(),
            'players': PlayerSerializer(available_players, many=True).data
        })

    # adds the player to your draft
    @action(detail=True, methods=['post'])
    def add_pick(self, request, pk=None):
        """Add a player to the draft"""
        draft = self.get_object()
        
        if draft.is_completed:
            return self._draft_completed_response()
        
        pick_number = self._validate_pick_number(request)
        if isinstance(pick_number, Response):
            return pick_number
        
        serializer = self._create_pick_serializer(draft, request)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        return self._process_valid_pick(draft, pick_number, serializer)
    
    # finalizes the draft for the user and calculates their grade
    @action(detail=True, methods=['post'])
    def complete_draft(self, request, pk=None):
        """Mark draft as completed and calculate grade"""
        draft = self.get_object()
        if draft.is_completed:
            return Response({
                'status': 'draft already completed',
                'draft_grade': draft.draft_grade,
            })

        draft_grade = self._calculate_draft_grade(draft)


        draft.is_completed = True
        draft.draft_grade = draft_grade
        draft.save()

        return Response({
            'status': 'draft completed',
            'draft_grade': draft_grade,
            'redirect_url': f'/drafts/{draft.id}/results/'
        })

    # Helper methods
    # calculates the current draft state and pick status
    def _get_draft_status(self, draft, TEAM_NAMES = Draft.TEAM_NAMES, TEAM_NEEDS = Draft.TEAM_NEEDS):
        #draft_picks = draft.DRAFT_PICKS.sort()
        draft_picks = DraftPick.objects.filter(draft=draft).order_by('pick_number')
        current_pick = next(
            (pick for pick in Draft.DRAFT_PICKS 
             if not draft_picks.filter(pick_number=pick).exists()),
            None
        )
        
        return {
            'is_completed': draft.is_completed,
            'current_pick': current_pick,
            'team_name': Draft.TEAM_NAMES[current_pick - 1] if current_pick else None,
            'completed_picks': DraftPickSerializer(draft_picks, many=True).data
        }

    # checks if the draft has already occured 
    def _draft_completed_response(self):
        return Response({
            'status': 'error',
            'message': 'This draft has already been completed'
        }, status=status.HTTP_400_BAD_REQUEST)

    # makes sure the pick number is correct at all times
    def _validate_pick_number(self, request):
        try:
            pick_number = request.data.get('pick_number')
            if not pick_number or pick_number not in Draft.DRAFT_PICKS:
                raise ValueError
            return pick_number
        except (ValueError, TypeError):
            return Response({
                'status': 'error',
                'message': 'Invalid pick number'
            }, status=status.HTTP_400_BAD_REQUEST)

    # handles all the pick serializer validations and creation validation
    def _create_pick_serializer(self, draft, request):
        return DraftPickSerializer(
            data=request.data,
            context={
                'draft': draft,
                'available_players': Player.objects.all().order_by('draft_ranking')
            }
        )

    # finishes the pick process by validaing the pick one last time
    def _process_valid_pick(self, draft, pick_number, serializer):
        player_id = self.request.data.get('player_id')

        if not player_id:
            return Response({'error'  'Player ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)
        
        team_name = Draft.TEAM_NAMES[pick_number - 1]
        
        draft_pick = serializer.save(
            draft=draft,
            pick_number=pick_number,
            round_number=1,
            team_name=team_name,
            player=player
        )
        
        if pick_number == Draft.DRAFT_PICKS[-1]:
            draft.is_completed = True
            draft.save()
            return Response({
                'status': 'draft completed',
                'pick': DraftPickSerializer(draft_pick).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'pick added',
            'pick': DraftPickSerializer(draft_pick).data
        }, status=status.HTTP_201_CREATED)

    # scoring of draft method
    def _calculate_draft_grade(self, draft):
        draft_picks = DraftPick.objects.filter(draft=draft)
        total_points = sum(
            10 if abs(pick.player.draft_ranking - pick.pick_number) <= 5 else
            7 if abs(pick.player.draft_ranking - pick.pick_number) <= 10 else
            5 if abs(pick.player.draft_ranking - pick.pick_number) <= 15 else
            2 for pick in draft_picks
        )
        return min(max(round((total_points / 100) * 100), 0), 100)



# Template Views
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
def draft_detail(request, draft_id = None):


    """Render the draft detail page"""
    if draft_id == 'new':
        current_pick = 1
        current_team = list(Draft.TEAM_NEEDS.keys())[0]
        context = {
            'is_new' : True,
            'available_players' : Player.objects.all().order_by('draft_ranking'),
            'team_needs' : Draft.TEAM_NEEDS,
            'current_pick': current_pick,
            'current_team': current_team,


        }
        return render(request, 'draft/draft_detail.html', context)
    
    draft = get_object_or_404(Draft, id = draft_id, user=request.user)
    context = {
        'draft': draft,
        'picks': draft.DRAFT_PICKS.sort(),
        'team_needs' : Draft.TEAM_NEEDS,
    }
    
    if not draft.is_completed:
        # Add draft status for in-progress drafts
        status_data = DraftViewSet()._get_draft_status(draft)
        context.update({
            'current_pick': status_data['current_pick'],
            'current_team': status_data['team_name'],
            'team_needs': Draft.TEAM_NEEDS,
            'available_players': Player.objects.exclude(
                id__in=draft.draft_picks.values_list('player__id', flat=True)  # flagged for change, may need changing (players back to draftpicks)
            ).order_by('draft_ranking')
        })
    
    return render(request, 'draft/draft_detail.html', context)

@login_required
def draft_results(request, draft_id):
    """Render the draft results page"""
    draft = get_object_or_404(Draft, id=draft_id, user=request.user)
    if not draft.is_completed:
        messages.error(request, 'This draft has not been completed yet.')
        return redirect('draft_detail', draft_id=draft_id)
    
    draft_picks = DraftPick.objects.filter(draft=draft).order_by('pick_number')

    # Check if there are any draft picks
    if not draft_picks.exists():
        # Handle case where there are no draft picks
        messages.warning(request, "No draft picks found for this draft."
                         
                         
                         )
    
    if not draft.is_completed:
    # This might indicate the draft didn't finish properly
        messages.warning(request, "This draft is not marked as completed.")

    
    if draft.draft_grade is None:
        total_points = 0

        for pick in draft_picks:
            diff =  abs(pick.player.draft_ranking - pick.pick_number)
            if diff <= 5:
                total_points += 10
            elif diff <= 10:
                total_points += 7
            elif diff <= 15:
                total_points += 5
            else:
                total_points += 2

        if draft_picks.count() > 0:
            draft.draft_grade = min(100, total_points)
            draft.save()


    context = {
        'draft': draft,
        'draft_picks': draft_picks,
        'total_picks' : draft_picks.count(),
        'team_needs': Draft.TEAM_NEEDS,
    }
    return render(request, 'draft/draft_results.html', {'draft': draft})