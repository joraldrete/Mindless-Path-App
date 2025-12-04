import wx
import json
import os
import datetime

DATA_FILE = "wellness_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------
# Better UI Helper
# ----------------------

def title_text(parent, text):
    label = wx.StaticText(parent, label=text)
    font = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    label.SetFont(font)
    return label

def label(parent, text):
    lbl = wx.StaticText(parent, label=text)
    lbl.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MEDIUM))
    return lbl


# ----------------------
# DAILY ENTRY
# ----------------------

class DayEntryWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title=f"Daily Entry - {date}", size=(420, 380))
        panel = wx.Panel(self)
        self.date = str(date)
        self.data = data

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text(panel, f"Daily Wellness Entry ({self.date})"), 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        form = wx.FlexGridSizer(5, 2, 10, 10)
        self.exercise = wx.TextCtrl(panel)
        self.sleep = wx.TextCtrl(panel)
        self.water = wx.TextCtrl(panel)
        self.calories = wx.TextCtrl(panel)
        self.mood = wx.ComboBox(panel,
                                choices=["😀 Happy", "😐 Okay", "😞 Sad", "😡 Angry", "😴 Tired"],
                                style=wx.CB_READONLY)

        form.AddMany([
            (label(panel, "Exercise (min):"), 0), (self.exercise, 1, wx.EXPAND),
            (label(panel, "Sleep (hrs):"), 0), (self.sleep, 1, wx.EXPAND),
            (label(panel, "Water (cups):"), 0), (self.water, 1, wx.EXPAND),
            (label(panel, "Calories:"), 0), (self.calories, 1, wx.EXPAND),
            (label(panel, "Mood:"), 0), (self.mood, 1, wx.EXPAND),
        ])
        form.AddGrowableCol(1, 1)

        vbox.Add(form, 1, wx.ALL | wx.EXPAND, 15)

        btn = wx.Button(panel, label="Save Entry")
        btn.Bind(wx.EVT_BUTTON, self.on_save)
        vbox.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(vbox)

        if self.date in self.data:
            e = self.data[self.date]
            self.exercise.SetValue(str(e.get("exercise", "")))
            self.sleep.SetValue(str(e.get("sleep", "")))
            self.water.SetValue(str(e.get("water", "")))
            self.calories.SetValue(str(e.get("calories", "")))
            self.mood.SetValue(e.get("mood", ""))

    def on_save(self, event):
        self.data[self.date] = {
            "exercise": self.exercise.GetValue(),
            "sleep": self.sleep.GetValue(),
            "water": self.water.GetValue(),
            "calories": self.calories.GetValue(),
            "mood": self.mood.GetValue(),
        }
        save_data(self.data)
        wx.MessageBox("Daily entry saved!", "Success")
        self.Close()


# ----------------------
# DAILY REPORT
# ----------------------

class DailyReportWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title=f"Daily Report - {date}", size=(450, 450))
        panel = wx.Panel(self)
        date = str(date)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text(panel, f"Report for {date}"), 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        entry = data.get(date)
        if not entry:
            vbox.Add(label(panel, "No data for this date."), 0, wx.ALIGN_CENTER | wx.ALL, 20)
            panel.SetSizer(vbox)
            return

        grid = wx.FlexGridSizer(8, 2, 10, 10)

        def add(label_text, value):
            grid.Add(label(panel, label_text), 0)
            grid.Add(label(panel, str(value)), 0)

        add("Exercise (min):", entry.get("exercise", "-"))
        add("Sleep (hrs):", entry.get("sleep", "-"))
        add("Water (cups):", entry.get("water", "-"))
        add("Calories:", entry.get("calories", "-"))
        add("Mood:", entry.get("mood", "-"))

        vbox.Add(grid, 1, wx.ALL | wx.EXPAND, 20)
        panel.SetSizer(vbox)


# ----------------------
# WEEKLY SUMMARY
# ----------------------

class WeeklySummaryWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Weekly Summary", size=(450, 350))
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text(panel, "7-Day Wellness Summary"), 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        today = datetime.date.today()
        start = today - datetime.timedelta(days=7)
        entries = []

        for d, e in data.items():
            if d == "goals":
                continue
            try:
                dt = datetime.datetime.strptime(d, "%Y-%m-%d").date()
                if start <= dt <= today:
                    entries.append(e)
            except:
                pass

        if not entries:
            vbox.Add(label(panel, "No entries in the last 7 days."), 0, wx.ALIGN_CENTER | wx.ALL, 20)
            panel.SetSizer(vbox)
            return

        grid = wx.FlexGridSizer(6, 2, 10, 10)

        totals = {"exercise": 0, "sleep": 0, "water": 0, "calories": 0}
        moods = {}

        for e in entries:
            for k in totals:
                totals[k] += float(e.get(k, 0) or 0)
            m = e.get("mood")
            if m:
                moods[m] = moods.get(m, 0) + 1

        num = len(entries)

        def add(lbl, val):
            grid.Add(label(panel, lbl))
            grid.Add(label(panel, val))

        add("Days Logged:", num)
        add("Avg Exercise:", f"{totals['exercise']/num:.1f}")
        add("Avg Sleep:", f"{totals['sleep']/num:.1f}")
        add("Avg Water:", f"{totals['water']/num:.1f}")
        add("Avg Calories:", f"{totals['calories']/num:.1f}")
        add("Most Common Mood:", max(moods, key=moods.get))

        vbox.Add(grid, 1, wx.ALL | wx.EXPAND, 20)
        panel.SetSizer(vbox)


# ----------------------
# MONTHLY REPORT
# ----------------------

class MonthlyReportWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Monthly Report", size=(500, 420))
        panel = wx.Panel(self)

        today = datetime.date.today()
        month_start = today.replace(day=1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text(panel, f"Monthly Report - {today.strftime('%B %Y')}"),
                 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        entries = []
        for d, e in data.items():
            if d == "goals":
                continue
            try:
                dt = datetime.datetime.strptime(d, "%Y-%m-%d").date()
                if month_start <= dt <= today:
                    entries.append(e)
            except:
                pass

        if not entries:
            vbox.Add(label(panel, "No entries this month."), 0, wx.ALIGN_CENTER | wx.ALL, 20)
            panel.SetSizer(vbox)
            return

        grid = wx.FlexGridSizer(6, 2, 10, 10)
        totals = {"exercise": 0, "sleep": 0, "water": 0, "calories": 0}
        moods = {}

        for e in entries:
            for k in totals:
                totals[k] += float(e.get(k, 0) or 0)
            m = e.get("mood")
            if m:
                moods[m] = moods.get(m, 0) + 1

        num = len(entries)

        def add(lbl, val):
            grid.Add(label(panel, lbl))
            grid.Add(label(panel, val))

        add("Days Logged:", num)
        add("Avg Exercise:", f"{totals['exercise']/num:.1f}")
        add("Avg Sleep:", f"{totals['sleep']/num:.1f}")
        add("Avg Water:", f"{totals['water']/num:.1f}")
        add("Avg Calories:", f"{totals['calories']/num:.1f}")
        add("Most Common Mood:", max(moods, key=moods.get))

        vbox.Add(grid, 1, wx.ALL | wx.EXPAND, 20)
        panel.SetSizer(vbox)


# ----------------------
# GOALS WINDOW
# ----------------------

class GoalsWindow(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Set Goals", size=(420, 350))
        panel = wx.Panel(self)
        self.data = data

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text(panel, "Daily Goals"), 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        form = wx.FlexGridSizer(4, 2, 10, 10)
        self.e = wx.TextCtrl(panel)
        self.s = wx.TextCtrl(panel)
        self.w = wx.TextCtrl(panel)
        self.c = wx.TextCtrl(panel)

        form.AddMany([
            (label(panel, "Exercise (min):"), 0), (self.e, 1, wx.EXPAND),
            (label(panel, "Sleep (hrs):"), 0), (self.s, 1, wx.EXPAND),
            (label(panel, "Water (cups):"), 0), (self.w, 1, wx.EXPAND),
            (label(panel, "Calories:"), 0), (self.c, 1, wx.EXPAND),
        ])
        form.AddGrowableCol(1, 1)

        vbox.Add(form, 1, wx.ALL | wx.EXPAND, 20)

        btn = wx.Button(panel, label="Save Goals")
        btn.Bind(wx.EVT_BUTTON, self.on_save)
        vbox.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        panel.SetSizer(vbox)

        g = data.get("goals", {})
        self.e.SetValue(str(g.get("exercise_goal", "")))
        self.s.SetValue(str(g.get("sleep_goal", "")))
        self.w.SetValue(str(g.get("water_goal", "")))
        self.c.SetValue(str(g.get("calories_goal", "")))

    def on_save(self, event):
        self.data["goals"] = {
            "exercise_goal": self.e.GetValue(),
            "sleep_goal": self.s.GetValue(),
            "water_goal": self.w.GetValue(),
            "calories_goal": self.c.GetValue(),
        }
        save_data(self.data)
        wx.MessageBox("Goals saved!", "Success")
        self.Close()


# ----------------------
# NUTRITION TRACKER
# ----------------------

class NutritionTrackerWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title="Nutrition Tracker", size=(420, 380))
        panel = wx.Panel(self)
        self.date = str(date)
        self.data = data

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text(panel, "Nutrition Tracker"), 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        form = wx.FlexGridSizer(4, 2, 10, 10)
        self.b = wx.TextCtrl(panel)
        self.l = wx.TextCtrl(panel)
        self.d = wx.TextCtrl(panel)
        self.s = wx.TextCtrl(panel)

        form.AddMany([
            (label(panel, "Breakfast (cal):"), 0), (self.b, 1, wx.EXPAND),
            (label(panel, "Lunch (cal):"), 0), (self.l, 1, wx.EXPAND),
            (label(panel, "Dinner (cal):"), 0), (self.d, 1, wx.EXPAND),
            (label(panel, "Snacks (cal):"), 0), (self.s, 1, wx.EXPAND),
        ])
        form.AddGrowableCol(1, 1)

        vbox.Add(form, 1, wx.ALL | wx.EXPAND, 20)

        btn = wx.Button(panel, label="Save Nutrition")
        btn.Bind(wx.EVT_BUTTON, self.on_save)
        vbox.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        panel.SetSizer(vbox)

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
# SLEEP TRACKER
# ----------------------

class SleepTrackerWindow(wx.Frame):
    def __init__(self, parent, date, data):
        super().__init__(parent, title="Sleep Tracker", size=(420, 330))
        panel = wx.Panel(self)
        self.date = str(date)
        self.data = data

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text(panel, "Sleep Tracker"), 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        form = wx.FlexGridSizer(3, 2, 10, 10)
        self.h = wx.TextCtrl(panel)
        self.q = wx.TextCtrl(panel)
        self.bt = wx.TextCtrl(panel)

        form.AddMany([
            (label(panel, "Hours:"), 0), (self.h, 1, wx.EXPAND),
            (label(panel, "Quality (1-10):"), 0), (self.q, 1, wx.EXPAND),
            (label(panel, "Bedtime:"), 0), (self.bt, 1, wx.EXPAND),
        ])
        form.AddGrowableCol(1, 1)

        vbox.Add(form, 1, wx.ALL | wx.EXPAND, 20)

        btn = wx.Button(panel, label="Save Sleep")
        btn.Bind(wx.EVT_BUTTON, self.on_save)
        vbox.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        panel.SetSizer(vbox)

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
        super().__init__(None, title="Mindful Path Wellness Tracker", size=(550, 500))
        panel = wx.Panel(self)

        self.data = load_data()
        self.current_date = datetime.date.today()

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text(panel, "Mindful Path Wellness Tracker"),
                 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        date_box = wx.BoxSizer(wx.HORIZONTAL)
        date_box.Add(wx.Button(panel, label="◀ Previous"), 0)
        date_box.AddSpacer(10)
        self.date_label = label(panel, str(self.current_date))
        date_box.Add(self.date_label, 0)
        date_box.AddSpacer(10)
        date_box.Add(wx.Button(panel, label="Next ▶"), 0)

        vbox.Add(date_box, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        # Buttons grid
        grid = wx.GridSizer(4, 2, 15, 15)

        def btn(text, handler):
            b = wx.Button(panel, label=text)
            b.Bind(wx.EVT_BUTTON, handler)
            return b

        grid.Add(btn("Daily Entry", self.open_entry))
        grid.Add(btn("Daily Report", self.open_report))
        grid.Add(btn("Nutrition Tracker", self.open_nutrition))
        grid.Add(btn("Sleep Tracker", self.open_sleep))
        grid.Add(btn("Weekly Summary", self.open_weekly))
        grid.Add(btn("Monthly Report", self.open_monthly))
        grid.Add(btn("Set Goals", self.open_goals))

        vbox.Add(grid, 1, wx.ALL | wx.EXPAND, 20)

        panel.SetSizer(vbox)

        # Navigation Bindings
        panel.Bind(wx.EVT_BUTTON, self.go_previous, date_box.GetChildren()[0].GetWindow())
        panel.Bind(wx.EVT_BUTTON, self.go_next, date_box.GetChildren()[3].GetWindow())

    def go_previous(self, event):
        self.current_date -= datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

    def go_next(self, event):
        self.current_date += datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

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


if __name__ == "__main__":
    app = wx.App()
    win = MainWindow()
    win.Show()
    app.MainLoop()

