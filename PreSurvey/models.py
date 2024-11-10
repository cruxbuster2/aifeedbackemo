from otree.api import *
import requests
from django import forms
import random
import string
from django.db import models as django_models

class Constants(BaseConstants):
    name_in_url = 'pre_survey'
    players_per_group = None
    num_rounds = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
      
    participant_code = models.StringField()
    
    # Survey fields
    age = models.IntegerField(label='What is your age?')
    gender = models.StringField(
        label='What is your gender?',
        choices=['Male', 'Female', 'Other', 'Prefer not to say']
    )
    
    def generate_unique_code(self):
        """Generate a unique 8-character code for the participant"""
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(chars, k=8))
        # You might want to check if code already exists in your database
        self.participant_code = code
        return code
    
    # Demographics   
    age = models.IntegerField(
        label='What is your age?',
        min=18, max=100
    )
    gender = models.StringField(
        label='What is your gender?',
        choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'],
        widget=widgets.RadioSelectHorizontal
    )
    education = models.StringField(
        label='What is your highest level of education?',
        choices=[
            'High School',
            'Some College',
            'Bachelors Degree',
            'Masters Degree',
            'Doctoral Degree',
            'Other'
        ],
        widget=widgets.RadioSelect
    )
    occupation = models.StringField(
        label='What is your current occupation?'
    )
    
    countrywrite = models.StringField(label='Please write the country you live in')
    english = models.StringField(label='Is english your first language?',
                                  choices=['yes', 'no'], 
                                  widget=widgets.RadioSelectHorizontal)
    glasses = models.StringField(label='Do you wear glasses?',
                                  choices=['yes', 'no'], 
                                  widget=widgets.RadioSelectHorizontal)
    contacts = models.BooleanField(label='Do you wear contacts?',
                                  choices=['yes', 'no'], 
                                  widget=widgets.RadioSelectHorizontal)

    work_experience = models.IntegerField(label='How many years of work experience do you have?',
                                 min =0 , max = 100)
    
    comments = models.LongStringField(label='Please write your comments here')
    alternative_use = models.LongStringField(initial=' ',blank=True)
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
    ai_improve_life = models.IntegerField(
        label="I believe AI will improve my life.", 
        choices=[1,2,3,4,5,6,7,8,9,10],
        widget=widgets.RadioSelectHorizontal
    )
    ai_improve_work = models.IntegerField(
        label="I believe AI will improve my work.", 
        choices=[1,2,3,4,5,6,7,8,9,10],
        widget=widgets.RadioSelectHorizontal
    )
    ai_future_use = models.IntegerField(
        label="I think I will use AI technology in the future.", 
        choices=[1,2,3,4,5,6,7,8,9,10],
        widget=widgets.RadioSelectHorizontal
    )
    ai_positive_humanity = models.IntegerField(
        label="I think AI technology is positive for humanity.", 
        choices=[1,2,3,4,5,6,7,8,9,10],
        widget=widgets.RadioSelectHorizontal
    )
    
    # Innovation Preferences
    pref_innovation_1 = models.IntegerField(
        label="If I heard about a new information technology, I would look for ways to experiment with it.",
        choices=[1,2,3,4,5],
        widget=widgets.RadioSelectHorizontal
    )
    pref_innovation_2 = models.IntegerField(
        label="Among my peers, I am usually the first to try out new information technologies.",
        choices=[1,2,3,4,5],
        widget=widgets.RadioSelectHorizontal
    )
    pref_innovation_3 = models.IntegerField(
        label="In general, I am hesitant to try out new information technologies.",
        choices=[1,2,3,4,5],
        widget=widgets.RadioSelectHorizontal
    )
    pref_innovation_4 = models.IntegerField(
        label="I like to experiment with new information technologies.",
        choices=[1,2,3,4,5],
        widget=widgets.RadioSelectHorizontal
    )


    # Feedback Utility (Pre)
    feedback_utility_1 = models.IntegerField(
        label="Feedback contributes to my success at work.", 
        choices=[1,2,3,4,5],
        widget=widgets.RadioSelectHorizontal
    )
    feedback_utility_2 = models.IntegerField(
        label="To develop my skills at work, I rely on feedback.", 
        choices=[1,2,3,4,5],
        widget=widgets.RadioSelectHorizontal
    )
    feedback_utility_3 = models.IntegerField(
        label="Feedback is critical for improving performance.", 
        choices=[1,2,3,4,5],
        widget=widgets.RadioSelectHorizontal
    )
    feedback_utility_4 = models.IntegerField(
        label="Feedback from supervisors can help me advance in a company.", 
        choices=[1,2,3,4,5],
        widget=widgets.RadioSelectHorizontal
    )
    feedback_utility_5 = models.IntegerField(
        label="I find that feedback is critical for reaching my goals.", 
        choices=[1,2,3,4,5],
        widget=widgets.RadioSelectHorizontal
    )

    # Attentional Measures
    attentional_effort = models.IntegerField(
        label="Rate the amount of effort needed to maintain attention during the task.", 
        widget=widgets.RadioSelectHorizontal,
        min=1, max=10
    )
    mind_wandering = models.IntegerField(
        label="How often did you find your mind wandering during the task?", 
        widget=widgets.RadioSelectHorizontal,
        min=1, max=10
    )
    refocus_ease = models.IntegerField(
        label="How easy was it to refocus or increase focus during the task?", 
        widget=widgets.RadioSelectHorizontal,
        min=1, max=10
    )

    # Self-Efficacy
    confidence_future = models.IntegerField(
        label="How confident are you in your ability to perform similar tasks in the future?", 
        widget=widgets.RadioSelectHorizontal,
        min=1, max=10
    )
    confidence_change = models.IntegerField(
        label="How much did confidence in your ability change over the course of the task?", 
        widget=widgets.RadioSelectHorizontal,
        min=1, max=10
    )
    confidence_improve = models.IntegerField(
        label="How confident are you that you could improve your performance with practice?", 
        widget=widgets.RadioSelectHorizontal,
        min=1, max=10
    )

    # Feedback Experience
    feedback_motivation = models.IntegerField(label="How motivating was the feedback?", min=1, max=10)
    feedback_accuracy = models.IntegerField(label="How accurate did you find the feedback to be?", min=1, max=10)
    feedback_clarity = models.IntegerField(label="How clear and understandable was the feedback?", min=1, max=10)
    feedback_usefulness = models.IntegerField(label="How useful was the feedback?", min=1, max=10)
    feedback_incorporation = models.IntegerField(
        label="How likely is it that the feedback helped adjust your approach?",
        min=1, max=10
    )

    # Psychological Distance
    psych_distance_1 = models.IntegerField(label="The AI is psychologically close to me.", min=1, max=7)
    psych_distance_2 = models.IntegerField(label="The AI is socially close to me.", min=1, max=7)
    psych_distance_3 = models.IntegerField(label="The AI can be seen as a typical in-group member.", min=1, max=7)

