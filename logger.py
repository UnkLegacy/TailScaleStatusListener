import os
from datetime import datetime

class Logger:
    """Handles logging with rotation"""

    def __init__(self, log_file: str = "monitor.log", max_size: int = 10 * 10 * 1024, max_files: int = 9):
        self.log_file = log_file
        self.max_size = max_size
        self.max_files = max_files

    def _rotate_logs(self):
        """Rotate log files when they exceed max size"""
        if not (os.path.exists(self.log_file) and os.path.getsize(self.log_file) > self.max_size):
            return

        # Remove oldest log file
        oldest = f"monitor_{self.max_files}.log"
        if os.path.exists(oldest):
            os.remove(oldest)

        # Shift all log files
        for i in range(self.max_files - 1, 0, -1):
            src = f"monitor_{i}.log"
            dst = f"monitor_{i + 1}.log"
            if os.path.exists(src):
                os.rename(src, dst)

        # Move current log to first backup
        os.rename(self.log_file, "monitor_1.log")

    def log(self, message: str):
        """Log a message with timestamp"""
        self._rotate_logs()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)

        with open(self.log_file, "a") as f:
            f.write(line + "\n")