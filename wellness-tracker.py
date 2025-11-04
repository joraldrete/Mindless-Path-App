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
        self.mood = wx.ComboBox(panel, choices=["😀 Happy", "😐 Okay", "😞 Sad", "😡 Angry", "😴 Tired"], pos=(180, 190), size=(150, -1))

        # Load existing data if available
        if self.date in self.data:
            entry = self.data[self.date]
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
        self.data[self.date] = {
            "exercise": self.exercise.GetValue(),
            "sleep": self.sleep.GetValue(),
            "water": self.water.GetValue(),
            "calories": self.calories.GetValue(),
            "mood": self.mood.GetValue(),
        }

        save_data(self.data)
        wx.MessageBox("Data saved successfully!", "Saved", wx.OK | wx.ICON_INFORMATION)
        self.Close()

# ----------------------
# Weekly Summary Window
# ----------------------

class WeeklySummaryWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Weekly Summary", size=(400, 300))
        panel = wx.Panel(self)

        wx.StaticText(panel, label="7-Day Wellness Summary", pos=(120, 20))

        # Calculate weekly averages
        last_7_days = sorted([d for d in data.keys() if d != "goals"])[-7:]
        total = {"exercise": 0, "sleep": 0, "water": 0, "calories": 0}
        mood_counts = {}

        for day in last_7_days:
            entry = data.get(day, {})
            for key in total.keys():
                total[key] += float(entry.get(key, 0) or 0)
            mood = entry.get("mood", "")
            if mood:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1

        if last_7_days:
            avg_exercise = total["exercise"] / len(last_7_days)
            avg_sleep = total["sleep"] / len(last_7_days)
            avg_water = total["water"] / len(last_7_days)
            avg_calories = total["calories"] / len(last_7_days)
            common_mood = max(mood_counts, key=mood_counts.get) if mood_counts else "N/A"
        else:
            avg_exercise = avg_sleep = avg_water = avg_calories = 0
            common_mood = "N/A"

        wx.StaticText(panel, label=f"Avg Exercise: {avg_exercise:.1f} min", pos=(50, 70))
        wx.StaticText(panel, label=f"Avg Sleep: {avg_sleep:.1f} hrs", pos=(50, 100))
        wx.StaticText(panel, label=f"Avg Water: {avg_water:.1f} glasses", pos=(50, 130))
        wx.StaticText(panel, label=f"Avg Calories: {avg_calories:.1f}", pos=(50, 160))
        wx.StaticText(panel, label=f"Most Common Mood: {common_mood}", pos=(50, 190))

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

        # Load existing goals
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
            "calories_goal": self.calories_goal.GetValue()
        }

        self.data["goals"] = goals
        save_data(self.data)

        wx.MessageBox("Goals saved successfully!", "Saved", wx.OK | wx.ICON_INFORMATION)
        self.Close()

# ----------------------
# Main Window
# ----------------------

class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Mindful Path Wellness Tracker", size=(400, 300))
        panel = wx.Panel(self)

        self.data = load_data()
        self.current_date = datetime.date.today()

        self.date_label = wx.StaticText(panel, label=str(self.current_date), pos=(160, 30))

        prev_btn = wx.Button(panel, label="<< Previous", pos=(50, 70))
        next_btn = wx.Button(panel, label="Next >>", pos=(230, 70))
        open_day_btn = wx.Button(panel, label="Open Daily Entry", pos=(130, 120))
        weekly_btn = wx.Button(panel, label="Weekly Summary", pos=(50, 180))
        goals_btn = wx.Button(panel, label="Set Goals", pos=(230, 180))

        prev_btn.Bind(wx.EVT_BUTTON, self.on_prev_day)
        next_btn.Bind(wx.EVT_BUTTON, self.on_next_day)
        open_day_btn.Bind(wx.EVT_BUTTON, self.on_open_day)
        weekly_btn.Bind(wx.EVT_BUTTON, self.on_weekly_summary)
        goals_btn.Bind(wx.EVT_BUTTON, self.on_goals)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Show()

    def on_prev_day(self, event):
        self.current_date -= datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

    def on_next_day(self, event):
        self.current_date += datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

    def on_open_day(self, event):
        window = DayEntryWindow(self, self.current_date, self.data)
        window.Show()

    def on_weekly_summary(self, event):
        window = WeeklySummaryWindow(self, self.data)
        window.Show()

    def on_goals(self, event):
        window = GoalsWindow(self, self.data)
        window.Show()

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

