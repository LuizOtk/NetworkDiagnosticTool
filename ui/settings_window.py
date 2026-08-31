from copy import deepcopy
from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QListWidget,
    QVBoxLayout,
    QWidget
)

from config.service_presets import (
    PRESET_SERVICOS
)

from config.settings import (
    CONFIG_PADRAO
)

from network.down_detector import (
    criar_chave_servico,
    normalizar_alvo
)

from services.audio_alert import (
    testar_alerta
)

from services.browser import (
    NAVEGADORES,
    abrir_url,
    obter_nome_navegador
)

from services.incidents import (
    limpar_incidentes_encerrados
)


class SettingsWindow(QDialog):
    def __init__(
        self,
        configuracoes,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.configuracoes = deepcopy(
            configuracoes
        )

        self.setWindowTitle(
            "Configurações"
        )

        self.resize(
            980,
            720
        )

        self.setMinimumSize(
            900,
            650
        )

        self.titulos_paginas = []
        self.descricoes_paginas = []

        layout_principal = QVBoxLayout(
            self
        )

        layout_principal.setContentsMargins(
            16,
            16,
            16,
            16
        )

        layout_principal.setSpacing(
            12
        )

        # =================================================
        # CABEÇALHO
        # =================================================

        cabecalho = QFrame()

        cabecalho.setObjectName(
            "painelConfiguracaoInfo"
        )

        layout_cabecalho = QVBoxLayout(
            cabecalho
        )

        layout_cabecalho.setContentsMargins(
            16,
            12,
            16,
            12
        )

        titulo = QLabel(
            "Configurações"
        )

        titulo.setObjectName(
            "tituloConfiguracaoInfo"
        )

        subtitulo = QLabel(
            "Ajuste o comportamento do diagnóstico, "
            "monitoramento, alertas e integrações do NDT."
        )

        subtitulo.setWordWrap(
            True
        )

        layout_cabecalho.addWidget(
            titulo
        )

        layout_cabecalho.addWidget(
            subtitulo
        )

        layout_principal.addWidget(
            cabecalho
        )

        # =================================================
        # CORPO: NAVEGAÇÃO LATERAL + CONTEÚDO
        # =================================================

        corpo = QHBoxLayout()

        corpo.setSpacing(
            14
        )

        painel_menu = QFrame()

        painel_menu.setObjectName(
            "painelConfiguracaoInfo"
        )

        painel_menu.setFixedWidth(
            210
        )

        layout_menu = QVBoxLayout(
            painel_menu
        )

        layout_menu.setContentsMargins(
            10,
            12,
            10,
            12
        )

        titulo_menu = QLabel(
            "Categorias"
        )

        titulo_menu.setObjectName(
            "subtituloConfiguracaoInfo"
        )

        layout_menu.addWidget(
            titulo_menu
        )

        self.menu_configuracoes = QListWidget()

        self.menu_configuracoes.setObjectName(
            "menuConfiguracoes"
        )

        self.menu_configuracoes.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .SingleSelection
        )

        self.menu_configuracoes.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.menu_configuracoes.setStyleSheet(
            """
            QListWidget#menuConfiguracoes {
                background: transparent;
                border: none;
                outline: none;
            }

            QListWidget#menuConfiguracoes::item {
                padding: 12px 14px;
                margin: 2px 0;
                border-radius: 6px;
            }

            QListWidget#menuConfiguracoes::item:hover {
                background-color: #13283a;
            }

            QListWidget#menuConfiguracoes::item:selected {
                background-color: #17324a;
                color: #66b3ff;
                border-left: 3px solid #2f81f7;
            }
            """
        )

        layout_menu.addWidget(
            self.menu_configuracoes,
            1
        )

        corpo.addWidget(
            painel_menu
        )

        painel_conteudo = QFrame()

        painel_conteudo.setObjectName(
            "painelConfiguracaoInfo"
        )

        layout_conteudo = QVBoxLayout(
            painel_conteudo
        )

        layout_conteudo.setContentsMargins(
            16,
            14,
            16,
            14
        )

        self.titulo_pagina = QLabel(
            ""
        )

        self.titulo_pagina.setObjectName(
            "tituloConfiguracaoInfo"
        )

        self.descricao_pagina = QLabel(
            ""
        )

        self.descricao_pagina.setWordWrap(
            True
        )

        layout_conteudo.addWidget(
            self.titulo_pagina
        )

        layout_conteudo.addWidget(
            self.descricao_pagina
        )

        separador = QFrame()

        separador.setFrameShape(
            QFrame.Shape.HLine
        )

        separador.setFrameShadow(
            QFrame.Shadow.Sunken
        )

        layout_conteudo.addWidget(
            separador
        )

        self.pilha_configuracoes = QStackedWidget()

        layout_conteudo.addWidget(
            self.pilha_configuracoes,
            1
        )

        corpo.addWidget(
            painel_conteudo,
            1
        )

        layout_principal.addLayout(
            corpo,
            1
        )

        # =================================================
        # PÁGINAS
        # =================================================

        self.criar_aba_geral()
        self.criar_aba_portas()
        self.criar_aba_down_detector()
        self.criar_aba_tracert_continuo()
        self.criar_aba_incidentes()
        self.criar_aba_alertas()
        self.criar_aba_navegador()

        self.menu_configuracoes.currentRowChanged.connect(
            self.mudar_pagina_configuracoes
        )

        self.menu_configuracoes.setCurrentRow(
            0
        )

        # =================================================
        # RODAPÉ FIXO
        # =================================================

        linha_rodape = QFrame()

        linha_rodape.setFrameShape(
            QFrame.Shape.HLine
        )

        linha_rodape.setFrameShadow(
            QFrame.Shadow.Sunken
        )

        layout_principal.addWidget(
            linha_rodape
        )

        botoes = QHBoxLayout()

        botoes.addStretch()

        botao_cancelar = QPushButton(
            "Cancelar"
        )

        botao_salvar = QPushButton(
            "Salvar"
        )

        botao_salvar.setObjectName(
            "botaoSalvarConfiguracoes"
        )

        botoes.addWidget(
            botao_cancelar
        )

        botoes.addWidget(
            botao_salvar
        )

        layout_principal.addLayout(
            botoes
        )

        botao_cancelar.clicked.connect(
            self.reject
        )

        botao_salvar.clicked.connect(
            self.salvar
        )

    def adicionar_pagina_configuracoes(
        self,
        pagina,
        titulo,
        descricao
    ):
        self.pilha_configuracoes.addWidget(
            pagina
        )

        self.menu_configuracoes.addItem(
            titulo
        )

        self.titulos_paginas.append(
            titulo
        )

        self.descricoes_paginas.append(
            descricao
        )

    def mudar_pagina_configuracoes(
        self,
        indice
    ):
        if (
            indice < 0
            or indice >= self.pilha_configuracoes.count()
        ):
            return

        self.pilha_configuracoes.setCurrentIndex(
            indice
        )

        self.titulo_pagina.setText(
            self.titulos_paginas[
                indice
            ]
        )

        self.descricao_pagina.setText(
            self.descricoes_paginas[
                indice
            ]
        )

    # ==================================================
    # GERAL
    # ==================================================

    def criar_aba_geral(
        self
    ):
        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        formulario = QFormLayout()

        self.quantidade_ping = QSpinBox()

        self.quantidade_ping.setRange(
            1,
            100
        )

        self.quantidade_ping.setValue(
            self.configuracoes[
                "quantidade_ping"
            ]
        )

        formulario.addRow(
            "Quantidade de Pings:",
            self.quantidade_ping
        )

        self.timeout_portas = QDoubleSpinBox()

        self.timeout_portas.setRange(
            0.1,
            30.0
        )

        self.timeout_portas.setDecimals(
            1
        )

        self.timeout_portas.setSingleStep(
            0.5
        )

        self.timeout_portas.setSuffix(
            " s"
        )

        self.timeout_portas.setValue(
            self.configuracoes[
                "timeout_portas"
            ]
        )

        formulario.addRow(
            "Timeout das portas:",
            self.timeout_portas
        )

        self.max_saltos = QSpinBox()

        self.max_saltos.setRange(
            1,
            255
        )

        self.max_saltos.setValue(
            self.configuracoes[
                "max_saltos"
            ]
        )

        formulario.addRow(
            "Máximo de saltos:",
            self.max_saltos
        )

        self.limite_variacao_ping = QSpinBox()

        self.limite_variacao_ping.setRange(
            1,
            5000
        )

        self.limite_variacao_ping.setSuffix(
            " ms"
        )

        self.limite_variacao_ping.setValue(
            self.configuracoes[
                "limite_variacao_ms"
            ]
        )

        formulario.addRow(
            "Limite de oscilação PING:",
            self.limite_variacao_ping
        )

        self.limite_variacao_http = QSpinBox()

        self.limite_variacao_http.setRange(
            50,
            10000
        )

        self.limite_variacao_http.setSuffix(
            " ms"
        )

        self.limite_variacao_http.setValue(
            self.configuracoes[
                "limite_variacao_http_ms"
            ]
        )

        formulario.addRow(
            "Limite de oscilação HTTP:",
            self.limite_variacao_http
        )

        self.limite_latencia_ping = QSpinBox()

        self.limite_latencia_ping.setRange(
            1,
            10000
        )

        self.limite_latencia_ping.setSuffix(
            " ms"
        )

        self.limite_latencia_ping.setValue(
            self.configuracoes.get(
                "limite_latencia_ping_ms",
                100
            )
        )

        formulario.addRow(
            "Limite de latência PING:",
            self.limite_latencia_ping
        )

        self.limite_latencia_http = QSpinBox()

        self.limite_latencia_http.setRange(
            50,
            30000
        )

        self.limite_latencia_http.setSuffix(
            " ms"
        )

        self.limite_latencia_http.setValue(
            self.configuracoes.get(
                "limite_latencia_http_ms",
                1000
            )
        )

        formulario.addRow(
            "Limite de latência HTTP:",
            self.limite_latencia_http
        )

        self.intervalo_ping = QDoubleSpinBox()

        self.intervalo_ping.setRange(
            0.1,
            60.0
        )

        self.intervalo_ping.setDecimals(
            1
        )

        self.intervalo_ping.setSuffix(
            " s"
        )

        self.intervalo_ping.setValue(
            self.configuracoes[
                "intervalo_ping_continuo"
            ]
        )

        formulario.addRow(
            "Intervalo do Monitor ICMP:",
            self.intervalo_ping
        )

        layout.addLayout(
            formulario
        )

        explicacao = QLabel(
            "Oscilação é a diferença entre as latências observadas "
            "ao longo das medições; não representa a latência máxima "
            "permitida. O limite de latência, por outro lado, indica "
            "quando um destino está respondendo acima do tempo esperado. "
            "PING e HTTP/HTTPS possuem limites separados."
        )

        explicacao.setWordWrap(
            True
        )

        layout.addWidget(
            explicacao
        )

        painel_inicializacao = QFrame()

        painel_inicializacao.setObjectName(
            "painelConfiguracaoInfo"
        )

        layout_inicializacao = QVBoxLayout(
            painel_inicializacao
        )

        titulo_inicializacao = QLabel(
            "Inicialização"
        )

        titulo_inicializacao.setObjectName(
            "subtituloConfiguracaoInfo"
        )

        self.checkbox_tela_inicializacao = QCheckBox(
            "Exibir tela de inicialização do NDT"
        )

        self.checkbox_tela_inicializacao.setChecked(
            self.configuracoes.get(
                "exibir_tela_inicializacao",
                True
            )
        )

        descricao_inicializacao = QLabel(
            "Exibe uma breve sequência visual enquanto o NDT "
            "prepara a interface e os componentes principais."
        )

        descricao_inicializacao.setObjectName(
            "textoSecundario"
        )

        descricao_inicializacao.setWordWrap(
            True
        )

        layout_inicializacao.addWidget(
            titulo_inicializacao
        )

        layout_inicializacao.addWidget(
            self.checkbox_tela_inicializacao
        )

        layout_inicializacao.addWidget(
            descricao_inicializacao
        )

        layout.addWidget(
            painel_inicializacao
        )

        linha_default = QHBoxLayout()

        linha_default.addStretch()

        botao_default = QPushButton(
            "Default"
        )

        botao_default.setObjectName(
            "botaoDefaultConfiguracoes"
        )

        botao_default.setToolTip(
            "Restaurar os valores padrão da aba Geral"
        )

        botao_default.clicked.connect(
            self.restaurar_padrao_geral
        )

        linha_default.addWidget(
            botao_default
        )

        layout.addLayout(
            linha_default
        )

        layout.addStretch()

        self.adicionar_pagina_configuracoes(
            aba,
            "Geral",
            "Parâmetros principais de diagnóstico, latência, "
            "oscilação e Monitor ICMP."
        )

    def restaurar_padrao_geral(
        self
    ):
        resposta = QMessageBox.question(
            self,
            "Restaurar padrões",
            "Deseja restaurar os valores padrão "
            "da aba Geral?\n\n"
            "As alterações só serão aplicadas "
            "depois que você clicar em Salvar.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if (
            resposta
            != QMessageBox.StandardButton.Yes
        ):
            return

        self.quantidade_ping.setValue(
            CONFIG_PADRAO[
                "quantidade_ping"
            ]
        )

        self.timeout_portas.setValue(
            CONFIG_PADRAO[
                "timeout_portas"
            ]
        )

        self.max_saltos.setValue(
            CONFIG_PADRAO[
                "max_saltos"
            ]
        )

        self.limite_variacao_ping.setValue(
            CONFIG_PADRAO[
                "limite_variacao_ms"
            ]
        )

        self.limite_variacao_http.setValue(
            CONFIG_PADRAO[
                "limite_variacao_http_ms"
            ]
        )

        self.limite_latencia_ping.setValue(
            CONFIG_PADRAO[
                "limite_latencia_ping_ms"
            ]
        )

        self.limite_latencia_http.setValue(
            CONFIG_PADRAO[
                "limite_latencia_http_ms"
            ]
        )

        self.intervalo_ping.setValue(
            CONFIG_PADRAO[
                "intervalo_ping_continuo"
            ]
        )

        self.checkbox_tela_inicializacao.setChecked(
            CONFIG_PADRAO[
                "exibir_tela_inicializacao"
            ]
        )

    # ==================================================
    # PORTAS
    # ==================================================

    def criar_aba_portas(
        self
    ):
        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        self.tabela_portas = QTableWidget()

        self.tabela_portas.setColumnCount(
            3
        )

        self.tabela_portas.setHorizontalHeaderLabels([
            "Porta",
            "Serviço",
            "Interface Web"
        ])

        self.configurar_tabela(
            self.tabela_portas
        )

        cabecalho = (
            self.tabela_portas
            .horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        cabecalho.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        layout.addWidget(
            self.tabela_portas
        )

        botoes = QHBoxLayout()

        adicionar = QPushButton(
            "Adicionar"
        )

        editar = QPushButton(
            "Editar"
        )

        remover = QPushButton(
            "Remover"
        )

        botoes.addWidget(
            adicionar
        )

        botoes.addWidget(
            editar
        )

        botoes.addWidget(
            remover
        )

        botoes.addStretch()

        layout.addLayout(
            botoes
        )

        self.carregar_portas()

        adicionar.clicked.connect(
            self.adicionar_porta
        )

        editar.clicked.connect(
            self.editar_porta
        )

        remover.clicked.connect(
            self.remover_porta
        )

        self.tabela_portas.doubleClicked.connect(
            self.editar_porta
        )

        self.adicionar_pagina_configuracoes(
            aba,
            "Portas",
            "Gerencie as portas TCP utilizadas nos diagnósticos."
        )

    # ==================================================
    # DOWNDETECTOR
    # ==================================================

    def criar_aba_down_detector(
        self
    ):
        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        formulario = QFormLayout()

        self.intervalo_down_detector = QDoubleSpinBox()

        self.intervalo_down_detector.setRange(
            1.0,
            300.0
        )

        self.intervalo_down_detector.setDecimals(
            1
        )

        self.intervalo_down_detector.setSuffix(
            " s"
        )

        self.intervalo_down_detector.setValue(
            self.configuracoes[
                "intervalo_down_detector"
            ]
        )

        formulario.addRow(
            "Intervalo de monitoramento:",
            self.intervalo_down_detector
        )

        self.falhas_offline = QSpinBox()

        self.falhas_offline.setRange(
            1,
            20
        )

        self.falhas_offline.setValue(
            self.configuracoes[
                "falhas_down_detector_offline"
            ]
        )

        formulario.addRow(
            "Falhas para considerar indisponível:",
            self.falhas_offline
        )

        layout.addLayout(
            formulario
        )

        self.tabela_servicos = QTableWidget()

        self.tabela_servicos.setColumnCount(
            5
        )

        self.tabela_servicos.setHorizontalHeaderLabels([
            "Serviço",
            "Tipo",
            "Endereço",
            "Alerta",
            "Som"
        ])

        self.configurar_tabela(
            self.tabela_servicos
        )

        cabecalho = (
            self.tabela_servicos
            .horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        cabecalho.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents
        )

        layout.addWidget(
            self.tabela_servicos
        )

        botoes = QHBoxLayout()

        predefinido = QPushButton(
            "Adicionar pré-definido"
        )

        adicionar = QPushButton(
            "Adicionar personalizado"
        )

        editar = QPushButton(
            "Editar"
        )

        configurar_alerta = QPushButton(
            "Configurar alerta"
        )

        remover = QPushButton(
            "Remover"
        )

        botoes.addWidget(
            predefinido
        )

        botoes.addWidget(
            adicionar
        )

        botoes.addWidget(
            editar
        )

        botoes.addWidget(
            configurar_alerta
        )

        botoes.addWidget(
            remover
        )

        layout.addLayout(
            botoes
        )

        self.carregar_servicos()

        predefinido.clicked.connect(
            self.adicionar_predefinido
        )

        adicionar.clicked.connect(
            self.adicionar_servico
        )

        editar.clicked.connect(
            self.editar_servico
        )

        configurar_alerta.clicked.connect(
            self.configurar_alerta_servico
        )

        remover.clicked.connect(
            self.remover_servico
        )

        self.tabela_servicos.doubleClicked.connect(
            self.editar_servico
        )

        self.adicionar_pagina_configuracoes(
            aba,
            "Monitor de Serviços",
            "Configure os serviços monitorados, frequência de "
            "verificação e critérios de indisponibilidade."
        )

    # ==================================================
    # TRACERT CONTÍNUO
    # ==================================================

    def criar_aba_tracert_continuo(
        self
    ):
        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        formulario = QFormLayout()

        self.tracert_amostra_minima = QSpinBox()

        self.tracert_amostra_minima.setRange(
            5,
            1000
        )

        self.tracert_amostra_minima.setSuffix(
            " ciclos"
        )

        self.tracert_amostra_minima.setValue(
            self.configuracoes.get(
                "tracert_continuo_amostra_minima",
                30
            )
        )

        formulario.addRow(
            "Amostra mínima para análise:",
            self.tracert_amostra_minima
        )

        layout.addLayout(
            formulario
        )

        explicacao = QLabel(
            "Antes da amostra mínima os resultados "
            "são considerados preliminares."
        )

        explicacao.setWordWrap(
            True
        )

        layout.addWidget(
            explicacao
        )

        layout.addStretch()

        self.adicionar_pagina_configuracoes(
            aba,
            "Monitor de Rota",
            "Defina a amostra mínima usada na análise contínua da rota."
        )

    # ==================================================
    # REGISTRO DE INCIDENTES
    # ==================================================

    def criar_aba_incidentes(
        self
    ):
        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        layout.setSpacing(
            14
        )

        self.checkbox_registro_incidentes = QCheckBox(
            "Registrar incidentes automaticamente"
        )

        self.checkbox_registro_incidentes.setChecked(
            self.configuracoes.get(
                "registro_incidentes_ativado",
                True
            )
        )

        layout.addWidget(
            self.checkbox_registro_incidentes
        )

        formulario = QFormLayout()

        self.retencao_incidentes = QSpinBox()

        self.retencao_incidentes.setRange(
            7,
            3650
        )

        self.retencao_incidentes.setSuffix(
            " dias"
        )

        self.retencao_incidentes.setValue(
            int(
                self.configuracoes.get(
                    "registro_incidentes_retencao_dias",
                    90
                )
            )
        )

        self.retencao_incidentes.setToolTip(
            "Incidentes normalizados mais antigos que este período "
            "serão removidos automaticamente."
        )

        formulario.addRow(
            "Retenção do histórico:",
            self.retencao_incidentes
        )

        layout.addLayout(
            formulario
        )

        painel_info = QFrame()

        painel_info.setObjectName(
            "painelConfiguracaoInfo"
        )

        layout_info = QVBoxLayout(
            painel_info
        )

        titulo_info = QLabel(
            "Como funciona o Registro de Incidentes?"
        )

        titulo_info.setObjectName(
            "tituloConfiguracaoInfo"
        )

        descricao = QLabel(
            "O NDT registra falhas críticas de serviços e episódios "
            "de instabilidade geral da rede. O histórico armazena o "
            "horário de início, normalização, duração e causa provável. "
            "O registro é independente dos alertas sonoros."
        )

        descricao.setWordWrap(
            True
        )

        observacao = QLabel(
            "A retenção é aplicada apenas a incidentes já normalizados. "
            "Incidentes em andamento nunca são removidos automaticamente."
        )

        observacao.setWordWrap(
            True
        )

        layout_info.addWidget(
            titulo_info
        )

        layout_info.addWidget(
            descricao
        )

        layout_info.addSpacing(
            8
        )

        layout_info.addWidget(
            observacao
        )

        layout.addWidget(
            painel_info
        )

        linha_limpar = QHBoxLayout()

        botao_limpar = QPushButton(
            "Limpar histórico"
        )

        botao_limpar.setObjectName(
            "botaoLimparHistorico"
        )

        botao_limpar.setToolTip(
            "Apagar todos os incidentes já normalizados"
        )

        botao_limpar.clicked.connect(
            self.limpar_historico_incidentes
        )

        linha_limpar.addWidget(
            botao_limpar
        )

        linha_limpar.addStretch()

        layout.addLayout(
            linha_limpar
        )

        layout.addStretch()

        self.checkbox_registro_incidentes.toggled.connect(
            self.atualizar_controles_incidentes
        )

        self.atualizar_controles_incidentes()

        self.adicionar_pagina_configuracoes(
            aba,
            "Incidentes",
            "Controle o Registro de Incidentes, retenção do histórico "
            "e limpeza de eventos já normalizados."
        )

    def atualizar_controles_incidentes(
        self
    ):
        self.retencao_incidentes.setEnabled(
            self.checkbox_registro_incidentes.isChecked()
        )

    def limpar_historico_incidentes(
        self
    ):
        resposta = QMessageBox.warning(
            self,
            "Limpar histórico",
            "Deseja apagar todos os incidentes já normalizados?\n\n"
            "Incidentes em andamento serão preservados.\n"
            "Esta ação é imediata e não pode ser desfeita.",
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
            removidos = limpar_incidentes_encerrados()

        except Exception as erro:
            QMessageBox.critical(
                self,
                "Registro de Incidentes",
                "Não foi possível limpar o histórico.\n\n"
                f"Detalhes: {erro}"
            )

            return

        QMessageBox.information(
            self,
            "Registro de Incidentes",
            (
                f"{removidos} incidente removido."
                if removidos == 1
                else f"{removidos} incidentes removidos."
            )
        )

    # ==================================================
    # ALERTAS
    # ==================================================

    def criar_aba_alertas(
        self
    ):
        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        layout.setSpacing(
            14
        )

        self.checkbox_alerta_sonoro_geral = QCheckBox(
            "Ativar alerta sonoro para falha geral da rede"
        )

        self.checkbox_alerta_sonoro_geral.setChecked(
            self.configuracoes.get(
                "alerta_sonoro_geral_ativado",
                True
            )
        )

        layout.addWidget(
            self.checkbox_alerta_sonoro_geral
        )

        self.checkbox_alerta_servico_indisponivel = QCheckBox(
            "Ativar alerta sonoro quando um serviço ficar indisponível"
        )

        self.checkbox_alerta_servico_indisponivel.setChecked(
            self.configuracoes.get(
                "alerta_sonoro_servico_indisponivel_ativado",
                True
            )
        )

        layout.addWidget(
            self.checkbox_alerta_servico_indisponivel
        )

        formulario = QFormLayout()

        self.combo_alerta_sonoro = QComboBox()

        self.combo_alerta_sonoro.addItem(
            "Padrão do Windows",
            "padrao"
        )

        self.combo_alerta_sonoro.addItem(
            "Arquivo WAV personalizado",
            "personalizado"
        )

        modo_atual = self.configuracoes.get(
            "alerta_sonoro_modo",
            "padrao"
        )

        indice = self.combo_alerta_sonoro.findData(
            modo_atual
        )

        if indice >= 0:
            self.combo_alerta_sonoro.setCurrentIndex(
                indice
            )

        formulario.addRow(
            "Som do alerta:",
            self.combo_alerta_sonoro
        )

        self.cooldown_alertas = QSpinBox()

        self.cooldown_alertas.setRange(
            0,
            1440
        )

        self.cooldown_alertas.setSuffix(
            " min"
        )

        self.cooldown_alertas.setSpecialValueText(
            "Desativado"
        )

        self.cooldown_alertas.setValue(
            int(
                self.configuracoes.get(
                    "alerta_cooldown_minutos",
                    5
                )
            )
        )

        self.cooldown_alertas.setToolTip(
            "Tempo mínimo para que uma nova queda do mesmo serviço "
            "possa gerar outro alerta sonoro após a normalização."
        )

        formulario.addRow(
            "Cooldown dos alertas:",
            self.cooldown_alertas
        )

        layout.addLayout(
            formulario
        )

        self.container_alerta_personalizado = QWidget()

        layout_personalizado = QHBoxLayout(
            self.container_alerta_personalizado
        )

        layout_personalizado.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.campo_alerta_sonoro = QLineEdit()

        self.campo_alerta_sonoro.setPlaceholderText(
            "Caminho do arquivo de áudio .WAV"
        )

        self.campo_alerta_sonoro.setText(
            self.configuracoes.get(
                "alerta_sonoro_arquivo",
                ""
            )
        )

        botao_procurar = QPushButton(
            "Procurar..."
        )

        botao_procurar.clicked.connect(
            self.procurar_som_alerta
        )

        layout_personalizado.addWidget(
            self.campo_alerta_sonoro,
            1
        )

        layout_personalizado.addWidget(
            botao_procurar
        )

        layout.addWidget(
            self.container_alerta_personalizado
        )

        painel_info = QFrame()

        painel_info.setObjectName(
            "painelConfiguracaoInfo"
        )

        layout_info = QVBoxLayout(
            painel_info
        )

        titulo_info = QLabel(
            "Como funciona o alerta geral?"
        )

        titulo_info.setObjectName(
            "tituloConfiguracaoInfo"
        )

        descricao = QLabel(
            "O alerta geral toca uma única vez quando vários serviços "
            "indicam uma possível falha da rede local. O alerta de "
            "serviço indisponível será usado quando um destino acumular "
            "o número configurado de falhas consecutivas e realmente "
            "entrar em estado indisponível. Após a normalização, o "
            "cooldown impede que o mesmo serviço gere novos sons em "
            "intervalos muito curtos caso fique alternando entre "
            "online e offline."
        )

        descricao.setWordWrap(
            True
        )

        observacao = QLabel(
            "Arquivos personalizados devem estar no formato WAV. "
            "Na categoria Monitor de Serviços, selecione um serviço e use "
            "“Configurar alerta” para definir uma configuração "
            "sonora específica para ele. Serviços sem configuração "
            "própria continuam usando o alerta global."
        )

        observacao.setWordWrap(
            True
        )

        layout_info.addWidget(
            titulo_info
        )

        layout_info.addWidget(
            descricao
        )

        layout_info.addSpacing(
            8
        )

        layout_info.addWidget(
            observacao
        )

        layout.addWidget(
            painel_info
        )

        botao_testar = QPushButton(
            "Testar som"
        )

        botao_testar.clicked.connect(
            self.testar_som_alerta
        )

        layout.addWidget(
            botao_testar
        )

        layout.addStretch()

        self.combo_alerta_sonoro.currentIndexChanged.connect(
            self.atualizar_alerta_personalizado
        )

        self.atualizar_alerta_personalizado()

        self.adicionar_pagina_configuracoes(
            aba,
            "Alertas",
            "Configure sons, alertas gerais, alertas por serviço "
            "e o cooldown entre notificações."
        )

    def atualizar_alerta_personalizado(
        self
    ):
        modo = (
            self.combo_alerta_sonoro
            .currentData()
        )

        self.container_alerta_personalizado.setVisible(
            modo == "personalizado"
        )

    def procurar_som_alerta(
        self
    ):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar som de alerta",
            "",
            "Arquivos WAV (*.wav);;Todos os arquivos (*)"
        )

        if caminho:
            self.campo_alerta_sonoro.setText(
                caminho
            )

    def testar_som_alerta(
        self
    ):
        modo = (
            self.combo_alerta_sonoro
            .currentData()
        )

        if modo is None:
            modo = "padrao"

        caminho = (
            self.campo_alerta_sonoro
            .text()
            .strip()
        )

        if (
            modo == "personalizado"
            and not caminho
        ):
            QMessageBox.warning(
                self,
                "Som personalizado",
                "Selecione um arquivo WAV para testar."
            )

            return

        sucesso = testar_alerta(
            modo=modo,
            arquivo=caminho
        )

        if sucesso:
            QMessageBox.information(
                self,
                "Teste de alerta",
                "O som de alerta foi reproduzido com sucesso."
            )

        else:
            QMessageBox.warning(
                self,
                "Falha no teste",
                "Não foi possível reproduzir o som.\n\n"
                "Verifique se o arquivo existe e está no formato WAV."
            )

    # ==================================================
    # NAVEGADOR
    # ==================================================

    def criar_aba_navegador(
        self
    ):
        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        layout.setSpacing(
            14
        )

        formulario = QFormLayout()

        self.combo_navegador = QComboBox()

        for chave, nome in NAVEGADORES.items():
            self.combo_navegador.addItem(
                nome,
                chave
            )

        navegador_atual = (
            self.configuracoes.get(
                "navegador_preferido",
                "padrao"
            )
        )

        indice = self.combo_navegador.findData(
            navegador_atual
        )

        if indice >= 0:
            self.combo_navegador.setCurrentIndex(
                indice
            )

        formulario.addRow(
            "Navegador:",
            self.combo_navegador
        )

        layout.addLayout(
            formulario
        )

        self.container_personalizado = QWidget()

        layout_personalizado = QHBoxLayout(
            self.container_personalizado
        )

        layout_personalizado.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.campo_navegador_personalizado = QLineEdit()

        self.campo_navegador_personalizado.setPlaceholderText(
            "Caminho do executável do navegador"
        )

        self.campo_navegador_personalizado.setText(
            self.configuracoes.get(
                "navegador_personalizado",
                ""
            )
        )

        botao_procurar = QPushButton(
            "Procurar..."
        )

        botao_procurar.clicked.connect(
            self.procurar_navegador
        )

        layout_personalizado.addWidget(
            self.campo_navegador_personalizado,
            1
        )

        layout_personalizado.addWidget(
            botao_procurar
        )

        layout.addWidget(
            self.container_personalizado
        )

        self.checkbox_abrir_interface = QCheckBox(
            "Abrir automaticamente uma interface web encontrada"
        )

        self.checkbox_abrir_interface.setChecked(
            self.configuracoes.get(
                "abrir_interface_web_automaticamente",
                True
            )
        )

        layout.addWidget(
            self.checkbox_abrir_interface
        )

        painel_info = QFrame()

        painel_info.setObjectName(
            "painelConfiguracaoInfo"
        )

        layout_info = QVBoxLayout(
            painel_info
        )

        titulo_info = QLabel(
            "Como funciona a abertura automática?"
        )

        titulo_info.setObjectName(
            "tituloConfiguracaoInfo"
        )

        descricao = QLabel(
            "Ao encontrar uma interface web acessível, "
            "o NDT abre apenas a opção preferencial, priorizando "
            "HTTPS quando disponível."
        )

        descricao.setWordWrap(
            True
        )

        prioridade_titulo = QLabel(
            "Prioridade de acesso"
        )

        prioridade_titulo.setObjectName(
            "subtituloConfiguracaoInfo"
        )

        prioridade = QLabel(
            "1. Interfaces configuradas ou detectadas como HTTPS\n"
            "2. Interfaces configuradas ou detectadas como HTTP\n"
            "3. Em modo Automático, o NDT testa HTTPS e depois HTTP"
        )

        prioridade.setWordWrap(
            True
        )

        observacao = QLabel(
            "Se você selecionar “Outro navegador...”, "
            "poderá apontar para qualquer executável, como "
            "Firefox, Opera, Vivaldi ou outro navegador instalado."
        )

        observacao.setWordWrap(
            True
        )

        layout_info.addWidget(
            titulo_info
        )

        layout_info.addWidget(
            descricao
        )

        layout_info.addSpacing(
            8
        )

        layout_info.addWidget(
            prioridade_titulo
        )

        layout_info.addWidget(
            prioridade
        )

        layout_info.addSpacing(
            8
        )

        layout_info.addWidget(
            observacao
        )

        layout.addWidget(
            painel_info
        )

        botao_testar = QPushButton(
            "Testar navegador"
        )

        botao_testar.setObjectName(
            "botaoTestarNavegador"
        )

        botao_testar.clicked.connect(
            self.testar_navegador
        )

        layout.addWidget(
            botao_testar
        )

        layout.addStretch()

        self.combo_navegador.currentIndexChanged.connect(
            self.atualizar_navegador_personalizado
        )

        self.atualizar_navegador_personalizado()

        self.adicionar_pagina_configuracoes(
            aba,
            "Navegador",
            "Escolha o navegador usado pelo NDT e o comportamento "
            "de abertura automática das interfaces web."
        )

    def atualizar_navegador_personalizado(
        self
    ):
        navegador = (
            self.combo_navegador
            .currentData()
        )

        self.container_personalizado.setVisible(
            navegador == "personalizado"
        )

    def procurar_navegador(
        self
    ):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar navegador",
            "",
            "Executáveis (*.exe);;Todos os arquivos (*)"
        )

        if caminho:
            self.campo_navegador_personalizado.setText(
                caminho
            )

    def testar_navegador(
        self
    ):
        navegador = (
            self.combo_navegador
            .currentData()
        )

        if navegador is None:
            navegador = "padrao"

        caminho = (
            self.campo_navegador_personalizado
            .text()
            .strip()
        )

        abriu_preferido, usado = abrir_url(
            "https://example.com",
            navegador,
            caminho
        )

        if (
            navegador == "padrao"
            or abriu_preferido
        ):
            QMessageBox.information(
                self,
                "Teste do navegador",
                "A página foi aberta usando:\n\n"
                f"{obter_nome_navegador(usado)}"
            )

        else:
            QMessageBox.warning(
                self,
                "Navegador não encontrado",
                "O navegador selecionado não foi localizado.\n\n"
                "O navegador padrão do Windows foi usado."
            )

    # ==================================================
    # TABELAS
    # ==================================================

    def configurar_tabela(
        self,
        tabela
    ):
        tabela.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        tabela.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .SingleSelection
        )

        tabela.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        tabela.verticalHeader().setVisible(
            False
        )

    # ==================================================
    # PORTAS
    # ==================================================

    def inferir_interface_web_porta(
        self,
        porta
    ):
        interfaces = self.configuracoes.get(
            "interfaces_web_portas",
            {}
        )

        protocolo = str(
            interfaces.get(
                str(
                    porta
                ),
                ""
            )
        ).strip().upper()

        if protocolo in {
            "HTTP",
            "HTTPS",
            "AUTOMATICO",
            "NENHUMA"
        }:
            return protocolo

        if porta in {
            443,
            8443
        }:
            return "HTTPS"

        if porta in {
            80,
            8000,
            8080
        }:
            return "HTTP"

        return "NENHUMA"

    def solicitar_interface_web(
        self,
        titulo,
        porta,
        valor_atual=None
    ):
        opcoes = [
            "Nenhuma",
            "HTTP",
            "HTTPS",
            "Automático (HTTP/HTTPS)"
        ]

        mapa = {
            "NENHUMA": "Nenhuma",
            "HTTP": "HTTP",
            "HTTPS": "HTTPS",
            "AUTOMATICO": "Automático (HTTP/HTTPS)"
        }

        if valor_atual is None:
            protocolo_atual = (
                self.inferir_interface_web_porta(
                    porta
                )
            )
        else:
            protocolo_atual = str(
                valor_atual
            ).strip().upper()

        if protocolo_atual == "AUTOMÁTICO":
            protocolo_atual = "AUTOMATICO"

        if protocolo_atual == "AUTOMÁTICO (HTTP/HTTPS)":
            protocolo_atual = "AUTOMATICO"

        if protocolo_atual == "AUTOMÁTICO":
            protocolo_atual = "AUTOMATICO"

        exibicao_atual = mapa.get(
            protocolo_atual,
            "Nenhuma"
        )

        indice = opcoes.index(
            exibicao_atual
        )

        escolha, ok = QInputDialog.getItem(
            self,
            titulo,
            "Interface Web:",
            opcoes,
            indice,
            False
        )

        if not ok:
            return None

        if escolha == "Nenhuma":
            return "NENHUMA"

        if escolha == "Automático (HTTP/HTTPS)":
            return "AUTOMATICO"

        return escolha.upper()

    def carregar_portas(
        self
    ):
        self.tabela_portas.setRowCount(
            0
        )

        for porta, servico in (
            self.configuracoes[
                "portas"
            ].items()
        ):
            linha = self.tabela_portas.rowCount()

            self.tabela_portas.insertRow(
                linha
            )

            self.tabela_portas.setItem(
                linha,
                0,
                QTableWidgetItem(
                    str(porta)
                )
            )

            self.tabela_portas.setItem(
                linha,
                1,
                QTableWidgetItem(
                    servico
                )
            )

            protocolo = self.inferir_interface_web_porta(
                int(
                    porta
                )
            )

            if protocolo == "NENHUMA":
                texto_protocolo = "Nenhuma"

            elif protocolo == "AUTOMATICO":
                texto_protocolo = "Automático"

            else:
                texto_protocolo = protocolo

            self.tabela_portas.setItem(
                linha,
                2,
                QTableWidgetItem(
                    texto_protocolo
                )
            )

    def porta_existe(
        self,
        porta
    ):
        for linha in range(
            self.tabela_portas.rowCount()
        ):
            item = self.tabela_portas.item(
                linha,
                0
            )

            if (
                item is not None
                and int(item.text()) == porta
            ):
                return True

        return False

    def adicionar_porta(
        self
    ):
        porta, ok = QInputDialog.getInt(
            self,
            "Adicionar porta",
            "Porta:",
            80,
            1,
            65535
        )

        if not ok:
            return

        if self.porta_existe(
            porta
        ):
            QMessageBox.warning(
                self,
                "Porta existente",
                "Essa porta já está cadastrada."
            )

            return

        servico, ok = QInputDialog.getText(
            self,
            "Serviço",
            "Nome:"
        )

        if not ok:
            return

        protocolo_web = self.solicitar_interface_web(
            "Interface Web",
            porta
        )

        if protocolo_web is None:
            return

        linha = self.tabela_portas.rowCount()

        self.tabela_portas.insertRow(
            linha
        )

        self.tabela_portas.setItem(
            linha,
            0,
            QTableWidgetItem(
                str(porta)
            )
        )

        self.tabela_portas.setItem(
            linha,
            1,
            QTableWidgetItem(
                servico.strip()
                or "TCP"
            )
        )

        self.tabela_portas.setItem(
            linha,
            2,
            QTableWidgetItem(
                (
                    "Nenhuma"
                    if protocolo_web == "NENHUMA"
                    else (
                        "Automático"
                        if protocolo_web == "AUTOMATICO"
                        else protocolo_web
                    )
                )
            )
        )

    def editar_porta(
        self
    ):
        linha = self.tabela_portas.currentRow()

        if linha < 0:
            return

        item_porta = self.tabela_portas.item(
            linha,
            0
        )

        item_servico = self.tabela_portas.item(
            linha,
            1
        )

        item_interface = self.tabela_portas.item(
            linha,
            2
        )

        if (
            item_porta is None
            or item_servico is None
            or item_interface is None
        ):
            return

        porta_atual = int(
            item_porta.text()
        )

        porta, ok = QInputDialog.getInt(
            self,
            "Editar porta",
            "Porta:",
            porta_atual,
            1,
            65535
        )

        if not ok:
            return

        if (
            porta != porta_atual
            and self.porta_existe(
                porta
            )
        ):
            QMessageBox.warning(
                self,
                "Porta existente",
                "Essa porta já está cadastrada."
            )

            return

        servico, ok = QInputDialog.getText(
            self,
            "Editar serviço",
            "Serviço:",
            text=item_servico.text()
        )

        if not ok:
            return

        protocolo_web = self.solicitar_interface_web(
            "Editar Interface Web",
            porta,
            item_interface.text()
        )

        if protocolo_web is None:
            return

        self.tabela_portas.setItem(
            linha,
            0,
            QTableWidgetItem(
                str(porta)
            )
        )

        self.tabela_portas.setItem(
            linha,
            1,
            QTableWidgetItem(
                servico.strip()
                or "TCP"
            )
        )

        self.tabela_portas.setItem(
            linha,
            2,
            QTableWidgetItem(
                (
                    "Nenhuma"
                    if protocolo_web == "NENHUMA"
                    else (
                        "Automático"
                        if protocolo_web == "AUTOMATICO"
                        else protocolo_web
                    )
                )
            )
        )

    def remover_porta(
        self
    ):
        linha = self.tabela_portas.currentRow()

        if linha >= 0:
            self.tabela_portas.removeRow(
                linha
            )

    # ==================================================
    # DOWNDETECTOR
    # ==================================================

    def carregar_servicos(
        self
    ):
        self.tabela_servicos.setRowCount(
            0
        )

        for servico in (
            self.configuracoes.get(
                "servicos_down_detector",
                []
            )
        ):
            self.inserir_servico_tabela(
                servico
            )

    def normalizar_config_alerta_servico(
        self,
        servico
    ):
        servico = deepcopy(
            servico
        )

        servico.setdefault(
            "alerta_individual_ativado",
            False
        )

        modo = servico.get(
            "alerta_individual_modo",
            "global"
        )

        if modo not in {
            "global",
            "padrao",
            "personalizado"
        }:
            modo = "global"

        servico[
            "alerta_individual_modo"
        ] = modo

        arquivo = servico.get(
            "alerta_individual_arquivo",
            ""
        )

        if not isinstance(
            arquivo,
            str
        ):
            arquivo = ""

        servico[
            "alerta_individual_arquivo"
        ] = arquivo

        return servico

    def obter_texto_alerta_servico(
        self,
        servico
    ):
        if not servico.get(
            "alerta_individual_ativado",
            False
        ):
            return (
                "Global",
                "Som global"
            )

        modo = servico.get(
            "alerta_individual_modo",
            "global"
        )

        if modo == "personalizado":
            arquivo = servico.get(
                "alerta_individual_arquivo",
                ""
            )

            nome_arquivo = (
                Path(
                    arquivo
                ).name
                if arquivo
                else "WAV"
            )

            return (
                "Personalizado",
                nome_arquivo
            )

        if modo == "padrao":
            return (
                "Personalizado",
                "Padrão NDT"
            )

        return (
            "Personalizado",
            "Som global"
        )

    def inserir_servico_tabela(
        self,
        servico
    ):
        servico = self.normalizar_config_alerta_servico(
            servico
        )

        linha = self.tabela_servicos.rowCount()

        self.tabela_servicos.insertRow(
            linha
        )

        item_nome = QTableWidgetItem(
            servico.get(
                "nome",
                "Serviço"
            )
        )

        item_nome.setData(
            Qt.ItemDataRole.UserRole,
            servico
        )

        self.tabela_servicos.setItem(
            linha,
            0,
            item_nome
        )

        self.tabela_servicos.setItem(
            linha,
            1,
            QTableWidgetItem(
                servico.get(
                    "tipo",
                    "PING"
                ).upper()
            )
        )

        self.tabela_servicos.setItem(
            linha,
            2,
            QTableWidgetItem(
                servico.get(
                    "endereco",
                    ""
                )
            )
        )

        texto_alerta, texto_som = (
            self.obter_texto_alerta_servico(
                servico
            )
        )

        self.tabela_servicos.setItem(
            linha,
            3,
            QTableWidgetItem(
                texto_alerta
            )
        )

        self.tabela_servicos.setItem(
            linha,
            4,
            QTableWidgetItem(
                texto_som
            )
        )

    def obter_servico_linha(
        self,
        linha
    ):
        item_nome = self.tabela_servicos.item(
            linha,
            0
        )

        item_tipo = self.tabela_servicos.item(
            linha,
            1
        )

        item_endereco = self.tabela_servicos.item(
            linha,
            2
        )

        if (
            item_nome is None
            or item_tipo is None
            or item_endereco is None
        ):
            return None

        metadados = item_nome.data(
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            metadados,
            dict
        ):
            metadados = {}

        servico = deepcopy(
            metadados
        )

        servico["nome"] = item_nome.text()
        servico["tipo"] = item_tipo.text()
        servico["endereco"] = item_endereco.text()

        return self.normalizar_config_alerta_servico(
            servico
        )

    def atualizar_servico_linha(
        self,
        linha,
        servico
    ):
        servico = self.normalizar_config_alerta_servico(
            servico
        )

        item_nome = self.tabela_servicos.item(
            linha,
            0
        )

        if item_nome is None:
            item_nome = QTableWidgetItem()
            self.tabela_servicos.setItem(
                linha,
                0,
                item_nome
            )

        item_nome.setText(
            servico.get(
                "nome",
                "Serviço"
            )
        )

        item_nome.setData(
            Qt.ItemDataRole.UserRole,
            servico
        )

        self.tabela_servicos.setItem(
            linha,
            1,
            QTableWidgetItem(
                servico.get(
                    "tipo",
                    "PING"
                ).upper()
            )
        )

        self.tabela_servicos.setItem(
            linha,
            2,
            QTableWidgetItem(
                servico.get(
                    "endereco",
                    ""
                )
            )
        )

        texto_alerta, texto_som = (
            self.obter_texto_alerta_servico(
                servico
            )
        )

        self.tabela_servicos.setItem(
            linha,
            3,
            QTableWidgetItem(
                texto_alerta
            )
        )

        self.tabela_servicos.setItem(
            linha,
            4,
            QTableWidgetItem(
                texto_som
            )
        )

    def obter_servicos_tabela(
        self
    ):
        servicos = []

        for linha in range(
            self.tabela_servicos.rowCount()
        ):
            servico = self.obter_servico_linha(
                linha
            )

            if servico is not None:
                servicos.append(
                    servico
                )

        return servicos

    def servico_existe(
        self,
        servico
    ):
        chave = criar_chave_servico(
            servico
        )

        for existente in self.obter_servicos_tabela():
            if (
                criar_chave_servico(
                    existente
                )
                == chave
            ):
                return True

        return False

    def adicionar_predefinido(
        self
    ):
        opcoes = [
            (
                f"[{item['categoria']}] "
                f"{item['nome']}"
            )
            for item in PRESET_SERVICOS
        ]

        escolha, ok = QInputDialog.getItem(
            self,
            "Serviço pré-definido",
            "Selecione:",
            opcoes,
            0,
            False
        )

        if not ok:
            return

        indice = opcoes.index(
            escolha
        )

        servico = deepcopy(
            PRESET_SERVICOS[
                indice
            ]
        )

        servico.pop(
            "categoria",
            None
        )

        if self.servico_existe(
            servico
        ):
            QMessageBox.information(
                self,
                "Serviço existente",
                "Esse serviço já está cadastrado."
            )

            return

        self.inserir_servico_tabela(
            servico
        )

    def adicionar_servico(
        self
    ):
        nome, ok = QInputDialog.getText(
            self,
            "Novo serviço",
            "Nome:"
        )

        if not ok:
            return

        nome = nome.strip()

        if not nome:
            return

        endereco, ok = QInputDialog.getText(
            self,
            "Novo serviço",
            "IP, domínio ou URL:"
        )

        if not ok:
            return

        endereco = endereco.strip()

        if normalizar_alvo(
            endereco
        ) is None:
            QMessageBox.warning(
                self,
                "Endereço inválido",
                "Informe um IP, domínio ou URL válido."
            )

            return

        escolha, ok = QInputDialog.getItem(
            self,
            "Tipo de monitoramento",
            "Tipo:",
            [
                "PING",
                "HTTP/HTTPS"
            ],
            0,
            False
        )

        if not ok:
            return

        tipo = (
            "HTTP"
            if escolha == "HTTP/HTTPS"
            else "PING"
        )

        servico = {
            "nome": nome,
            "endereco": endereco,
            "tipo": tipo,
            "alerta_individual_ativado": False,
            "alerta_individual_modo": "global",
            "alerta_individual_arquivo": ""
        }

        if self.servico_existe(
            servico
        ):
            QMessageBox.information(
                self,
                "Serviço existente",
                "Esse serviço já está cadastrado."
            )

            return

        self.inserir_servico_tabela(
            servico
        )

    def editar_servico(
        self
    ):
        linha = self.tabela_servicos.currentRow()

        if linha < 0:
            return

        servico_atual = self.obter_servico_linha(
            linha
        )

        if servico_atual is None:
            return

        nome, ok = QInputDialog.getText(
            self,
            "Editar serviço",
            "Nome:",
            text=servico_atual.get(
                "nome",
                ""
            )
        )

        if not ok:
            return

        endereco, ok = QInputDialog.getText(
            self,
            "Editar serviço",
            "IP, domínio ou URL:",
            text=servico_atual.get(
                "endereco",
                ""
            )
        )

        if not ok:
            return

        endereco = endereco.strip()

        if normalizar_alvo(
            endereco
        ) is None:
            QMessageBox.warning(
                self,
                "Endereço inválido",
                "Informe um IP, domínio ou URL válido."
            )
            return

        escolha_atual = (
            1
            if servico_atual.get(
                "tipo",
                "PING"
            ) == "HTTP"
            else 0
        )

        escolha, ok = QInputDialog.getItem(
            self,
            "Tipo",
            "Monitoramento:",
            [
                "PING",
                "HTTP/HTTPS"
            ],
            escolha_atual,
            False
        )

        if not ok:
            return

        tipo = (
            "HTTP"
            if escolha == "HTTP/HTTPS"
            else "PING"
        )

        servico_atual["nome"] = (
            nome.strip()
            or "Serviço"
        )
        servico_atual["tipo"] = tipo
        servico_atual["endereco"] = endereco

        self.atualizar_servico_linha(
            linha,
            servico_atual
        )

    def configurar_alerta_servico(
        self
    ):
        linha = self.tabela_servicos.currentRow()

        if linha < 0:
            QMessageBox.information(
                self,
                "Configurar alerta",
                "Selecione um serviço na tabela."
            )
            return

        servico = self.obter_servico_linha(
            linha
        )

        if servico is None:
            return

        janela = QDialog(
            self
        )
        janela.setWindowTitle(
            "Alerta do serviço"
        )
        janela.resize(
            560,
            330
        )

        layout = QVBoxLayout(
            janela
        )

        titulo = QLabel(
            servico.get(
                "nome",
                "Serviço"
            )
        )
        titulo.setObjectName(
            "tituloConfiguracaoInfo"
        )
        layout.addWidget(
            titulo
        )

        descricao = QLabel(
            "A configuração específica substitui o som global "
            "somente para este serviço quando ele ficar indisponível."
        )
        descricao.setWordWrap(
            True
        )
        layout.addWidget(
            descricao
        )

        checkbox_especifico = QCheckBox(
            "Usar configuração de alerta específica para este serviço"
        )
        checkbox_especifico.setChecked(
            servico.get(
                "alerta_individual_ativado",
                False
            )
        )
        layout.addWidget(
            checkbox_especifico
        )

        formulario = QFormLayout()
        combo_modo = QComboBox()
        combo_modo.addItem(
            "Usar som global",
            "global"
        )
        combo_modo.addItem(
            "Som padrão do NDT",
            "padrao"
        )
        combo_modo.addItem(
            "Arquivo WAV personalizado",
            "personalizado"
        )

        indice = combo_modo.findData(
            servico.get(
                "alerta_individual_modo",
                "global"
            )
        )
        if indice >= 0:
            combo_modo.setCurrentIndex(
                indice
            )

        formulario.addRow(
            "Som:",
            combo_modo
        )
        layout.addLayout(
            formulario
        )

        container_arquivo = QWidget()
        layout_arquivo = QHBoxLayout(
            container_arquivo
        )
        layout_arquivo.setContentsMargins(
            0,
            0,
            0,
            0
        )

        campo_arquivo = QLineEdit()
        campo_arquivo.setPlaceholderText(
            "Caminho do arquivo WAV"
        )
        campo_arquivo.setText(
            servico.get(
                "alerta_individual_arquivo",
                ""
            )
        )

        botao_procurar = QPushButton(
            "Procurar..."
        )
        layout_arquivo.addWidget(
            campo_arquivo,
            1
        )
        layout_arquivo.addWidget(
            botao_procurar
        )
        layout.addWidget(
            container_arquivo
        )

        botoes_audio = QHBoxLayout()
        botao_testar = QPushButton(
            "Testar som"
        )
        botoes_audio.addWidget(
            botao_testar
        )
        botoes_audio.addStretch()
        layout.addLayout(
            botoes_audio
        )
        layout.addStretch()

        botoes_final = QHBoxLayout()
        botao_cancelar = QPushButton(
            "Cancelar"
        )
        botao_salvar = QPushButton(
            "Salvar"
        )
        botoes_final.addStretch()
        botoes_final.addWidget(
            botao_cancelar
        )
        botoes_final.addWidget(
            botao_salvar
        )
        layout.addLayout(
            botoes_final
        )

        def atualizar_campos():
            habilitado = checkbox_especifico.isChecked()
            combo_modo.setEnabled(
                habilitado
            )
            modo = combo_modo.currentData()
            container_arquivo.setVisible(
                habilitado
                and modo == "personalizado"
            )
            botao_testar.setEnabled(
                habilitado
            )

        def procurar_arquivo():
            caminho, _ = QFileDialog.getOpenFileName(
                janela,
                "Selecionar som do serviço",
                "",
                "Arquivos WAV (*.wav);;Todos os arquivos (*)"
            )
            if caminho:
                campo_arquivo.setText(
                    caminho
                )

        def testar_som():
            modo = combo_modo.currentData()

            if modo == "global":
                modo_teste = (
                    self.combo_alerta_sonoro.currentData()
                    or "padrao"
                )
                arquivo_teste = (
                    self.campo_alerta_sonoro.text().strip()
                )
            else:
                modo_teste = modo
                arquivo_teste = campo_arquivo.text().strip()

            if (
                modo_teste == "personalizado"
                and not arquivo_teste
            ):
                QMessageBox.warning(
                    janela,
                    "Som personalizado",
                    "Selecione um arquivo WAV para testar."
                )
                return

            sucesso = testar_alerta(
                modo=modo_teste,
                arquivo=arquivo_teste
            )

            if not sucesso:
                QMessageBox.warning(
                    janela,
                    "Falha no teste",
                    "Não foi possível reproduzir o som."
                )

        def salvar_alerta():
            habilitado = checkbox_especifico.isChecked()
            modo = combo_modo.currentData() or "global"
            arquivo = campo_arquivo.text().strip()

            if (
                habilitado
                and modo == "personalizado"
            ):
                if not arquivo:
                    QMessageBox.warning(
                        janela,
                        "Alerta do serviço",
                        "Selecione um arquivo WAV."
                    )
                    return

                caminho = Path(
                    arquivo
                ).expanduser()

                if (
                    not caminho.is_file()
                    or caminho.suffix.lower() != ".wav"
                ):
                    QMessageBox.warning(
                        janela,
                        "Alerta do serviço",
                        "O arquivo selecionado não é um WAV válido."
                    )
                    return

            servico["alerta_individual_ativado"] = habilitado
            servico["alerta_individual_modo"] = modo
            servico["alerta_individual_arquivo"] = arquivo

            self.atualizar_servico_linha(
                linha,
                servico
            )
            janela.accept()

        checkbox_especifico.toggled.connect(
            atualizar_campos
        )
        combo_modo.currentIndexChanged.connect(
            atualizar_campos
        )
        botao_procurar.clicked.connect(
            procurar_arquivo
        )
        botao_testar.clicked.connect(
            testar_som
        )
        botao_cancelar.clicked.connect(
            janela.reject
        )
        botao_salvar.clicked.connect(
            salvar_alerta
        )

        atualizar_campos()
        janela.exec()

    def remover_servico(
        self
    ):
        linha = self.tabela_servicos.currentRow()

        if linha >= 0:
            self.tabela_servicos.removeRow(
                linha
            )

    # ==================================================
    # SALVAR
    # ==================================================

    def salvar(
        self
    ):
        portas = {}
        interfaces_web_portas = {}

        for linha in range(
            self.tabela_portas.rowCount()
        ):
            item_porta = self.tabela_portas.item(
                linha,
                0
            )

            item_servico = self.tabela_portas.item(
                linha,
                1
            )

            item_interface = self.tabela_portas.item(
                linha,
                2
            )

            if (
                item_porta is None
                or item_servico is None
                or item_interface is None
            ):
                continue

            porta_texto = item_porta.text()

            portas[
                porta_texto
            ] = item_servico.text()

            protocolo = (
                item_interface.text()
                .strip()
                .upper()
            )

            if protocolo in {
                "AUTOMÁTICO",
                "AUTOMÁTICO (HTTP/HTTPS)"
            }:
                protocolo = "AUTOMATICO"

            if protocolo not in {
                "HTTP",
                "HTTPS",
                "AUTOMATICO",
                "NENHUMA"
            }:
                protocolo = "NENHUMA"

            interfaces_web_portas[
                porta_texto
            ] = protocolo

        if not portas:
            QMessageBox.warning(
                self,
                "Sem portas",
                "Cadastre pelo menos uma porta."
            )

            return

        navegador = (
            self.combo_navegador
            .currentData()
        )

        if navegador is None:
            navegador = "padrao"

        caminho_personalizado = (
            self.campo_navegador_personalizado
            .text()
            .strip()
        )

        if (
            navegador == "personalizado"
            and not caminho_personalizado
        ):
            QMessageBox.warning(
                self,
                "Navegador",
                "Selecione o executável do navegador personalizado."
            )

            return

        alerta_modo = (
            self.combo_alerta_sonoro
            .currentData()
        )

        if alerta_modo is None:
            alerta_modo = "padrao"

        alerta_arquivo = (
            self.campo_alerta_sonoro
            .text()
            .strip()
        )

        if alerta_modo == "personalizado":
            if not alerta_arquivo:
                QMessageBox.warning(
                    self,
                    "Alerta sonoro",
                    "Selecione um arquivo WAV para o alerta personalizado."
                )

                return

            caminho_alerta = Path(
                alerta_arquivo
            ).expanduser()

            if (
                not caminho_alerta.is_file()
                or caminho_alerta.suffix.lower() != ".wav"
            ):
                QMessageBox.warning(
                    self,
                    "Alerta sonoro",
                    "O arquivo de alerta não é válido.\n\n"
                    "Selecione um arquivo existente no formato WAV."
                )

                return

        self.configuracoes = {
            "quantidade_ping":
                self.quantidade_ping.value(),

            "timeout_portas":
                self.timeout_portas.value(),

            "max_saltos":
                self.max_saltos.value(),

            "limite_variacao_ms":
                self.limite_variacao_ping.value(),

            "limite_variacao_http_ms":
                self.limite_variacao_http.value(),

            "limite_latencia_ping_ms":
                self.limite_latencia_ping.value(),

            "limite_latencia_http_ms":
                self.limite_latencia_http.value(),

            "intervalo_ping_continuo":
                self.intervalo_ping.value(),

            "intervalo_down_detector":
                self.intervalo_down_detector.value(),

            "falhas_down_detector_offline":
                self.falhas_offline.value(),

            "tracert_continuo_amostra_minima":
                self.tracert_amostra_minima.value(),

            "navegador_preferido":
                navegador,

            "navegador_personalizado":
                caminho_personalizado,

            "abrir_interface_web_automaticamente":
                self.checkbox_abrir_interface.isChecked(),

            "exibir_tela_inicializacao":
                self.checkbox_tela_inicializacao.isChecked(),

            "alerta_sonoro_geral_ativado":
                self.checkbox_alerta_sonoro_geral.isChecked(),

            "alerta_sonoro_servico_indisponivel_ativado":
                self.checkbox_alerta_servico_indisponivel.isChecked(),

            "alerta_sonoro_modo":
                alerta_modo,

            "alerta_sonoro_arquivo":
                alerta_arquivo,

            "alerta_cooldown_minutos":
                self.cooldown_alertas.value(),

            "registro_incidentes_ativado":
                self.checkbox_registro_incidentes.isChecked(),

            "registro_incidentes_retencao_dias":
                self.retencao_incidentes.value(),

            "servicos_padrao_inicializados":
                True,

            "servicos_down_detector":
                self.obter_servicos_tabela(),

            "portas":
                portas,

            "interfaces_web_portas":
                interfaces_web_portas
        }

        self.accept()

    def obter_configuracoes(
        self
    ):
        return self.configuracoes
