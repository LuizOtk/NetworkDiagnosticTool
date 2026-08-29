import logging
import sys
import traceback

from logging.handlers import RotatingFileHandler
from pathlib import Path


def obter_diretorio_aplicacao():
    if getattr(
        sys,
        "frozen",
        False
    ):
        return (
            Path(sys.executable)
            .resolve()
            .parent
        )

    return (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )


DIRETORIO_LOGS = (
    obter_diretorio_aplicacao()
    / "logs"
)

ARQUIVO_APP = (
    DIRETORIO_LOGS
    / "app.log"
)

ARQUIVO_ERROS = (
    DIRETORIO_LOGS
    / "errors.log"
)


def configurar_logs():
    DIRETORIO_LOGS.mkdir(
        parents=True,
        exist_ok=True
    )

    logger = logging.getLogger(
        "NetworkDiagnosticTool"
    )

    logger.setLevel(
        logging.DEBUG
    )

    if logger.handlers:
        return logger

    formato = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(threadName)s | "
        "%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    arquivo_app = RotatingFileHandler(
        ARQUIVO_APP,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8"
    )

    arquivo_app.setLevel(
        logging.INFO
    )

    arquivo_app.setFormatter(
        formato
    )

    arquivo_erros = RotatingFileHandler(
        ARQUIVO_ERROS,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8"
    )

    arquivo_erros.setLevel(
        logging.ERROR
    )

    arquivo_erros.setFormatter(
        formato
    )

    logger.addHandler(
        arquivo_app
    )

    logger.addHandler(
        arquivo_erros
    )

    return logger


logger = configurar_logs()


def capturar_excecao(
    tipo_excecao,
    valor_excecao,
    traceback_excecao
):
    if issubclass(
        tipo_excecao,
        KeyboardInterrupt
    ):
        sys.__excepthook__(
            tipo_excecao,
            valor_excecao,
            traceback_excecao
        )
        return

    detalhes = "".join(
        traceback.format_exception(
            tipo_excecao,
            valor_excecao,
            traceback_excecao
        )
    )

    logger.critical(
        "Exceção não tratada:\n%s",
        detalhes
    )


def instalar_captura_global():
    sys.excepthook = capturar_excecao
