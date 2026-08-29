import threading
import time
import winsound

from pathlib import Path

from services.logger import logger


_audio_lock = threading.Lock()


def _tocar_padrao_ndt():
    """
    Alerta padrão do NDT.

    Usa winsound.Beep em vez de depender do esquema de sons do
    Windows. Isso deixa o alerta mais confiável mesmo quando a
    aplicação está minimizada/oculta na bandeja.
    """
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
    if not _audio_lock.acquire(
        blocking=False
    ):
        logger.info(
            "Alerta sonoro ignorado porque outro áudio "
            "já está em reprodução."
        )
        return

    try:
        if modo == "personalizado":
            caminho = Path(
                arquivo
            ).expanduser()

            if not caminho.exists():
                logger.warning(
                    "Arquivo de alerta sonoro não encontrado: %s",
                    caminho
                )
                return

            if not caminho.is_file():
                logger.warning(
                    "Caminho de alerta sonoro não é um arquivo: %s",
                    caminho
                )
                return

            if caminho.suffix.lower() != ".wav":
                logger.warning(
                    "Formato de áudio não suportado: %s",
                    caminho.suffix
                )
                return

            winsound.PlaySound(
                str(caminho),
                winsound.SND_FILENAME
                | winsound.SND_NODEFAULT
            )

            logger.info(
                "Alerta sonoro personalizado reproduzido: %s",
                caminho
            )

            return

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

    finally:
        _audio_lock.release()


def tocar_alerta(
    modo="padrao",
    arquivo="",
    assincrono=True
):
    """
    Agenda a reprodução do alerta.

    A reprodução ocorre em uma thread Python independente da
    interface Qt. Isso evita travar a janela principal e mantém
    o áudio funcionando quando o NDT está oculto na bandeja.

    Retorna True quando a reprodução foi iniciada/agendada.
    """
    modo = (
        modo
        if modo in {
            "padrao",
            "personalizado"
        }
        else "padrao"
    )

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
            return False

    if assincrono:
        thread_audio = threading.Thread(
            target=_reproduzir_alerta,
            args=(
                modo,
                arquivo
            ),
            name="NDT-AudioAlert",
            daemon=True
        )

        thread_audio.start()

        logger.info(
            "Alerta sonoro agendado | Modo=%s",
            modo
        )

        return True

    _reproduzir_alerta(
        modo,
        arquivo
    )

    return True


def parar_alerta():
    """
    Interrompe um WAV reproduzido por PlaySound.

    O alerta padrão do NDT usa uma sequência curta de Beeps e
    termina sozinho em menos de um segundo.
    """
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
    """
    Testa o som sem bloquear a interface.
    """
    return tocar_alerta(
        modo=modo,
        arquivo=arquivo,
        assincrono=True
    )
