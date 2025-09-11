import logging

COLORS = {
    "DEBUG": "\033[94m",
    "INFO": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[95m",
    "RESET": "\033[0m",
}


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        original_level = record.levelname
        padded_level = f"{original_level:<7}"
        if original_level in COLORS:
            record.levelname = f"{COLORS[original_level]}{padded_level}{COLORS['RESET']}"
        else:
            record.levelname = padded_level
        asctime = self.formatTime(record, "%Y-%m-%d %H:%M").rjust(12).rjust(18)
        message = record.getMessage()
        return f"{record.levelname:<8} {asctime} - {record.name} - {message}"