from copy import deepcopy
from pathlib import Path

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
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget
)

from config.service_presets import (
    PRESET_SERVICOS
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
            780,
            650
        )

        layout = QVBoxLayout(
            self
        )

        self.abas = QTabWidget()

        layout.addWidget(
            self.abas
        )

        self.criar_aba_geral()
        self.criar_aba_portas()
        self.criar_aba_down_detector()
        self.criar_aba_tracert_continuo()
        self.criar_aba_alertas()
        self.criar_aba_navegador()

        botoes = QHBoxLayout()

        botao_cancelar = QPushButton(
            "Cancelar"
        )

        botao_salvar = QPushButton(
            "Salvar"
        )

        botoes.addStretch()

        botoes.addWidget(
            botao_cancelar
        )

        botoes.addWidget(
            botao_salvar
        )

        layout.addLayout(
            botoes
        )

        botao_cancelar.clicked.connect(
            self.reject
        )

        botao_salvar.clicked.connect(
            self.salvar
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

        layout.addStretch()

        self.abas.addTab(
            aba,
            "Geral"
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
            2
        )

        self.tabela_portas.setHorizontalHeaderLabels([
            "Porta",
            "Serviço"
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

        self.abas.addTab(
            aba,
            "Portas"
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
            3
        )

        self.tabela_servicos.setHorizontalHeaderLabels([
            "Serviço",
            "Tipo",
            "Endereço"
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

        remover.clicked.connect(
            self.remover_servico
        )

        self.tabela_servicos.doubleClicked.connect(
            self.editar_servico
        )

        self.abas.addTab(
            aba,
            "DownDetector"
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

        self.abas.addTab(
            aba,
            "Monitor de Rota"
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
            "entrar em estado indisponível. Cada alerta é rearmado "
            "somente após a respectiva condição normalizar."
        )

        descricao.setWordWrap(
            True
        )

        observacao = QLabel(
            "Arquivos personalizados devem estar no formato WAV. "
            "Nesta etapa, o alerta de serviço indisponível usa o "
            "mesmo som configurado para o alerta geral. Sons exclusivos "
            "por serviço poderão ser adicionados depois."
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

        self.abas.addTab(
            aba,
            "Alertas"
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
            "o Network Diagnostic Tool abre apenas uma delas, "
            "usando a opção mais segura disponível."
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
            "1. HTTPS 443\n"
            "2. HTTPS 8443\n"
            "3. HTTP 80\n"
            "4. HTTP 8000\n"
            "5. HTTP 8080"
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

        self.abas.addTab(
            aba,
            "Navegador"
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

        if (
            item_porta is None
            or item_servico is None
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

    def inserir_servico_tabela(
        self,
        servico
    ):
        linha = self.tabela_servicos.rowCount()

        self.tabela_servicos.insertRow(
            linha
        )

        self.tabela_servicos.setItem(
            linha,
            0,
            QTableWidgetItem(
                servico.get(
                    "nome",
                    "Serviço"
                )
            )
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

    def obter_servicos_tabela(
        self
    ):
        servicos = []

        for linha in range(
            self.tabela_servicos.rowCount()
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
                continue

            servicos.append({
                "nome": item_nome.text(),
                "tipo": item_tipo.text(),
                "endereco": item_endereco.text()
            })

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
            "tipo": tipo
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
            return

        nome, ok = QInputDialog.getText(
            self,
            "Editar serviço",
            "Nome:",
            text=item_nome.text()
        )

        if not ok:
            return

        endereco, ok = QInputDialog.getText(
            self,
            "Editar serviço",
            "IP, domínio ou URL:",
            text=item_endereco.text()
        )

        if not ok:
            return

        escolha_atual = (
            1
            if item_tipo.text() == "HTTP"
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

        self.tabela_servicos.setItem(
            linha,
            0,
            QTableWidgetItem(
                nome.strip()
                or "Serviço"
            )
        )

        self.tabela_servicos.setItem(
            linha,
            1,
            QTableWidgetItem(
                tipo
            )
        )

        self.tabela_servicos.setItem(
            linha,
            2,
            QTableWidgetItem(
                endereco.strip()
            )
        )

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

            if (
                item_porta is None
                or item_servico is None
            ):
                continue

            portas[
                item_porta.text()
            ] = item_servico.text()

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

            "alerta_sonoro_geral_ativado":
                self.checkbox_alerta_sonoro_geral.isChecked(),

            "alerta_sonoro_servico_indisponivel_ativado":
                self.checkbox_alerta_servico_indisponivel.isChecked(),

            "alerta_sonoro_modo":
                alerta_modo,

            "alerta_sonoro_arquivo":
                alerta_arquivo,

            "servicos_padrao_inicializados":
                True,

            "servicos_down_detector":
                self.obter_servicos_tabela(),

            "portas":
                portas
        }

        self.accept()

    def obter_configuracoes(
        self
    ):
        return self.configuracoes
