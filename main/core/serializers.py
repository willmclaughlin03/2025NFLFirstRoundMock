from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Player, Draft, DraftPick, PlayerNote, CombineStats

class CombineStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CombineStats
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    #combine_stats = CombineStatsSerializer(required=False, read_only = True)

    class Meta:
        model = Player
        fields = [
            'id', 
            'first_name', 
            'last_name', 'position', 
            'age', 'college', 
            'draft_ranking']
        
class DraftPickSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    player_id = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all(), 
                                                   source='player', write_only=True)

    class Meta:
        model = DraftPick
        fields = ['id', 'player', 'player_id' , 'pick_number', 'round_number', 'team_name']

    def validate(self, data):
        draft = self.context.get('draft')
        player = data.get('player_id')

        if DraftPick.objects.filter(draft=draft, player_id=player).exists():
            raise ValidationError("Player has already been selected")
        
        return data
    

class DraftSerializer(serializers.ModelSerializer):
    picks = DraftPickSerializer(many=True, read_only=True)

    class Meta:
        model = Draft
        fields = ['id', 'user', 'draft_date', 'draft_grade', 'is_completed', 'picks', 'TEAM_NAMES', 'DRAFT_PICKS']

        read_only_fields = ['user', 'draft_date', 'draft_grade']