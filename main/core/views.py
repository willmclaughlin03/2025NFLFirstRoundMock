from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .models import Player, Draft, DraftPick
from .serializers import PlayerSerializer, DraftSerializer, DraftPickSerializer

class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
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
    permission_classes = [permissions.IsAuthenticated]
    
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
            2 
            for pick in draft_picks
        )
        
        return min(max(round((total_points / 100) * 100), 0), 100)