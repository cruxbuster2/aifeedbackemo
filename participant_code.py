from otree.api import *

# First, define your oTree models
class Constants(BaseConstants):
    name_in_url = 'experiment'
    players_per_group = None
    num_rounds = 1
    CODE_LENGTH = 8
    MAX_ATTEMPTS = 100
    participation_fee = cu(5)
    max_bonus = cu(5)

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

# Move the ParticipantCode model to a separate file
# Create a new file: experiment/participant_code.py