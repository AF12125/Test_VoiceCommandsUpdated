import os
import sys
import time
import playsound
from gtts import gTTS
import datetime
import os.path
import sched
from datetime import datetime, timedelta
from plyer import notification
import speech_recognition as sr


class EventScheduler:
    def __init__(self):
        self.events = []
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def add_event(self, name, date, time):
        self.events.append({'name': name, 'date': date, 'time': time})
        print(f"Event '{name}' added on {date} at {time}")
        # Schedule reminders for the added event
        event_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        self.set_reminders(name, event_datetime)

    def edit_event(self, index, name, date, time):
        if 0 <= index < len(self.events):
            self.events[index] = {'name': name, 'date': date, 'time': time}
            print(f"Event at index {index} edited: '{name}' on {date} at {time}")
            # Reschedule reminders for the edited event
            event_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            self.set_reminders(name, event_datetime)
        else:
            print("Invalid index")

    def view_events(self):
        if self.events:
            print("Events:")
            for i, event in enumerate(self.events):
                print(f"{i}: {event['name']} on {event['date']} at {event['time']}")
        else:
            print("No events")

    def delete_event(self, index):
        if 0 <= index < len(self.events):
            deleted_event = self.events.pop(index)
            print(
                f"Event at index {index} deleted: '{deleted_event['name']}' on {deleted_event['date']} at {deleted_event['time']}")
        else:
            print("Invalid index")

    def set_reminders(self, event_name, event_datetime):
        """ Set multiple reminders for an event. """
        reminders = [15, 60, 120]  # Reminders in minutes before the event
        for reminder_delta in reminders:
            reminder_time = event_datetime - timedelta(minutes=reminder_delta)
            self.schedule_notification(f"Reminder for {event_name}", reminder_time)

    def schedule_notification(self, event_name, event_time):
        """ Schedule a notification for the event. """
        self.scheduler.enterabs(event_time.timestamp(), 1, self.notify, argument=(event_name,))
        self.scheduler.run()

    def notify(self, event_name):
        """ Send a desktop notification about the event. """
        notification.notify(
            title='Event Reminder',
            message=f'Remember your event: {event_name}',
            app_icon=None,  # Path to an .ico file can be added here
            timeout=10,  # Notification duration in seconds
        )


def speak(text):
    tts = gTTS(text=text, lang="en")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)  # Remove the temporary audio file after playing


def manual_input(prompt):
    return input(prompt)


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except Exception as e:
        print("Exception:", str(e))
        return ""


def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_time(time_str):
    try:
        time.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def main():
    scheduler = EventScheduler()

    while True:
        print("1. Add Event")
        print("2. Edit Event")
        print("3. View Events")
        print("4. Delete Event")
        print("5. Voice Command")
        print("6. Stop")

        choice = manual_input("Select an option: ")

        if choice == "1":
            try:
                event_name = manual_input("Enter event name: ")
                event_date = manual_input("Enter event date (YYYY-MM-DD): ")
                event_time = manual_input("Enter event time (HH:MM): ")
                scheduler.add_event(event_name, event_date, event_time)
                print("Event added successfully")

            except ValueError:
                print("Invalid input. Please enter valid data.")

        elif choice == "2":
            if scheduler.events:
                scheduler.view_events()
                try:
                    index = int(manual_input("Enter the index of the event you want to edit: "))
                    new_name = manual_input("Enter the new name of the event: ")
                    new_date = manual_input("Enter the new date of the event (YYYY-MM-DD): ")
                    new_time = manual_input("Enter the new time of the event (HH:MM): ")
                    scheduler.edit_event(index, new_name, new_date, new_time)
                except ValueError:
                    print("Invalid input. Please enter valid data.")
            else:
                print("No events to edit.")
        elif choice == "3":
            scheduler.view_events()
        elif choice == "4":
            if scheduler.events:
                scheduler.view_events()
                try:
                    index = int(manual_input("Enter the index of the event you want to delete: "))
                    scheduler.delete_event(index)
                except ValueError:
                    print("Invalid index. Please enter a valid index.")
            else:
                print("No events to delete.")
        elif choice == "5":
            command = get_audio()
            if "add event" in command:
                speak("What's the name of the event?")
                event_name = get_audio()
                speak("On which date? Please say the date in year-month-day format.")
                event_date = get_audio()
                if validate_date(event_date):
                    speak("At what time? Please say the time in hour and minute format.")
                    event_time = get_audio()
                    if validate_time(event_time):
                        scheduler.add_event(event_name, event_date, event_time)
                        speak("Event added successfully.")
                    else:
                        speak("Invalid time format. Please try again.")
                else:
                    speak("Invalid date format. Please try again.")
            elif "edit event" in command:
                # Implement edit event functionality
                speak("Edit event implementation is not included in this version of VoiceCommands, we are sorry.")
                pass
            elif "view events" in command:
                scheduler.view_events()
            elif "delete event" in command:
                if scheduler.events:
                    speak("Here are the current events.")
                    scheduler.view_events()  # This will list events with indexes
                    speak("Please say the index of the event you want to delete.")
                    index_command = get_audio()  # Expecting a spoken number
                    try:
                        index = int(index_command)
                        if 0 <= index < len(scheduler.events):
                            speak(
                                f"Do you really want to delete the event: {scheduler.events[index]['name']}? Say yes to confirm.")
                            confirmation = get_audio()
                            if 'yes' in confirmation:
                                scheduler.delete_event(index)
                                speak("Event deleted successfully.")
                            else:
                                speak("Deletion cancelled.")
                        else:
                            speak("Invalid index. Please try again.")
                    except ValueError:
                        speak("I did not understand the index. Please try again.")
                else:
                    speak("There are no events to delete.")
            elif "stop" in command:
                break
        elif choice == "6":
            sys.exit()


if __name__ == '__main__':
    main()
