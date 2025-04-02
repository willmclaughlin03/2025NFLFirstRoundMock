from MySQLdb import DatabaseError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from .serializers import PlayerSerializer
from .models import Player, Draft, DraftPick, CombineStats
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .models import Player, Draft, DraftPick
from .serializers import PlayerSerializer, DraftSerializer, DraftPickSerializer
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from authentication.models import User
from authentication.views import UserSignUpTempView, UserLoginTempView


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter players based on query parameters
        queryset = Player.objects.all()
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(position=position)
        return queryset

class DraftViewSet(viewsets.ModelViewSet):
    serializer_class = DraftSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return drafts for the current user
        return Draft.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign current user
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def add_pick(self, request, pk=None):
        draft = self.get_object()
        # Prepare serializer context
        context = {
            'draft': draft
        }
        # Create draft pick serializer with context
        serializer = DraftPickSerializer(
            data=request.data,
            context=context
        )
        if serializer.is_valid():
            # Save draft pick
            draft_pick = serializer.save(
                draft=draft,
                player=serializer.validated_data['player_id']
            )
            return Response({
                'status': 'pick added',
                'pick': DraftPickSerializer(draft_pick).data
            }, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['POST'])
    def complete_draft(self, request, pk=None):
        draft = self.get_object()
        # Calculate draft grade (similar to previous implementation)
        draft_grade = self._calculate_draft_grade(draft)
        draft.is_completed = True
        draft.draft_grade = draft_grade
        draft.save()
        return Response({
            'status': 'draft completed',
            'draft_grade': draft_grade
        })

    def _calculate_draft_grade(self, draft):
        # Draft grade calculation logic
        draft_picks = DraftPick.objects.filter(draft=draft)
        total_points = sum(
            10 if abs(pick.player.draft_ranking - pick.pick_number) <= 5 else
            7 if abs(pick.player.draft_ranking - pick.pick_number) <= 10 else
            5 if abs(pick.player.draft_ranking - pick.pick_number) <= 15 else
            2 for pick in draft_picks
        )
        return min(max(round((total_points / 100) * 100), 0), 100)

# All are allowed to the draft home page


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def draft_home(request):

        # Check if the user is authenticated
    if request.user.is_authenticated:
            # Get the user's drafts
        drafts = Draft.objects.filter(user=request.user).order_by('-draft_date')[:3]

    
    return render(request, 'draft/draft_home.html')

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def quick_draft(request):
    # Create a new draft object

    if request.method == 'GET':
        return render(request, 'draft/quick_draft.html')
    
    if request.method == 'POST':
        draft = Draft.objects.create(
            user = request.user,
            is_completed = False,
        )
        while draft.is_completed == False:
            available_players = Player.objects.all().order_by('draft_ranking')

            for pick_number in Draft.DRAFT_PICKS:
                    TEAM_NAMES = Draft.TEAM_NAMES[pick_number - 1]  # Get the team name based on the pick number
                    draft_pick = DraftPick.objects.create(
                        draft=draft,
                        player=available_players,
                        pick_number=pick_number,
                        round_number=1,  # Quick draft has only 1 round
                        team_name=TEAM_NAMES,
                    )

                    available_players = available_players.exclude(id=draft_pick.player.id)
                    draft_pick.save()

                    if pick_number == Draft.DRAFT_PICKS[-1]:  # Check if it's the last pick
                        draft.is_completed = True  # Mark the draft as completed after all picks are made
                        draft.save()
                        break
                    

    
    # Get available players for the draft
    available_players = Player.objects.all().order_by('draft_ranking')
    
    context = {
        'draft': draft,
        'available_players': Player.objects.all().order_by('draft_ranking'),
        'rounds': 1,  # Quick draft has only 1 round
    }
    
    return render(request, 'draft/draft_simulator.html', context)


@login_required
def draft_detail(request, draft_id):
    draft = get_object_or_404(Draft, id=draft_id, user=request.user)
    picks = DraftPick.objects.filter(draft=draft).order_by('round_number', 'pick_number')
    
    context = {
        'draft': draft,
        'picks': picks
    }
    
    return render(request, 'draft/draft_detail.html', context)

@login_required
def draft_results(request, draft_id):
    draft = get_object_or_404(Draft, id=draft_id, user=request.user)
    
    # Make sure the draft is completed
    if not draft.is_completed:
        messages.error(request, 'This draft has not been completed yet.')
        return redirect('draft_detail', draft_id=draft_id)
    
    context = {
        'draft': draft
    }
    
    return render(request, 'draft/draft_results.html', context)

@api_view(['POST'])
def PicksLogic(draft, request):

    if request.method == 'POST':
        try:
            player = get_object_or_404(Player, id = player)
            draft_pick = get_object_or_404(DraftPick, pick_number = pick_number)
            draft_round = get_object_or_404(DraftPick, round_number = round_number)
            team = get_object_or_404(Player, team_name = team_name)  # potentially change to a specific team model

            draft_pick = DraftPick.objects.create(
                draft=draft,
                player=player,
                pick_number= pick_number,
                round_number=round_number,
                team_name=team_name,)
            
            serializer = DraftPickSerializer(draft_pick, many = True)

            # Save the draft pick to the database

            draft_pick.save()
            return Response({'status': 'success', 'draft_pick_id': draft_pick.id}, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def draft_history(request):
        try: 
            response = Draft.objects.filter(user = request.user).order_by('-draft_date')
            serializer = DraftSerializer(response, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except DatabaseError as e:
            return Response({'error': 'server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def full_draft(request):

    try:
    # Create a new draft object
        draft = Draft.objects.create(
            user=request.user,
            mode='full',
            is_completed=False
        )

        context = {
            'draft': draft,
            'available_players': Player.objects.all().order_by('draft_ranking'),
            'rounds': 7,  # Full draft has 7 rounds
        }

        

    
        return render(request, 'draft/draft_simulator.html', context)
    # Handle any database errors
    except DatabaseError as e:
        return Response({'error': 'server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
'''