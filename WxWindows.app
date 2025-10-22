import wx
import datetime
import json
import os

DATA_FILE = "wellness_data.json"

class DayWindow(wx.Frame):
    """A blank pop-up window for now."""
    def __init__(self, parent):
        super().__init__(parent, title="Day Details", size=(300, 200))
        panel = wx.Panel(self)
        wx.StaticText(panel, label="(Future: Daily Data Entry Screen)", pos=(40, 70))


class MainWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Wellness Tracker", size=(400, 200))
        self.panel = wx.Panel(self)

        # Load data
        self.data = self.load_data()

        # Current date
        self.current_date = datetime.date.today()

        # UI Elements
        self.date_label = wx.StaticText(self.panel, label=str(self.current_date), pos=(160, 20))

        prev_btn = wx.Button(self.panel, label="<< Previous", pos=(50, 60))
        next_btn = wx.Button(self.panel, label="Next >>", pos=(230, 60))
        open_window_btn = wx.Button(self.panel, label="Open Day Window", pos=(120, 110))

        # Bind events
        prev_btn.Bind(wx.EVT_BUTTON, self.on_prev_day)
        next_btn.Bind(wx.EVT_BUTTON, self.on_next_day)
        open_window_btn.Bind(wx.EVT_BUTTON, self.on_open_window)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.Show()

    def on_prev_day(self, event):
        self.current_date -= datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

    def on_next_day(self, event):
        self.current_date += datetime.timedelta(days=1)
        self.date_label.SetLabel(str(self.current_date))

    def on_open_window(self, event):
        window = DayWindow(self)
        window.Show()

    def load_data(self):
        """Load data from JSON if exists, otherwise return empty structure."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {"days": []}

    def on_close(self, event):
        """Save data before closing."""
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        MainWindow()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
