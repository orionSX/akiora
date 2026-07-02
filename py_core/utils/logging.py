import logging
import os
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Настраивает логгер для всего приложения в зависимости от окружения.
    """
    # Удаляем стандартный обработчик, чтобы избежать дублирования
    logger.remove()

    # Определяем формат для консоли (разработка)
    dev_format = (
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )

    # Определяем формат для файла (продакшен)
    prod_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function} | {message}"
    env = os.getenv("ENV_TYPE")
    app_name = os.getenv("APP_NAME")
    if not app_name:
        app_name = "UNKNOWN_APP"
    if not env:
        env = "prod"
    if env.lower() == "dev":
        logger.add(sys.stderr, level="DEBUG", format=dev_format, colorize=True)
        logger.info("Режим разработки: логирование настроено для вывода в консоль.")

    else:
        logger.add(sys.stderr, level="INFO", format=prod_format, colorize=False)

        # В файл пишем все, начиная с DEBUG, в формате JSON для машинного анализа
        logger.add(
            f"logs/{app_name}.log",
            level="DEBUG",
            rotation="10 MB",
            retention="1 month",
            serialize=True,  # Структурированное логирование в JSON
        )
        logger.info(
            "Режим продакшена: логирование настроено для вывода в консоль и файл."
        )
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logger.info("Стандартный logging перехвачен и направлен в Loguru.")
