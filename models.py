from otree.api import *
import random
import string

class Constants(BaseConstants):
    name_in_url = 'experiment'
    players_per_group = None
    num_rounds = 1
    CODE_LENGTH = 8
    MAX_ATTEMPTS = 100
    participation_fee = cu(5)
    max_bonus = cu(5)

    LIKERT_CHOICES = [
    [1, 'Strongly Disagree'],
    [2, 'Disagree'],
    [3, 'Neutral'],
    [4, 'Agree'],
    [5, 'Strongly Agree']
    ]

    SCALE10 = [[i, str(i)] for i in range(1, 11)]
    
    SCALE7 = [[i, str(i)] for i in range(1, 8)]

    YESNO_CHOICES = [
        ['yes', 'Yes'],
        ['no', 'No']
    ]
    
    GENDER_CHOICES = [
        ['Male', 'Male'],
        ['Female', 'Female'],
        ['Non-binary', 'Non-binary'],
        ['Prefer not to say', 'Prefer not to say']
    ]
    
    EDUCATION_CHOICES = [
        ['High School', 'High School'],
        ['Some College', 'Some College'],
        ['Bachelors Degree', 'Bachelors Degree'],
        ['Masters Degree', 'Masters Degree'],
        ['Doctoral Degree', 'Doctoral Degree'],
        ['Other', 'Other']
    ]
class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

# Instead of using Django's models, we'll use oTree's model fields
class Player(BasePlayer):
    # Fields for participant code functionality
    participant_code = models.StringField(
        label='Please enter your participant code from the survey:'
    )
    code_used = models.BooleanField(initial=False)
    
    def validate_participant_code(self):
        # Instead of using a separate model, we'll use participant.vars to store codes
        valid_codes = self.session.vars.get('valid_codes', {})
        if self.participant_code not in valid_codes:
            return False, "Invalid participant code. Please check and try again."
        
        if valid_codes[self.participant_code]['used']:
            return False, "This code has already been used in the laboratory task."
        
        # Mark code as used
        valid_codes[self.participant_code]['used'] = True
        self.session.vars['valid_codes'] = valid_codes
        return True, "Code validated successfully"
    
    @staticmethod
    def generate_unique_code(session):
        valid_codes = session.vars.get('valid_codes', {})
        for _ in range(Constants.MAX_ATTEMPTS):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=Constants.CODE_LENGTH))
            if code not in valid_codes:
                valid_codes[code] = {'used': False, 'created_at': None}  # You can add timestamp if needed
                session.vars['valid_codes'] = valid_codes
                return code
        raise Exception("Failed to generate unique code")

    # Demographics   
    age = models.IntegerField(
        label='What is your age?',
        min=18, max=100
    )
        # Update these fields to use Constants
    gender = models.StringField(
        label='What is your gender?',
        choices=Constants.GENDER_CHOICES,
        widget=widgets.RadioSelectHorizontal
    )
    education = models.StringField(
        label='What is your highest level of education?',
        choices=Constants.EDUCATION_CHOICES,
        widget=widgets.RadioSelect
    )
    
    english = models.StringField(
        label='Is english your first language?',
        choices=Constants.YESNO_CHOICES, 
        widget=widgets.RadioSelectHorizontal
    )
    glasses = models.StringField(
        label='Do you wear glasses?',
        choices=Constants.YESNO_CHOICES, 
        widget=widgets.RadioSelectHorizontal
    )
    contacts = models.StringField(
        label='Do you wear contacts?',
        choices=Constants.YESNO_CHOICES, 
        widget=widgets.RadioSelectHorizontal
    )
    occupation = models.StringField(
        label='What is your current occupation?'
    )
    
    countrywrite = models.StringField(label='Please write the country you live in')

    work_experience = models.IntegerField(label='How many years of work experience do you have?',
                                 min =0 , max = 100)
    
    comments = models.LongStringField(label='Please write your comments here')
    alternative_use = models.LongStringField(initial=' ',
                                             blank=True
                                             )
    feedback = models.LongStringField(blank=True)
    def custom_export(players):
    # header row
        yield ['session', 'participant_code', 'round_number', 'id_in_group', 'payoff']
        for p in players:
            participant = p.participant
            session = p.session
            yield [session.code, participant.code, p.round_number, p.id_in_group, p.payoff]
    arousal = models.FloatField()
    valence = models.FloatField()
    alternative_use = models.LongStringField(blank=True)
    feedback_history = models.LongStringField(blank=True)
    submission_times = models.LongStringField(blank=True)



    # Pre Survey Fields
    # AI Acceptance
    ai_improve_life = models.IntegerField(label="I believe AI will improve my life.", 
    choices=Constants.LIKERT_CHOICES,
    widget=widgets.RadioSelectHorizontal
    )
    ai_improve_work = models.IntegerField(label="I believe AI will improve my work.", 
    choices=Constants.LIKERT_CHOICES,
    widget=widgets.RadioSelectHorizontal
    )
    ai_future_use = models.IntegerField(label="I think I will use AI technology in the future.", 
    choices=Constants.LIKERT_CHOICES,
    widget=widgets.RadioSelectHorizontal
    )
    ai_positive_humanity = models.IntegerField(label="I think AI technology is positive for humanity.", 
    choices=Constants.LIKERT_CHOICES,
    widget=widgets.RadioSelectHorizontal
    )
    
    # Innovation Preferences
    pref_innovation_1 = models.IntegerField(
        label="If I heard about a new information technology, I would look for ways to experiment with it.",
        choices=Constants.LIKERT_CHOICES, 
        widget=widgets.RadioSelectHorizontal
    )
    pref_innovation_2 = models.IntegerField(
        label="Among my peers, I am usually the first to try out new information technologies.",
        choices=Constants.LIKERT_CHOICES, 
        widget=widgets.RadioSelectHorizontal
    )
    pref_innovation_3 = models.IntegerField(
        label="In general, I am hesitant to try out new information technologies.",
        choices=Constants.LIKERT_CHOICES, 
        widget=widgets.RadioSelectHorizontal
    )
    pref_innovation_4 = models.IntegerField(
        label="I like to experiment with new information technologies.",
        choices=Constants.LIKERT_CHOICES, 
        widget=widgets.RadioSelectHorizontal
    )

    # Feedback Utility (Pre)
    feedback_utility_1 = models.IntegerField(label="Feedback contributes to my success at work.", 
    choices=Constants.LIKERT_CHOICES,
    widget=widgets.RadioSelectHorizontal)
    feedback_utility_2 = models.IntegerField(label="To develop my skills at work, I rely on feedback.", 
    choices=Constants.LIKERT_CHOICES,
    widget=widgets.RadioSelectHorizontal)
    feedback_utility_3 = models.IntegerField(label="Feedback is critical for improving performance.", 
    choices=Constants.LIKERT_CHOICES,
    widget=widgets.RadioSelectHorizontal)
    feedback_utility_4 = models.IntegerField(label="Feedback from supervisors can help me advance in a company.", 
    choices=Constants.LIKERT_CHOICES,
    widget=widgets.RadioSelectHorizontal)
    feedback_utility_5 = models.IntegerField(label="I find that feedback is critical for reaching my goals.", 
    choices=Constants.LIKERT_CHOICES,
    widget=widgets.RadioSelectHorizontal)

    # Post Survey Fields
    img_choice = models.StringField(
        choices=['A', 'B', 'C', 'D', 'E', 'F', 'G'],
        label="Please select the diagram that best represents your relationship with the AI:"
    )

    # Attentional Measures
    attentional_effort = models.IntegerField(
        label="Rate the amount of effort needed to maintain attention during the task.", 
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )
    mind_wandering = models.IntegerField(
        label="How often did you find your mind wandering during the task?", 
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )
    refocus_ease = models.IntegerField(
        label="How easy was it to refocus or increase focus during the task?", 
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )

    # Self-Efficacy
    confidence_future = models.IntegerField(
        label="How confident are you in your ability to perform similar tasks in the future?", 
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )
    confidence_change = models.IntegerField(
        label="How much did confidence in your ability change over the course of the task?", 
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )
    confidence_improve = models.IntegerField(
        label="How confident are you that you could improve your performance with practice?", 
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )

    # Feedback Experience
    feedback_motivation = models.IntegerField(
    label="How motivating was the feedback?", 
    choices=Constants.SCALE10,
    widget=widgets.RadioSelectHorizontal
    )
    feedback_accuracy = models.IntegerField(
        label="How accurate did you find the feedback to be?", 
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )
    feedback_clarity = models.IntegerField(
        label="How clear and understandable was the feedback?", 
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )
    feedback_usefulness = models.IntegerField(
        label="How useful was the feedback?", 
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )
    feedback_incorporation = models.IntegerField(
        label="How likely is it that the feedback helped adjust your approach?",
        choices=Constants.SCALE10,
        widget=widgets.RadioSelectHorizontal
    )

    # Psychological Distance
    psych_distance_1 = models.IntegerField(
        label="The AI is psychologically close to me.", 
        choices=Constants.SCALE7,
        widget=widgets.RadioSelectHorizontal
    )
    psych_distance_2 = models.IntegerField(
        label="The AI is socially close to me.", 
        choices=Constants.SCALE7,
        widget=widgets.RadioSelectHorizontal
    )
    psych_distance_3 = models.IntegerField(
        label="The AI can be seen as a typical in-group member.", 
        choices=Constants.SCALE7,
        widget=widgets.RadioSelectHorizontal
    )
    # Performance metrics (for payment calculation)
    creativity_score = models.FloatField(initial=0)
    bonus_earned = models.CurrencyField(initial=0)

     # Calculate bonus based on creativity score (0-100)
    def calculate_bonus(self):
        max_bonus = Constants.max_bonus
        self.bonus_earned = max_bonus * (self.creativity_score / 100)
        self.payoff = Constants.participation_fee + self.bonus_earned

