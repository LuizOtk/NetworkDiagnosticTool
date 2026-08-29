import re
import subprocess
import time

from services.logger import logger


CREATE_NO_WINDOW = getattr(
    subprocess,
    "CREATE_NO_WINDOW",
    0
)


def extrair_tempo(valor):
    if valor is None:
        return None

    valor = valor.strip()

    if valor == "*":
        return None

    numero = re.search(
        r"\d+",
        valor
    )

    if numero is None:
        return None

    return int(
        numero.group()
    )


def analisar_saida_tracert(
    saida
):
    saltos = []

    padrao_salto = re.compile(
        r"^\s*(\d+)\s+"
        r"(\*|<?\s*\d+\s*ms)\s+"
        r"(\*|<?\s*\d+\s*ms)\s+"
        r"(\*|<?\s*\d+\s*ms)"
        r"(?:\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})"
        r")?",
        re.IGNORECASE
    )

    for linha in saida.splitlines():
        resultado = padrao_salto.search(
            linha
        )

        if resultado is None:
            continue

        numero_salto = int(
            resultado.group(1)
        )

        tempo1 = extrair_tempo(
            resultado.group(2)
        )

        tempo2 = extrair_tempo(
            resultado.group(3)
        )

        tempo3 = extrair_tempo(
            resultado.group(4)
        )

        ip = resultado.group(5)

        tempos_validos = [
            tempo
            for tempo in (
                tempo1,
                tempo2,
                tempo3
            )
            if tempo is not None
        ]

        if not tempos_validos:
            status = "sem resposta"
            media = None

        elif len(tempos_validos) < 3:
            status = "parcial"

            media = round(
                sum(tempos_validos)
                / len(tempos_validos),
                2
            )

        else:
            status = "ok"

            media = round(
                sum(tempos_validos)
                / len(tempos_validos),
                2
            )

        saltos.append({
            "salto": numero_salto,
            "ip": ip,
            "tempo1": tempo1,
            "tempo2": tempo2,
            "tempo3": tempo3,
            "media": media,
            "status": status
        })

    return saltos


def encerrar_processo(
    processo
):
    if processo.poll() is not None:
        return

    try:
        processo.terminate()

        processo.wait(
            timeout=1
        )

    except (
        subprocess.TimeoutExpired,
        OSError
    ):
        try:
            processo.kill()

        except OSError:
            pass


def executar_tracert(
    ip,
    max_saltos=30,
    timeout_salto_ms=1000,
    timeout_global=25,
    cancelado=None
):
    logger.info(
        "Tracert iniciado | IP=%s | "
        "Máximo de saltos=%s",
        ip,
        max_saltos
    )

    comando = [
        "tracert",
        "-d",
        "-w",
        str(timeout_salto_ms),
        "-h",
        str(max_saltos),
        ip
    ]

    try:
        processo = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="cp850",
            errors="replace",
            creationflags=CREATE_NO_WINDOW
        )

    except OSError:
        logger.exception(
            "Erro ao iniciar Tracert | IP=%s",
            ip
        )

        return []

    inicio = time.monotonic()

    foi_cancelado = False
    atingiu_timeout = False

    while processo.poll() is None:

        if (
            cancelado is not None
            and cancelado()
        ):
            foi_cancelado = True

            logger.info(
                "Cancelamento solicitado ao "
                "Tracert | IP=%s",
                ip
            )

            encerrar_processo(
                processo
            )

            break

        tempo_decorrido = (
            time.monotonic()
            - inicio
        )

        if (
            tempo_decorrido
            >= timeout_global
        ):
            atingiu_timeout = True

            logger.warning(
                "Timeout global do Tracert "
                "atingido | IP=%s | Limite=%ss",
                ip,
                timeout_global
            )

            encerrar_processo(
                processo
            )

            break

        time.sleep(
            0.1
        )

    try:
        stdout, _ = processo.communicate(
            timeout=1
        )

    except subprocess.TimeoutExpired:
        encerrar_processo(
            processo
        )

        stdout, _ = processo.communicate()

    stdout = stdout or ""

    saltos = analisar_saida_tracert(
        stdout
    )

    if foi_cancelado:
        logger.info(
            "Tracert cancelado | "
            "IP=%s | Saltos parciais=%s",
            ip,
            len(saltos)
        )

    elif atingiu_timeout:
        logger.warning(
            "Tracert interrompido por timeout | "
            "IP=%s | Saltos parciais=%s",
            ip,
            len(saltos)
        )

    else:
        logger.info(
            "Tracert concluído | "
            "IP=%s | Saltos identificados=%s",
            ip,
            len(saltos)
        )

    return saltos
