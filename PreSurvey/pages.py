from otree.api import Page
from openai import OpenAI
import os
import json
from datetime import datetime

class WelcomePage(Page):
    pass

class DemoPage(Page):
    form_model = 'player'
    form_fields = ['age','gender','english','education','occupation','work_experience','glasses','contacts']

class PreSurveyPage(Page):
    form_model = 'player'
    form_fields = [
        'ai_improve_life', 'ai_improve_work', 'ai_future_use', 'ai_positive_humanity',
        'pref_innovation_1', 'pref_innovation_2', 'pref_innovation_3', 'pref_innovation_4',
        'feedback_utility_1', 'feedback_utility_2', 'feedback_utility_3', 'feedback_utility_4', 
        'feedback_utility_5'
    ]
    
    def vars_for_template(self):
        return {
            'progress': '20%',
            'page_title': 'Pre-Task Survey',
            'widget_specs': {
                'pref_innovation_1': 'radio',
                'pref_innovation_2': 'radio',
                'pref_innovation_3': 'radio',
                'pref_innovation_4': 'radio',
                'feedback_utility_1': 'radio',
                'feedback_utility_2': 'radio',
                'feedback_utility_3': 'radio',
                'feedback_utility_4': 'radio',
                'feedback_utility_5': 'radio'
            }
        }
    
    def before_next_page(self):
        # Generate unique code for participant
        code = self.player.generate_unique_code()
        
        # Save survey data to a JSON file
        data = {
            'participant_code': code,
            'age': self.player.age,
            'gender': self.player.gender,
        }
        
        # Create directory if it doesn't exist
        os.makedirs('survey_data', exist_ok=True)
        
        # Save to file
        filename = f'survey_data/{code}.json'
        with open(filename, 'w') as f:
            json.dump(data, f)

# Update page sequence
page_sequence = [
    WelcomePage,
    DemoPage,
    PreSurveyPage
]


