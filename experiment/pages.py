from otree.api import Page
from openai import OpenAI
import os
import json
from datetime import datetime

class EnterCode(Page):
    form_model = 'player'
    form_fields = ['participant_code']
    
    def error_message(self, values):
        is_valid, message = self.player.validate_participant_code()
        if not is_valid:
            return message

class PreSurveyPage(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'occupation']
    
    def before_next_page(self):
        # Generate a unique code for this participant
        code = self.player.generate_unique_code(self.session)
        self.participant.vars['participant_code'] = code


class WelcomePage(Page):
    pass

class DemoPage(Page):
    form_model = 'player'
    form_fields = ['age','gender','english','education','occupation','work_experience','glasses','contacts']

class CreativeTaskInstructions(Page):
    pass

class AlternativeUsesPage(Page):
    form_model = 'player'
    form_fields = ['alternative_use']
    
    def live_method(self, data):
        if 'metrics_update' in data:
            self.participant.vars['metrics'] = {
                'keystrokes': data.get('keystrokes', 0),
                'wpm': data.get('wpm', 0),
                'ideas': data.get('ideas', 0),
                'removed': data.get('removed', 0)
            }
            return

        if 'alternative_use' in data:
            user_input = data['alternative_use']
            # Handle empty input
            if not user_input or user_input.strip() == '':
                return {self.id_in_group: {
                    'ideas': [],
                    'analysis': "No text submitted for analysis.",
                    'error': 'Please enter some text before submitting.'
                }}
            
            self.alternative_use = user_input  # Save to player model

            try:
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    return {self.id_in_group: {'error': 'API key not configured'}}

                client = OpenAI(api_key=api_key)
                
                # Ideas extraction
                ideas_prompt = (
                    "Extract the 5 most significant main ideas from this text as a conceptual outline. "
                    "Each idea should be 3-5 words. Return ONLY the ideas, one per line:\n\n"
                    f"Text: {user_input}"
                )

                ideas_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a concise idea extractor."},
                        {"role": "user", "content": ideas_prompt}
                    ],
                    max_tokens=150,
                    temperature=0.3
                )

                ideas = [idea.strip() for idea in 
                        ideas_response.choices[0].message.content.split('\n') 
                        if idea.strip()]

                # Analysis
                analysis_prompt = (
                    "Analyze this text and provide only these metrics:\n"
                    "- Unique ideas: [number]\n"
                    "- Feasibility (1-10): [score]\n"
                    "- Innovation (1-10): [score]\n"
                    "- Completeness (1-10): [score]\n"
                    f"\nText: {user_input}"
                )

                analysis_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a concise metrics analyzer."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=150,
                    temperature=0.3
                )

                analysis = analysis_response.choices[0].message.content

                # Handle different submission types
                if data.get('final_submit'):
                    # Store final submission data in participant vars
                    self.participant.vars['final_submission'] = {
                        'text': user_input,
                        'metrics': data.get('metrics', {}),
                        'ideas': ideas,
                        'analysis': analysis
                    }
                    # Also store in player model
                    self.alternative_use = user_input
                    return {self.id_in_group: {
                        'ideas': ideas,
                        'analysis': analysis,
                        'advance_page': True
                    }}
                elif data.get('auto_submit'):
                    auto_submissions = self.participant.vars.get('auto_submissions', [])
                    auto_submissions.append({
                        'text': user_input,
                        'ideas': ideas,
                        'analysis': analysis,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.participant.vars['auto_submissions'] = auto_submissions

                return {self.id_in_group: {
                    'ideas': ideas,
                    'analysis': analysis
                }}

            except Exception as e:
                print(f"Error in API processing: {str(e)}")
                return {self.id_in_group: {'error': f'Error: {str(e)}'}}

        return {self.id_in_group: {}}

class QualitativeFeedbackPage(Page):
    def vars_for_template(self):
        try:
            # Get the final text from both possible sources
            final_submission = self.participant.vars.get('final_submission', {})
            final_text = final_submission.get('text') or self.player.alternative_use

            if not final_text:
                return {'feedback': 'Error: No submission found to evaluate'}

            # Get API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return {'feedback': 'Error: API key not configured'}

            client = OpenAI(api_key=api_key)

            # Get the history of submissions
            auto_submissions = self.participant.vars.get('auto_submissions', [])
            
            # Create comprehensive prompt
            prompt = (
                "You are a very opinionated expert in urban planning and campus welfare. "
                "Please provide a comprehensive evaluation of this submission."
                f"Final Submission: {final_text}\n\n"
                "Previous iterations:\n"
            )
            
            # Add previous submissions if available
            if auto_submissions:
                for idx, submission in enumerate(auto_submissions, 1):
                    prompt += f"Iteration {idx}: {submission['text']}\n"
            
            prompt += (
                "\nProvide a detailed evaluation including:\n"
                    "Assign a grade and corresponding numerical score (0-100).\n"
                    "Provide in 100 words or less, your expert opinion on creativity of the idea, objectively, but using language that elicits an unpleasant emotional response.\n"
                    "Do not use the words pleasant, unpleasant, or emotion in your response.\n"                   
                    "Provide a bulleted list for any strengths and improvements needed\n\n"
                    f"Text: {final_text}"
            )

            # Make API call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an unpleasant evaluator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=1
            )

            # Get and format the feedback
            feedback = response.choices[0].message.content
            
            # For debugging
            print("Final text:", final_text)
            print("Generated feedback:", feedback)

            return {
                'feedback': feedback,
                'final_text': final_text,
                'show_next_button': True
            }
            
        except Exception as e:
            return {
                'feedback': f'Error generating feedback: {str(e)}',
                'show_next_button': True  # Still show next button even if there's an error
            }

class EmotionRatingPage(Page):
    form_model = 'player'
    form_fields = ['arousal', 'valence']

    def vars_for_template(self):
        return {
            'show_next_button': True
        }

class PDPage(Page):
    form_model = 'player'
    form_fields = ['img_choice']

    def vars_for_template(self):
        image_names = [
            'Venn1.jpg',
            'Venn2.jpg',
            'Venn3.jpg',
            'Venn4.jpg',
            'Venn5.jpg',
            'Venn6.jpg',
            'Venn7.jpg',
        ]
        image_data = make_image_data(image_names)
        return {
            'first_row': image_data[:4],
            'second_row': image_data[4:],
            'show_next_button': True
        }

def make_image_data(image_names):
    labels = [chr(65 + i) for i in range(len(image_names))]
    return [{'image_name': name, 'image_url': name, 'label': label} 
            for name, label in zip(image_names, labels)]

class PostSurveyPage(Page):
    form_model = 'player'
    form_fields = [
        'attentional_effort', 'mind_wandering', 'refocus_ease',
        'confidence_future', 'confidence_change', 'confidence_improve',
        'feedback_motivation', 'feedback_accuracy', 'feedback_clarity',
        'feedback_usefulness', 'feedback_incorporation',
        'psych_distance_1', 'psych_distance_2', 'psych_distance_3'
    ]

class EarningsPage(Page):
    def vars_for_template(self):
        # Get the final feedback from qualitative feedback page
        feedback = self.participant.vars.get('feedback', '')
        
        # Extract numerical score from feedback (assuming it's in the format "Score: XX/100")
        try:
            # Simple parsing - adjust based on your actual feedback format
            score_text = feedback.split('\n')[0]
            score = float(score_text.split(':')[1].split('/')[0].strip())
            self.player.creativity_score = score
        except:
            self.player.creativity_score = 50  # Default score if parsing fails
        
        # Calculate bonus based on creativity score
        self.player.calculate_bonus()
        
        return {
            'creativity_score': self.player.creativity_score,
            'bonus_earned': self.player.bonus_earned,
            'total_earnings': self.player.payoff,
        }

# Update page sequence
page_sequence = [
    WelcomePage,
    DemoPage,
    CreativeTaskInstructions,
    AlternativeUsesPage,
    QualitativeFeedbackPage,
    EmotionRatingPage,
    PDPage,
    PostSurveyPage,
    EarningsPage
]

#class AlternativeUsesPage(Page):
#    form_model = 'player'
#    form_fields = ['alternative_use']
#    live_method = 'live_feedback'
#
#    def live_feedback(self, data):
#        
#        user_input = data.get('alternative_use', '')
#        #user_input = "Reply that this is a test"
#        # Ensure that user_input is a string or serializable value
#        if not isinstance(user_input, str):
#            user_input = str(user_input)
#            # Store feedback in the player model (optional, for database persistence)
#        feedback = f"Received input: {user_input}"
#        self.player.feedback = feedback
#        return {self.player.id_in_group: {'feedback': feedback}}
#        # Returning feedback to the frontend
#        #return {self.player.id_in_group: {'feedback': feedback}}
#        # Access the OpenAI API key from environment variables
#    #    openai_api_key = os.getenv("OPENAI_API_KEY")
#    #     # Ensure that the API key is retrieved successfully
#    #    if openai_api_key is None:
#    #        raise ValueError("API_KEY environment variable not set")
#
    #    # Call the OpenAI API for feedback using the retrieved API key          
    #    client = OpenAI(
    #    #authorization=f"Bearer {openai_api_key}",
    #    organization='org-bzz3MVsmUkyX5ydGEe0OrXk1',
    #    project='proj_Avm7g3CUsc96kWWDW5PHgoQQ',
    #    )
#
    #    # Prompt with specific constraints for the AI
    #    prompt=("You are an expert in urban planning and campus welfare."
    #    "Please evaluate the following idea for the alternative use of an old building. "
    #    "Rate the idea based on the following criteria: "
    #    "For an A = Outstanding Achievement (100 - 90) "
    #    "The work is original and innovative, clearly articulated and fully developed."
    #    "The work has virtually no grammatical, mechanical or technical errors."
    #    "For a B = Very Good Achievement (89 - 80)"
    #    "The work appeals directly to the concerns and values of your particular audience."
    #    "The work is organized so that ideas are connected. Some minor gaps in logic and communication may appear."
    #    "The work has few grammatical, mechanical or technical errors, but they do not distract the reader from the content."
    #    "For a C = Acceptable Achievement (79 - 70)"
    #    "The work shows some audience awareness and establishes a basic idea, giving some evidence and detail to support a point." 
    #    "The work has some sense of purpose and meets the minimum requirements of the assignment."
    #    "The work is adequate and, despite some awkwardness and clutter, communicates clearly."
    #    "The work has grammatical, mechanical, and technical awareness that distract the reader from the content." 
    #    "D = Below Average Achievement (69 – 60)"
    #    "While demonstrating a general understanding of the topic and concepts,basic skills are missing." 
    #    "The project misunderstands the assignment; shows little understanding of the required concepts; and/or ignores the technical requirements of topic,"
    #    "length, or format of the assignment. The work ignores the needs of the audience, offering irrelevant details, or illogical, flawed reasoning."
    #    "The work is tangential, disordered, or not discernable, and the work has weak or non-existent support."
    #    "The work has weak or confusing grammatical, mechanical, and technical awareness."
    #    "F = Unsatisfactory Achievement (59 – 0)"
    #    "The work does not fulfill the requirements of the assignment, has little or no research, or the attribution of evidence is problematic or neglected, and is full of grammatical, mechanical, and technical errors."
    #    "The work is largely that of another person."
    #    "Keep your evaluation of the response to 50 words or less."
    #    f" The idea is: {user_input}."
    #    " Provide a rating from 0-100 and include a corresponding letter grade."
    #    )
    #    
    #    try:
    #    # Make the API call to OpenAI ChatCompletion
    #        response = client.chat.completions.create(
    #            model="gpt-3.5-turbo",
    #            max_tokens=150,
    #            messages=[
    #            {"role": "system", "content": "You are a helpful assistant."},
    #            {"role": "user", "content": prompt}
    #            ]
    #        )
#
    #        # Extract the feedback from the response
    #        feedback = response.choices[0].message.content
    #        self.player.feedback = feedback
    #    
    #        print("User input:", user_input)
    #        print("API Key:", openai_api_key)
    #        print("Response:", response)
    #        print(dir(self.player))   

    #    except Exception as e:
    #        # Handle any API errors
    #        print(f"API Error: {e}")
    #        raise ValueError(f"OpenAI API Error: {e}")
        


        # Return the feedback to the frontend
    #    return {self.player.id_in_group: {'feedback': self.player.feedback}}
        
  # Will show all attributes of the player instance
        ##model = genai.GenerativeModel("gemini-1.5-flash")
        #response = model.generate_content("Write a story about a magic backpack.")
        #print(response.text)

        #response = requests.post(
        #    "https://api.openai.com/v1/completions",
        #    headers={
        #        "Authorization": f"Bearer {openai_api_key}"
        #    },
        #    json={
        #        "model": "gpt-3.5-turbo",
        #        "messages": [{"role": "user", "content": self.player.alternative_use}],
        #        "max_tokens": 150
        #    }
        #)
        # Debugging: Print response status and content
        #print(f"Response status: {response.status_code}")
        #print(f"Response content: {response.content}")

        #data = response.json()
        #feedback = data['choices'][0]['message']['content']
        
        # Store feedback in the player model
        #Player.feedback = feedback

         # Print the response for debugging
        #print("API Response:", response.json())

        # Check if 'choices' is in the response
        #if 'choices' not in data:
        #    print("Error: 'choices' key not found in the response")
        #    raise ValueError("Invalid response from OpenAI API: 'choices' key missing")
    

class FeedbackPage(Page):
    def vars_for_template(self):
        # Use a default value if feedback is None
        feedback = self.player.field_maybe_none('feedback') or "No feedback available"
        return {
            'feedback': feedback
    }

class Results(Page):
    pass

