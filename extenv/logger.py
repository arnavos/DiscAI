import logging
import sys
import pathlib
import os
import inspect
from typing import Optional
from colorama import init, Style, Fore


def get_caller_filename():
    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0])
    try:
        file = pathlib.Path(module.__file__)
        filename = f"{os.path.basename(file)}"
    except Exception as exe:
        print(f"Error retrieving caller filename: {type(exe).__name__} - {exe}")
        filename = "Global"
    return filename


class MainLogger:
    def __init__(
            self,
            name="Logger",
            level=logging.INFO,
            debug_mode: Optional[bool] = False,
            suppress_warnings: Optional[bool] = False,
            suppress_information: Optional[bool] = False,
            suppress_critical: Optional[bool] = False,
            suppress_errors: Optional[bool] = False

    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.suppress_errors = suppress_errors
        self.suppress_critical = suppress_critical
        self.suppress_warnings = suppress_warnings
        self.suppress_information = suppress_information

        if debug_mode:
            self.suppress_information = True
            self.suppress_warnings = True
            self.suppress_critical = True
            self.suppress_errors = True

        init(autoreset=True)

        # Create a console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Define custom log format with colors
        log_format = f"%(caller_filename)s @ {Fore.CYAN}{Style.BRIGHT}%(asctime)s{Style.RESET_ALL} - %(message)s"
        color_format = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(color_format)
        self.logger.addHandler(console_handler)

    def info(self, message):
        if not self.suppress_information:
            self.logger.info(
                f"{Fore.GREEN}{Style.BRIGHT}{message}{Style.RESET_ALL}",
                extra={"caller_filename": get_caller_filename()},
            )

    def warning(self, message):
        if not self.suppress_warnings:
            self.logger.warning(
                f"{Fore.YELLOW}{Style.BRIGHT}{message}{Style.RESET_ALL}",
                extra={"caller_filename": get_caller_filename()},
            )

    def error(self, message):
        if not self.suppress_errors:
            self.logger.error(
                f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}",
                extra={"caller_filename": get_caller_filename()},
            )

    def critical(self, message):
        if not self.suppress_critical:
            self.logger.critical(
                f"{Fore.MAGENTA}{Style.BRIGHT}{message}{Style.RESET_ALL}",
                extra={"caller_filename": get_caller_filename()},
            )
