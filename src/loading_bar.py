import threading
import time
from colored_print import print_debug


class LoadingBar:
    def __init__(self, message="Processing", total=100):
        self.spinner_chars = ["|", "/", "-", "\\"]
        self.message = message
        self.spinning = False
        self.spinner_thread = None
        self.total = total
        self.current = 0
        self.lock = threading.Lock()

    def start(self):
        self.spinning = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.start()

    def stop(self):
        self.spinning = False
        if self.spinner_thread:
            self.spinner_thread.join()
        print("\r" + " " * 80, end="\r")  # Clear the line

    def update(self, progress=None):
        with self.lock:
            if progress is not None:
                self.current = progress
            else:
                self.current += 1

    def _create_progress_bar(self, bar_length=20):
        if self.total == 0:
            return "[-" + " " * (bar_length - 2) + "]"

        percent = min(self.current / self.total, 1.0)
        filled = int(bar_length * percent)
        bar = "█" * filled + "-" * (bar_length - filled)
        return f"[{bar}] {self.current}/{self.total} ({percent:.1%})"

    def _spin(self):
        i = 0
        while self.spinning:
            with self.lock:
                spinner_char = self.spinner_chars[i % len(self.spinner_chars)]
                progress_bar = self._create_progress_bar()
                display = f"\r{spinner_char} {self.message} {progress_bar}"

            print_debug(display, end="", flush=True)
            i += 1
            time.sleep(0.1)
