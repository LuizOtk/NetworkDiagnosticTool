import json
import ipaddress
import time

from datetime import datetime

from PySide6.QtCore import (
    QSize,
    QThread,
    Signal,
    Qt
)

from PySide6.QtGui import (
    QColor,
    QCloseEvent
)


from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)

from config.settings import (
    carregar_configuracoes,
    salvar_configuracoes
)
from services.network_health import (
    analisar_saude_rede
)

from network.down_detector import (
    DownDetectorThread,
    criar_chave_servico
)

from network.ping import (
    executar_ping
)

from network.ports import (
    testar_portas
)

from network.tracert import (
    executar_tracert
)

from network.tracert_continuo import (
    TracertContinuoThread
)

from services.browser import (
    abrir_url,
    enriquecer_resultados_portas_web,
    obter_urls_web,
    obter_url_preferencial
)

from services.logger import (
    logger
)

from services.config_transfer import (
    criar_backup_automatico,
    exportar_configuracoes,
    importar_configuracoes
)

from services.audio_alert import (
    tocar_alerta
)

from services.incidents import (
    abrir_incidente,
    atualizar_metricas_incidente,
    encerrar_incidente,
    limpar_incidentes_antigos,
    listar_incidentes,
    obter_incidente_aberto,
    obter_resumo_hoje
)

from services.report import (
    exportar_relatorio,
    exportar_tracert_continuo_csv,
    exportar_tracert_continuo_json,
    exportar_tracert_continuo_txt
)

from ui.dashboard import (
    DashboardPage,
    IncidentsPage,
    MonitoringPage,
    ReportsPage,
    criar_icone
)

from ui.down_detector_window import (
    DownDetectorWindow
)

from ui.log_window import (
    LogWindow
)

from ui.incidents_window import (
    IncidentsWindow
)

from ui.ping_telemetry import (
    PingTelemetryWidget
)

from ui.route_telemetry import (
    RouteTelemetryWidget
)

from ui.settings_window import (
    SettingsWindow
)


class PingCard(QFrame):
    def __init__(
        self,
        titulo,
        valor="-"
    ):
        super().__init__()

        self.setObjectName(
            "cardPing"
        )

        layout = QVBoxLayout(
            self
        )

        titulo_label = QLabel(
            titulo
        )

        titulo_label.setObjectName(
            "cardTitulo"
        )

        self.valor_label = QLabel(
            valor
        )

        self.valor_label.setObjectName(
            "cardValor"
        )

        layout.addWidget(
            titulo_label
        )

        layout.addWidget(
            self.valor_label
        )


class DiagnosticoThread(QThread):
    resultado_ping = Signal(dict)
    resultado_tracert = Signal(list)
    resultado_portas = Signal(list)
    status = Signal(str)

    def __init__(
        self,
        ip,
        configuracoes
    ):
        super().__init__()

        self.ip = ip
        self.configuracoes = configuracoes

    def run(self):
        logger.info(
            "Diagnóstico iniciado | IP=%s",
            self.ip
        )

        if self.isInterruptionRequested():
            return

        self.status.emit(
            "Testando portas..."
        )

        portas = testar_portas(
            self.ip,
            self.configuracoes[
                "portas"
            ],
            self.configuracoes[
                "timeout_portas"
            ]
        )

        portas = enriquecer_resultados_portas_web(
            self.ip,
            portas,
            self.configuracoes.get(
                "interfaces_web_portas",
                {}
            )
        )

        if self.isInterruptionRequested():
            logger.info(
                "Diagnóstico cancelado após "
                "teste de portas | IP=%s",
                self.ip
            )
            return

        self.resultado_portas.emit(
            portas
        )

        self.status.emit(
            "Executando Ping..."
        )

        dados_ping = executar_ping(
            self.ip,
            self.configuracoes[
                "quantidade_ping"
            ],
            limite_variacao_ms=
                self.configuracoes[
                    "limite_variacao_ms"
                ]
        )

        if self.isInterruptionRequested():
            logger.info(
                "Diagnóstico cancelado após "
                "Ping | IP=%s",
                self.ip
            )
            return

        self.resultado_ping.emit(
            dados_ping
        )

        self.status.emit(
            "Analisando rota..."
        )

        saltos = executar_tracert(
            self.ip,
            self.configuracoes[
                "max_saltos"
            ],
            timeout_salto_ms=1000,
            timeout_global=25,
            cancelado=
                self.isInterruptionRequested
        )

        if saltos:
            self.resultado_tracert.emit(
                saltos
            )

        if self.isInterruptionRequested():
            logger.info(
                "Diagnóstico cancelado durante "
                "análise de rota | IP=%s | "
                "Saltos preservados=%s",
                self.ip,
                len(saltos)
            )

            return

        self.status.emit(
            "Diagnóstico concluído."
        )

        logger.info(
            "Diagnóstico concluído | IP=%s",
            self.ip
        )


class PingContinuoThread(QThread):
    novo_resultado = Signal(dict)

    def __init__(
        self,
        ip,
        intervalo
    ):
        super().__init__()

        self.ip = ip

        self.intervalo_ms = max(
            100,
            int(
                intervalo * 1000
            )
        )

    def run(self):
        while not (
            self.isInterruptionRequested()
        ):
            resultado = executar_ping(
                self.ip,
                quantidade=1,
                timeout_ms=1000
            )

            self.novo_resultado.emit(
                resultado
            )

            restante = (
                self.intervalo_ms
            )

            while restante > 0:
                if (
                    self
                    .isInterruptionRequested()
                ):
                    return

                passo = min(
                    100,
                    restante
                )

                self.msleep(
                    passo
                )

                restante -= passo


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.thread_diagnostico = None
        self.thread_ping_continuo = None
        self.thread_tracert_continuo = None
        self.thread_down_detector = None
        self.down_detector_reinicio_pendente = False

        self.diagnostico_cancelado = False

        self.tracert_ciclos = 0

        self.tracert_inicio_monotonic = None

        self.sessao_tracert_continuo = None

        self.interface_web_aberta_automaticamente = False

        self.rede_local_instavel_ativa = False

        self.servicos_indisponiveis_alertados = set()

        # Controle de cooldown dos alertas sonoros.
        # O monotonic evita problemas caso o relógio do Windows
        # seja alterado enquanto o NDT estiver aberto.
        self.ultimo_alerta_geral_monotonic = None
        self.ultimos_alertas_servicos = {}

        # Registro de Incidentes
        self.incidentes_servicos_ativos = {}
        self.incidente_rede_local_id = None
        self.incidente_rede_local_causa = ""

        self.encerramento_real = False

        self.configuracoes = (
            carregar_configuracoes()
        )

        self.ultima_limpeza_incidentes_monotonic = None

        self.executar_limpeza_incidentes(
            forcar=True
        )

        self.ip_atual = None

        self.dados_ping = None
        self.saltos = None
        self.portas = None
        self.urls_web = []

        self.cont_ping_enviados = 0
        self.cont_ping_recebidos = 0
        self.cont_ping_tempos = []

        self.historico_ping_continuo = []
        self.visualizacao_ping_atual = "tabela"
        self.visualizacao_tracert_atual = "tabela"

        self.resultados_down_detector = {}

        self.servicos_reconhecidos = set()

        self.janela_down_detector = (
            DownDetectorWindow(
                self
            )
        )

        self.janela_down_detector.reconhecer_servico.connect(
            self.reconhecer_alerta_down_detector
        )

        self.janela_logs = None
        self.janela_incidentes = None

        self.setWindowTitle(
            "Network Diagnostic Tool"
        )

        self.resize(
            1240,
            840
        )

        self.exportacoes_bloqueadas = False

        widget_central = QWidget()

        self.setCentralWidget(
            widget_central
        )

        layout_principal = QVBoxLayout(
            widget_central
        )

        layout_principal.setContentsMargins(
            16,
            14,
            16,
            10
        )

        layout_principal.setSpacing(
            10
        )

        self.criar_barra_navegacao(
            layout_principal
        )

        self.stack_paginas = QStackedWidget()

        self.pagina_dashboard = DashboardPage(
            self
        )

        self.pagina_diagnostico = (
            self.criar_pagina_diagnostico()
        )

        self.pagina_monitoramento = MonitoringPage(
            self
        )

        self.pagina_incidentes = IncidentsPage(
            self
        )

        self.pagina_relatorios = ReportsPage(
            self
        )

        self.stack_paginas.addWidget(
            self.pagina_dashboard
        )

        self.stack_paginas.addWidget(
            self.pagina_diagnostico
        )

        self.stack_paginas.addWidget(
            self.pagina_monitoramento
        )

        self.stack_paginas.addWidget(
            self.pagina_incidentes
        )

        self.stack_paginas.addWidget(
            self.pagina_relatorios
        )

        layout_principal.addWidget(
            self.stack_paginas,
            1
        )

        # Compatibilidade com a lógica já existente.
        self.botao_down_detector = (
            self.pagina_monitoramento
            .botao_servicos
        )

        self.botao_down_detector.setObjectName(
            "botaoDownDetector"
        )

        self.botao_down_detector.setProperty(
            "estado",
            "vazio"
        )

        self.botao_incidentes = (
            self.pagina_incidentes
            .botao_abrir_registro
        )

        self.botao_logs = (
            self.pagina_relatorios
            .botao_logs
        )

        self.botao_exportar = (
            self.pagina_relatorios
            .botao_diagnostico
        )

        layout_rodape = QHBoxLayout()

        self.status = QLabel(
            "Pronto"
        )

        self.status.setObjectName(
            "statusBar"
        )

        self.versao = QLabel(
            "Versão 1.2 DEV"
        )

        self.versao.setObjectName(
            "versaoApp"
        )

        layout_rodape.addWidget(
            self.status
        )

        layout_rodape.addStretch()

        layout_rodape.addWidget(
            self.versao
        )

        layout_principal.addLayout(
            layout_rodape
        )

        self.conectar_eventos()

        self.atualizar_menu_exportacao()

        self.mostrar_pagina(
            "dashboard"
        )

        self.reiniciar_down_detector()

    # ==================================================
    # TOPO
    # ==================================================

    def criar_barra_navegacao(
        self,
        layout_principal
    ):
        barra = QFrame()

        barra.setObjectName(
            "topNavigation"
        )

        layout = QHBoxLayout(
            barra
        )

        layout.setContentsMargins(
            12,
            7,
            8,
            7
        )

        layout.setSpacing(
            5
        )

        marca_icone = QLabel()

        marca_icone.setPixmap(
            criar_icone(
                "pulse",
                "#2388ff",
                27
            ).pixmap(
                27,
                27
            )
        )

        marca = QLabel(
            "NDT"
        )

        marca.setObjectName(
            "brandNdt"
        )

        layout.addWidget(
            marca_icone
        )

        layout.addWidget(
            marca
        )

        layout.addSpacing(
            12
        )

        self.botao_nav_dashboard = QPushButton(
            "Dashboard"
        )

        self.botao_nav_diagnostico = QPushButton(
            "Diagnóstico"
        )

        self.botao_nav_monitoramento = QPushButton(
            "Monitoramento"
        )

        self.botao_nav_incidentes = QPushButton(
            "Incidentes"
        )

        self.botao_nav_relatorios = QPushButton(
            "Relatórios"
        )

        self.botao_nav_dashboard.setIcon(
            criar_icone(
                "home",
                "#8fbfff",
                20
            )
        )

        self.botao_nav_diagnostico.setIcon(
            criar_icone(
                "diagnostic",
                "#a6b8c8",
                20
            )
        )

        self.botao_nav_monitoramento.setIcon(
            criar_icone(
                "chart",
                "#a6b8c8",
                20
            )
        )

        self.botao_nav_incidentes.setIcon(
            criar_icone(
                "bell",
                "#a6b8c8",
                20
            )
        )

        self.botao_nav_relatorios.setIcon(
            criar_icone(
                "document",
                "#a6b8c8",
                20
            )
        )

        self.botoes_navegacao = [
            self.botao_nav_dashboard,
            self.botao_nav_diagnostico,
            self.botao_nav_monitoramento,
            self.botao_nav_incidentes,
            self.botao_nav_relatorios
        ]

        for botao in self.botoes_navegacao:
            botao.setIconSize(
                QSize(
                    20,
                    20
                )
            )
        for botao in self.botoes_navegacao:
            botao.setObjectName(
                "navButton"
            )

            botao.setCheckable(
                True
            )

            botao.setAutoExclusive(
                True
            )

            layout.addWidget(
                botao
            )

        layout.addStretch()

        self.botao_configuracoes = QPushButton(
            ""
        )

        self.botao_configuracoes.setIcon(
            criar_icone(
                "settings",
                "#9fb6ca",
                21
            )
        )

        self.botao_configuracoes.setIconSize(
            QSize(
                21,
                21
            )
        )

        self.botao_configuracoes.setObjectName(
            "navSettingsButton"
        )

        self.botao_configuracoes.setToolTip(
            "Configurações"
        )

        layout.addWidget(
            self.botao_configuracoes
        )

        layout_principal.addWidget(
            barra
        )

    def criar_pagina_diagnostico(
        self
    ):
        pagina = QWidget()

        layout_principal = QVBoxLayout(
            pagina
        )

        layout_principal.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout_principal.setSpacing(
            10
        )

        bloco_titulo = QVBoxLayout()

        titulo = QLabel(
            "Diagnóstico de Rede"
        )

        titulo.setObjectName(
            "pageTitle"
        )

        subtitulo = QLabel(
            "Ping, rota e portas TCP em uma única análise."
        )

        subtitulo.setObjectName(
            "pageSubtitle"
        )

        bloco_titulo.addWidget(
            titulo
        )

        bloco_titulo.addWidget(
            subtitulo
        )

        layout_principal.addLayout(
            bloco_titulo
        )

        self.criar_topo_diagnostico(
            layout_principal
        )

        self.splitter_vertical = QSplitter(
            Qt.Orientation.Vertical
        )

        self.splitter_vertical.setChildrenCollapsible(
            False
        )

        self.splitter_vertical.addWidget(
            self.criar_area_ping_tracert()
        )

        self.splitter_vertical.addWidget(
            self.criar_area_portas()
        )

        self.splitter_vertical.setStretchFactor(
            0,
            3
        )

        self.splitter_vertical.setStretchFactor(
            1,
            2
        )

        self.splitter_vertical.setSizes([
            430,
            300
        ])

        layout_principal.addWidget(
            self.splitter_vertical,
            1
        )

        return pagina

    def criar_topo_diagnostico(
        self,
        layout_principal
    ):
        linha = QHBoxLayout()

        self.container_ip = QFrame()

        self.container_ip.setObjectName(
            "campoIpContainer"
        )

        self.container_ip.setMinimumHeight(
            42
        )

        layout_ip = QHBoxLayout(
            self.container_ip
        )

        layout_ip.setContentsMargins(
            10,
            0,
            4,
            0
        )

        layout_ip.setSpacing(
            4
        )

        self.campo_ip = QLineEdit()

        self.campo_ip.setObjectName(
            "campoIpInterno"
        )

        self.campo_ip.setPlaceholderText(
            "Digite um endereço IPv4"
        )

        self.campo_ip.setFrame(
            False
        )

        self.botao_executar = QPushButton(
            "➜"
        )

        self.botao_executar.setObjectName(
            "botaoExecutarIp"
        )

        self.botao_executar.setFixedSize(
            38,
            32
        )

        self.botao_executar.setToolTip(
            "Iniciar diagnóstico"
        )

        layout_ip.addWidget(
            self.campo_ip,
            1
        )

        layout_ip.addWidget(
            self.botao_executar
        )

        linha.addWidget(
            self.container_ip,
            1
        )

        layout_principal.addLayout(
            linha
        )

    def mostrar_pagina(
        self,
        nome
    ):
        mapa = {
            "dashboard": (
                self.pagina_dashboard,
                self.botao_nav_dashboard
            ),
            "diagnostico": (
                self.pagina_diagnostico,
                self.botao_nav_diagnostico
            ),
            "monitoramento": (
                self.pagina_monitoramento,
                self.botao_nav_monitoramento
            ),
            "incidentes": (
                self.pagina_incidentes,
                self.botao_nav_incidentes
            ),
            "relatorios": (
                self.pagina_relatorios,
                self.botao_nav_relatorios
            )
        }

        destino = mapa.get(
            nome
        )

        if destino is None:
            return

        pagina, botao = destino

        self.stack_paginas.setCurrentWidget(
            pagina
        )

        botao.setChecked(
            True
        )

        self.atualizar_resumos_interface()

    def ir_para_diagnostico(
        self
    ):
        self.mostrar_pagina(
            "diagnostico"
        )

        self.campo_ip.setFocus()

    def ir_para_monitor_icmp(
        self
    ):
        self.mostrar_pagina(
            "diagnostico"
        )

        self.status.setText(
            "Informe o IPv4 e use Monitor ICMP."
        )

        self.campo_ip.setFocus()

    def ir_para_monitor_rota(
        self
    ):
        self.mostrar_pagina(
            "diagnostico"
        )

        self.status.setText(
            "Informe o IPv4 e use Monitor de Rota."
        )

        self.campo_ip.setFocus()

    def formatar_duracao_dashboard(
        self,
        segundos
    ):
        try:
            segundos = int(
                segundos
            )
        except (
            TypeError,
            ValueError
        ):
            segundos = 0

        if segundos < 60:
            return f"{segundos}s"

        minutos = segundos // 60

        if minutos < 60:
            return f"{minutos} min"

        horas = minutos // 60
        restante = minutos % 60

        if restante:
            return f"{horas}h {restante}min"

        return f"{horas}h"

    def obter_resumo_interface(
        self
    ):
        resultados = list(
            self.resultados_down_detector
            .values()
        )

        if resultados:
            analise = analisar_saude_rede(
                resultados
            )
        else:
            analise = {
                "problemas": [],
                "criticos": [],
                "rede_local_instavel": False,
                "total_verificados": 0,
                "total_problemas": 0
            }

        problemas = analise.get(
            "problemas",
            []
        )

        criticos = analise.get(
            "criticos",
            []
        )

        nao_reconhecidos = [
            item
            for item in problemas
            if item.get(
                "chave"
            )
            not in self.servicos_reconhecidos
        ]

        total_configurado = len(
            self.configuracoes.get(
                "servicos_down_detector",
                []
            )
        )

        total_servicos = max(
            total_configurado,
            len(
                resultados
            )
        )

        online = sum(
            1
            for item in resultados
            if item.get(
                "status"
            )
            == "ONLINE"
        )

        verificados = analise.get(
            "total_verificados",
            0
        )

        if not resultados:
            saude_texto = "AGUARDANDO"
            saude_estado = "neutro"
            saude_subtitulo = "Monitor de Serviços iniciando"

        elif analise.get(
            "rede_local_instavel",
            False
        ):
            saude_texto = "INSTÁVEL"
            saude_estado = "critico"
            saude_subtitulo = "Possível instabilidade da rede local"

        elif criticos:
            saude_texto = "ATENÇÃO"
            saude_estado = "critico"
            saude_subtitulo = (
                f"{len(criticos)} serviço(s) crítico(s)"
            )

        elif problemas:
            saude_texto = "ATENÇÃO"
            saude_estado = "alerta"
            saude_subtitulo = (
                f"{len(problemas)} serviço(s) com alerta"
            )

        else:
            saude_texto = "SAUDÁVEL"
            saude_estado = "normal"
            saude_subtitulo = "Nenhum problema detectado"

        if not resultados:
            servicos_estado = "neutro"
            servicos_subtitulo = "Aguardando primeiro ciclo"

        elif problemas:
            servicos_estado = (
                "critico"
                if criticos
                else "alerta"
            )

            servicos_subtitulo = (
                f"{len(problemas)} com atenção"
            )

        else:
            servicos_estado = "normal"
            servicos_subtitulo = (
                f"{verificados} verificados"
            )

        alertas = []

        for item in nao_reconhecidos:
            status_alerta = str(
                item.get(
                    "status",
                    "-"
                )
            )

            if status_alerta in (
                "SEM RESPOSTA",
                "FALHA HTTP",
                "ERRO"
            ):
                estado_alerta = "critico"
            else:
                estado_alerta = "alerta"

            alertas.append({
                "origem": item.get(
                    "nome",
                    "Serviço"
                ),
                "status": status_alerta,
                "detalhe": item.get(
                    "endereco",
                    ""
                ),
                "estado": estado_alerta
            })

        resumo_hoje = obter_resumo_hoje()

        incidentes_recentes_brutos = listar_incidentes(
            limite=8
        )

        incidentes_abertos = listar_incidentes(
            limite=200,
            somente_abertos=True
        )

        hoje = datetime.now().date()

        registros_hoje = [
            item
            for item in listar_incidentes(
                limite=500
            )
            if str(
                item.get(
                    "inicio",
                    ""
                )
            ).startswith(
                hoje.isoformat()
            )
        ]

        tempo_afetado = 0
        agora = datetime.now()

        for item in registros_hoje:
            duracao = item.get(
                "duracao_segundos"
            )

            if (
                duracao is None
                and not item.get(
                    "encerrado"
                )
            ):
                try:
                    inicio_incidente = datetime.fromisoformat(
                        item[
                            "inicio"
                        ]
                    )

                    duracao = max(
                        0,
                        int(
                            (
                                agora
                                - inicio_incidente
                            ).total_seconds()
                        )
                    )

                except (
                    KeyError,
                    TypeError,
                    ValueError
                ):
                    duracao = 0

            try:
                tempo_afetado += int(
                    duracao
                    or 0
                )
            except (
                TypeError,
                ValueError
            ):
                pass

        incidentes_recentes = []
        atividade_recente = []

        for item in incidentes_recentes_brutos:
            inicio_texto = "-"

            try:
                inicio_obj = datetime.fromisoformat(
                    item.get(
                        "inicio",
                        ""
                    )
                )

                inicio_texto = inicio_obj.strftime(
                    "%d/%m %H:%M:%S"
                )

                horario = inicio_obj.strftime(
                    "%H:%M:%S"
                )

            except (
                TypeError,
                ValueError
            ):
                horario = "-"

            status_texto = (
                "EM ANDAMENTO"
                if not item.get(
                    "encerrado"
                )
                else "NORMALIZADO"
            )

            registro = dict(
                item
            )

            registro[
                "inicio_texto"
            ] = inicio_texto

            registro[
                "status_texto"
            ] = status_texto

            incidentes_recentes.append(
                registro
            )

            atividade_recente.append({
                "horario": horario,
                "origem": item.get(
                    "origem",
                    "-"
                ),
                "evento": item.get(
                    "status_inicial",
                    "-"
                ),
                "status": status_texto
            })

        ping_ativo = (
            self.thread_ping_continuo
            is not None
            and self.thread_ping_continuo.isRunning()
        )

        rota_ativa = (
            self.thread_tracert_continuo
            is not None
            and self.thread_tracert_continuo.isRunning()
        )

        if ping_ativo:
            monitor_ping_texto = (
                f"Ativo para {self.ip_atual or '-'}"
            )
            monitor_ping_estado = "normal"
            monitor_ping_badge = "● ATIVO"
        else:
            monitor_ping_texto = "Inativo"
            monitor_ping_estado = "neutro"
            monitor_ping_badge = "○ INATIVO"

        if rota_ativa:
            monitor_rota_texto = (
                f"Ativo • {self.tracert_ciclos} ciclo(s)"
            )
            monitor_rota_estado = "normal"
            monitor_rota_badge = "● ATIVO"
        else:
            monitor_rota_texto = "Inativo"
            monitor_rota_estado = "neutro"
            monitor_rota_badge = "○ INATIVO"

        if not resultados:
            monitor_servicos_texto = "Aguardando primeiro ciclo"
            monitor_servicos_estado = "neutro"
            monitor_servicos_badge = "● INICIANDO"

        elif problemas:
            monitor_servicos_texto = (
                f"{online}/{total_servicos} online • "
                f"{len(problemas)} alerta(s)"
            )
            monitor_servicos_estado = (
                "critico"
                if criticos
                else "alerta"
            )
            monitor_servicos_badge = "● ALERTA"

        else:
            monitor_servicos_texto = (
                f"{online}/{total_servicos} online"
            )
            monitor_servicos_estado = "normal"
            monitor_servicos_badge = "● ONLINE"

        alertas_estado = (
            "critico"
            if criticos
            else (
                "alerta"
                if alertas
                else "normal"
            )
        )

        servicos_monitoramento = []

        prioridades_status = {
            "SEM RESPOSTA": 0,
            "FALHA HTTP": 0,
            "ERRO": 0,
            "PERDA PERSISTENTE": 0,
            "POSSÍVEL INSTABILIDADE": 1,
            "LATÊNCIA ALTA": 1,
            "ONLINE": 2,
            "AGUARDANDO": 3
        }

        def obter_latencia_dashboard(
            item
        ):
            for chave_latencia in (
                "latencia_ms",
                "latencia",
                "tempo_ms",
                "tempo_resposta_ms",
                "tempo"
            ):
                valor = item.get(
                    chave_latencia
                )

                if isinstance(
                    valor,
                    (
                        int,
                        float
                    )
                ):
                    return float(
                        valor
                    )

            return -1.0

        resultados_dashboard = sorted(
            resultados,
            key=lambda item: (
                prioridades_status.get(
                    str(
                        item.get(
                            "status",
                            ""
                        )
                    ),
                    2
                ),
                -obter_latencia_dashboard(
                    item
                ),
                str(
                    item.get(
                        "nome",
                        ""
                    )
                ).lower()
            )
        )

        for item in resultados_dashboard:
            nome_servico = str(
                item.get(
                    "nome",
                    "Serviço"
                )
            )

            status_servico = str(
                item.get(
                    "status",
                    "AGUARDANDO"
                )
            )

            if status_servico in (
                "SEM RESPOSTA",
                "FALHA HTTP",
                "ERRO"
            ):
                estado_servico = "critico"

            elif status_servico in (
                "POSSÍVEL INSTABILIDADE",
                "LATÊNCIA ALTA"
            ):
                estado_servico = "alerta"

            elif status_servico == "ONLINE":
                estado_servico = "normal"

            else:
                estado_servico = "neutro"

            latencia = None

            for chave_latencia in (
                "latencia_ms",
                "latencia",
                "tempo_ms",
                "tempo_resposta_ms",
                "tempo"
            ):
                valor_latencia = item.get(
                    chave_latencia
                )

                if isinstance(
                    valor_latencia,
                    (
                        int,
                        float
                    )
                ):
                    latencia = float(
                        valor_latencia
                    )
                    break

            if latencia is not None:
                resultado_texto = (
                    f"{latencia:.0f} ms"
                )

            elif status_servico == "POSSÍVEL INSTABILIDADE":
                resultado_texto = "Oscilação"

            else:
                resultado_texto = status_servico

            nome_minusculo = nome_servico.lower()

            if "cloudflare" in nome_minusculo:
                cor_servico = "#f59e0b"
                icone_servico = "globe"

            elif (
                "google" in nome_minusculo
                or "dns" in nome_minusculo
            ):
                cor_servico = "#4285f4"
                icone_servico = "globe"

            elif (
                "steam" in nome_minusculo
                or "jogo" in nome_minusculo
                or "game" in nome_minusculo
            ):
                cor_servico = "#5ea6ff"
                icone_servico = "route"

            elif (
                "gmail" in nome_minusculo
                or "mail" in nome_minusculo
            ):
                cor_servico = "#ff6b6b"
                icone_servico = "document"

            elif "banco" in nome_minusculo:
                cor_servico = "#39d98a"
                icone_servico = "shield"

            else:
                cor_servico = "#2f81f7"
                icone_servico = "server"

            servicos_monitoramento.append({
                "nome": nome_servico,
                "resultado": resultado_texto,
                "estado": estado_servico,
                "cor": cor_servico,
                "icone": icone_servico
            })

        return {
            "saude_texto": saude_texto,
            "saude_estado": saude_estado,
            "saude_subtitulo": saude_subtitulo,

            "servicos_total": total_servicos,
            "servicos_online": online,
            "servicos_estado": servicos_estado,
            "servicos_subtitulo": servicos_subtitulo,
            "servicos_monitoramento": servicos_monitoramento,

            "incidentes_hoje": resumo_hoje.get(
                "total",
                0
            ),
            "incidentes_criticos_hoje": resumo_hoje.get(
                "criticos",
                0
            ),
            "incidentes_andamento": len(
                incidentes_abertos
            ),
            "incidentes_tempo_texto":
                self.formatar_duracao_dashboard(
                    tempo_afetado
                ),
            "incidentes_recentes": incidentes_recentes,

            "alertas_ativos": alertas,
            "alertas_estado": alertas_estado,

            "atividade_recente": atividade_recente[:6],

            "monitor_servicos_texto": monitor_servicos_texto,
            "monitor_servicos_estado": monitor_servicos_estado,
            "monitor_servicos_badge": monitor_servicos_badge,

            "monitor_ping_texto": monitor_ping_texto,
            "monitor_ping_estado": monitor_ping_estado,
            "monitor_ping_badge": monitor_ping_badge,

            "monitor_rota_texto": monitor_rota_texto,
            "monitor_rota_estado": monitor_rota_estado,
            "monitor_rota_badge": monitor_rota_badge
        }

    def atualizar_resumos_interface(
        self
    ):
        if not hasattr(
            self,
            "pagina_dashboard"
        ):
            return

        try:
            resumo = self.obter_resumo_interface()

            self.pagina_dashboard.atualizar(
                resumo
            )

            self.pagina_monitoramento.atualizar(
                resumo
            )

            self.pagina_incidentes.atualizar(
                resumo
            )

        except Exception as erro:
            logger.exception(
                "Falha ao atualizar Dashboard: %s",
                erro
            )

    # ==================================================
    # PING / TRACERT
    # ==================================================
    # ==================================================

    def criar_area_ping_tracert(
        self
    ):
        container = QWidget()

        layout = QHBoxLayout(
            container
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        grupo_ping = QGroupBox(
            "Ping"
        )

        layout_ping = QVBoxLayout(
            grupo_ping
        )

        linha_controle_ping = QHBoxLayout()

        self.botao_ping_continuo = QPushButton(
            "Monitor ICMP"
        )

        self.botao_ping_continuo.setObjectName(
            "botaoMonitorIcmp"
        )

        linha_controle_ping.addWidget(
            self.botao_ping_continuo
        )

        linha_controle_ping.addStretch()

        layout_ping.addLayout(
            linha_controle_ping
        )

        layout_cards = QGridLayout()

        self.card_enviados = PingCard(
            "Enviados"
        )

        self.card_recebidos = PingCard(
            "Recebidos"
        )

        self.card_perda = PingCard(
            "Perda"
        )

        self.card_media = PingCard(
            "Latência média"
        )

        layout_cards.addWidget(
            self.card_enviados,
            0,
            0
        )

        layout_cards.addWidget(
            self.card_recebidos,
            0,
            1
        )

        layout_cards.addWidget(
            self.card_perda,
            0,
            2
        )

        layout_cards.addWidget(
            self.card_media,
            0,
            3
        )

        layout_ping.addLayout(
            layout_cards
        )

        painel = QFrame()

        painel.setObjectName(
            "painelStatusPing"
        )

        layout_status = QVBoxLayout(
            painel
        )

        self.ping_status = QLabel(
            "AGUARDANDO"
        )

        self.ping_status.setObjectName(
            "pingStatus"
        )

        self.ping_detalhes = QLabel(
            "Aguardando diagnóstico..."
        )

        self.ping_detalhes.setObjectName(
            "pingDetalhes"
        )

        self.ping_detalhes.setWordWrap(
            True
        )

        layout_status.addWidget(
            self.ping_status
        )

        layout_status.addWidget(
            self.ping_detalhes
        )

        layout_ping.addWidget(
            painel
        )

        linha_visualizacao_ping = QHBoxLayout()

        titulo = QLabel(
            "Respostas individuais"
        )

        titulo.setObjectName(
            "tituloSecao"
        )

        linha_visualizacao_ping.addWidget(
            titulo
        )

        linha_visualizacao_ping.addStretch()

        label_visualizacao = QLabel(
            "Visualização:"
        )

        label_visualizacao.setObjectName(
            "textoSecundario"
        )

        linha_visualizacao_ping.addWidget(
            label_visualizacao
        )

        self.botao_visualizacao_ping_tabela = QPushButton(
            "Tabela"
        )

        self.botao_visualizacao_ping_tabela.setCheckable(
            True
        )

        self.botao_visualizacao_ping_tabela.setAutoExclusive(
            True
        )

        self.botao_visualizacao_ping_telemetria = QPushButton(
            "Telemetria"
        )

        self.botao_visualizacao_ping_telemetria.setCheckable(
            True
        )

        self.botao_visualizacao_ping_telemetria.setAutoExclusive(
            True
        )

        linha_visualizacao_ping.addWidget(
            self.botao_visualizacao_ping_tabela
        )

        linha_visualizacao_ping.addWidget(
            self.botao_visualizacao_ping_telemetria
        )

        layout_ping.addLayout(
            linha_visualizacao_ping
        )

        self.stack_visualizacao_ping = QStackedWidget()

        self.tabela_ping = QTableWidget()

        self.tabela_ping.setColumnCount(
            5
        )

        self.tabela_ping.setHorizontalHeaderLabels([
            "#",
            "IP",
            "Tempo",
            "TTL",
            "Status"
        ])

        self.configurar_tabela(
            self.tabela_ping
        )

        cabecalho_ping = (
            self.tabela_ping
            .horizontalHeader()
        )

        cabecalho_ping.setSectionResizeMode(
            0,
            QHeaderView
            .ResizeMode
            .ResizeToContents
        )

        cabecalho_ping.setSectionResizeMode(
            1,
            QHeaderView
            .ResizeMode
            .Stretch
        )

        for coluna in range(
            2,
            5
        ):
            cabecalho_ping.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents
            )

        self.telemetria_ping = PingTelemetryWidget(
            limite_latencia=self.configuracoes.get(
                "limite_latencia_ping_ms",
                100
            ),
            max_amostras=1800
        )

        self.stack_visualizacao_ping.addWidget(
            self.tabela_ping
        )

        self.stack_visualizacao_ping.addWidget(
            self.telemetria_ping
        )

        layout_ping.addWidget(
            self.stack_visualizacao_ping,
            1
        )

        self.botao_visualizacao_ping_tabela.clicked.connect(
            self.mostrar_tabela_ping
        )

        self.botao_visualizacao_ping_telemetria.clicked.connect(
            self.mostrar_telemetria_ping
        )

        self.botao_visualizacao_ping_tabela.setChecked(
            True
        )

        grupo_tracert = QGroupBox(
            "Rota"
        )

        layout_tracert = QVBoxLayout(
            grupo_tracert
        )

        linha_controle = QHBoxLayout()

        self.label_tracert_ciclos = QLabel(
            "Ciclos: 0"
        )

        self.label_tracert_ciclos.setObjectName(
            "textoSecundario"
        )

        self.label_tracert_ciclos.setVisible(
            False
        )

        linha_controle.addWidget(
            self.label_tracert_ciclos
        )

        linha_controle.addStretch()

        label_visualizacao_rota = QLabel(
            "Visualização:"
        )

        label_visualizacao_rota.setObjectName(
            "textoSecundario"
        )

        linha_controle.addWidget(
            label_visualizacao_rota
        )

        self.botao_visualizacao_tracert_tabela = QPushButton(
            "Tabela"
        )

        self.botao_visualizacao_tracert_tabela.setCheckable(
            True
        )

        self.botao_visualizacao_tracert_tabela.setAutoExclusive(
            True
        )

        self.botao_visualizacao_tracert_telemetria = QPushButton(
            "Telemetria"
        )

        self.botao_visualizacao_tracert_telemetria.setCheckable(
            True
        )

        self.botao_visualizacao_tracert_telemetria.setAutoExclusive(
            True
        )

        linha_controle.addWidget(
            self.botao_visualizacao_tracert_tabela
        )

        linha_controle.addWidget(
            self.botao_visualizacao_tracert_telemetria
        )

        linha_controle.addSpacing(
            8
        )

        self.botao_tracert_continuo = QPushButton(
            "Monitor de Rota"
        )

        self.botao_tracert_continuo.setObjectName(
            "botaoMonitorRota"
        )

        linha_controle.addWidget(
            self.botao_tracert_continuo
        )

        layout_tracert.addLayout(
            linha_controle
        )

        self.stack_visualizacao_tracert = QStackedWidget()

        self.tabela_tracert = QTableWidget()

        self.configurar_tabela(
            self.tabela_tracert
        )

        self.configurar_tabela_tracert_normal()

        self.telemetria_rota = RouteTelemetryWidget(
            max_amostras=1800
        )

        self.stack_visualizacao_tracert.addWidget(
            self.tabela_tracert
        )

        self.stack_visualizacao_tracert.addWidget(
            self.telemetria_rota
        )

        layout_tracert.addWidget(
            self.stack_visualizacao_tracert,
            1
        )

        self.botao_visualizacao_tracert_tabela.clicked.connect(
            self.mostrar_tabela_tracert
        )

        self.botao_visualizacao_tracert_telemetria.clicked.connect(
            self.mostrar_telemetria_tracert
        )

        self.botao_visualizacao_tracert_tabela.setChecked(
            True
        )

        layout.addWidget(
            grupo_ping,
            1
        )

        layout.addWidget(
            grupo_tracert,
            2
        )

        return container

    def mostrar_tabela_ping(
        self
    ):
        self.visualizacao_ping_atual = "tabela"

        self.stack_visualizacao_ping.setCurrentWidget(
            self.tabela_ping
        )

        self.botao_visualizacao_ping_tabela.setChecked(
            True
        )

    def mostrar_telemetria_ping(
        self
    ):
        self.visualizacao_ping_atual = "telemetria"

        self.stack_visualizacao_ping.setCurrentWidget(
            self.telemetria_ping
        )

        self.botao_visualizacao_ping_telemetria.setChecked(
            True
        )

    def mostrar_tabela_tracert(
        self
    ):
        self.visualizacao_tracert_atual = "tabela"

        self.stack_visualizacao_tracert.setCurrentWidget(
            self.tabela_tracert
        )

        self.botao_visualizacao_tracert_tabela.setChecked(
            True
        )

    def mostrar_telemetria_tracert(
        self
    ):
        self.visualizacao_tracert_atual = "telemetria"

        self.stack_visualizacao_tracert.setCurrentWidget(
            self.telemetria_rota
        )

        self.botao_visualizacao_tracert_telemetria.setChecked(
            True
        )

    def configurar_tabela_tracert_normal(
        self
    ):
        self.tabela_tracert.clear()

        self.tabela_tracert.setColumnCount(
            7
        )

        self.tabela_tracert.setHorizontalHeaderLabels([
            "Salto",
            "IP",
            "Tempo 1",
            "Tempo 2",
            "Tempo 3",
            "Média",
            "Status"
        ])

        cabecalho = (
            self.tabela_tracert
            .horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView
            .ResizeMode
            .ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            1,
            QHeaderView
            .ResizeMode
            .Stretch
        )

        for coluna in range(
            2,
            7
        ):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents
            )

    def configurar_tabela_tracert_continuo(
        self
    ):
        self.tabela_tracert.clear()

        self.tabela_tracert.setColumnCount(
            10
        )

        self.tabela_tracert.setHorizontalHeaderLabels([
            "Salto",
            "IP",
            "Enviados",
            "Recebidos",
            "Perda",
            "Melhor",
            "Média",
            "Pior",
            "Último",
            "Status"
        ])

        cabecalho = (
            self.tabela_tracert
            .horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView
            .ResizeMode
            .ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            1,
            QHeaderView
            .ResizeMode
            .Stretch
        )

        for coluna in range(
            2,
            10
        ):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents
            )

    # ==================================================
    # PORTAS
    # ==================================================

    def criar_area_portas(
        self
    ):
        grupo = QGroupBox(
            "Portas TCP"
        )

        grupo.setMinimumHeight(
            220
        )

        layout = QVBoxLayout(
            grupo
        )

        self.tabela_portas = QTableWidget()

        self.tabela_portas.setColumnCount(
            5
        )

        self.tabela_portas.setHorizontalHeaderLabels([
            "Porta",
            "Serviço",
            "Interface Web",
            "Status",
            "Ação"
        ])

        self.configurar_tabela(
            self.tabela_portas
        )

        self.tabela_portas.verticalHeader().setDefaultSectionSize(
            42
        )

        cabecalho = (
            self.tabela_portas
            .horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView
            .ResizeMode
            .ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            1,
            QHeaderView
            .ResizeMode
            .Stretch
        )

        cabecalho.setSectionResizeMode(
            2,
            QHeaderView
            .ResizeMode
            .ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            3,
            QHeaderView
            .ResizeMode
            .ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            4,
            QHeaderView
            .ResizeMode
            .Fixed
        )

        self.tabela_portas.setColumnWidth(
            4,
            180
        )

        layout.addWidget(
            self.tabela_portas
        )

        return grupo

    def configurar_tabela(
        self,
        tabela
    ):
        tabela.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        tabela.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        tabela.setAlternatingRowColors(
            True
        )

        tabela.verticalHeader().setVisible(
            False
        )

    # ==================================================
    # EVENTOS
    # ==================================================

    def conectar_eventos(
        self
    ):
        self.botao_executar.clicked.connect(
            self.alternar_diagnostico
        )

        self.campo_ip.returnPressed.connect(
            self.acao_enter_ip
        )

        self.botao_ping_continuo.clicked.connect(
            self.alternar_ping_continuo
        )

        self.botao_tracert_continuo.clicked.connect(
            self.alternar_tracert_continuo
        )

        self.pagina_incidentes.solicitar_abrir_registro.connect(
            self.abrir_incidentes
        )

        self.botao_configuracoes.clicked.connect(
            self.abrir_configuracoes
        )

        self.botao_logs.clicked.connect(
            self.abrir_logs
        )

        self.botao_nav_dashboard.clicked.connect(
            lambda:
                self.mostrar_pagina(
                    "dashboard"
                )
        )

        self.botao_nav_diagnostico.clicked.connect(
            lambda:
                self.mostrar_pagina(
                    "diagnostico"
                )
        )

        self.botao_nav_monitoramento.clicked.connect(
            lambda:
                self.mostrar_pagina(
                    "monitoramento"
                )
        )

        self.botao_nav_incidentes.clicked.connect(
            lambda:
                self.mostrar_pagina(
                    "incidentes"
                )
        )

        self.botao_nav_relatorios.clicked.connect(
            lambda:
                self.mostrar_pagina(
                    "relatorios"
                )
        )

        self.pagina_dashboard.solicitar_diagnostico.connect(
            self.ir_para_diagnostico
        )

        self.pagina_dashboard.solicitar_ping.connect(
            self.ir_para_monitor_icmp
        )

        self.pagina_dashboard.solicitar_rota.connect(
            self.ir_para_monitor_rota
        )

        self.pagina_dashboard.solicitar_servicos.connect(
            self.abrir_down_detector
        )

        self.pagina_dashboard.solicitar_incidentes.connect(
            lambda:
                self.mostrar_pagina(
                    "incidentes"
                )
        )

        self.pagina_monitoramento.solicitar_ping.connect(
            self.ir_para_monitor_icmp
        )

        self.pagina_monitoramento.solicitar_rota.connect(
            self.ir_para_monitor_rota
        )

        self.pagina_monitoramento.solicitar_servicos.connect(
            self.abrir_down_detector
        )

        self.pagina_relatorios.botao_diagnostico.clicked.connect(
            self.exportar_diagnostico_txt
        )

        self.pagina_relatorios.botao_rota_txt.clicked.connect(
            self.exportar_sessao_tracert_txt
        )

        self.pagina_relatorios.botao_rota_csv.clicked.connect(
            self.exportar_sessao_tracert_csv
        )

        self.pagina_relatorios.botao_rota_json.clicked.connect(
            self.exportar_sessao_tracert_json
        )

        self.pagina_relatorios.botao_config_export.clicked.connect(
            self.exportar_backup_configuracoes
        )

        self.pagina_relatorios.botao_config_import.clicked.connect(
            self.importar_backup_configuracoes
        )

    def acao_enter_ip(
        self
    ):
        if (
            self.thread_diagnostico is None
            and self.thread_ping_continuo is None
            and self.thread_tracert_continuo is None
        ):
            self.iniciar_diagnostico()

    # ==================================================
    # DOWNDETECTOR
    # ==================================================

    def reiniciar_down_detector(
        self
    ):
        thread = (
            self.thread_down_detector
        )

        if (
            thread is not None
            and thread.isRunning()
        ):
            self.down_detector_reinicio_pendente = True

            logger.info(
                "Reinício do Monitor de Serviços solicitado."
            )

            if hasattr(
                thread,
                "solicitar_parada"
            ):
                thread.solicitar_parada()
            else:
                thread.requestInterruption()

            return

        self.down_detector_reinicio_pendente = False

        self.iniciar_down_detector()

    def iniciar_down_detector(
        self
    ):
        self.resultados_down_detector = {}

        self.servicos_reconhecidos.clear()

        servicos = self.configuracoes.get(
            "servicos_down_detector",
            []
        )

        self.janela_down_detector.atualizar_progresso(
            0,
            len(
                servicos
            )
        )

        chaves_atuais = {
            criar_chave_servico(
                servico
            )
            for servico in servicos
        }

        self.servicos_indisponiveis_alertados.intersection_update(
            chaves_atuais
        )

        self.ultimos_alertas_servicos = {
            chave: instante
            for chave, instante
            in self.ultimos_alertas_servicos.items()
            if chave in chaves_atuais
        }

        for indice, servico in enumerate(
            servicos
        ):
            tipo = servico.get(
                "tipo",
                "PING"
            )

            chave = criar_chave_servico(
                servico
            )

            self.resultados_down_detector[
                indice
            ] = {
                "id": indice,
                "chave": chave,
                "nome":
                    servico.get(
                        "nome",
                        "Serviço"
                    ),
                "endereco":
                    servico.get(
                        "endereco",
                        ""
                    ),
                "tipo": tipo,
                "latencia": None,
                "codigo_http": None,
                "variacao": 0,
                "perdas_recentes": 0,
                "status": "AGUARDANDO",
                "ultima_verificacao": "-"
            }

        self.atualizar_down_detector_ui()

        if not servicos:
            self.thread_down_detector = None

            logger.info(
                "Monitor de Serviços não iniciado: "
                "nenhum serviço cadastrado."
            )

            return

        thread = DownDetectorThread(
            servicos,
            self.configuracoes[
                "intervalo_down_detector"
            ],
            self.configuracoes[
                "limite_variacao_ms"
            ],
            self.configuracoes[
                "limite_variacao_http_ms"
            ],
            self.configuracoes[
                "falhas_down_detector_offline"
            ],
            self.configuracoes.get(
                "limite_latencia_ping_ms",
                100
            ),
            self.configuracoes.get(
                "limite_latencia_http_ms",
                1000
            )
        )

        self.thread_down_detector = thread

        thread.resultado_servico.connect(
            self.receber_resultado_down_detector
        )

        thread.progresso_ciclo.connect(
            self.receber_progresso_down_detector
        )

        thread.ciclo_concluido.connect(
            self.processar_alertas_down_detector
        )

        thread.finished.connect(
            self.down_detector_finalizado
        )

        thread.start()

    def down_detector_finalizado(
        self
    ):
        thread_finalizada = (
            self.sender()
        )

        if (
            self.thread_down_detector
            is thread_finalizada
        ):
            self.thread_down_detector = None

        logger.info(
            "Thread do Monitor de Serviços encerrada."
        )

        if self.encerramento_real:
            self.down_detector_reinicio_pendente = False
            return

        if self.down_detector_reinicio_pendente:
            self.down_detector_reinicio_pendente = False

            logger.info(
                "Aplicando novas configurações "
                "ao Monitor de Serviços."
            )

            self.iniciar_down_detector()

    def parar_down_detector(
        self,
        aguardar=False
    ):
        thread = (
            self.thread_down_detector
        )

        self.down_detector_reinicio_pendente = False

        if thread is None:
            return

        if thread.isRunning():
            if hasattr(
                thread,
                "solicitar_parada"
            ):
                thread.solicitar_parada()
            else:
                thread.requestInterruption()

            if aguardar:
                logger.info(
                    "Aguardando encerramento do "
                    "Monitor de Serviços..."
                )

                # No encerramento real da aplicação é melhor
                # aguardar a thread terminar do que destruir
                # um QThread ainda em execução.
                thread.wait()

                if (
                    self.thread_down_detector
                    is thread
                ):
                    self.thread_down_detector = None

        else:
            if (
                self.thread_down_detector
                is thread
            ):
                self.thread_down_detector = None

    def receber_progresso_down_detector(
        self,
        verificados,
        total
    ):
        self.janela_down_detector.atualizar_progresso(
            verificados,
            total
        )

    def receber_resultado_down_detector(
        self,
        resultado
    ):
        identificador = resultado[
            "id"
        ]

        chave = resultado.get(
            "chave",
            ""
        )

        if (
            resultado.get(
                "status"
            )
            == "ONLINE"
        ):
            self.servicos_reconhecidos.discard(
                chave
            )

        self.resultados_down_detector[
            identificador
        ] = resultado

        self.atualizar_down_detector_ui()

    def reconhecer_alerta_down_detector(
        self,
        chave
    ):
        self.servicos_reconhecidos.add(
            chave
        )

        self.atualizar_down_detector_ui()

    def atualizar_down_detector_ui(
        self
    ):
        resultados = list(
            self.resultados_down_detector
            .values()
        )

        self.janela_down_detector.atualizar_servicos(
            resultados,
            self.servicos_reconhecidos
        )

        analise_rede = analisar_saude_rede(
            resultados
        )

        problemas = analise_rede[
            "problemas"
        ]

        nao_reconhecidos = [
            item
            for item in problemas
            if item.get(
                "chave"
            )
            not in self.servicos_reconhecidos
        ]

        criticos_nao_reconhecidos = [
            item
            for item in analise_rede[
                "criticos"
            ]
            if item.get(
                "chave"
            )
            not in self.servicos_reconhecidos
        ]

        quantidade = len(
            nao_reconhecidos
        )

        rede_local_instavel = (
            analise_rede[
                "rede_local_instavel"
            ]
        )

        # ------------------------------------------
        # Grande quantidade de falhas simultâneas
        # ------------------------------------------

        if (
            rede_local_instavel
            and quantidade > 0
        ):
            self.botao_down_detector.setText(
                "⚠ Rede local instável  "
                f"{quantidade}"
            )

            self.botao_down_detector.setToolTip(
                "Monitor de Serviços — possível instabilidade da rede local"
            )

            if criticos_nao_reconhecidos:
                estado = "critico"
            else:
                estado = "alerta"

        # ------------------------------------------
        # Problemas individuais
        # ------------------------------------------

        elif quantidade > 0:
            self.botao_down_detector.setText(
                f"⚠ Serviços  {quantidade}"
            )

            self.botao_down_detector.setToolTip(
                f"Monitor de Serviços — {quantidade} alerta(s)"
            )

            if criticos_nao_reconhecidos:
                estado = "critico"
            else:
                estado = "alerta"

        # ------------------------------------------
        # Existem problemas, mas todos já foram
        # reconhecidos pelo usuário.
        # ------------------------------------------

        elif problemas:
            self.botao_down_detector.setText(
                "Monitor de Serviços"
            )

            self.botao_down_detector.setToolTip(
                "Monitor de Serviços — alertas reconhecidos"
            )

            estado = "reconhecido"

        # ------------------------------------------
        # Todos os serviços normais.
        # ------------------------------------------

        elif resultados:
            self.botao_down_detector.setText(
                "Monitor de Serviços"
            )

            self.botao_down_detector.setToolTip(
                "Monitor de Serviços — todos os serviços normais"
            )

            estado = "ok"

        else:
            self.botao_down_detector.setText(
                "Monitor de Serviços"
            )

            self.botao_down_detector.setToolTip(
                "Abrir Monitor de Serviços"
            )

            estado = "vazio"

        self.botao_down_detector.setProperty(
            "estado",
            estado
        )

        estilo = (
            self.botao_down_detector
            .style()
        )

        estilo.unpolish(
            self.botao_down_detector
        )

        estilo.polish(
            self.botao_down_detector
        )

    def obter_configuracao_servico_down_detector(
        self,
        chave
    ):
        for servico in self.configuracoes.get(
            "servicos_down_detector",
            []
        ):
            if (
                criar_chave_servico(
                    servico
                )
                == chave
            ):
                return servico

        return None

    def obter_audio_alerta_servico(
        self,
        item
    ):
        """
        Retorna:
            modo,
            arquivo,
            origem

        origem informa se o som veio da configuração
        global ou da configuração específica do serviço.
        """
        modo_global = self.configuracoes.get(
            "alerta_sonoro_modo",
            "padrao"
        )

        arquivo_global = self.configuracoes.get(
            "alerta_sonoro_arquivo",
            ""
        )

        chave = item.get(
            "chave",
            ""
        )

        configuracao_servico = (
            self.obter_configuracao_servico_down_detector(
                chave
            )
        )

        if not configuracao_servico:
            return (
                modo_global,
                arquivo_global,
                "global"
            )

        if not configuracao_servico.get(
            "alerta_individual_ativado",
            False
        ):
            return (
                modo_global,
                arquivo_global,
                "global"
            )

        modo_individual = configuracao_servico.get(
            "alerta_individual_modo",
            "global"
        )

        if modo_individual == "padrao":
            return (
                "padrao",
                "",
                "individual"
            )

        if modo_individual == "personalizado":
            arquivo_individual = configuracao_servico.get(
                "alerta_individual_arquivo",
                ""
            )

            return (
                "personalizado",
                arquivo_individual,
                "individual"
            )

        return (
            modo_global,
            arquivo_global,
            "individual-global"
        )

    def obter_cooldown_alertas_segundos(
        self
    ):
        minutos = self.configuracoes.get(
            "alerta_cooldown_minutos",
            5
        )

        try:
            minutos = float(
                minutos
            )

        except (
            TypeError,
            ValueError
        ):
            minutos = 5.0

        minutos = max(
            0.0,
            minutos
        )

        return minutos * 60.0

    def verificar_cooldown_alerta(
        self,
        ultimo_disparo
    ):
        """
        Retorna:
            permitido,
            restante_segundos

        Cooldown 0 significa desativado.
        """
        cooldown = self.obter_cooldown_alertas_segundos()

        if cooldown <= 0:
            return (
                True,
                0.0
            )

        if ultimo_disparo is None:
            return (
                True,
                0.0
            )

        decorrido = (
            time.monotonic()
            - ultimo_disparo
        )

        restante = max(
            0.0,
            cooldown - decorrido
        )

        return (
            restante <= 0,
            restante
        )

    def formatar_tempo_cooldown(
        self,
        segundos
    ):
        segundos = max(
            0,
            int(
                round(
                    segundos
                )
            )
        )

        if segundos < 60:
            return f"{segundos}s"

        minutos, segundos_restantes = divmod(
            segundos,
            60
        )

        if segundos_restantes == 0:
            return f"{minutos} min"

        return (
            f"{minutos} min "
            f"{segundos_restantes}s"
        )

    def valor_numerico_seguro(
        self,
        valor,
        padrao=0.0
    ):
        try:
            return float(
                valor
            )

        except (
            TypeError,
            ValueError
        ):
            return float(
                padrao
            )

    def determinar_causa_provavel_rede(
        self,
        resultados
    ):
        """
        Classifica a causa provável do incidente geral.

        O NDT observa sintomas em múltiplos destinos. Por isso
        usamos "causa provável", e não uma afirmação absoluta
        sobre a origem física da falha.
        """
        verificados = [
            item
            for item in resultados
            if item.get(
                "status"
            )
            not in {
                None,
                "",
                "AGUARDANDO"
            }
        ]

        if not verificados:
            return "Instabilidade generalizada"

        indisponiveis = sum(
            1
            for item in verificados
            if item.get(
                "status"
            )
            in {
                "SEM RESPOSTA",
                "FALHA HTTP",
                "ERRO"
            }
        )

        com_perdas = sum(
            1
            for item in verificados
            if self.valor_numerico_seguro(
                item.get(
                    "perdas_recentes",
                    0
                )
            ) > 0
        )

        com_oscilacao = sum(
            1
            for item in verificados
            if (
                item.get(
                    "status"
                )
                == "POSSÍVEL INSTABILIDADE"
                or self.valor_numerico_seguro(
                    item.get(
                        "variacao",
                        0
                    )
                )
                >= (
                    self.configuracoes.get(
                        "limite_variacao_http_ms",
                        500
                    )
                    if str(
                        item.get(
                            "tipo",
                            "PING"
                        )
                    ).upper().startswith(
                        "HTTP"
                    )
                    else self.configuracoes.get(
                        "limite_variacao_ms",
                        50
                    )
                )
            )
        )

        latencia_alta = sum(
            1
            for item in verificados
            if item.get(
                "status"
            )
            == "LATÊNCIA ALTA"
        )

        if (
            indisponiveis >= 2
            and indisponiveis
            >= max(
                com_perdas,
                com_oscilacao,
                latencia_alta
            )
        ):
            return "Indisponibilidade generalizada"

        if (
            com_perdas >= 2
            and com_perdas
            >= max(
                com_oscilacao,
                latencia_alta
            )
        ):
            return "Perda generalizada de pacotes"

        if (
            com_oscilacao >= 2
            and com_oscilacao
            >= latencia_alta
        ):
            return "Oscilação elevada de latência"

        if latencia_alta >= 2:
            return "Latência generalizada elevada"

        sintomas = sum([
            indisponiveis > 0,
            com_perdas > 0,
            com_oscilacao > 0,
            latencia_alta > 0
        ])

        if sintomas >= 2:
            return "Instabilidade mista"

        return "Instabilidade generalizada"

    def obter_metricas_incidente(
        self,
        item
    ):
        return {
            "max_perda":
                self.valor_numerico_seguro(
                    item.get(
                        "perdas_recentes",
                        0
                    )
                ),

            "max_latencia":
                self.valor_numerico_seguro(
                    item.get(
                        "latencia",
                        0
                    )
                ),

            "max_oscilacao":
                self.valor_numerico_seguro(
                    item.get(
                        "variacao",
                        0
                    )
                )
        }

    def processar_incidentes_servicos(
        self,
        resultados,
        permitir_novos=True
    ):
        estados_criticos = {
            "SEM RESPOSTA",
            "FALHA HTTP",
            "ERRO"
        }

        atuais = {
            item.get(
                "chave",
                ""
            ): item
            for item in resultados
            if item.get(
                "chave"
            )
            and item.get(
                "status"
            )
            in estados_criticos
        }

        # -------------------------------------------------
        # Abre ou atualiza incidentes críticos.
        # -------------------------------------------------
        for chave, item in atuais.items():
            nome = item.get(
                "nome",
                "Serviço"
            )

            endereco = item.get(
                "endereco",
                ""
            )

            status = item.get(
                "status",
                "ERRO"
            )

            metricas = self.obter_metricas_incidente(
                item
            )

            incidente_id = (
                self.incidentes_servicos_ativos.get(
                    chave
                )
            )

            if incidente_id is None:
                existente = obter_incidente_aberto(
                    "SERVICO",
                    nome
                )

                if existente is not None:
                    incidente_id = existente.get(
                        "id"
                    )

                    logger.info(
                        "Incidente de serviço retomado | "
                        "ID=%s | Serviço=%s",
                        incidente_id,
                        nome
                    )

                elif permitir_novos:
                    incidente_id = abrir_incidente(
                        tipo="SERVICO",
                        origem=nome,
                        endereco=endereco,
                        status_inicial=status,
                        causa_provavel=status,
                        max_perda=metricas[
                            "max_perda"
                        ],
                        max_latencia=metricas[
                            "max_latencia"
                        ],
                        max_oscilacao=metricas[
                            "max_oscilacao"
                        ],
                        detalhes=(
                            "Falha crítica detectada "
                            "pelo Monitor de Serviços."
                        )
                    )

                    logger.warning(
                        "Incidente de serviço aberto | "
                        "ID=%s | Serviço=%s | "
                        "Endereço=%s | Status=%s",
                        incidente_id,
                        nome,
                        endereco,
                        status
                    )

                if incidente_id is not None:
                    self.incidentes_servicos_ativos[
                        chave
                    ] = incidente_id

            if incidente_id is not None:
                atualizar_metricas_incidente(
                    incidente_id,
                    max_perda=metricas[
                        "max_perda"
                    ],
                    max_latencia=metricas[
                        "max_latencia"
                    ],
                    max_oscilacao=metricas[
                        "max_oscilacao"
                    ],
                    causa_provavel=status
                )

        # -------------------------------------------------
        # Encerra incidentes que voltaram a responder.
        # -------------------------------------------------
        chaves_ativas = set(
            self.incidentes_servicos_ativos
        )

        chaves_criticas = set(
            atuais
        )

        normalizados = (
            chaves_ativas
            - chaves_criticas
        )

        for chave in normalizados:
            incidente_id = (
                self.incidentes_servicos_ativos.get(
                    chave
                )
            )

            item_atual = next(
                (
                    item
                    for item in resultados
                    if item.get(
                        "chave"
                    ) == chave
                ),
                None
            )

            if item_atual is None:
                detalhes = (
                    "Incidente encerrado porque o serviço "
                    "deixou de fazer parte do ciclo atual "
                    "de monitoramento."
                )

                nome = chave

            else:
                nome = item_atual.get(
                    "nome",
                    "Serviço"
                )

                detalhes = (
                    "Serviço voltou a responder. "
                    "Status após a falha: "
                    f"{item_atual.get('status', 'ONLINE')}."
                )

            if (
                incidente_id is not None
                and encerrar_incidente(
                    incidente_id,
                    detalhes=detalhes
                )
            ):
                logger.info(
                    "Incidente de serviço encerrado | "
                    "ID=%s | Serviço=%s",
                    incidente_id,
                    nome
                )

            self.incidentes_servicos_ativos.pop(
                chave,
                None
            )

    def processar_incidente_rede_local(
        self,
        resultados,
        analise_rede,
        permitir_novo=True
    ):
        rede_instavel = bool(
            analise_rede.get(
                "rede_local_instavel",
                False
            )
        )

        if rede_instavel:
            causa = (
                self.determinar_causa_provavel_rede(
                    resultados
                )
            )

            self.incidente_rede_local_causa = causa

            max_latencia = max(
                (
                    self.valor_numerico_seguro(
                        item.get(
                            "latencia",
                            0
                        )
                    )
                    for item in resultados
                ),
                default=0.0
            )

            max_oscilacao = max(
                (
                    self.valor_numerico_seguro(
                        item.get(
                            "variacao",
                            0
                        )
                    )
                    for item in resultados
                ),
                default=0.0
            )

            max_perda = max(
                (
                    self.valor_numerico_seguro(
                        item.get(
                            "perdas_recentes",
                            0
                        )
                    )
                    for item in resultados
                ),
                default=0.0
            )

            if self.incidente_rede_local_id is None:
                existente = obter_incidente_aberto(
                    "REDE_LOCAL",
                    "Rede local"
                )

                if existente is not None:
                    self.incidente_rede_local_id = (
                        existente.get(
                            "id"
                        )
                    )

                    logger.info(
                        "Incidente de rede local retomado | "
                        "ID=%s",
                        self.incidente_rede_local_id
                    )

                elif permitir_novo:
                    self.incidente_rede_local_id = abrir_incidente(
                        tipo="REDE_LOCAL",
                        origem="Rede local",
                        status_inicial="REDE LOCAL INSTÁVEL",
                        causa_provavel=causa,
                        max_servicos_afetados=analise_rede.get(
                            "total_problemas",
                            0
                        ),
                        max_perda=max_perda,
                        max_latencia=max_latencia,
                        max_oscilacao=max_oscilacao,
                        detalhes=(
                            "Instabilidade simultânea detectada "
                            "em múltiplos serviços."
                        )
                    )

                    logger.warning(
                        "Incidente de rede local aberto | "
                        "ID=%s | Causa provável=%s | "
                        "Serviços afetados=%s/%s",
                        self.incidente_rede_local_id,
                        causa,
                        analise_rede.get(
                            "total_problemas",
                            0
                        ),
                        analise_rede.get(
                            "total_verificados",
                            0
                        )
                    )

            if self.incidente_rede_local_id is not None:
                atualizar_metricas_incidente(
                    self.incidente_rede_local_id,
                    max_servicos_afetados=analise_rede.get(
                        "total_problemas",
                        0
                    ),
                    max_perda=max_perda,
                    max_latencia=max_latencia,
                    max_oscilacao=max_oscilacao,
                    causa_provavel=causa
                )

            return

        if self.incidente_rede_local_id is None:
            return

        incidente_id = (
            self.incidente_rede_local_id
        )

        causa = (
            self.incidente_rede_local_causa
            or "Instabilidade generalizada"
        )

        if encerrar_incidente(
            incidente_id,
            causa_provavel=causa,
            detalhes=(
                "A condição de instabilidade geral "
                "foi normalizada."
            )
        ):
            logger.info(
                "Incidente de rede local encerrado | "
                "ID=%s | Causa provável=%s",
                incidente_id,
                causa
            )

        self.incidente_rede_local_id = None
        self.incidente_rede_local_causa = ""

    def executar_limpeza_incidentes(
        self,
        forcar=False
    ):
        """
        Remove incidentes normalizados além do período de retenção.

        A limpeza é feita na inicialização, após alterações de
        configuração e, no máximo, uma vez a cada 6 horas durante
        o monitoramento contínuo.
        """
        agora = time.monotonic()

        if (
            not forcar
            and self.ultima_limpeza_incidentes_monotonic is not None
            and (
                agora
                - self.ultima_limpeza_incidentes_monotonic
            ) < 21600
        ):
            return

        retencao = self.configuracoes.get(
            "registro_incidentes_retencao_dias",
            90
        )

        try:
            removidos = limpar_incidentes_antigos(
                retencao
            )

            self.ultima_limpeza_incidentes_monotonic = agora

            if removidos:
                logger.info(
                    "Limpeza automática do Registro de Incidentes | "
                    "Removidos=%s | Retenção=%s dias",
                    removidos,
                    retencao
                )

        except Exception as erro:
            logger.exception(
                "Falha ao executar limpeza automática "
                "do Registro de Incidentes: %s",
                erro
            )

    def processar_registro_incidentes(
        self,
        resultados,
        analise_rede
    ):
        """
        O registro é independente dos alertas sonoros.

        Mesmo que um som seja desativado, reconhecido ou
        suprimido por cooldown, o incidente continua sendo
        registrado normalmente.
        """
        try:
            registrar_novos = bool(
                self.configuracoes.get(
                    "registro_incidentes_ativado",
                    True
                )
            )

            self.processar_incidentes_servicos(
                resultados,
                permitir_novos=registrar_novos
            )

            self.processar_incidente_rede_local(
                resultados,
                analise_rede,
                permitir_novo=registrar_novos
            )

            self.executar_limpeza_incidentes()

            if (
                self.janela_incidentes is not None
                and self.janela_incidentes.isVisible()
            ):
                self.janela_incidentes.atualizar()

            self.atualizar_resumos_interface()

        except Exception as erro:
            # Uma falha no histórico nunca deve interromper
            # o Monitor de Serviços.
            logger.exception(
                "Falha ao processar Registro de Incidentes: %s",
                erro
            )

    def processar_alertas_down_detector(
        self
    ):
        """
        Processa alertas somente após um ciclo completo do
        Monitor de Serviços. Isso evita decisões baseadas em
        resultados parciais enquanto a thread percorre a lista.
        """
        resultados = list(
            self.resultados_down_detector
            .values()
        )

        analise_rede = analisar_saude_rede(
            resultados
        )

        if (
            analise_rede[
                "total_verificados"
            ] == 0
        ):
            return

        rede_local_instavel = (
            analise_rede[
                "rede_local_instavel"
            ]
        )

        self.janela_down_detector.atualizar_resumo(
            total=len(
                resultados
            ),
            verificados=analise_rede[
                "total_verificados"
            ],
            alertas=analise_rede[
                "total_problemas"
            ],
            criticos=len(
                analise_rede[
                    "criticos"
                ]
            )
        )

        # O histórico é processado antes da lógica sonora.
        # Assim ele não depende do cooldown nem da prioridade
        # do alerta geral sobre os alertas individuais.
        self.processar_registro_incidentes(
            resultados,
            analise_rede
        )

        # -------------------------------------------------
        # ALERTA GERAL
        # -------------------------------------------------

        if (
            rede_local_instavel
            and not self.rede_local_instavel_ativa
        ):
            logger.warning(
                "Possível instabilidade da rede local | "
                "Serviços com problema=%s/%s | "
                "Percentual=%s%%",
                analise_rede[
                    "total_problemas"
                ],
                analise_rede[
                    "total_verificados"
                ],
                analise_rede[
                    "percentual_problemas"
                ]
            )

            if self.configuracoes.get(
                "alerta_sonoro_geral_ativado",
                True
            ):
                permitido, restante = (
                    self.verificar_cooldown_alerta(
                        self.ultimo_alerta_geral_monotonic
                    )
                )

                if permitido:
                    alerta_reproduzido = tocar_alerta(
                        modo=self.configuracoes.get(
                            "alerta_sonoro_modo",
                            "padrao"
                        ),
                        arquivo=self.configuracoes.get(
                            "alerta_sonoro_arquivo",
                            ""
                        ),
                        assincrono=True
                    )

                    if alerta_reproduzido:
                        self.ultimo_alerta_geral_monotonic = (
                            time.monotonic()
                        )

                        logger.warning(
                            "Alerta sonoro geral disparado | "
                            "Motivo=Rede local instável"
                        )

                    else:
                        logger.warning(
                            "Não foi possível reproduzir "
                            "o alerta sonoro geral."
                        )

                else:
                    logger.info(
                        "Alerta sonoro geral suprimido por cooldown | "
                        "Restante=%s",
                        self.formatar_tempo_cooldown(
                            restante
                        )
                    )

        elif (
            not rede_local_instavel
            and self.rede_local_instavel_ativa
        ):
            logger.info(
                "Rede local voltou ao estado normal | "
                "Serviços com problema=%s/%s",
                analise_rede[
                    "total_problemas"
                ],
                analise_rede[
                    "total_verificados"
                ]
            )

            logger.info(
                "Alerta sonoro geral rearmado."
            )

        self.rede_local_instavel_ativa = (
            rede_local_instavel
        )

        # -------------------------------------------------
        # ALERTAS INDIVIDUAIS DE INDISPONIBILIDADE
        # -------------------------------------------------

        criticos_atuais = {
            item.get(
                "chave",
                ""
            ): item
            for item in resultados
            if item.get(
                "status"
            )
            in {
                "SEM RESPOSTA",
                "FALHA HTTP"
            }
            and item.get(
                "chave"
            )
        }

        chaves_criticas = set(
            criticos_atuais
        )

        # Rearma serviços que voltaram a responder.
        recuperados = (
            self.servicos_indisponiveis_alertados
            - chaves_criticas
        )

        for chave in recuperados:
            servico = next(
                (
                    item
                    for item in resultados
                    if item.get(
                        "chave"
                    ) == chave
                ),
                None
            )

            if servico is not None:
                logger.info(
                    "Serviço normalizado | "
                    "Nome=%s | Endereço=%s | Status=%s",
                    servico.get(
                        "nome",
                        "Serviço"
                    ),
                    servico.get(
                        "endereco",
                        ""
                    ),
                    servico.get(
                        "status",
                        "ONLINE"
                    )
                )

        self.servicos_indisponiveis_alertados.difference_update(
            recuperados
        )

        # Se o quadro geral já caracteriza falha de rede,
        # o alerta geral tem prioridade. Não tocamos vários
        # alertas individuais no mesmo evento.
        if rede_local_instavel:
            return

        if not self.configuracoes.get(
            "alerta_sonoro_servico_indisponivel_ativado",
            True
        ):
            return

        novos_indisponiveis = [
            item
            for chave, item
            in criticos_atuais.items()
            if chave
            not in self.servicos_indisponiveis_alertados
        ]

        if not novos_indisponiveis:
            return

        alertas_agendados = 0

        for item in novos_indisponiveis:
            nome = item.get(
                "nome",
                "Serviço"
            )

            endereco = item.get(
                "endereco",
                ""
            )

            status = item.get(
                "status",
                ""
            )

            chave = item.get(
                "chave",
                ""
            )

            modo_audio, arquivo_audio, origem_audio = (
                self.obter_audio_alerta_servico(
                    item
                )
            )

            ultimo_disparo = (
                self.ultimos_alertas_servicos.get(
                    chave
                )
            )

            permitido, restante = (
                self.verificar_cooldown_alerta(
                    ultimo_disparo
                )
            )

            logger.warning(
                "Serviço indisponível | "
                "Nome=%s | Endereço=%s | Status=%s | "
                "Falhas consecutivas=%s | "
                "Origem do som=%s | Modo=%s",
                nome,
                endereco,
                status,
                item.get(
                    "falhas_consecutivas",
                    0
                ),
                origem_audio,
                modo_audio
            )

            if permitido:
                alerta_reproduzido = tocar_alerta(
                    modo=modo_audio,
                    arquivo=arquivo_audio,
                    assincrono=True
                )

                if alerta_reproduzido:
                    alertas_agendados += 1

                    if chave:
                        self.ultimos_alertas_servicos[
                            chave
                        ] = time.monotonic()

                    logger.warning(
                        "Alerta sonoro de serviço indisponível "
                        "agendado | Serviço=%s | "
                        "Origem=%s | Modo=%s",
                        nome,
                        origem_audio,
                        modo_audio
                    )

                else:
                    logger.warning(
                        "Não foi possível agendar o alerta "
                        "sonoro do serviço | Serviço=%s | "
                        "Origem=%s | Modo=%s",
                        nome,
                        origem_audio,
                        modo_audio
                    )

            else:
                logger.info(
                    "Alerta sonoro de serviço suprimido por cooldown | "
                    "Serviço=%s | Restante=%s",
                    nome,
                    self.formatar_tempo_cooldown(
                        restante
                    )
                )

            # Mesmo quando o som é suprimido pelo cooldown,
            # marcamos a ocorrência atual como reconhecida para
            # não reavaliá-la em todos os ciclos. Ela será
            # rearmada quando o serviço normalizar.
            if chave:
                self.servicos_indisponiveis_alertados.add(
                    chave
                )

        logger.info(
            "Processamento de alertas individuais concluído | "
            "Novos indisponíveis=%s | Sons agendados=%s",
            len(
                novos_indisponiveis
            ),
            alertas_agendados
        )

    def abrir_down_detector(
        self
    ):
        self.atualizar_down_detector_ui()

        self.janela_down_detector.show()

        self.janela_down_detector.raise_()

        self.janela_down_detector.activateWindow()

    def abrir_incidentes(
        self
    ):
        if self.janela_incidentes is None:
            self.janela_incidentes = IncidentsWindow(
                self
            )

        self.janela_incidentes.atualizar()
        self.janela_incidentes.show()
        self.janela_incidentes.raise_()
        self.janela_incidentes.activateWindow()

    # ==================================================
    # VALIDAÇÃO
    # ==================================================

    def validar_ip(
        self
    ):
        ip = (
            self.campo_ip
            .text()
            .strip()
        )

        try:
            ipaddress.IPv4Address(
                ip
            )

        except ValueError:
            QMessageBox.warning(
                self,
                "IP inválido",
                "Digite um endereço IPv4 válido."
            )

            return None

        return ip

    # ==================================================
    # DIAGNÓSTICO NORMAL
    # ==================================================

    def alternar_diagnostico(
        self
    ):
        if (
            self.thread_diagnostico
            is not None
            and
            self.thread_diagnostico
            .isRunning()
        ):
            self.cancelar_diagnostico()

        else:
            self.iniciar_diagnostico()

    def iniciar_diagnostico(
        self
    ):
        ip = self.validar_ip()

        if ip is None:
            return

        self.configurar_tabela_tracert_normal()

        self.telemetria_rota.limpar()
        self.mostrar_tabela_tracert()

        self.label_tracert_ciclos.setVisible(
            False
        )

        self.ip_atual = ip

        self.exportacoes_bloqueadas = True

        self.interface_web_aberta_automaticamente = False

        self.dados_ping = None
        self.saltos = None
        self.portas = None
        self.urls_web = []

        self.diagnostico_cancelado = False

        self.limpar_resultados()

        self.botao_executar.setText(
            "■"
        )

        self.botao_executar.setToolTip(
            "Cancelar diagnóstico"
        )

        self.botao_executar.setEnabled(
            True
        )

        self.botao_ping_continuo.setEnabled(
            False
        )

        self.botao_tracert_continuo.setEnabled(
            False
        )

        self.botao_configuracoes.setEnabled(
            False
        )

        self.botao_exportar.setEnabled(
            False
        )

        self.atualizar_menu_exportacao()

        self.campo_ip.setEnabled(
            False
        )

        self.status.setText(
            "Iniciando diagnóstico..."
        )

        logger.info(
            "Solicitado diagnóstico | IP=%s",
            ip
        )

        self.thread_diagnostico = (
            DiagnosticoThread(
                ip,
                self.configuracoes
            )
        )

        self.thread_diagnostico.resultado_ping.connect(
            self.mostrar_ping
        )

        self.thread_diagnostico.resultado_tracert.connect(
            self.mostrar_tracert
        )

        self.thread_diagnostico.resultado_portas.connect(
            self.mostrar_portas
        )

        self.thread_diagnostico.status.connect(
            self.status.setText
        )

        self.thread_diagnostico.finished.connect(
            self.diagnostico_finalizado
        )

        self.thread_diagnostico.start()

    def cancelar_diagnostico(
        self
    ):
        if (
            self.thread_diagnostico
            is None
            or not
            self.thread_diagnostico
            .isRunning()
        ):
            return

        self.diagnostico_cancelado = True

        logger.info(
            "Cancelamento solicitado pelo usuário | "
            "IP=%s",
            self.ip_atual
        )

        self.status.setText(
            "Cancelando diagnóstico..."
        )

        self.botao_executar.setEnabled(
            False
        )

        self.thread_diagnostico.requestInterruption()

    def diagnostico_finalizado(
        self
    ):
        foi_cancelado = (
            self.diagnostico_cancelado
        )

        self.botao_executar.setText(
            "➜"
        )

        self.botao_executar.setToolTip(
            "Iniciar diagnóstico"
        )

        self.botao_executar.setEnabled(
            True
        )

        self.botao_ping_continuo.setEnabled(
            True
        )

        self.botao_tracert_continuo.setEnabled(
            True
        )

        self.botao_configuracoes.setEnabled(
            True
        )

        self.campo_ip.setEnabled(
            True
        )

        if foi_cancelado:
            self.status.setText(
                "Diagnóstico cancelado. "
                "Resultados parciais preservados."
            )

        self.thread_diagnostico = None

        self.diagnostico_cancelado = False

        self.exportacoes_bloqueadas = False

        self.atualizar_menu_exportacao()

        self.atualizar_resumos_interface()

    # ==================================================
    # TRACERT CONTÍNUO
    # ==================================================

    def limpar_para_tracert_continuo(
        self
    ):
        self.dados_ping = None
        self.saltos = None
        self.portas = None
        self.urls_web = []

        self.card_enviados.valor_label.setText(
            "-"
        )

        self.card_recebidos.valor_label.setText(
            "-"
        )

        self.card_perda.valor_label.setText(
            "-"
        )

        self.card_media.valor_label.setText(
            "-"
        )

        self.atualizar_status_ping(
            "NÃO EXECUTADO",
            "#8294a5"
        )

        self.ping_detalhes.setText(
            "O diagnóstico Ping fica inativo durante "
            "o Monitor de Rota."
        )

        self.tabela_ping.setRowCount(
            0
        )

        self.tabela_portas.setRowCount(
            0
        )

    def alternar_tracert_continuo(
        self
    ):
        if (
            self.thread_tracert_continuo
            is not None
            and
            self.thread_tracert_continuo
            .isRunning()
        ):
            self.parar_tracert_continuo()
            return

        self.iniciar_tracert_continuo()

    def iniciar_tracert_continuo(
        self
    ):
        ip = self.validar_ip()

        if ip is None:
            return

        self.ip_atual = ip

        self.exportacoes_bloqueadas = True

        self.tracert_ciclos = 0

        self.tracert_inicio_monotonic = (
            time.monotonic()
        )

        agora = datetime.now()

        amostra_minima = (
            self.configuracoes[
                "tracert_continuo_amostra_minima"
            ]
        )

        self.sessao_tracert_continuo = {
            "versao": "1.1",
            "tipo": "tracert_continuo",
            "destino": ip,
            "inicio":
                agora.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            "fim": None,
            "duracao_segundos": 0,
            "ciclos": 0,
            "amostra_minima":
                amostra_minima,
            "amostra_atingida": False,
            "resultados": []
        }

        self.limpar_para_tracert_continuo()

        self.configurar_tabela_tracert_continuo()

        self.telemetria_rota.limpar()

        self.tabela_tracert.setRowCount(
            0
        )

        self.label_tracert_ciclos.setText(
            "Ciclos: 0"
        )

        self.label_tracert_ciclos.setVisible(
            True
        )

        self.botao_tracert_continuo.setText(
            "■ Parar Monitor"
        )

        self.botao_executar.setEnabled(
            False
        )

        self.botao_ping_continuo.setEnabled(
            False
        )

        self.botao_configuracoes.setEnabled(
            False
        )

        self.botao_exportar.setEnabled(
            False
        )

        self.atualizar_menu_exportacao()

        self.campo_ip.setEnabled(
            False
        )

        self.status.setText(
            "Monitor de Rota: descobrindo rota..."
        )

        logger.info(
            "Nova sessão de Tracert contínuo | "
            "Destino=%s",
            ip
        )

        self.thread_tracert_continuo = (
            TracertContinuoThread(
                ip,
                max_saltos=
                    self.configuracoes[
                        "max_saltos"
                    ],
                intervalo=1.0,
                timeout_sonda_ms=700,
                max_workers=8,
                amostra_minima=
                    amostra_minima
            )
        )

        self.thread_tracert_continuo.status.connect(
            self.status.setText
        )

        self.thread_tracert_continuo.resultado_atualizado.connect(
            self.receber_tracert_continuo
        )

        self.thread_tracert_continuo.finished.connect(
            self.tracert_continuo_finalizado
        )

        self.thread_tracert_continuo.start()

        self.atualizar_menu_exportacao()

        self.atualizar_resumos_interface()

    def parar_tracert_continuo(
        self
    ):
        if (
            self.thread_tracert_continuo
            is None
        ):
            return

        logger.info(
            "Parada do Monitor de Rota solicitada | "
            "IP=%s",
            self.ip_atual
        )

        self.botao_tracert_continuo.setText(
            "Parando..."
        )

        self.botao_tracert_continuo.setEnabled(
            False
        )

        self.thread_tracert_continuo.requestInterruption()

    def receber_tracert_continuo(
        self,
        resultados,
        ciclos
    ):
        self.tracert_ciclos = ciclos

        self.label_tracert_ciclos.setText(
            f"Ciclos: {ciclos}"
        )

        if (
            self.sessao_tracert_continuo
            is not None
        ):
            self.sessao_tracert_continuo[
                "ciclos"
            ] = ciclos

            amostra_minima = (
                self.sessao_tracert_continuo[
                    "amostra_minima"
                ]
            )

            self.sessao_tracert_continuo[
                "amostra_atingida"
            ] = (
                ciclos
                >= amostra_minima
            )

            self.sessao_tracert_continuo[
                "resultados"
            ] = [
                dict(
                    resultado
                )
                for resultado
                in resultados
            ]

        self.telemetria_rota.atualizar_ciclo(
            resultados,
            ciclos,
            time.time()
        )

        self.tabela_tracert.setRowCount(
            len(resultados)
        )

        for linha, salto in enumerate(
            resultados
        ):
            def valor_ms(
                valor
            ):
                if valor is None:
                    return "-"

                return f"{valor} ms"

            valores = [
                salto["salto"],
                salto["ip"],
                salto["enviados"],
                salto["recebidos"],
                f"{salto['perda']}%",
                valor_ms(
                    salto["melhor"]
                ),
                valor_ms(
                    salto["media"]
                ),
                valor_ms(
                    salto["pior"]
                ),
                valor_ms(
                    salto["ultimo"]
                )
            ]

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela_tracert.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(
                        str(valor)
                    )
                )

            status = salto[
                "status"
            ]

            item_status = QTableWidgetItem(
                status
            )

            if status == "OK":
                cor = "#35d07f"

            elif status == "COLETANDO":
                cor = "#6eb6ff"

            elif status == "ICMP LIMITADO":
                cor = "#8294a5"

            elif status == "POSSÍVEL PERDA":
                cor = "#ffcc66"

            elif status == "PERDA PERSISTENTE":
                cor = "#ff9f43"

            elif status == "PERDA NO DESTINO":
                cor = "#ff6b6b"

            elif status in {
                "DESTINO SEM RESPOSTA",
                "SEM RESPOSTA"
            }:
                cor = "#ff5c5c"

            else:
                cor = "#8294a5"

            item_status.setForeground(
                QColor(
                    cor
                )
            )

            self.tabela_tracert.setItem(
                linha,
                9,
                item_status
            )

    def tracert_continuo_finalizado(
        self
    ):
        ciclos = self.tracert_ciclos

        if (
            self.sessao_tracert_continuo
            is not None
        ):
            self.sessao_tracert_continuo[
                "fim"
            ] = (
                datetime.now()
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            if (
                self.tracert_inicio_monotonic
                is not None
            ):
                duracao = (
                    time.monotonic()
                    - self.tracert_inicio_monotonic
                )

                self.sessao_tracert_continuo[
                    "duracao_segundos"
                ] = round(
                    duracao,
                    2
                )

            self.sessao_tracert_continuo[
                "ciclos"
            ] = ciclos

            logger.info(
                "Sessão do Monitor de Rota finalizada | "
                "Destino=%s | Ciclos=%s",
                self.sessao_tracert_continuo[
                    "destino"
                ],
                ciclos
            )

        self.botao_tracert_continuo.setText(
            "Monitor de Rota"
        )

        self.botao_tracert_continuo.setEnabled(
            True
        )

        self.botao_executar.setEnabled(
            True
        )

        self.botao_ping_continuo.setEnabled(
            True
        )

        self.botao_configuracoes.setEnabled(
            True
        )

        self.campo_ip.setEnabled(
            True
        )

        self.status.setText(
            "Monitor de Rota parado. "
            f"Ciclos realizados: {ciclos}."
        )

        self.label_tracert_ciclos.setText(
            f"Ciclos: {ciclos} — parado"
        )

        self.thread_tracert_continuo = None

        self.exportacoes_bloqueadas = False

        self.atualizar_menu_exportacao()

        self.atualizar_resumos_interface()

    # ==================================================
    # PING CONTÍNUO
    # ==================================================

    def alternar_ping_continuo(
        self
    ):
        if (
            self.thread_ping_continuo
            is not None
            and
            self.thread_ping_continuo
            .isRunning()
        ):
            self.parar_ping_continuo()
            return

        self.iniciar_ping_continuo()

    def iniciar_ping_continuo(
        self
    ):
        ip = self.validar_ip()

        if ip is None:
            return

        self.ip_atual = ip

        self.exportacoes_bloqueadas = True

        self.dados_ping = None

        self.cont_ping_enviados = 0
        self.cont_ping_recebidos = 0
        self.cont_ping_tempos = []

        self.historico_ping_continuo = []

        self.telemetria_ping.definir_limite_latencia(
            self.configuracoes.get(
                "limite_latencia_ping_ms",
                100
            )
        )

        self.telemetria_ping.limpar()

        self.tabela_ping.setRowCount(
            0
        )

        self.card_enviados.valor_label.setText(
            "0"
        )

        self.card_recebidos.valor_label.setText(
            "0"
        )

        self.card_perda.valor_label.setText(
            "0%"
        )

        self.card_media.valor_label.setText(
            "-"
        )

        self.atualizar_status_ping(
            "MONITORANDO",
            "#6eb6ff"
        )

        self.botao_executar.setEnabled(
            False
        )

        self.botao_tracert_continuo.setEnabled(
            False
        )

        self.botao_configuracoes.setEnabled(
            False
        )

        self.botao_exportar.setEnabled(
            False
        )

        self.atualizar_menu_exportacao()

        self.campo_ip.setEnabled(
            False
        )

        self.botao_ping_continuo.setText(
            "■ Parar Monitor"
        )

        self.status.setText(
            f"Monitor ICMP ativo para {ip}..."
        )

        self.thread_ping_continuo = (
            PingContinuoThread(
                ip,
                self.configuracoes[
                    "intervalo_ping_continuo"
                ]
            )
        )

        self.thread_ping_continuo.novo_resultado.connect(
            self.receber_ping_continuo
        )

        self.thread_ping_continuo.finished.connect(
            self.ping_continuo_finalizado
        )

        self.thread_ping_continuo.start()

        self.atualizar_menu_exportacao()

        self.atualizar_resumos_interface()

    def parar_ping_continuo(
        self
    ):
        if (
            self.thread_ping_continuo
            is None
        ):
            return

        self.botao_ping_continuo.setEnabled(
            False
        )

        self.botao_ping_continuo.setText(
            "Parando..."
        )

        self.thread_ping_continuo.requestInterruption()

    def receber_ping_continuo(
        self,
        dados_ping
    ):
        self.cont_ping_enviados += 1

        respostas = dados_ping.get(
            "respostas",
            []
        )

        linha = (
            self.tabela_ping
            .rowCount()
        )

        if linha >= 100:
            self.tabela_ping.removeRow(
                0
            )

            linha -= 1

        self.tabela_ping.insertRow(
            linha
        )

        numero = (
            self.cont_ping_enviados
        )

        if respostas:
            resposta = respostas[
                0
            ]

            self.cont_ping_recebidos += 1

            tempo = resposta[
                "tempo"
            ]

            self.cont_ping_tempos.append(
                tempo
            )

            self.historico_ping_continuo.append(
                tempo
            )

            self.telemetria_ping.adicionar_amostra(
                tempo,
                time.time()
            )

            if resposta[
                "menor_que"
            ]:
                tempo_texto = (
                    f"<{tempo} ms"
                )

            else:
                tempo_texto = (
                    f"{tempo} ms"
                )

            valores = [
                numero,
                resposta["ip"],
                tempo_texto,
                resposta["ttl"]
            ]

            item_status = QTableWidgetItem(
                "OK"
            )

            item_status.setForeground(
                QColor(
                    "#35d07f"
                )
            )

        else:
            self.historico_ping_continuo.append(
                None
            )

            self.telemetria_ping.adicionar_amostra(
                None,
                time.time()
            )

            valores = [
                numero,
                self.ip_atual,
                "-",
                "-"
            ]

            item_status = QTableWidgetItem(
                "PERDIDO"
            )

            item_status.setForeground(
                QColor(
                    "#ff5c5c"
                )
            )

        for coluna, valor in enumerate(
            valores
        ):
            self.tabela_ping.setItem(
                linha,
                coluna,
                QTableWidgetItem(
                    str(valor)
                )
            )

        self.tabela_ping.setItem(
            linha,
            4,
            item_status
        )

        self.atualizar_resumo_ping_continuo()

        self.tabela_ping.scrollToBottom()

    def atualizar_resumo_ping_continuo(
        self
    ):
        enviados = (
            self.cont_ping_enviados
        )

        recebidos = (
            self.cont_ping_recebidos
        )

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
                * 100
            )

        else:
            perda = 0

        self.card_enviados.valor_label.setText(
            str(enviados)
        )

        self.card_recebidos.valor_label.setText(
            str(recebidos)
        )

        self.card_perda.valor_label.setText(
            f"{perda}%"
        )

        if self.cont_ping_tempos:
            minimo = min(
                self.cont_ping_tempos
            )

            maximo = max(
                self.cont_ping_tempos
            )

            media = round(
                sum(
                    self.cont_ping_tempos
                )
                /
                len(
                    self.cont_ping_tempos
                ),
                1
            )

            self.card_media.valor_label.setText(
                f"{media} ms"
            )

        else:
            minimo = None
            maximo = None

            self.card_media.valor_label.setText(
                "-"
            )

        recentes = (
            self.historico_ping_continuo[
                -10:
            ]
        )

        tempos = [
            tempo
            for tempo in recentes
            if tempo is not None
        ]

        perdas_recentes = sum(
            1
            for tempo in recentes
            if tempo is None
        )

        if len(
            tempos
        ) >= 2:
            variacao = (
                max(
                    tempos
                )
                - min(
                    tempos
                )
            )

        else:
            variacao = 0

        limite = (
            self.configuracoes[
                "limite_variacao_ms"
            ]
        )

        if not tempos:
            self.atualizar_status_ping(
                "SEM RESPOSTA",
                "#ff5c5c"
            )

        elif (
            perdas_recentes > 0
            or variacao >= limite
        ):
            self.atualizar_status_ping(
                "POSSÍVEL INSTABILIDADE",
                "#ffcc66"
            )

        else:
            self.atualizar_status_ping(
                "ONLINE",
                "#35d07f"
            )

        detalhes = []

        if minimo is not None:
            detalhes.append(
                f"Mínimo: {minimo} ms"
            )

            detalhes.append(
                f"Máximo: {maximo} ms"
            )

        detalhes.append(
            f"Perda total: {perda}%"
        )

        detalhes.append(
            f"Variação recente: {variacao} ms"
        )

        detalhes.append(
            f"Limite: {limite} ms"
        )

        self.ping_detalhes.setText(
            "   |   ".join(
                detalhes
            )
        )

    def ping_continuo_finalizado(
        self
    ):
        self.botao_ping_continuo.setText(
            "Monitor ICMP"
        )

        self.botao_ping_continuo.setEnabled(
            True
        )

        self.botao_tracert_continuo.setEnabled(
            True
        )

        self.botao_executar.setEnabled(
            True
        )

        self.botao_configuracoes.setEnabled(
            True
        )

        self.campo_ip.setEnabled(
            True
        )

        self.status.setText(
            "Monitor ICMP parado."
        )

        self.thread_ping_continuo = None

        self.exportacoes_bloqueadas = False

        self.atualizar_menu_exportacao()

        self.atualizar_resumos_interface()

    # ==================================================
    # RESULTADOS
    # ==================================================

    def limpar_resultados(
        self
    ):
        self.card_enviados.valor_label.setText(
            "-"
        )

        self.card_recebidos.valor_label.setText(
            "-"
        )

        self.card_perda.valor_label.setText(
            "-"
        )

        self.card_media.valor_label.setText(
            "-"
        )

        self.atualizar_status_ping(
            "EXECUTANDO...",
            "#6eb6ff"
        )

        self.ping_detalhes.setText(
            "Aguardando resultado do Ping..."
        )

        self.tabela_ping.setRowCount(
            0
        )

        self.tabela_tracert.setRowCount(
            0
        )

        self.tabela_portas.setRowCount(
            0
        )

    def atualizar_status_ping(
        self,
        texto,
        cor
    ):
        self.ping_status.setText(
            texto
        )

        self.ping_status.setStyleSheet(
            f"color: {cor};"
            "font-size: 15pt;"
            "font-weight: 700;"
        )

    def mostrar_ping(
        self,
        dados_ping
    ):
        self.dados_ping = dados_ping

        self.card_enviados.valor_label.setText(
            str(
                dados_ping[
                    "enviados"
                ]
            )
        )

        self.card_recebidos.valor_label.setText(
            str(
                dados_ping[
                    "recebidos"
                ]
            )
        )

        self.card_perda.valor_label.setText(
            f"{dados_ping['perda']}%"
        )

        if (
            dados_ping[
                "media"
            ]
            is not None
        ):
            self.card_media.valor_label.setText(
                f"{dados_ping['media']} ms"
            )

            detalhes = (
                f"Mínimo: {dados_ping['minimo']} ms"
                f"   |   "
                f"Máximo: {dados_ping['maximo']} ms"
                f"   |   "
                f"Variação: {dados_ping['variacao']} ms"
            )

        else:
            self.card_media.valor_label.setText(
                "-"
            )

            detalhes = (
                "Latência indisponível."
            )

        if (
            dados_ping[
                "recebidos"
            ]
            == 0
        ):
            self.atualizar_status_ping(
                "SEM RESPOSTA",
                "#ff5c5c"
            )

        elif dados_ping[
            "instavel"
        ]:
            self.atualizar_status_ping(
                "POSSÍVEL INSTABILIDADE",
                "#ffcc66"
            )

            detalhes += (
                "\n"
                + dados_ping[
                    "alerta"
                ]
            )

        else:
            self.atualizar_status_ping(
                "ONLINE",
                "#35d07f"
            )

        self.ping_detalhes.setText(
            detalhes
        )

        respostas = dados_ping.get(
            "respostas",
            []
        )

        self.tabela_ping.setRowCount(
            len(
                respostas
            )
        )

        for linha, resposta in enumerate(
            respostas
        ):
            if resposta[
                "menor_que"
            ]:
                tempo = (
                    f"<{resposta['tempo']} ms"
                )

            else:
                tempo = (
                    f"{resposta['tempo']} ms"
                )

            valores = [
                resposta["numero"],
                resposta["ip"],
                tempo,
                resposta["ttl"]
            ]

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela_ping.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(
                        str(valor)
                    )
                )

            status = QTableWidgetItem(
                "OK"
            )

            status.setForeground(
                QColor(
                    "#35d07f"
                )
            )

            self.tabela_ping.setItem(
                linha,
                4,
                status
            )

    def mostrar_tracert(
        self,
        saltos
    ):
        self.saltos = saltos

        self.configurar_tabela_tracert_normal()

        self.tabela_tracert.setRowCount(
            len(
                saltos
            )
        )

        for linha, salto in enumerate(
            saltos
        ):
            def tempo_texto(
                valor
            ):
                if valor is None:
                    return "*"

                return f"{valor} ms"

            valores = [
                salto["salto"],
                salto["ip"] or "-",
                tempo_texto(
                    salto["tempo1"]
                ),
                tempo_texto(
                    salto["tempo2"]
                ),
                tempo_texto(
                    salto["tempo3"]
                ),
                (
                    f"{salto['media']} ms"
                    if salto["media"]
                    is not None
                    else "-"
                )
            ]

            status_salto = salto.get(
                "status"
            )

            if status_salto == "ok":
                texto_status = "OK"
                cor = "#35d07f"

            elif status_salto == "parcial":
                texto_status = "PARCIAL"
                cor = "#ffcc66"

            else:
                texto_status = (
                    "SEM RESPOSTA"
                )

                cor = "#ffcc66"

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela_tracert.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(
                        str(valor)
                    )
                )

            item_status = QTableWidgetItem(
                texto_status
            )

            item_status.setForeground(
                QColor(
                    cor
                )
            )

            self.tabela_tracert.setItem(
                linha,
                6,
                item_status
            )

    # ==================================================
    # PORTAS + NAVEGADOR
    # ==================================================

    def mostrar_portas(
        self,
        portas
    ):
        self.portas = portas

        self.tabela_portas.setRowCount(
            len(portas)
        )

        navegador = self.configuracoes.get(
            "navegador_preferido",
            "padrao"
        )

        navegador_personalizado = (
            self.configuracoes.get(
                "navegador_personalizado",
                ""
            )
        )

        interfaces_web = self.configuracoes.get(
            "interfaces_web_portas",
            {}
        )

        for linha, porta in enumerate(
            portas
        ):
            numero_porta = porta.get(
                "porta"
            )

            self.tabela_portas.setItem(
                linha,
                0,
                QTableWidgetItem(
                    str(
                        numero_porta
                    )
                )
            )

            self.tabela_portas.setItem(
                linha,
                1,
                QTableWidgetItem(
                    porta.get(
                        "servico",
                        "TCP"
                    )
                )
            )

            modo = porta.get(
                "interface_web_modo",
                "NENHUMA"
            )

            protocolo = porta.get(
                "protocolo_web"
            )

            if modo == "AUTOMATICO":
                if protocolo:
                    texto_web = (
                        f"Automático → {protocolo}"
                    )
                else:
                    texto_web = "Automático"

            elif modo == "NENHUMA":
                texto_web = "Nenhuma"

            else:
                texto_web = modo

            item_web = QTableWidgetItem(
                texto_web
            )

            if protocolo == "HTTPS":
                item_web.setForeground(
                    QColor(
                        "#39d98a"
                    )
                )

            elif protocolo == "HTTP":
                item_web.setForeground(
                    QColor(
                        "#58a6ff"
                    )
                )

            self.tabela_portas.setItem(
                linha,
                2,
                item_web
            )

            status = QTableWidgetItem(
                porta.get(
                    "status",
                    "ERRO"
                )
            )

            self.aplicar_cor_status(
                status,
                porta.get(
                    "status",
                    "ERRO"
                )
            )

            self.tabela_portas.setItem(
                linha,
                3,
                status
            )

            url = porta.get(
                "url_web"
            )

            if (
                porta.get(
                    "status"
                )
                == "ABERTA"
                and url
            ):
                botao = QPushButton(
                    "Abrir no navegador"
                )

                botao.setObjectName(
                    "botaoAbrirWeb"
                )

                botao.clicked.connect(
                    lambda
                    checked=False,
                    endereco=url,
                    nav=navegador,
                    caminho=navegador_personalizado:
                        abrir_url(
                            endereco,
                            nav,
                            caminho
                        )
                )

                self.tabela_portas.setCellWidget(
                    linha,
                    4,
                    botao
                )

            else:
                self.tabela_portas.setItem(
                    linha,
                    4,
                    QTableWidgetItem(
                        "-"
                    )
                )

        self.urls_web = obter_urls_web(
            self.ip_atual,
            portas,
            interfaces_web
        )

        abrir_automaticamente = (
            self.configuracoes.get(
                "abrir_interface_web_automaticamente",
                True
            )
        )

        if (
            abrir_automaticamente
            and not
            self.interface_web_aberta_automaticamente
        ):
            url_preferencial = (
                obter_url_preferencial(
                    self.ip_atual,
                    portas,
                    interfaces_web
                )
            )

            if url_preferencial:
                logger.info(
                    "Interface web encontrada | "
                    "IP=%s | URL=%s",
                    self.ip_atual,
                    url_preferencial
                )

                abriu_preferido, navegador_usado = (
                    abrir_url(
                        url_preferencial,
                        navegador,
                        navegador_personalizado
                    )
                )

                self.interface_web_aberta_automaticamente = (
                    True
                )

                logger.info(
                    "Abertura automática da interface | "
                    "URL=%s | "
                    "Navegador solicitado=%s | "
                    "Navegador usado=%s | "
                    "Preferido encontrado=%s",
                    url_preferencial,
                    navegador,
                    navegador_usado,
                    abriu_preferido
                )

    def aplicar_cor_status(
        self,
        item,
        status
    ):
        if status == "ABERTA":
            cor = "#35d07f"

        elif status == "TIMEOUT":
            cor = "#ffcc66"

        else:
            cor = "#ff5c5c"

        item.setForeground(
            QColor(
                cor
            )
        )

    # ==================================================
    # EXPORTAÇÃO
    # ==================================================

    def atualizar_menu_exportacao(
        self
    ):
        diagnostico_disponivel = (
            self.ip_atual is not None
            and self.dados_ping is not None
            and self.saltos is not None
            and self.portas is not None
        )

        sessao_disponivel = (
            self.sessao_tracert_continuo
            is not None
            and
            self.sessao_tracert_continuo.get(
                "ciclos",
                0
            ) > 0
            and bool(
                self.sessao_tracert_continuo.get(
                    "resultados"
                )
            )
            and (
                self.thread_tracert_continuo
                is None
            )
        )

        if hasattr(
            self,
            "pagina_relatorios"
        ):
            self.pagina_relatorios.atualizar_exportacoes(
                diagnostico_disponivel,
                sessao_disponivel,
                bloqueado=self.exportacoes_bloqueadas
            )

    def exportar_backup_configuracoes(
        self
    ):
        nome = (
            "NDT_Config_"
            + datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            + ".json"
        )

        destino, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar configurações",
            nome,
            "Configuração do NDT (*.json)"
        )

        if not destino:
            return

        if not destino.lower().endswith(
            ".json"
        ):
            destino += ".json"

        try:
            caminho = exportar_configuracoes(
                self.configuracoes,
                destino
            )

        except (
            OSError,
            TypeError,
            ValueError
        ) as erro:
            logger.exception(
                "Falha ao exportar configurações: %s",
                erro
            )

            QMessageBox.critical(
                self,
                "Exportar configurações",
                "Não foi possível exportar as configurações.\n\n"
                f"Detalhes: {erro}"
            )

            return

        logger.info(
            "Configurações exportadas | Arquivo=%s",
            caminho
        )

        QMessageBox.information(
            self,
            "Exportar configurações",
            "Backup criado com sucesso.\n\n"
            f"{caminho}"
        )

    def importar_backup_configuracoes(
        self
    ):
        origem, _ = QFileDialog.getOpenFileName(
            self,
            "Importar configurações",
            "",
            "Configuração do NDT (*.json);;Arquivos JSON (*.json)"
        )

        if not origem:
            return

        resposta = QMessageBox.warning(
            self,
            "Importar configurações",
            "As configurações atuais serão substituídas pelos "
            "valores do arquivo selecionado.\n\n"
            "Antes disso, o NDT criará um backup automático "
            "da configuração atual.\n\n"
            "O Registro de Incidentes não será alterado.\n\n"
            "Deseja continuar?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if (
            resposta
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            backup = criar_backup_automatico(
                self.configuracoes
            )

            (
                novas_configuracoes,
                metadados
            ) = importar_configuracoes(
                origem,
                self.configuracoes
            )

        except (
            OSError,
            ValueError,
            TypeError,
            json.JSONDecodeError
        ) as erro:
            logger.exception(
                "Falha ao importar configurações: %s",
                erro
            )

            QMessageBox.critical(
                self,
                "Importar configurações",
                "Não foi possível importar o arquivo.\n\n"
                f"Detalhes: {erro}"
            )

            return

        self.configuracoes = novas_configuracoes

        try:
            salvar_configuracoes(
                self.configuracoes
            )

        except OSError as erro:
            logger.exception(
                "Falha ao salvar configurações importadas: %s",
                erro
            )

            QMessageBox.critical(
                self,
                "Importar configurações",
                "O arquivo foi validado, mas não foi possível "
                "salvar as configurações.\n\n"
                f"Backup preservado em:\n{backup}\n\n"
                f"Detalhes: {erro}"
            )

            return

        self.executar_limpeza_incidentes(
            forcar=True
        )

        if (
            self.janela_incidentes is not None
            and self.janela_incidentes.isVisible()
        ):
            self.janela_incidentes.atualizar()

        self.reiniciar_down_detector()

        self.atualizar_resumos_interface()

        logger.info(
            "Configurações importadas | Origem=%s | "
            "Backup anterior=%s | Versão origem=%s",
            origem,
            backup,
            metadados.get(
                "versao_app_origem",
                "desconhecida"
            )
        )

        avisos = metadados.get(
            "avisos",
            []
        )

        mensagem = (
            "Configurações importadas com sucesso.\n\n"
            f"Backup automático anterior:\n{backup}"
        )

        if avisos:
            mensagem += (
                "\n\nAtenção:\n• "
                + "\n• ".join(
                    avisos
                )
            )

        QMessageBox.information(
            self,
            "Importar configurações",
            mensagem
        )

    def exportar_diagnostico_txt(
        self
    ):
        if (
            self.ip_atual is None
            or self.dados_ping is None
            or self.saltos is None
            or self.portas is None
        ):
            return

        try:
            arquivo = exportar_relatorio(
                self.ip_atual,
                self.dados_ping,
                self.saltos,
                self.portas,
                self.urls_web
            )

        except OSError:
            logger.exception(
                "Erro ao exportar diagnóstico TXT."
            )

            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível exportar "
                "o relatório."
            )

            return

        self.mostrar_exportacao_concluida(
            arquivo
        )

    def exportar_sessao_tracert_txt(
        self
    ):
        self.exportar_sessao_tracert(
            exportar_tracert_continuo_txt,
            "TXT"
        )

    def exportar_sessao_tracert_csv(
        self
    ):
        self.exportar_sessao_tracert(
            exportar_tracert_continuo_csv,
            "CSV"
        )

    def exportar_sessao_tracert_json(
        self
    ):
        self.exportar_sessao_tracert(
            exportar_tracert_continuo_json,
            "JSON"
        )

    def exportar_sessao_tracert(
        self,
        funcao_exportacao,
        formato
    ):
        if (
            self.sessao_tracert_continuo
            is None
        ):
            return

        try:
            arquivo = funcao_exportacao(
                self.sessao_tracert_continuo
            )

        except OSError:
            logger.exception(
                "Erro ao exportar sessão "
                "do Monitor de Rota | "
                "Formato=%s",
                formato
            )

            QMessageBox.critical(
                self,
                "Erro",
                "Não foi possível exportar "
                f"a sessão em {formato}."
            )

            return

        logger.info(
            "Sessão exportada | "
            "Formato=%s | Arquivo=%s",
            formato,
            arquivo
        )

        self.mostrar_exportacao_concluida(
            arquivo
        )

    def mostrar_exportacao_concluida(
        self,
        arquivo
    ):
        QMessageBox.information(
            self,
            "Exportação concluída",
            "Arquivo salvo em:\n\n"
            f"{arquivo}"
        )

    # ==================================================
    # LOGS
    # ==================================================

    def abrir_logs(
        self
    ):
        if self.janela_logs is None:
            self.janela_logs = LogWindow(
                self
            )

        self.janela_logs.atualizar()
        self.janela_logs.show()
        self.janela_logs.raise_()
        self.janela_logs.activateWindow()

    # ==================================================
    # CONFIGURAÇÕES
    # ==================================================

    def abrir_configuracoes(
        self
    ):
        janela = SettingsWindow(
            self.configuracoes,
            self
        )

        resultado = janela.exec()

        if (
            resultado
            == QDialog
            .DialogCode
            .Accepted
        ):
            self.configuracoes = (
                janela
                .obter_configuracoes()
            )

            salvar_configuracoes(
                self.configuracoes
            )

            self.executar_limpeza_incidentes(
                forcar=True
            )

            if (
                self.janela_incidentes is not None
                and self.janela_incidentes.isVisible()
            ):
                self.janela_incidentes.atualizar()

            self.reiniciar_down_detector()

            self.atualizar_resumos_interface()

            logger.info(
                "Configurações atualizadas."
            )

            QMessageBox.information(
                self,
                "Configurações",
                "Configurações salvas com sucesso."
            )

    # ==================================================
    # BANDEJA
    # ==================================================

    def ocultar_na_bandeja(
        self
    ):
        self.hide()

        logger.info(
            "Janela ocultada na bandeja."
        )

    def restaurar_da_bandeja(
        self
    ):
        self.showNormal()

        self.raise_()

        self.activateWindow()

        logger.info(
            "Janela restaurada da bandeja."
        )

    def encerrar_aplicacao(
        self
    ):
        logger.info(
            "Encerramento solicitado pela bandeja."
        )

        self.encerramento_real = True

        self.parar_threads()

        self.close()

    def parar_threads(
        self
    ):
        self.parar_down_detector(
            aguardar=True
        )

        if (
            self.thread_ping_continuo
            is not None
            and
            self.thread_ping_continuo
            .isRunning()
        ):
            self.thread_ping_continuo.requestInterruption()

            self.thread_ping_continuo.wait(
                2500
            )

        if (
            self.thread_tracert_continuo
            is not None
            and
            self.thread_tracert_continuo
            .isRunning()
        ):
            self.thread_tracert_continuo.requestInterruption()

            self.thread_tracert_continuo.wait(
                4000
            )

        if (
            self.thread_diagnostico
            is not None
            and
            self.thread_diagnostico
            .isRunning()
        ):
            logger.info(
                "Encerramento solicitado com "
                "diagnóstico ativo."
            )

            self.thread_diagnostico.requestInterruption()

            self.thread_diagnostico.wait(
                4000
            )

    # ==================================================
    # ENCERRAMENTO
    # ==================================================

    def closeEvent(
        self,
        event: QCloseEvent
    ):
        if not self.encerramento_real:
            event.ignore()

            self.ocultar_na_bandeja()

            return

        logger.info(
            "Aplicação encerrada."
        )

        self.parar_threads()

        event.accept()
