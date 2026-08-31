import queue
import threading
import time
import winsound

from pathlib import Path

from services.logger import logger


_fila_audio = queue.Queue()
_worker_audio = None
_worker_lock = threading.Lock()


def _tocar_padrao_ndt():
    winsound.Beep(
        1100,
        220
    )

    time.sleep(
        0.08
    )

    winsound.Beep(
        850,
        320
    )


def _reproduzir_alerta(
    modo,
    arquivo
):
    try:
        if modo == "personalizado":
            caminho = Path(
                arquivo
            ).expanduser()

            winsound.PlaySound(
                str(caminho),
                winsound.SND_FILENAME
                | winsound.SND_NODEFAULT
            )

            logger.info(
                "Alerta sonoro personalizado reproduzido: %s",
                caminho
            )

        else:
            _tocar_padrao_ndt()

            logger.info(
                "Alerta sonoro padrão do NDT reproduzido."
            )

    except (
        RuntimeError,
        OSError
    ) as erro:
        logger.exception(
            "Falha ao reproduzir alerta sonoro: %s",
            erro
        )


def _processar_fila_audio():
    while True:
        modo, arquivo = _fila_audio.get()

        try:
            _reproduzir_alerta(
                modo,
                arquivo
            )

            # Pequena separação entre alertas consecutivos.
            time.sleep(
                0.15
            )

        finally:
            _fila_audio.task_done()


def _garantir_worker_audio():
    global _worker_audio

    with _worker_lock:
        if (
            _worker_audio is not None
            and _worker_audio.is_alive()
        ):
            return

        _worker_audio = threading.Thread(
            target=_processar_fila_audio,
            name="NDT-AudioWorker",
            daemon=True
        )

        _worker_audio.start()


def validar_alerta(
    modo,
    arquivo
):
    if modo not in {
        "padrao",
        "personalizado"
    }:
        modo = "padrao"

    if modo == "personalizado":
        caminho = Path(
            arquivo
        ).expanduser()

        if (
            not caminho.exists()
            or not caminho.is_file()
            or caminho.suffix.lower() != ".wav"
        ):
            logger.warning(
                "Alerta personalizado inválido: %s",
                arquivo
            )

            return (
                False,
                modo
            )

    return (
        True,
        modo
    )


def tocar_alerta(
    modo="padrao",
    arquivo="",
    assincrono=True
):
    valido, modo = validar_alerta(
        modo,
        arquivo
    )

    if not valido:
        return False

    if not assincrono:
        _reproduzir_alerta(
            modo,
            arquivo
        )

        return True

    _garantir_worker_audio()

    _fila_audio.put(
        (
            modo,
            arquivo
        )
    )

    logger.info(
        "Alerta sonoro adicionado à fila | "
        "Modo=%s | Pendentes=%s",
        modo,
        _fila_audio.qsize()
    )

    return True


def parar_alerta():
    try:
        winsound.PlaySound(
            None,
            winsound.SND_PURGE
        )

    except (
        RuntimeError,
        OSError
    ):
        pass


def testar_alerta(
    modo="padrao",
    arquivo=""
):
    return tocar_alerta(
        modo=modo,
        arquivo=arquivo,
        assincrono=True
    )
