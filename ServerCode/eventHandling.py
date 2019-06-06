import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class EventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print event


if __name__ == "__main__":

    path = os.path.abspath("Resources")
    print path
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
