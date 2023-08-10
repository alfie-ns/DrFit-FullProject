# Path: django-api/nutrition/meal_planner/meal_planner.py

'''This file contains function that will create a meal plan for the user.'''

from dotenv import load_dotenv
from accounts.models import UserProfile
from response.calculations import calculate_calorific_needs, calculate_macronutrient_split
from response.models import Conversation
import json, os, openai, time

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-3.5-turbo"

def get_meal_plan(request):

    # Get request data
    data = json.loads(request.body.decode('utf-8'))
    meal_plan_length = data.get('meal_plan_length')
    meal_plan_type = data.get('meal_plan_type') # 'vegan', 'vegetarian', 'pescatarian', 'keto', 'paleo', 'gluten-free', 'dairy-free', 'low-carb', 'low-fat', 'low-sodium', 'low-sugar', 'high-protein', 'high-fiber', 'balanced'
    allergies = data.get('allergies', [])
    preferences = data.get('preferences', [])
    number_of_meals = data.get('number_of_meals', 3) 

    # Get user profile
    user_profile = UserProfile.objects.get(user=request.user)
    print(f'User profile: {user_profile}')

    goal = user_profile.goal
    weight = user_profile.weight
    height = user_profile.height
    age = user_profile.age
    gender = user_profile.gender

    # Calculations
    daily_calorific_needs = calculate_calorific_needs(user_profile.age, user_profile.height, user_profile.weight, user_profile.goal, user_profile.determination_level, user_profile.activity_level, user_profile.bmr_type, user_profile.gender)
    macronutrient_split = calculate_macronutrient_split(user_profile.gender, user_profile.height, user_profile.weight, user_profile.bmr_type, user_profile.activity_level, user_profile.age, user_profile.goal)
    print(f'Calorific needs: {daily_calorific_needs}')
    print(f'Macronutrient split: {macronutrient_split}')

    # Create conversation
    # Try to get the existing conversation from the database
    conversation, created = Conversation.objects.get_or_create(user=user_profile.user)

    # If the conversation was just created, initialize an empty history
    if created:
       conversation.history = []

    # Timestamp the start of the initial plan generation
    start_time = time.time()

    # Create meal plan response
    res = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'user', 'content': f'''Create a {meal_plan_length}-day meal plan that follows a {meal_plan_type} diet.
                                             Here are the details to consider:
                                             - Calorific needs: {daily_calorific_needs}
                                             - Macronutrient split: {macronutrient_split}
                                             - Goal: {goal}
                                             - Weight: {weight}
                                             - Height: {height}
                                             - Gender: {gender}
                                             - Age: {age}
                                             - Allergies: {', '.join(allergies)}
                                             - Preferences: {', '.join(preferences)}
                                             - Number of Meals Per Day: {number_of_meals}
                                             Please remember, I need to consume at least 1.6g of protein per kg of bodyweight to maintain muscle mass in a calorie deficit, if my goal is to build muscle.

                                             FINALLY, make sure to only respond with the meal plan itself, and not any other information.
                                          '''},
        ])
    response = res['choices'][0]['message']['content']
    print(f'MEAL PLAN RESPONSE: {response}')

    # Add the response to the conversation history
    conversation.history.append({'role': 'assistant', 'content': response})
    conversation.save() # Save the conversation to the database

    # Timestamp the end of the initial plan generation
    print(f'TIME TAKEN TO GENERATE MEAL PLAN: {time.time() - start_time} seconds')

    # Return the response
    return response
