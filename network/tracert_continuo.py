from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from PySide6.QtCore import (
    QThread,
    Signal
)

from network.ping import (
    executar_ping
)

from network.tracert import (
    executar_tracert
)

from services.logger import (
    logger
)


def testar_hop(
    numero_salto,
    ip,
    timeout_ms=700
):
    if (
        ip is None
        or ip == "-"
    ):
        return {
            "salto": numero_salto,
            "ip": "-",
            "respondeu": False,
            "tempo": None
        }

    try:
        resultado = executar_ping(
            ip,
            quantidade=1,
            timeout_ms=timeout_ms,
            limite_variacao_ms=999999
        )

    except Exception:
        logger.exception(
            "Erro ao testar hop | "
            "Salto=%s | IP=%s",
            numero_salto,
            ip
        )

        return {
            "salto": numero_salto,
            "ip": ip,
            "respondeu": False,
            "tempo": None
        }

    respostas = resultado.get(
        "respostas",
        []
    )

    if not respostas:
        return {
            "salto": numero_salto,
            "ip": ip,
            "respondeu": False,
            "tempo": None
        }

    resposta = respostas[0]

    return {
        "salto": numero_salto,
        "ip": ip,
        "respondeu": True,
        "tempo": resposta["tempo"]
    }


class TracertContinuoThread(QThread):
    resultado_atualizado = Signal(
        list,
        int
    )

    status = Signal(str)

    def __init__(
        self,
        ip,
        max_saltos=30,
        intervalo=1.0,
        timeout_sonda_ms=700,
        max_workers=8,
        amostra_minima=30
    ):
        super().__init__()

        self.ip = ip
        self.max_saltos = max_saltos

        self.intervalo_ms = max(
            500,
            int(
                intervalo * 1000
            )
        )

        self.timeout_sonda_ms = (
            timeout_sonda_ms
        )

        self.max_workers = max(
            1,
            max_workers
        )

        self.amostra_minima = max(
            5,
            amostra_minima
        )

        self.ciclos = 0

        self.estatisticas = {}

        self.rota = {}

        self.total_saltos = 0

        self.destino_encontrado = False

        self.analise_ativada = False

    def run(self):
        logger.info(
            "Tracert contínuo iniciado | "
            "IP=%s | Amostra mínima=%s",
            self.ip,
            self.amostra_minima
        )

        self.status.emit(
            "Tracert contínuo: "
            "descobrindo rota..."
        )

        if not self.descobrir_rota():
            if (
                self
                .isInterruptionRequested()
            ):
                logger.info(
                    "Tracert contínuo cancelado "
                    "durante descoberta da rota | "
                    "IP=%s",
                    self.ip
                )

                return

            logger.warning(
                "Não foi possível descobrir "
                "completamente a rota | IP=%s",
                self.ip
            )

        if self.total_saltos <= 0:
            self.total_saltos = 1

            self.rota = {
                1: self.ip
            }

            self.destino_encontrado = True

        self.preparar_estatisticas()

        logger.info(
            "Rota preparada | "
            "Destino=%s | Saltos=%s",
            self.ip,
            self.total_saltos
        )

        self.status.emit(
            "Tracert contínuo ativo | "
            f"{self.total_saltos} saltos monitorados | "
            f"Amostra: 0/{self.amostra_minima}."
        )

        numero_workers = min(
            self.max_workers,
            max(
                1,
                self.total_saltos
            )
        )

        with ThreadPoolExecutor(
            max_workers=numero_workers
        ) as executor:

            while not (
                self
                .isInterruptionRequested()
            ):
                futuros = []

                for numero_salto in range(
                    1,
                    self.total_saltos + 1
                ):
                    ip_hop = self.rota.get(
                        numero_salto
                    )

                    futuro = executor.submit(
                        testar_hop,
                        numero_salto,
                        ip_hop,
                        self.timeout_sonda_ms
                    )

                    futuros.append(
                        futuro
                    )

                resultados_ciclo = []

                for futuro in as_completed(
                    futuros
                ):
                    if (
                        self
                        .isInterruptionRequested()
                    ):
                        break

                    try:
                        resultado = (
                            futuro.result()
                        )

                    except Exception:
                        logger.exception(
                            "Erro inesperado em "
                            "sondagem do Tracert contínuo."
                        )

                        continue

                    resultados_ciclo.append(
                        resultado
                    )

                if (
                    self
                    .isInterruptionRequested()
                ):
                    break

                resultados_ciclo.sort(
                    key=lambda item:
                        item["salto"]
                )

                self.ciclos += 1

                self.atualizar_estatisticas(
                    resultados_ciclo
                )

                resultados = (
                    self.gerar_resultados()
                )

                resultados = (
                    self.analisar_resultados(
                        resultados
                    )
                )

                if (
                    not self.analise_ativada
                    and self.ciclos
                    >= self.amostra_minima
                ):
                    self.analise_ativada = True

                    logger.info(
                        "Amostra mínima atingida | "
                        "IP=%s | Ciclos=%s",
                        self.ip,
                        self.ciclos
                    )

                    self.status.emit(
                        "Tracert contínuo ativo | "
                        "Amostra mínima atingida | "
                        "Análise automática ativa."
                    )

                elif (
                    self.ciclos
                    < self.amostra_minima
                ):
                    self.status.emit(
                        "Tracert contínuo ativo | "
                        f"Amostra: "
                        f"{self.ciclos}/"
                        f"{self.amostra_minima}."
                    )

                self.resultado_atualizado.emit(
                    resultados,
                    self.ciclos
                )

                restante = (
                    self.intervalo_ms
                )

                while restante > 0:
                    if (
                        self
                        .isInterruptionRequested()
                    ):
                        break

                    passo = min(
                        100,
                        restante
                    )

                    self.msleep(
                        passo
                    )

                    restante -= passo

        logger.info(
            "Tracert contínuo finalizado | "
            "IP=%s | Ciclos=%s",
            self.ip,
            self.ciclos
        )

    def descobrir_rota(
        self
    ):
        saltos = executar_tracert(
            self.ip,
            max_saltos=self.max_saltos,
            timeout_salto_ms=700,
            timeout_global=15,
            cancelado=
                self.isInterruptionRequested
        )

        if (
            self
            .isInterruptionRequested()
        ):
            return False

        if not saltos:
            return False

        numeros_encontrados = []

        for salto in saltos:
            numero = salto.get(
                "salto"
            )

            if numero is None:
                continue

            numeros_encontrados.append(
                numero
            )

            ip_hop = salto.get(
                "ip"
            )

            self.rota[
                numero
            ] = ip_hop

            if ip_hop == self.ip:
                self.destino_encontrado = True

        if numeros_encontrados:
            self.total_saltos = max(
                numeros_encontrados
            )

        for salto in saltos:
            if (
                salto.get("ip")
                == self.ip
            ):
                self.total_saltos = (
                    salto["salto"]
                )

                self.destino_encontrado = True

                break

        logger.info(
            "Rota inicial descoberta | "
            "Destino=%s | Saltos=%s | "
            "Destino encontrado=%s",
            self.ip,
            self.total_saltos,
            self.destino_encontrado
        )

        for numero in range(
            1,
            self.total_saltos + 1
        ):
            logger.info(
                "Rota | Hop=%s | IP=%s",
                numero,
                self.rota.get(
                    numero
                )
                or "*"
            )

        return True

    def preparar_estatisticas(
        self
    ):
        self.estatisticas = {}

        for numero in range(
            1,
            self.total_saltos + 1
        ):
            self.estatisticas[
                numero
            ] = {
                "salto": numero,

                "ip":
                    self.rota.get(
                        numero
                    )
                    or "-",

                "enviados": 0,
                "recebidos": 0,

                "melhor": None,
                "pior": None,

                "soma_tempos": 0,

                "ultimo": None
            }

    def atualizar_estatisticas(
        self,
        resultados
    ):
        for resultado in resultados:
            numero = resultado[
                "salto"
            ]

            if (
                numero
                not in self.estatisticas
            ):
                continue

            dados = self.estatisticas[
                numero
            ]

            dados[
                "enviados"
            ] += 1

            if not resultado[
                "respondeu"
            ]:
                dados[
                    "ultimo"
                ] = None

                continue

            tempo = resultado[
                "tempo"
            ]

            if tempo is None:
                dados[
                    "ultimo"
                ] = None

                continue

            dados[
                "recebidos"
            ] += 1

            dados[
                "ultimo"
            ] = tempo

            dados[
                "soma_tempos"
            ] += tempo

            if (
                dados[
                    "melhor"
                ]
                is None
                or tempo
                < dados[
                    "melhor"
                ]
            ):
                dados[
                    "melhor"
                ] = tempo

            if (
                dados[
                    "pior"
                ]
                is None
                or tempo
                > dados[
                    "pior"
                ]
            ):
                dados[
                    "pior"
                ] = tempo

    def gerar_resultados(
        self
    ):
        resultados = []

        for numero in sorted(
            self.estatisticas
        ):
            dados = self.estatisticas[
                numero
            ]

            enviados = dados[
                "enviados"
            ]

            recebidos = dados[
                "recebidos"
            ]

            perdidos = (
                enviados
                - recebidos
            )

            if enviados > 0:
                perda = round(
                    (
                        perdidos
                        / enviados
                    )
                    * 100,
                    1
                )

            else:
                perda = 0.0

            if recebidos > 0:
                media = round(
                    dados[
                        "soma_tempos"
                    ]
                    / recebidos,
                    2
                )

            else:
                media = None

            resultados.append({
                "salto":
                    dados[
                        "salto"
                    ],

                "ip":
                    dados[
                        "ip"
                    ],

                "enviados":
                    enviados,

                "recebidos":
                    recebidos,

                "perda":
                    perda,

                "melhor":
                    dados[
                        "melhor"
                    ],

                "media":
                    media,

                "pior":
                    dados[
                        "pior"
                    ],

                "ultimo":
                    dados[
                        "ultimo"
                    ],

                "status":
                    "COLETANDO"
            })

        return resultados

    def analisar_resultados(
        self,
        resultados
    ):
        if not resultados:
            return resultados

        # Antes da amostra mínima, não tiramos
        # conclusões da rota.
        if (
            self.ciclos
            < self.amostra_minima
        ):
            for resultado in resultados:
                resultado[
                    "status"
                ] = "COLETANDO"

            return resultados

        tolerancia_perda = 1.0

        quantidade = len(
            resultados
        )

        destino_indice = None

        for indice, resultado in enumerate(
            resultados
        ):
            if (
                resultado.get(
                    "ip"
                )
                == self.ip
            ):
                destino_indice = indice
                break

        for indice, resultado in enumerate(
            resultados
        ):
            perda_atual = resultado[
                "perda"
            ]

            recebidos = resultado[
                "recebidos"
            ]

            ip_hop = resultado[
                "ip"
            ]

            posteriores = (
                resultados[
                    indice + 1:
                ]
            )

            posteriores_responsivos = [
                item
                for item in posteriores
                if item[
                    "recebidos"
                ] > 0
            ]

            # ----------------------------------
            # Destino
            # ----------------------------------

            if ip_hop == self.ip:
                if recebidos == 0:
                    resultado[
                        "status"
                    ] = (
                        "DESTINO SEM RESPOSTA"
                    )

                elif perda_atual > 0:
                    resultado[
                        "status"
                    ] = (
                        "PERDA NO DESTINO"
                    )

                else:
                    resultado[
                        "status"
                    ] = "OK"

                continue

            # ----------------------------------
            # Hop completamente silencioso
            # ----------------------------------

            if recebidos == 0:
                if posteriores_responsivos:
                    resultado[
                        "status"
                    ] = (
                        "ICMP LIMITADO"
                    )

                else:
                    resultado[
                        "status"
                    ] = (
                        "SEM RESPOSTA"
                    )

                continue

            # ----------------------------------
            # Sem perda
            # ----------------------------------

            if perda_atual <= 0:
                resultado[
                    "status"
                ] = "OK"

                continue

            # ----------------------------------
            # Houve perda neste hop.
            #
            # Se algum hop posterior responde
            # significativamente melhor, este
            # roteador provavelmente está apenas
            # limitando ICMP direcionado a ele.
            # ----------------------------------

            perdas_posteriores = [
                item[
                    "perda"
                ]
                for item
                in posteriores_responsivos
            ]

            if perdas_posteriores:
                menor_perda_posterior = min(
                    perdas_posteriores
                )

                if (
                    menor_perda_posterior
                    + tolerancia_perda
                    < perda_atual
                ):
                    resultado[
                        "status"
                    ] = (
                        "ICMP LIMITADO"
                    )

                    continue

            # ----------------------------------
            # Se conhecemos o destino e a perda
            # continua aproximadamente até ele,
            # consideramos persistente.
            # ----------------------------------

            if destino_indice is not None:
                destino = resultados[
                    destino_indice
                ]

                perda_destino = destino[
                    "perda"
                ]

                if (
                    perda_destino > 0
                    and
                    perda_atual
                    <= (
                        perda_destino
                        + tolerancia_perda
                    )
                ):
                    resultado[
                        "status"
                    ] = (
                        "PERDA PERSISTENTE"
                    )

                    continue

            # ----------------------------------
            # Se os hops seguintes também têm
            # perda parecida, mesmo sem termos
            # alcançado o destino no Tracert,
            # existe indício de continuidade.
            # ----------------------------------

            perdas_semelhantes = [
                perda
                for perda
                in perdas_posteriores
                if (
                    perda
                    + tolerancia_perda
                    >= perda_atual
                )
            ]

            if (
                len(perdas_semelhantes)
                >= 2
            ):
                resultado[
                    "status"
                ] = (
                    "PERDA PERSISTENTE"
                )

            else:
                resultado[
                    "status"
                ] = (
                    "POSSÍVEL PERDA"
                )

        return resultados
