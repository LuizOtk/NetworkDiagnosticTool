from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from PySide6.QtCore import QThread, Signal

from network.ping import executar_ping
from services.logger import logger


def normalizar_alvo(endereco):
    endereco = endereco.strip()

    if not endereco:
        return None

    if "://" in endereco:
        resultado = urlparse(
            endereco
        )
    else:
        resultado = urlparse(
            f"//{endereco}"
        )

    return resultado.hostname


def normalizar_url(endereco):
    endereco = endereco.strip()

    if not endereco:
        return None

    if endereco.startswith(
        ("http://", "https://")
    ):
        return endereco

    return f"https://{endereco}"


def criar_chave_servico(servico):
    nome = servico.get(
        "nome",
        ""
    ).strip().casefold()

    endereco = servico.get(
        "endereco",
        ""
    ).strip().casefold()

    tipo = servico.get(
        "tipo",
        "PING"
    ).upper()

    return (
        f"{tipo}|"
        f"{nome}|"
        f"{endereco}"
    )


def testar_http(
    endereco,
    timeout=4.0
):
    url = normalizar_url(
        endereco
    )

    if url is None:
        return {
            "disponivel": False,
            "respondeu": False,
            "latencia": None,
            "codigo_http": None,
            "tipo_falha": "ENDERECO"
        }

    requisicao = Request(
        url,
        headers={
            "User-Agent":
                "Mozilla/5.0 "
                "NetworkDiagnosticTool/1.0"
        },
        method="GET"
    )

    inicio = perf_counter()

    try:
        with urlopen(
            requisicao,
            timeout=timeout
        ) as resposta:

            codigo = (
                resposta.getcode()
            )

            resposta.read(1)

        latencia = round(
            (
                perf_counter()
                - inicio
            )
            * 1000
        )

        if codigo < 500:
            disponivel = True
            tipo_falha = None
        else:
            disponivel = False
            tipo_falha = "HTTP_5XX"

        return {
            "disponivel": disponivel,
            "respondeu": True,
            "latencia": latencia,
            "codigo_http": codigo,
            "tipo_falha": tipo_falha
        }

    except HTTPError as erro:
        latencia = round(
            (
                perf_counter()
                - inicio
            )
            * 1000
        )

        codigo = erro.code

        # Respostas 4xx ainda significam que o servidor respondeu.
        if codigo < 500:
            return {
                "disponivel": True,
                "respondeu": True,
                "latencia": latencia,
                "codigo_http": codigo,
                "tipo_falha": None
            }

        return {
            "disponivel": False,
            "respondeu": True,
            "latencia": latencia,
            "codigo_http": codigo,
            "tipo_falha": "HTTP_5XX"
        }

    except (
        URLError,
        TimeoutError,
        OSError,
        ValueError
    ):
        return {
            "disponivel": False,
            "respondeu": False,
            "latencia": None,
            "codigo_http": None,
            "tipo_falha": "CONEXAO"
        }


class DownDetectorThread(QThread):
    resultado_servico = Signal(dict)
    progresso_ciclo = Signal(int, int)
    ciclo_concluido = Signal()

    def __init__(
        self,
        servicos,
        intervalo,
        limite_variacao_ping,
        limite_variacao_http,
        falhas_offline,
        limite_latencia_ping=100,
        limite_latencia_http=1000,
        max_workers=8
    ):
        super().__init__()

        self.setObjectName(
            "DownDetectorThread"
        )

        self.servicos = servicos

        self.intervalo_ms = max(
            1000,
            int(intervalo * 1000)
        )

        self.limite_variacao_ping = (
            limite_variacao_ping
        )

        self.limite_variacao_http = (
            limite_variacao_http
        )

        self.falhas_offline = (
            falhas_offline
        )

        self.limite_latencia_ping = (
            limite_latencia_ping
        )

        self.limite_latencia_http = (
            limite_latencia_http
        )

        self.max_workers = max(
            1,
            int(max_workers)
        )

        self.historicos_latencia = {}
        self.historicos_falhas = {}
        self.falhas_consecutivas = {}

    def solicitar_parada(
        self
    ):
        self.requestInterruption()

    def esperar_intervalo(
        self,
        duracao_ms
    ):
        restante = duracao_ms

        while restante > 0:
            if self.isInterruptionRequested():
                return False

            passo = min(
                100,
                restante
            )

            self.msleep(
                passo
            )

            restante -= passo

        return True

    def run(self):
        quantidade_servicos = len(
            self.servicos
        )

        workers = min(
            self.max_workers,
            max(
                1,
                quantidade_servicos
            )
        )

        logger.info(
            "Monitor de Serviços iniciado | "
            "Serviços=%s | Workers=%s",
            quantidade_servicos,
            workers
        )

        try:
            for indice in range(
                quantidade_servicos
            ):
                self.historicos_latencia[
                    indice
                ] = deque(
                    maxlen=10
                )

                self.historicos_falhas[
                    indice
                ] = deque(
                    maxlen=10
                )

                self.falhas_consecutivas[
                    indice
                ] = 0

            with ThreadPoolExecutor(
                max_workers=workers,
                thread_name_prefix="NDT-ServiceCheck"
            ) as executor:

                while not (
                    self.isInterruptionRequested()
                ):
                    futuros = {}

                    total_ciclo = len(
                        self.servicos
                    )

                    processados = 0

                    self.progresso_ciclo.emit(
                        0,
                        total_ciclo
                    )

                    for indice, servico in enumerate(
                        self.servicos
                    ):
                        if (
                            self
                            .isInterruptionRequested()
                        ):
                            return

                        futuro = executor.submit(
                            self.testar_servico,
                            indice,
                            servico
                        )

                        futuros[
                            futuro
                        ] = indice

                    for futuro in as_completed(
                        futuros
                    ):
                        if (
                            self
                            .isInterruptionRequested()
                        ):
                            for pendente in futuros:
                                pendente.cancel()

                            return

                        try:
                            continuar = futuro.result()

                        except Exception:
                            indice = futuros[
                                futuro
                            ]

                            logger.exception(
                                "Erro ao verificar serviço | "
                                "Índice=%s",
                                indice
                            )

                            continuar = True

                        if not continuar:
                            for pendente in futuros:
                                pendente.cancel()

                            return

                        processados += 1

                        self.progresso_ciclo.emit(
                            processados,
                            total_ciclo
                        )

                    if (
                        self
                        .isInterruptionRequested()
                    ):
                        return

                    self.ciclo_concluido.emit()

                    if not self.esperar_intervalo(
                        self.intervalo_ms
                    ):
                        return

        finally:
            logger.info(
                "Monitor de Serviços finalizado."
            )

    def testar_servico(
        self,
        indice,
        servico
    ):
        if self.isInterruptionRequested():
            return False

        nome = servico.get(
            "nome",
            "Serviço"
        )

        endereco = servico.get(
            "endereco",
            ""
        )

        tipo = servico.get(
            "tipo",
            "PING"
        ).upper()

        chave = criar_chave_servico(
            servico
        )

        latencia = None
        codigo_http = None
        tipo_falha = None
        disponivel = False

        if tipo == "HTTP":
            limite_variacao = (
                self.limite_variacao_http
            )

            limite_latencia = (
                self.limite_latencia_http
            )

            resultado = testar_http(
                endereco
            )

            # urlopen não pode ser interrompido no meio da chamada,
            # então verificamos a solicitação imediatamente ao retornar.
            if self.isInterruptionRequested():
                return False

            disponivel = resultado[
                "disponivel"
            ]

            latencia = resultado[
                "latencia"
            ]

            codigo_http = resultado[
                "codigo_http"
            ]

            tipo_falha = resultado[
                "tipo_falha"
            ]

            alvo = normalizar_alvo(
                endereco
            )

        else:
            tipo = "PING"

            limite_variacao = (
                self.limite_variacao_ping
            )

            limite_latencia = (
                self.limite_latencia_ping
            )

            alvo = normalizar_alvo(
                endereco
            )

            if alvo is not None:
                resultado = executar_ping(
                    alvo,
                    quantidade=1,
                    timeout_ms=1000,
                    limite_variacao_ms=
                        self.limite_variacao_ping
                )

                if self.isInterruptionRequested():
                    return False

                respostas = resultado.get(
                    "respostas",
                    []
                )

                if respostas:
                    disponivel = True

                    latencia = respostas[
                        0
                    ]["tempo"]

                else:
                    tipo_falha = (
                        "CONEXAO"
                    )

        if self.isInterruptionRequested():
            return False

        historico_latencia = (
            self.historicos_latencia[
                indice
            ]
        )

        historico_falhas = (
            self.historicos_falhas[
                indice
            ]
        )

        historico_latencia.append(
            latencia
        )

        historico_falhas.append(
            not disponivel
        )

        if disponivel:
            self.falhas_consecutivas[
                indice
            ] = 0

        else:
            self.falhas_consecutivas[
                indice
            ] += 1

        tempos = [
            tempo
            for tempo in historico_latencia
            if tempo is not None
        ]

        falhas_recentes = sum(
            1
            for falhou in historico_falhas
            if falhou
        )

        if len(tempos) >= 2:
            variacao = (
                max(tempos)
                - min(tempos)
            )
        else:
            variacao = 0

        falhas_consecutivas = (
            self.falhas_consecutivas[
                indice
            ]
        )

        if not disponivel:
            if (
                falhas_consecutivas
                >= self.falhas_offline
            ):
                if (
                    tipo == "HTTP"
                    and tipo_falha
                    == "HTTP_5XX"
                ):
                    status = (
                        "FALHA HTTP"
                    )

                else:
                    status = (
                        "SEM RESPOSTA"
                    )

            else:
                status = (
                    "POSSÍVEL INSTABILIDADE"
                )

        else:
            possui_instabilidade = (
                falhas_recentes > 0
                or variacao
                >= limite_variacao
            )

            latencia_alta = (
                latencia is not None
                and latencia
                >= limite_latencia
            )

            if possui_instabilidade:
                status = (
                    "POSSÍVEL INSTABILIDADE"
                )

            elif latencia_alta:
                status = (
                    "LATÊNCIA ALTA"
                )

            else:
                status = "ONLINE"

        if self.isInterruptionRequested():
            return False

        self.resultado_servico.emit({
            "id": indice,
            "chave": chave,
            "nome": nome,
            "endereco": endereco,
            "alvo": alvo or "-",
            "tipo": tipo,
            "latencia": latencia,
            "codigo_http": codigo_http,
            "variacao": variacao,
            "limite_variacao":
                limite_variacao,
            "limite_latencia":
                limite_latencia,
            "perdas_recentes":
                falhas_recentes,
            "falhas_consecutivas":
                falhas_consecutivas,
            "tipo_falha":
                tipo_falha,
            "status": status,
            "ultima_verificacao":
                datetime.now().strftime(
                    "%H:%M:%S"
                )
        })

        return True
