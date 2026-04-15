from datetime import datetime
from random import randint
from os import makedirs
from sys import exc_info
from traceback import extract_tb, format_exception_only, format_exc
from logging import ERROR, DEBUG, FileHandler, Formatter, Logger as Logger_


class Logger(Logger_):
    formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def __init__(self, type: str = "info") -> None:
        makedirs("logs", exist_ok=True)
        if type == "info":
            super().__init__("info_logger" + str(randint(10000, 99999)))
            self.setLevel(DEBUG)
            handler = FileHandler("logs/docreport.log")
        elif type == "error":
            super().__init__("error_logger" + str(randint(10000, 99999)))
            self.setLevel(ERROR)
            handler = FileHandler("logs/docreport.err.log")
        else:
            raise ValueError("Logger type must be either 'info' or 'error'")
        handler.setFormatter(self.formatter)
        self.addHandler(handler)

    def info(self, parser: str, count: int, *args, **kwargs) -> None:
        message = {
            (False, 1): f"{parser} parsing started",
            (False, 2): f"{parser} parsed successfully",
            (True, 1): "COMPILING started",
            (True, 2): "COMPILED successfully",
        }
        msg = message.get((parser == "COMPILER", count))
        if msg:
            return super().info(f"[{datetime.now():%H:%M:%S}] {msg}", *args, **kwargs)
        return super().info(f"[{datetime.now():%H:%M:%S}] {parser} {count}", *args, **kwargs)

    def error_with_trace(self, parser: str, *args, **kwargs) -> None:
        """Метод для логирования исключений с номером строки в начале."""
        exc_type, exc_value, exc_tb = exc_info()
        if exc_tb:
            last_frame = extract_tb(exc_tb)[-1]
            line_no = last_frame.lineno
            error_text = "".join(format_exception_only(exc_type, exc_value)).strip()
            full_msg = f"{parser.upper()} [Line: {line_no}] -- {error_text}\n{format_exc()}"
            return super().error(full_msg, *args, **kwargs)
        else:
            return super().error(f"{parser.upper()} -- No traceback available", *args, **kwargs)
