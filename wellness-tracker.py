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

        # Load existing data
        if self.date in self.data:
            existing = self.data[self.date]
            self.exercise.SetValue(str(existing.get("exercise", "")))
            self.sleep.SetValue(str(existing.get("sleep", "")))
            self.water.SetValue(str(existing.get("water", "")))
            self.calories.SetValue(str(existing.get("calories", "")))
            self.mood.SetValue(existing.get("mood", ""))

        save_btn = wx.Button(panel, label="Save Entry", pos=(130, 250))
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        entry = self.data.get(self.date, {})
        entry.update({
            "exercise": self.exercise.GetValue(),
            "sleep": self.sleep.GetValue(),
            "water": self.water.GetValue(),
            "calories": self.calories.GetValue(),
            "mood": self.mood.GetValue(),
        })
        self.data[self.date] = entry
        save_data(self.data)

        wx.MessageBox("Data saved!", "Success")
        self.Close()

# ----------------------
# Daily Report
# ----------------------

class DailyReportWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title=f"Daily Report - {date}", size=(420, 380))
        panel = wx.Panel(self)

        date = str(date)
        wx.StaticText(panel, label=f"Report for {date}", pos=(140, 20))

        entry = data.get(date)
        goals = data.get("goals", {})

        if not entry:
            wx.StaticText(panel, label="No data for this date.", pos=(130, 150))
            return

        exercise = float(entry.get("exercise", 0) or 0)
        sleep = float(entry.get("sleep", 0) or 0)
        water = float(entry.get("water", 0) or 0)
        calories = float(entry.get("calories", 0) or 0)
        mood = entry.get("mood", "None")

        nutrition = entry.get("nutrition", {})
        sleep_tracker = entry.get("sleep_tracker", {})

        wx.StaticText(panel, label=f"Exercise: {exercise} min", pos=(30, 70))
        wx.StaticText(panel, label=f"Sleep: {sleep} hours", pos=(30, 100))
        wx.StaticText(panel, label=f"Water: {water} glasses", pos=(30, 130))
        wx.StaticText(panel, label=f"Calories: {calories}", pos=(30, 160))
        wx.StaticText(panel, label=f"Mood: {mood}", pos=(30, 190))

        # Nutrition
        wx.StaticText(panel, label="Nutrition:", pos=(220, 70))
        wx.StaticText(panel, label=f"Breakfast: {nutrition.get('breakfast','-')}", pos=(220, 100))
        wx.StaticText(panel, label=f"Lunch: {nutrition.get('lunch','-')}", pos=(220, 130))
        wx.StaticText(panel, label=f"Dinner: {nutrition.get('dinner','-')}", pos=(220, 160))
        wx.StaticText(panel, label=f"Snacks: {nutrition.get('snacks','-')}", pos=(220, 190))

        # Sleep tracker
        wx.StaticText(panel, label="Sleep Tracker:", pos=(30, 220))
        wx.StaticText(panel, label=f"Hours: {sleep_tracker.get('hours','-')}", pos=(30, 250))
        wx.StaticText(panel, label=f"Quality: {sleep_tracker.get('quality','-')}", pos=(150, 250))
        wx.StaticText(panel, label=f"Bedtime: {sleep_tracker.get('bedtime','-')}", pos=(280, 250))

# ----------------------
# Monthly Report
# ----------------------

class MonthlyReportWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Monthly Report", size=(500, 420))
        panel = wx.Panel(self)

        today = datetime.date.today()
        month_start = today.replace(day=1)

        wx.StaticText(panel, label=f"Monthly Report - {today.strftime('%B %Y')}", pos=(150, 20))

        entries = []
        for date_str, entry in data.items():
            if date_str == "goals":
                continue
            try:
                d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if month_start <= d <= today:
                    entries.append(entry)
            except:
                pass

        if not entries:
            wx.StaticText(panel, label="No entries this month.", pos=(150, 150))
            return

        total = {"exercise": 0, "sleep": 0, "water": 0, "calories": 0}
        moods = {}

        for e in entries:
            for k in total:
                total[k] += float(e.get(k, 0) or 0)
            m = e.get("mood")
            if m:
                moods[m] = moods.get(m, 0) + 1

        num = len(entries)

        wx.StaticText(panel, label=f"Days logged: {num}", pos=(30, 80))
        wx.StaticText(panel, label=f"Avg Exercise: {total['exercise']/num:.1f}", pos=(30, 120))
        wx.StaticText(panel, label=f"Avg Sleep: {total['sleep']/num:.1f}", pos=(30, 150))
        wx.StaticText(panel, label=f"Avg Water: {total['water']/num:.1f}", pos=(30, 180))
        wx.StaticText(panel, label=f"Avg Calories: {total['calories']/num:.1f}", pos=(30, 210))
        wx.StaticText(panel, label=f"Most Common Mood: {max(moods,key=moods.get)}", pos=(30, 240))

# ----------------------
# Weekly Summary
# ----------------------

class WeeklySummaryWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Weekly Summary", size=(400, 300))
        panel = wx.Panel(self)

        wx.StaticText(panel, label="7-Day Wellness Summary", pos=(120, 20))

        today = datetime.date.today()
        start = today - datetime.timedelta(days=7)

        entries = []
        for d, entry in data.items():
            if d == "goals":
                continue
            try:
                dt = datetime.datetime.strptime(d, "%Y-%m-%d").date()
                if start <= dt <= today:
                    entries.append(entry)
            except:
                pass

        if not entries:
            wx.StaticText(panel, label="No entries in the last week.", pos=(100, 140))
            return

        total = {"exercise": 0, "sleep": 0, "water": 0, "calories": 0}
        moods = {}

        for e in entries:
            for k in total:
                total[k] += float(e.get(k, 0) or 0)
            m = e.get("mood")
            if m:
                moods[m] = moods.get(m, 0) + 1

        num = len(entries)

        wx.StaticText(panel, label=f"Days logged: {num}", pos=(50, 60))
        wx.StaticText(panel, label=f"Avg Exercise: {total['exercise']/num:.1f}", pos=(50, 90))
        wx.StaticText(panel, label=f"Avg Sleep: {total['sleep']/num:.1f}", pos=(50, 120))
        wx.StaticText(panel, label=f"Avg Water: {total['water']/num:.1f}", pos=(50, 150))
        wx.StaticText(panel, label=f"Avg Calories: {total['calories']/num:.1f}", pos=(50, 180))
        wx.StaticText(panel, label=f"Most Common Mood: {max(moods,key=moods.get)}", pos=(50, 210))

# ----------------------
# Goals Window
# ----------------------

class GoalsWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Set Goals", size=(400, 300))
        panel = wx.Panel(self)
        self.data = data

        wx.StaticText(panel, label="Daily Goals", pos=(150, 20))

        wx.StaticText(panel, label="Exercise (min):", pos=(30, 70))
        self.e_goal = wx.TextCtrl(panel, pos=(180, 70))

        wx.StaticText(panel, label="Sleep (hrs):", pos=(30, 110))
        self.s_goal = wx.TextCtrl(panel, pos=(180, 110))

        wx.StaticText(panel, label="Water (cups):", pos=(30, 150))
        self.w_goal = wx.TextCtrl(panel, pos=(180, 150))

        wx.StaticText(panel, label="Calories:", pos=(30, 190))
        self.c_goal = wx.TextCtrl(panel, pos=(180, 190))

        # Load existing
        g = data.get("goals", {})
        self.e_goal.SetValue(str(g.get("exercise_goal", "")))
        self.s_goal.SetValue(str(g.get("sleep_goal", "")))
        self.w_goal.SetValue(str(g.get("water_goal", "")))
        self.c_goal.SetValue(str(g.get("calories_goal", "")))

        save_btn = wx.Button(panel, label="Save", pos=(150, 230))
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        self.data["goals"] = {
            "exercise_goal": self.e_goal.GetValue(),
            "sleep_goal": self.s_goal.GetValue(),
            "water_goal": self.w_goal.GetValue(),
            "calories_goal": self.c_goal.GetValue(),
        }
        save_data(self.data)
        wx.MessageBox("Goals saved!", "Success")
        self.Close()

# ----------------------
# Nutrition Tracker
# ----------------------

class NutritionTrackerWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title="Nutrition Tracker", size=(400, 380))
        self.date = str(date)
        self.data = data

        panel = wx.Panel(self)
        wx.StaticText(panel, label="Nutrition", pos=(160, 20))

        wx.StaticText(panel, label="Breakfast (cal):", pos=(30, 70))
        self.b = wx.TextCtrl(panel, pos=(180, 70))

        wx.StaticText(panel, label="Lunch (cal):", pos=(30, 110))
        self.l = wx.TextCtrl(panel, pos=(180, 110))

        wx.StaticText(panel, label="Dinner (cal):", pos=(30, 150))
        self.d = wx.TextCtrl(panel, pos=(180, 150))

        wx.StaticText(panel, label="Snacks (cal):", pos=(30, 190))
        self.s = wx.TextCtrl(panel, pos=(180, 190))

        save_btn = wx.Button(panel, label="Save Nutrition", pos=(130, 250))
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

        if self.date in data and "nutrition" in data[self.date]:
            e = data[self.date]["nutrition"]
            self.b.SetValue(str(e.get("breakfast", "")))
            self.l.SetValue(str(e.get("lunch", "")))
            self.d.SetValue(str(e.get("dinner", "")))
            self.s.SetValue(str(e.get("snacks", "")))

    def on_save(self, event):
        if self.date not in self.data:
            self.data[self.date] = {}

        self.data[self.date]["nutrition"] = {
            "breakfast": self.b.GetValue(),
            "lunch": self.l.GetValue(),
            "dinner": self.d.GetValue(),
            "snacks": self.s.GetValue(),
        }

        save_data(self.data)
        wx.MessageBox("Nutrition saved!", "Success")
        self.Close()

# ----------------------
# Sleep Tracker
# ----------------------

class SleepTrackerWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title="Sleep Tracker", size=(400, 300))
        self.date = str(date)
        self.data = data

        panel = wx.Panel(self)
        wx.StaticText(panel, label="Sleep Tracker", pos=(150, 20))

        wx.StaticText(panel, label="Hours:", pos=(30, 70))
        self.h = wx.TextCtrl(panel, pos=(180, 70))

        wx.StaticText(panel, label="Quality (1-10):", pos=(30, 110))
        self.q = wx.TextCtrl(panel, pos=(180, 110))

        wx.StaticText(panel, label="Bedtime:", pos=(30, 150))
        self.bt = wx.TextCtrl(panel, pos=(180, 150))

        save_btn = wx.Button(panel, label="Save Sleep", pos=(130, 200))
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)

        if self.date in data and "sleep_tracker" in data[self.date]:
            e = data[self.date]["sleep_tracker"]
            self.h.SetValue(str(e.get("hours", "")))
            self.q.SetValue(str(e.get("quality", "")))
            self.bt.SetValue(str(e.get("bedtime", "")))

    def on_save(self, event):
        if self.date not in self.data:
            self.data[self.date] = {}

        self.data[self.date]["sleep_tracker"] = {
            "hours": self.h.GetValue(),
            "quality": self.q.GetValue(),
            "bedtime": self.bt.GetValue(),
        }

        save_data(self.data)
        wx.MessageBox("Sleep saved!", "Success")
        self.Close()

# ----------------------
# MAIN WINDOW
# ----------------------

class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Mindful Path Wellness Tracker", size=(520, 420))
        panel = wx.Panel(self)

        self.data = load_data()
        self.current_date = datetime.date.today()

        self.date_label = wx.StaticText(panel, label=str(self.current_date), pos=(225, 20))

        # Navigation buttons
        prev_btn = wx.Button(panel, label="<< Previous", pos=(50, 70))
        next_btn = wx.Button(panel, label="Next >>", pos=(350, 70))
        prev_btn.Bind(wx.EVT_BUTTON, self.go_previous)
        next_btn.Bind(wx.EVT_BUTTON, self.go_next)

        # Action buttons
        entry_btn = wx.Button(panel, label="Daily Entry", pos=(200, 120))
        entry_btn.Bind(wx.EVT_BUTTON, self.open_entry)

        report_btn = wx.Button(panel, label="Daily Report", pos=(200, 160))
        report_btn.Bind(wx.EVT_BUTTON, self.open_report)

        nutrition_btn = wx.Button(panel, label="Nutrition Tracker", pos=(190, 200))
        nutrition_btn.Bind(wx.EVT_BUTTON, self.open_nutrition)

        sleep_btn = wx.Button(panel, label="Sleep Tracker", pos=(200, 240))
        sleep_btn.Bind(wx.EVT_BUTTON, self.open_sleep)

        weekly_btn = wx.Button(panel, label="Weekly Summary", pos=(195, 280))
        weekly_btn.Bind(wx.EVT_BUTTON, self.open_weekly)

        monthly_btn = wx.Button(panel, label="Monthly Report", pos=(195, 320))
        monthly_btn.Bind(wx.EVT_BUTTON, self.open_monthly)

        goals_btn = wx.Button(panel, label="Set Goals", pos=(210, 360))
        goals_btn.Bind(wx.EVT_BUTTON, self.open_goals)

    # Navigation
    def go_previous(self, event):
        self.current_date -= datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

    def go_next(self, event):
        self.current_date += datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

    # Open windows
    def open_entry(self, event):
        DayEntryWindow(self, self.current_date, self.data).Show()

    def open_report(self, event):
        DailyReportWindow(self, self.current_date, self.data).Show()

    def open_nutrition(self, event):
        NutritionTrackerWindow(self, self.current_date, self.data).Show()

    def open_sleep(self, event):
        SleepTrackerWindow(self, self.current_date, self.data).Show()

    def open_weekly(self, event):
        WeeklySummaryWindow(self, self.data).Show()

    def open_monthly(self, event):
        MonthlyReportWindow(self, self.data).Show()

    def open_goals(self, event):
        GoalsWindow(self, self.data).Show()

# ----------------------
# Run Application
# ----------------------

if __name__ == "__main__":
    app = wx.App()
    win = MainWindow()
    win.Show()
    app.MainLoop()


