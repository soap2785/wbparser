from services.logger import Logger


class BaseMethods:
    __error_logger = Logger("error")
    __info_logger = Logger()

    @classmethod
    def TraceError(cls, parser: str) -> None:
        return cls.__error_logger.error_with_trace(parser)

    @classmethod
    def Error(cls, msg: str) -> None:
        return cls.__error_logger.error(msg)

    @classmethod
    def Info(cls, parser: str, count: int) -> None:
        return cls.__info_logger.info(parser.upper(), count)
