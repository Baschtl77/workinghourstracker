import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtCore import QRegExp, QTimer, pyqtSignal

import os
from pathlib import Path

CONFIG_FILE = "timetracker_config.json"

def resource_path(relative_path):
    """ Holt den absoluten Pfad für Ressourcen, unabhängig davon, ob das Skript gepackt ist. """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)
    
class TimeTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_config()
        self.adjust_window_size()  # Fenstergröße anpassen

    def init_ui(self):
        self.main_layout = QVBoxLayout()

        # Timer list
        self.timer_list = QListWidget()
        self.main_layout.addWidget(self.timer_list)

        # Buttons
        self.add_timer_button = QPushButton("Add New Timer")
        self.add_timer_button.clicked.connect(self.add_timer)
        self.main_layout.addWidget(self.add_timer_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_config)
        self.main_layout.addWidget(self.save_button)

        self.reset_all_button = QPushButton("Reset all timers")
        self.reset_all_button.clicked.connect(self.reset_all_timers)
        self.main_layout.addWidget(self.reset_all_button)

        self.setLayout(self.main_layout)
        self.setWindowTitle("Working Hours Tracker")

    def add_timer(self, name="New Timer", hours="00", minutes="00", seconds="00", running=False):
        """Adds a new timer with the specified values."""

        if not name:
            name =""


        timer_item = TimerItem(str(name), str(hours), str(minutes), str(seconds), running)
        timer_item.timer_started.connect(self.stop_all_other_timers)  # Signal verbinden
        timer_item.timer_removed.connect(lambda: self.remove_timer_from_list(timer_item))  # Signal verbinden
        list_item = QListWidgetItem()
        list_item.setSizeHint(timer_item.sizeHint())

        self.timer_list.addItem(list_item)
        self.timer_list.setItemWidget(list_item, timer_item)
    def remove_timer_from_list(self, timer_item):
        """Removes the timer from the list."""
        for i in range(self.timer_list.count()):
            item = self.timer_list.item(i)
            widget = self.timer_list.itemWidget(item)
            if widget == timer_item:
                self.timer_list.takeItem(i)
                break
    def stop_all_other_timers(self, active_timer):
        """Stops all timers except the one that was just started."""
        for i in range(self.timer_list.count()):
            item = self.timer_list.item(i)
            widget = self.timer_list.itemWidget(item)
            if widget != active_timer and widget.running:
                widget.toggle_timer()  # Timer stoppen

    def reset_all_timers(self):
        """Resets all timers"""
        reply = QMessageBox.question(self, "Confirm reset all timers", "Really want to reset all the Timers?",
                                     QMessageBox.Yes | QMessageBox.Abort, QMessageBox.Abort)
        
        if reply == QMessageBox.Yes:
            for i in range(self.timer_list.count()):
                item = self.timer_list.item(i)
                widget = self.timer_list.itemWidget(item)
                widget.reset_timer() # Timer resetten

    def save_config(self):
        """Saves the current timer configuration to a JSON file."""
        config = []
        for i in range(self.timer_list.count()):
            item = self.timer_list.item(i)
            widget = self.timer_list.itemWidget(item)
            config.append(widget.get_timer_data())

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print("Configuration saved.")
        self.show_confirmation_popup("Configuration saved.")

    def load_config(self):
        """Loads the timer configuration from a JSON file."""
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                for timer in config:
                    self.add_timer(
                        name=str(timer.get("name", "New Timer")),
                        hours=str(timer.get("hours", "00")),
                        minutes=str(timer.get("minutes", "00")),
                        seconds=str(timer.get("seconds", "00")),
                        running=timer.get("running", False)
                    )
            print("Configuration loaded.")
        except FileNotFoundError:
            print("No saved configuration found.")

    def closeEvent(self, event):
        """Automatically saves configuration when closing."""
        self.save_config()
        event.accept()
    
    def adjust_window_size(self):
        """Adjust the window size to fit all timers."""
        base_height = 200  # Höhe für Header und Buttons
        timer_height = 80  # Höhe eines einzelnen Timer-Items
        maxtimercount = 10
        timercount = maxtimercount
        if timercount > self.timer_list.count():
            timercount = self.timer_list.count()
        total_height = base_height + timercount * timer_height

        # Begrenzungen für das Fenster
        max_height = 800
        min_height = 400
        adjusted_height = max(min(total_height, max_height), min_height)

        self.resize(870, adjusted_height)
    
    def show_confirmation_popup(self, message="Speichern erfolgreich!"):
        # Erstellt eine Nachricht mit einem OK-Button
        popup = QMessageBox()
        popup.setIcon(QMessageBox.Information)
        popup.setWindowTitle("Bestätigung")
        popup.setText(message)
        popup.setStandardButtons(QMessageBox.Ok)

        # QTimer einrichten, um das Popup nach 1 Sekunden zu schließen
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(popup.accept)  # Schließt das Popup
        timer.start(1000)  # 1000 Millisekunden = 1 Sekunden

        # Zeigt das Popup an und wartet auf Nutzerinteraktion oder Timeout
        popup.exec_()

class TimerItem(QWidget):
    timer_started = pyqtSignal(object)  # Signal, das bei Timer-Start gesendet wird
    timer_removed = pyqtSignal()  # Signal für das Entfernen des Timers
    def __init__(self, name="New Timer", hours="00", minutes="00", seconds="00", running=False):
        super().__init__()
        self.init_ui(name, hours, minutes, seconds, running)

    def init_ui(self, name, hours, minutes, seconds, running):
        layout = QHBoxLayout()

        self.name_input = QLineEdit(name)
        self.name_input.setFixedSize(180, 25)  # Optional: Größe anpassen

        # Input fields for hours, minutes, seconds
        self.hours_input = QLineEdit(hours)
        self.hours_input.setFixedSize(40, 25)
        self.minutes_input = QLineEdit(minutes)
        self.minutes_input.setFixedSize(40, 25)
        self.seconds_input = QLineEdit(seconds)
        self.seconds_input.setFixedSize(40, 25)

        # Validator for input fields (max 3 characters)
        time_validator = QRegExpValidator(QRegExp(r"^\d{1,3}$"))
        self.hours_input.setValidator(time_validator)
        self.minutes_input.setValidator(time_validator)
        self.seconds_input.setValidator(time_validator)

        # Start/Stop button with icons
        self.start_stop_button = QPushButton()

        self.start_icon = QIcon(resource_path("images/start_icon.png"))
        self.stop_icon = QIcon(resource_path("images/stop_icon.png"))

        self.start_stop_button.setIcon(self.start_icon if not running else self.stop_icon)
        self.start_stop_button.setFixedSize(60, 60)  # Button-Größe setzen
        self.start_stop_button.setIconSize(self.start_stop_button.size())  # Icon auf Button-Größe skalieren
        self.start_stop_button.clicked.connect(self.toggle_timer)

        # Remove button
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_timer)

        # Reset Button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer_click)

        # Timer logic
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.running = running
        if running:
            self.timer.start(1000)

        # Assemble layout
        layout.addWidget(self.start_stop_button)
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Time (hh,mm,ss):"))
        layout.addWidget(self.hours_input)
        layout.addWidget(self.minutes_input)
        layout.addWidget(self.seconds_input)
        
        layout.addWidget(self.remove_button)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def toggle_timer(self):
        """Starts or stops the timer."""
        if self.running:
            self.timer.stop()
            self.start_stop_button.setIcon(self.start_icon)
        else:
            self.timer_started.emit(self)  # Signal an Hauptanwendung senden
            self.timer.start(1000)
            self.start_stop_button.setIcon(self.stop_icon)
        self.running = not self.running

    def update_time(self):
        """Updates the time based on input fields."""
        if (len(self.hours_input.text()) > 0 and len(self.minutes_input.text()) > 0 and len(self.seconds_input.text()) > 0):
            hours = int(self.hours_input.text())
            minutes = int(self.minutes_input.text())
            seconds = int(self.seconds_input.text())

            # Increment time
            seconds += 1
            if seconds >= 60:
                seconds = 0
                minutes += 1
            if minutes >= 60:
                minutes = 0
                hours += 1

            # Display updated time
            self.hours_input.setText(f"{hours:02}")
            self.minutes_input.setText(f"{minutes:02}")
            self.seconds_input.setText(f"{seconds:02}")

    def remove_timer(self):
        """Displays a confirmation popup before removing the timer."""
        reply = QMessageBox.question(self, "Confirm Deletion", "Really want to delete the Timer?",
                                     QMessageBox.Yes | QMessageBox.Abort, QMessageBox.Abort)
        
        if reply == QMessageBox.Yes:
            self.timer_removed.emit()  # Signal an die Hauptanwendung senden, um den Timer zu entfernen

    
    def reset_timer_click(self):
        """Reset the timer to 00:00:00"""
        reply = QMessageBox.question(self, "Confirm Reset", "Really want to reset the Timer?",
                                     QMessageBox.Yes | QMessageBox.Abort, QMessageBox.Abort)
        if reply == QMessageBox.Yes:
            self.reset_timer()
    
    def reset_timer(self):
            print("Resetting timer")
            hours = 0
            minutes = 0
            seconds = 0

            # Display updated time
            self.hours_input.setText(f"{hours:02}")
            self.minutes_input.setText(f"{minutes:02}")
            self.seconds_input.setText(f"{seconds:02}")

    def get_timer_data(self):
        """Returns the current timer data."""
        return {
            "name": self.name_input.text(),
            "hours": self.hours_input.text(),
            "minutes": self.minutes_input.text(),
            "seconds": self.seconds_input.text(),
            "running": self.running
        }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tracker = TimeTrackerApp()
    tracker.show()
    sys.exit(app.exec_())
