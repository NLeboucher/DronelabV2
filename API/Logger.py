from datetime import datetime
import os
class Logger:
    def __init__(self, filename):
        self.filename = filename
        print(f"Logger started. Logging to {os.path.dirname(os.path.abspath(__file__))}/{self.filename}")
        with open(self.filename, 'a+') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] [init] Started Logger\n"
            f.write(log_message)

    def log(self, level, message):
        with open(self.filename, 'a+') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] [{level}] {message}\n"
            f.write(log_message)
            #print(log_message, end='')

    def info(self, message):
        self.log("INFO", message)

    def warning(self, message):
        self.log("WARNING", message)

    def error(self, message):
        self.log("ERROR", message)
