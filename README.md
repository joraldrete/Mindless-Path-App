# Weekly Health & Mental Wellness Tracker Data Structure

wellness_week = {
    "user": "Sample User",
    "week_start": "2025-09-29",
    "week_end": "2025-10-05",
    "days": [
        {
            "date": "2025-09-29",
            "physical_health": {
                "exercise_minutes": 30,
                "water_intake_glasses": 8,
                "sleep_hours": 7.5,
                "nutrition": {"fruits_veggies_servings": 4, "junk_food": False},
					 "calories": 2000 
                "medication_taken": True
            },
            "mental_wellness": {
                "mood": "happy",
                "stress_level": 3,  # scale 1–10
                "journal_entry": "Felt productive and energetic today.",
                "meditation_minutes": 10,
                "screen_time_hours": 2.5
            },
            "lifestyle_productivity": {
                "tasks_completed": ["Finish assignment", "Grocery shopping"],
                "focus_hours": 3,
                "expenses_logged": 25.50
            },
            "social_relationships": {
                "family_time_hours": 1,
                "friend_interactions": ["Called Jorge"],
                "community_activity": None
            },
            "self_care_growth": {
                "hobbies": ["Read 20 pages of book"],
                "relaxation_minutes": 15,
                "gratitude_list": ["Health", "Family", "Good weather"],
                "learning_activity": "Watched 1 online course video"
            }
        },
        # ... Repeat for remaining days of the week ...
    ]
}
