from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from authentication.models import User

class CombineStats(models.Model):
    """Detailed combine performance statistics for a player"""
    height = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    weight = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    forty_yard_dash = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    bench_press_reps = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    three_cone_drill = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    broad_jump = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    vertical_jump = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    
    def __str__(self):
        return f"Combine Stats for Player"

class Player(models.Model):
    """Detailed player information for NFL Draft"""
    POSITION_CHOICES = [
        ('QB', 'Quarterback'),
        ('RB', 'Running Back'),
        ('WR', 'Wide Receiver'),
        ('TE', 'Tight End'),
        ('OT', 'Offensive Tackle'),
        ('OG', 'Offensive Guard'),
        ('C', 'Center'),
        ('DE', 'Defensive End'),
        ('DT', 'Defensive Tackle'),
        ('LB', 'Linebacker'),
        ('CB', 'Cornerback'),
        ('S', 'Safety'),
        ('K', 'Kicker'),
        ('P', 'Punter'),
    ]
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=4, choices=POSITION_CHOICES)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(30)])
    college = models.CharField(max_length=100)
    
    # Ranking and draft-related fields
    draft_ranking = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    #projected_round = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)], null=True, blank=True)
    
    # Combine stats relationship
    #combine_stats = models.OneToOneField(CombineStats, on_delete=models.SET_NULL, null=True, blank=True)
    
    # College performance stats
    #college_touchdowns = models.IntegerField(default=0)
    #college_yards = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"

class Draft(models.Model):

    name = models.CharField(max_length=100, default="Untitled Draft")
    """Represents a user's draft session"""
    DRAFT_PICKS = [1,2,3,4,5,6,7,8,9,10,11,12, 13,14,15,16,17,18,19,20, 21,22,23,24,25,26,27,28,29,30,31,32]
    TEAM_NAMES = [
    "Tennessee Titans","Cleveland Browns","New York Giants","New England Patriots",
    "Jacksonville Jaguars","Las Vegas Raiders","New York Jets","Carolina Panthers",
    "New Orleans Saints","Chicago Bears","San Francisco 49ers","Dallas Cowboys",
    "Miami Dolphins","Indianapolis Colts","Atlanta Falcons","Arizona Cardinals",
    "Cincinnati Bengals","Seattle Seahawks","Tampa Bay Buccaneers","Denver Broncos",
    "Pittsburgh Steelers","Los Angeles Chargers","Green Bay Packers","Minnesota Vikings",
    "Houston Texans","Los Angeles Rams","Baltimore Ravens","Detroit Lions",
    "Washington Commanders","Buffalo Bills","Kansas City Chiefs","Philadelphia Eagles"
]
    TEAM_NEEDS = {
        "Tennessee Titans" : ['QB', 'CB', 'WR', 'OT', 'DE'],
        "Cleveland Browns" : ['QB', 'OT', 'WR', 'HB', 'CB'],
        "New York Giants" : ['QB', 'OT', 'OG', 'CB', 'S'],
        "New England Patriots" : ['OT', 'OG', 'WR', 'HB', 'DT'],
        "Jacksonville Jaguars" : ['OT', 'OG', 'CB', 'LB', 'HB'],
        "Las Vegas Raiders" : ['WR', 'CB', 'LB', 'HB', 'S'],
        "New York Jets" : ['QB', 'OT', 'DE', 'CB', 'WR'],
        "Carolina Panthers" : ['DE', 'CB', 'LB', 'WR', ''],
        "New Orleans Saints" : ['QB', 'OG', 'DT', 'LB', 'WR'],
        "Chicago Bears" : ['OT', 'S', 'HB', 'CB', 'TE'],
        "San Francisco 49ers" : ['OG', 'DT', 'CB', 'DE', 'OT'],
        "Dallas Cowboys" : ['WR', 'DT', 'OG', 'LB', 'HB'],
        "Miami Dolphins" : ['OG', 'OT', 'C', 'DT', 'S'],
        "Indianapolis Colts" : ['OT', 'DE', 'S', 'TE', 'OG'],
        "Atlanta Falcons" : ['DE', 'S', 'DT', 'LB', 'CB'],
        "Arizona Cardinals" : ['CB', 'DT', 'OG', 'OT', 'DE'],
        "Cincinnati Bengals" : ['OT', 'OG', 'CB', 'LB', 'S'],
        "Seattle Seahawks" : ['QB', 'OT', 'OG', 'DE', 'CB'],
        "Tampa Bay Buccaneers" : ['DE', 'OG', 'CB', 'LB', 'WR'], 
        "Denver Broncos" : ['WR', 'CB', 'DT', 'C', 'S'],
        "Pittsburgh Steelers" : ['QB', 'OT', 'DT', 'CB', 'LB'],
        "Los Angeles Chargers" : ['WR', 'OG', 'C', 'CB', 'DT'],
        "Green Bay Packers" : ['WR', 'CB', 'DE', 'DT', 'LB'],
        "Minnesota Vikings" : ['CB', 'LB', 'S', 'OT', 'DE'],
        "Houston Texans" : ['OT', 'OG', 'C', 'WR', 'TE'],
        "Los Angeles Rams" : ['CB', 'S', 'OG', 'OT', 'LB'],
        "Baltimore Ravens" : ['WR', 'OG', 'DE', 'LB', 'S'],
        "Detroit Lions" : ['DE', 'DT', 'CB', 'OG', 'WR'],
        "Washington Commanders" : ['OG', 'C', 'DT', 'LB', 'CB'],
        "Buffalo Bills" : ['WR', 'CB', 'S', 'LB', 'DT'],
        "Kansas City Chiefs" : ['OT', 'OG', 'CB', 'DE', 'DT'],
        "Philadelphia Eagles" : ['C', 'OG', 'DE', 'LB', 'TE'],}

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drafts')
    draft_date = models.DateTimeField(auto_now_add=True)
    draft_grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)], 
        null=True, 
        blank=True
    )
    is_completed = models.BooleanField(default=False)
    new = models.BooleanField(default = False)
    selected_player = models.ForeignKey('DraftPick', on_delete=models.CASCADE, null=True, blank=True, related_name='selected_in_draft')
    player_id = models.ForeignKey('Player', on_delete=models.CASCADE, null=True, blank=True, related_name='selected_in_draft')

    def get_grade_feedback(self):
    
        if self.draft_grade is None:
            return "Draft not graded yet"
    
        if self.draft_grade >= 90:
            return "Outstanding draft! You maximized value at nearly every pick."
        elif self.draft_grade >= 80:
            return "Great draft! You found excellent value throughout your selections."
        elif self.draft_grade >= 70:
            return "Good draft with solid value. A few picks could have been better optimized."
        elif self.draft_grade >= 60:
            return "Decent draft with some good selections, but room for improvement."
        elif self.draft_grade >= 50:
            return "Average draft. Some good picks mixed with some reaches."
        else:
            return "Below average draft. Consider focusing more on player value in future drafts."
    
    
    def __str__(self):
        return f"Draft by {self.user.username} on {self.draft_date}"

class DraftPick(models.Model):
    """Represents an individual draft pick in a draft session"""
    draft = models.ForeignKey(Draft, on_delete=models.CASCADE, related_name='draft_picks')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    pick_number = models.IntegerField(validators=[MinValueValidator(1)])
    round_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])
    team_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ['draft', 'pick_number']
        ordering = ['round_number', 'pick_number']
    
    def __str__(self):
        return f"Pick {self.pick_number} - {self.player} in {self.draft}"

class PlayerNote(models.Model):
    """Additional notes or scouting information for players"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Note for {self.player} by {self.user}"