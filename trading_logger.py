"""Real-time trading logger for web display."""

from datetime import datetime
from collections import deque
import threading


class TradingLogger:
    """Thread-safe logger for real-time trading updates."""
    
    def __init__(self, max_logs=100):
        self.logs = deque(maxlen=max_logs)
        self.lock = threading.Lock()
        
    def log(self, message, level='info'):
        """Add a log entry."""
        with self.lock:
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_entry = {
                'timestamp': timestamp,
                'message': message,
                'level': level
            }
            self.logs.append(log_entry)
            try:
                print(f"[{timestamp}] {message}")
            except UnicodeEncodeError:
                # Handle unicode characters that can't be printed to console
                safe_message = message.encode('ascii', 'ignore').decode('ascii')
                print(f"[{timestamp}] {safe_message}")
    
    def info(self, message):
        """Log info message."""
        self.log(message, 'info')
    
    def success(self, message):
        """Log success message."""
        self.log(message, 'success')
    
    def warning(self, message):
        """Log warning message."""
        self.log(message, 'warning')
    
    def error(self, message):
        """Log error message."""
        self.log(message, 'error')
    
    def get_logs(self, count=50):
        """Get recent logs."""
        with self.lock:
            return list(self.logs)[-count:]
    
    def clear(self):
        """Clear all logs."""
        with self.lock:
            self.logs.clear()


# Global logger instance
trading_logger = TradingLogger()
