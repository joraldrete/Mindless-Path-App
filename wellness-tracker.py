import wx
import json
import os
import datetime

DATA_FILE = "wellness_data.json"

# ----------------------
# Helper functions
# ----------------------

def load_data():
    """Load data from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    """Save data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ----------------------
# Daily Entry Window
# ----------------------

class DayEntryWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title=f"Daily Entry - {date}", size=(400, 350))
        self.date = str(date)
        self.parent = parent
        self.data = data

        panel = wx.Panel(self)

        # Labels and fields
        wx.StaticText(panel, label="Exercise (minutes):", pos=(30, 30))
        self.exercise = wx.TextCtrl(panel, pos=(180, 30), size=(150, -1))

        wx.StaticText(panel, label="Sleep (hours):", pos=(30, 70))
        self.sleep = wx.TextCtrl(panel, pos=(180, 70), size=(150, -1))

        wx.StaticText(panel, label="Water (glasses):", pos=(30, 110))
        self.water = wx.TextCtrl(panel, pos=(180, 110), size=(150, -1))

        wx.StaticText(panel, label="Calories:", pos=(30, 150))
        self.calories = wx.TextCtrl(panel, pos=(180, 150), size=(150, -1))

        wx.StaticText(panel, label="Mood:", pos=(30, 190))
        self.mood = wx.ComboBox(
            panel,
            choices=["😀 Happy", "😐 Okay", "😞 Sad", "😡 Angry", "😴 Tired"],
            pos=(180, 190),
            size=(150, -1)
        )

        # Load existing data if available
        if self.date in self.data:
            entry = self.data[self.date]
            # top-level keys
            self.exercise.SetValue(str(entry.get("exercise", "")))
            self.sleep.SetValue(str(entry.get("sleep", "")))
            self.water.SetValue(str(entry.get("water", "")))
            self.calories.SetValue(str(entry.get("calories", "")))
            self.mood.SetValue(entry.get("mood", ""))

        # Save Button
        save_btn = wx.Button(panel, label="Save Entry", pos=(130, 250))
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        """Save data for this day."""
        # Ensure date contains a dict (merge with existing nested trackers if present)
        existing = self.data.get(self.date, {})
        existing.update({
            "exercise": self.exercise.GetValue(),
            "sleep": self.sleep.GetValue(),
            "water": self.water.GetValue(),
            "calories": self.calories.GetValue(),
            "mood": self.mood.GetValue(),
        })
        self.data[self.date] = existing

        save_data(self.data)
        wx.MessageBox("Data saved successfully!", "Saved", wx.OK | wx.ICON_INFORMATION)
        self.Close()

# ----------------------
# Daily Report Window
# ----------------------

class DailyReportWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title=f"Daily Report - {date}", size=(420, 380))
        panel = wx.Panel(self)

        date = str(date)
        wx.StaticText(panel, label=f"Report for {date}", pos=(140, 20))

        entry = data.get(date, None)
        goals = data.get("goals", {})

        if not entry:
            wx.StaticText(panel, label="No data recorded for this day.", pos=(100, 150))
            return

        # Pull top-level values (fall back to nested trackers if present)
        exercise = float(entry.get("exercise", 0) or 0)
        sleep = float(entry.get("sleep", 0) or 0)
        water = float(entry.get("water", 0) or 0)
        calories = float(entry.get("calories", 0) or 0)
        mood = entry.get("mood", "None")

        # Nutrition and sleep tracker nested info (if present)
        nutrition = entry.get("nutrition", {})
        sleep_tracker = entry.get("sleep_tracker", {})

        wx.StaticText(panel, label=f"Exercise: {exercise} min", pos=(30, 70))
        wx.StaticText(panel, label=f"Sleep: {sleep} hours", pos=(30, 100))
        wx.StaticText(panel, label=f"Water: {water} glasses", pos=(30, 130))
        wx.StaticText(panel, label=f"Calories: {calories}", pos=(30, 160))
        wx.StaticText(panel, label=f"Mood: {mood}", pos=(30, 190))

        # Nutrition summary
        wx.StaticText(panel, label="Nutrition (cal):", pos=(220, 70))
        wx.StaticText(panel, label=f"Breakfast: {nutrition.get('breakfast','-')}", pos=(220, 100))
        wx.StaticText(panel, label=f"Lunch: {nutrition.get('lunch','-')}", pos=(220, 130))
        wx.StaticText(panel, label=f"Dinner: {nutrition.get('dinner','-')}", pos=(220, 160))
        wx.StaticText(panel, label=f"Snacks: {nutrition.get('snacks','-')}", pos=(220, 190))

        # Sleep tracker nested info
        wx.StaticText(panel, label="Sleep Tracker:", pos=(30, 220))
        wx.StaticText(panel, label=f"Hours: {sleep_tracker.get('hours','-')}", pos=(30, 250))
        wx.StaticText(panel, label=f"Quality: {sleep_tracker.get('quality','-')}", pos=(170, 250))
        wx.StaticText(panel, label=f"Bedtime: {sleep_tracker.get('bedtime','-')}", pos=(320, 250))

        # Goal comparisons
        def compare(value, goal):
            if goal is None or goal == "":
                return "No goal set"
            try:
                if float(value) >= float(goal):
                    return "Goal met ✔"
                else:
                    return "Goal missed ✘"
            except:
                return "N/A"

        wx.StaticText(panel, label="Goal Check:", pos=(30, 280))
        wx.StaticText(panel, label=f"Exercise: {compare(exercise, goals.get('exercise_goal'))}", pos=(30, 300))
        wx.StaticText(panel, label=f"Sleep: {compare(sleep, goals.get('sleep_goal'))}", pos=(220, 300))

# ----------------------
# Monthly Report Window
# ----------------------

class MonthlyReportWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Monthly Report", size=(500, 420))
        panel = wx.Panel(self)

        today = datetime.date.today()
        month_start = today.replace(day=1)

        wx.StaticText(panel, label=f"Monthly Report - {today.strftime('%B %Y')}", pos=(150, 20))

        entries = []
        for key, entry in data.items():
            if key == "goals":
                continue
            try:
                d = datetime.datetime.strptime(key, "%Y-%m-%d").date()
                if d >= month_start and d <= today:
                    entries.append(entry)
            except:
                pass

        if not entries:
            wx.StaticText(panel, label="No data recorded this month.", pos=(150, 150))
            return

        # Summaries
        total = {"exercise": 0, "sleep": 0, "water": 0, "calories": 0}
        moods = {}

        for entry in entries:
            for k in total:
                total[k] += float(entry.get(k, 0) or 0)

            mood = entry.get("mood", "")
            if mood:
                moods[mood] = moods.get(mood, 0) + 1

        num = len(entries)
        avg_exercise = total["exercise"] / num
        avg_sleep = total["sleep"] / num
        avg_water = total["water"] / num
        avg_calories = total["calories"] / num
        common_mood = max(moods, key=moods.get) if moods else "N/A"

        wx.StaticText(panel, label=f"Days logged: {num}", pos=(30, 80))
        wx.StaticText(panel, label=f"Avg Exercise: {avg_exercise:.1f} min", pos=(30, 120))
        wx.StaticText(panel, label=f"Avg Sleep: {avg_sleep:.1f} hrs", pos=(30, 150))
        wx.StaticText(panel, label=f"Avg Water: {avg_water:.1f} glasses", pos=(30, 180))
        wx.StaticText(panel, label=f"Avg Calories: {avg_calories:.1f}", pos=(30, 210))
        wx.StaticText(panel, label=f"Most Common Mood: {common_mood}", pos=(30, 240))

# ----------------------
# Weekly Summary Window (corrected 7 calendar days)
# ----------------------

class WeeklySummaryWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Weekly Summary", size=(400, 300))
        panel = wx.Panel(self)

        wx.StaticText(panel, label="7-Day Wellness Summary", pos=(120, 20))

        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=7)

        valid_entries = {}
        for key, entry in data.items():
            if key == "goals":
                continue

            try:
                entry_date = datetime.datetime.strptime(key, "%Y-%m-%d").date()

                # Only include true last 7 calendar days
                if seven_days_ago <= entry_date <= today:
                    valid_entries[key] = entry

            except ValueError:
                continue

        sorted_entries = sorted(valid_entries.items(), key=lambda x: x[0], reverse=True)

        total = {"exercise": 0, "sleep": 0, "water": 0, "calories": 0}
        mood_counts = {}

        for _, entry in sorted_entries:
            for key in total.keys():
                total[key] += float(entry.get(key, 0) or 0)
            mood = entry.get("mood", "")
            if mood:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1

        num_days = len(sorted_entries)

        if num_days > 0:
            avg_exercise = total["exercise"] / num_days
            avg_sleep = total["sleep"] / num_days
            avg_water = total["water"] / num_days
            avg_calories = total["calories"] / num_days
            common_mood = max(mood_counts, key=mood_counts.get) if mood_counts else "N/A"
        else:
            avg_exercise = avg_sleep = avg_water = avg_calories = 0
            common_mood = "N/A"

        if num_days == 0:
            wx.StaticText(panel, label="No data available for the past 7 days.", pos=(80, 130))
        else:
            wx.StaticText(panel, label=f"Days included: {num_days}", pos=(50, 50))
            wx.StaticText(panel, label=f"Avg Exercise: {avg_exercise:.1f} min", pos=(50, 80))
            wx.StaticText(panel, label=f"Avg Sleep: {avg_sleep:.1f} hrs", pos=(50, 110))
            wx.StaticText(panel, label=f"Avg Water: {avg_water:.1f} glasses", pos=(50, 140))
            wx.StaticText(panel, label=f"Avg Calories: {avg_calories:.1f}", pos=(50, 170))
            wx.StaticText(panel, label=f"Most Common Mood: {common_mood}", pos=(50, 200))

# ----------------------
# Goals Window
# ----------------------

class GoalsWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Set Your Goals", size=(400, 300))
        panel = wx.Panel(self)
        self.data = data

        wx.StaticText(panel, label="Daily Goals:", pos=(150, 20))
        wx.StaticText(panel, label="Exercise (min):", pos=(30, 70))
        wx.StaticText(panel, label="Sleep (hours):", pos=(30, 110))
        wx.StaticText(panel, label="Water (glasses):", pos=(30, 150))
        wx.StaticText(panel, label="Calories (max):", pos=(30, 190))

        self.exercise_goal = wx.TextCtrl(panel, pos=(180, 70), size=(150, -1))
        self.sleep_goal = wx.TextCtrl(panel, pos=(180, 110), size=(150, -1))
        self.water_goal = wx.TextCtrl(panel, pos=(180, 150), size=(150, -1))
        self.calories_goal = wx.TextCtrl(panel, pos=(180, 190), size=(150, -1))

        # Load saved goals
        goals = self.data.get("goals", {})
        self.exercise_goal.SetValue(str(goals.get("exercise_goal", "")))
        self.sleep_goal.SetValue(str(goals.get("sleep_goal", "")))
        self.water_goal.SetValue(str(goals.get("water_goal", "")))
        self.calories_goal.SetValue(str(goals.get("calories_goal", "")))

        save_btn = wx.Button(panel, label="Save Goals", pos=(140, 230))
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        goals = {
            "exercise_goal": self.exercise_goal.GetValue(),
            "sleep_goal": self.sleep_goal.GetValue(),
            "water_goal": self.water_goal.GetValue(),
            "calories_goal": self.calories_goal.GetValue(),
        }
        self.data["goals"] = goals
        save_data(self.data)
        wx.MessageBox("Goals saved successfully!", "Saved", wx.OK | wx.ICON_INFORMATION)
        self.Close()

# ----------------------
# Nutrition Tracker
# ----------------------

class NutritionTrackerWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title=f"Nutrition Tracker - {date}", size=(400, 400))
        self.date = str(date)
        self.data = data

        panel = wx.Panel(self)
        wx.StaticText(panel, label="Log Your Meals and Calories:", pos=(100, 20))

        wx.StaticText(panel, label="Breakfast (cal):", pos=(30, 70))
        self.breakfast = wx.TextCtrl(panel, pos=(180, 70), size=(150, -1))

        wx.StaticText(panel, label="Lunch (cal):", pos=(30, 110))
        self.lunch = wx.TextCtrl(panel, pos=(180, 110), size=(150, -1))

        wx.StaticText(panel, label="Dinner (cal):", pos=(30, 150))
        self.dinner = wx.TextCtrl(panel, pos=(180, 150), size=(150, -1))

        wx.StaticText(panel, label="Snacks (cal):", pos=(30, 190))
        self.snacks = wx.TextCtrl(panel, pos=(180, 190), size=(150, -1))

        save_btn = wx.Button(panel, label="Save Nutrition", pos=(130, 250))
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

        if self.date in self.data and "nutrition" in self.data[self.date]:
            entry = self.data[self.date]["nutrition"]
            self.breakfast.SetValue(str(entry.get("breakfast", "")))
            self.lunch.SetValue(str(entry.get("lunch", "")))
            self.dinner.SetValue(str(entry.get("dinner", "")))
            self.snacks.SetValue(str(entry.get("snacks", "")))

    def on_save(self, event):
        if self.date not in self.data:
            self.data[self.date] = {}

        self.data[self.date]["nutrition"] = {
            "breakfast": self.breakfast.GetValue(),
            "lunch": self.lunch.GetValue(),
            "dinner": self.dinner.GetValue(),
            "snacks": self.snacks.GetValue(),
        }

        save_data(self.data)
        wx.MessageBox("Nutrition data saved!", "Saved", wx.OK | wx.ICON_INFORMATION)
        self.Close()

# ----------------------
# Sleep Tracker
# ----------------------

class SleepTrackerWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title=f"Sleep Tracker - {date}", size=(400, 300))
        self.date = str(date)
        self.data = data

        panel = wx.Panel(self)
        wx.StaticText(panel, label="Sleep Tracking", pos=(150, 20))
        wx.StaticText(panel, label="Hours Slept:", pos=(30, 70))
        wx.StaticText(panel, label="Sleep Quality (1-10):", pos=(30, 110))
        wx.StaticText(panel, label="Bedtime (HH:MM):", pos=(30, 150))

        self.hours = wx.TextCtrl(panel, pos=(180, 70), size=(150, -1))
        self.quality = wx.TextCtrl(panel, pos=(180, 110), size=(150, -1))
        self.bedtime = wx.TextCtrl(panel, pos=(180, 150), size=(150, -1))

        save_btn = wx.Button(panel, label="Save Sleep Data", pos=(130, 200))
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

        if self.date in self.data and "sleep_tracker" in self.data[self.date]:
            entry = self.data[self.date]["sleep_tracker"]
            self.hours.SetValue(str(entry.get("hours", "")))
            self.quality.SetValue(str(entry.get("quality", "")))
            self.bedtime.SetValue(str(entry.get("bedtime", "")))

    def on_save(self, event):
        if self.date not in self.data:
            self.data[self.date] = {}

        self.data[self.date]["sleep_tracker"] = {
            "hours": self.hours.GetValue(),
            "quality": self.quality.GetValue(),
            "bedtime": self.bedtime.GetValue(),
        }

        save_data(self.data)
        wx.MessageBox("Sleep data saved!", "Saved", wx.OK | wx.ICON_INFORMATION)
        self.Close()

# ----------------------
# Main Window
# ----------------------

class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Mindful Path Wellness Tracker", size=(520, 420))
        panel = wx.Panel(self)

        self.data = load_data()
        self.current_date = datetime.date.today()

        self.date_label = wx.StaticText(panel, label=str(self.current_date), pos=(200, 20))

        prev_btn = wx.Button(panel, label="<< Previous", pos=(50, 70))
        next_btn = wx.Button(panel, label="Next >>", pos=(370, 70))
        open_day_btn = wx.Button(panel, label="Open Daily Entry", pos=(200, 70))

        weekly_btn = wx.Button(panel, label="Weekly Summary", pos=(50, 140))
        goals_btn = wx.Button(panel, label="Set Goals", pos=(370, 140))

        # Daily and Monthly Report buttons (added)
        daily_report_btn = wx.Button(panel, label="Daily Report", pos=(50, 200))
        monthly_report_btn = wx.Button(panel, label="Monthly Report", pos=(370, 200))

        nutrition_btn = wx.Button(panel, label="Nutrition Tracker", pos=(50, 260))
        sleep_btn = wx.Button(panel, label="Sleep Tracker", pos=(370, 260))

        # Bindings
        prev_btn.Bind(wx.EVT_BUTTON, self.on_prev_day)
        next_btn.Bind(wx.EVT_BUTTON, self.on_next_day)
        open_day_btn.Bind(wx.EVT_BUTTON, self.on_open_day)

        weekly_btn.Bind(wx.EVT_BUTTON, self.on_weekly_summary)
        goals_btn.Bind(wx.EVT_BUTTON, self.on_goals)

        daily_report_btn.Bind(wx.EVT_BUTTON, self.on_daily_report)
        monthly_report_btn.Bind(wx.EVT_BUTTON, self.on_monthly_report)

        nutrition_btn.Bind(wx.EVT_BUTTON, self.on_nutrition)
        sleep_btn.Bind(wx.EVT_BUTTON, self.on_sleep)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Show()

    def on_prev_day(self, event):
        self.current_date -= datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

    def on_next_day(self, event):
        self.current_date += datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

    def on_open_day(self, event):
        DayEntryWindow(self, self.current_date, self.data).Show()

    def on_weekly_summary(self, event):
        WeeklySummaryWindow(self, self.data).Show()

    def on_goals(self, event):
        GoalsWindow(self, self.data).Show()

    def on_daily_report(self, event):
        DailyReportWindow(self, self.current_date, self.data).Show()

    def on_monthly_report(self, event):
        MonthlyReportWindow(self, self.data).Show()

    def on_nutrition(self, event):
        NutritionTrackerWindow(self, self.current_date, self.data).Show()

    def on_sleep(self, event):
        SleepTrackerWindow(self, self.current_date, self.data).Show()

    def on_close(self, event):
        save_data(self.data)
        self.Destroy()

# ----------------------
# App Runner
# ----------------------

class MindfulPathApp(wx.App):
    def OnInit(self):
        MainWindow()
        return True


if __name__ == "__main__":
    app = MindfulPathApp()
    app.MainLoop()

