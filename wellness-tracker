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
# Main Window
# ----------------------

class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Mindful Path Wellness Tracker", size=(400, 250))
        panel = wx.Panel(self)

        self.data = load_data()
        self.current_date = datetime.date.today()

        self.date_label = wx.StaticText(panel, label=str(self.current_date), pos=(160, 30))

        prev_btn = wx.Button(panel, label="<< Previous", pos=(50, 70))
        next_btn = wx.Button(panel, label="Next >>", pos=(230, 70))
        open_day_btn = wx.Button(panel, label="Open Daily Entry", pos=(130, 130))

        prev_btn.Bind(wx.EVT_BUTTON, self.on_prev_day)
        next_btn.Bind(wx.EVT_BUTTON, self.on_next_day)
        open_day_btn.Bind(wx.EVT_BUTTON, self.on_open_day)

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
