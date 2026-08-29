from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout
)

from services.incidents import (
    listar_incidentes,
    obter_resumo_hoje
)


class IncidentsWindow(QDialog):
    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.setWindowTitle(
            "Registro de Incidentes"
        )

        self.resize(
            1100,
            680
        )

        self.incidentes = []

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            16,
            16,
            16,
            16
        )

        layout.setSpacing(
            12
        )

        # =================================================
        # CABEÇALHO
        # =================================================

        titulo = QLabel(
            "Registro de Incidentes"
        )

        titulo.setObjectName(
            "tituloJanela"
        )

        layout.addWidget(
            titulo
        )

        subtitulo = QLabel(
            "Falhas críticas e eventos de instabilidade "
            "registrados automaticamente pelo Monitor de Serviços."
        )

        subtitulo.setWordWrap(
            True
        )

        layout.addWidget(
            subtitulo
        )

        # =================================================
        # RESUMO
        # =================================================

        resumo = QHBoxLayout()

        (
            self.card_total,
            self.valor_total
        ) = self.criar_card(
            "Incidentes hoje",
            "0"
        )

        (
            self.card_criticos,
            self.valor_criticos
        ) = self.criar_card(
            "Críticos hoje",
            "0"
        )

        (
            self.card_tempo,
            self.valor_tempo
        ) = self.criar_card(
            "Tempo afetado hoje",
            "0s"
        )

        (
            self.card_abertos,
            self.valor_abertos
        ) = self.criar_card(
            "Em andamento",
            "0"
        )

        resumo.addWidget(
            self.card_total,
            1
        )

        resumo.addWidget(
            self.card_criticos,
            1
        )

        resumo.addWidget(
            self.card_tempo,
            1
        )

        resumo.addWidget(
            self.card_abertos,
            1
        )

        layout.addLayout(
            resumo
        )

        # =================================================
        # FILTROS
        # =================================================

        filtros = QHBoxLayout()

        filtros.addWidget(
            QLabel(
                "Período:"
            )
        )

        self.combo_periodo = QComboBox()

        self.combo_periodo.addItem(
            "Hoje",
            "hoje"
        )

        self.combo_periodo.addItem(
            "Últimas 24 horas",
            "24h"
        )

        self.combo_periodo.addItem(
            "Últimos 7 dias",
            "7d"
        )

        self.combo_periodo.addItem(
            "Últimos 30 dias",
            "30d"
        )

        self.combo_periodo.addItem(
            "Todos",
            "todos"
        )

        filtros.addWidget(
            self.combo_periodo
        )

        filtros.addSpacing(
            10
        )

        filtros.addWidget(
            QLabel(
                "Tipo:"
            )
        )

        self.combo_tipo = QComboBox()

        self.combo_tipo.addItem(
            "Todos",
            "todos"
        )

        self.combo_tipo.addItem(
            "Serviços",
            "SERVICO"
        )

        self.combo_tipo.addItem(
            "Rede local",
            "REDE_LOCAL"
        )

        filtros.addWidget(
            self.combo_tipo
        )

        filtros.addSpacing(
            10
        )

        filtros.addWidget(
            QLabel(
                "Origem:"
            )
        )

        self.combo_origem = QComboBox()

        filtros.addWidget(
            self.combo_origem,
            1
        )

        botao_atualizar = QPushButton(
            "Atualizar"
        )

        botao_atualizar.clicked.connect(
            self.atualizar
        )

        filtros.addWidget(
            botao_atualizar
        )

        layout.addLayout(
            filtros
        )

        # =================================================
        # TABELA
        # =================================================

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(
            6
        )

        self.tabela.setHorizontalHeaderLabels([
            "Início",
            "Origem",
            "Evento",
            "Duração",
            "Causa provável",
            "Status"
        ])

        self.tabela.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        self.tabela.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .SingleSelection
        )

        self.tabela.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        self.tabela.verticalHeader().setVisible(
            False
        )

        cabecalho = self.tabela.horizontalHeader()

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
            QHeaderView.ResizeMode.ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Stretch
        )

        cabecalho.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.tabela.doubleClicked.connect(
            self.abrir_detalhes_selecionado
        )

        layout.addWidget(
            self.tabela,
            1
        )

        # =================================================
        # RODAPÉ
        # =================================================

        rodape = QHBoxLayout()

        self.label_resultados = QLabel(
            "0 registros"
        )

        rodape.addWidget(
            self.label_resultados
        )

        rodape.addStretch()

        botao_detalhes = QPushButton(
            "Ver detalhes"
        )

        botao_detalhes.clicked.connect(
            self.abrir_detalhes_selecionado
        )

        botao_fechar = QPushButton(
            "Fechar"
        )

        botao_fechar.clicked.connect(
            self.close
        )

        rodape.addWidget(
            botao_detalhes
        )

        rodape.addWidget(
            botao_fechar
        )

        layout.addLayout(
            rodape
        )

        # =================================================
        # EVENTOS
        # =================================================

        self.combo_periodo.currentIndexChanged.connect(
            self.aplicar_filtros
        )

        self.combo_tipo.currentIndexChanged.connect(
            self.aplicar_filtros
        )

        self.combo_origem.currentIndexChanged.connect(
            self.aplicar_filtros
        )

        self.atualizar()

    def criar_card(
        self,
        titulo,
        valor
    ):
        card = QFrame()

        card.setObjectName(
            "painelConfiguracaoInfo"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            14,
            10,
            14,
            10
        )

        label_titulo = QLabel(
            titulo
        )

        label_valor = QLabel(
            valor
        )

        label_valor.setObjectName(
            "tituloConfiguracaoInfo"
        )

        layout.addWidget(
            label_titulo
        )

        layout.addWidget(
            label_valor
        )

        return (
            card,
            label_valor
        )

    def atualizar(
        self
    ):
        self.incidentes = listar_incidentes(
            limite=5000
        )

        self.atualizar_origens()
        self.atualizar_resumo()
        self.aplicar_filtros()

    def atualizar_origens(
        self
    ):
        origem_atual = (
            self.combo_origem.currentData()
        )

        origens = sorted({
            str(
                item.get(
                    "origem",
                    ""
                )
            )
            for item in self.incidentes
            if item.get(
                "origem"
            )
        })

        self.combo_origem.blockSignals(
            True
        )

        self.combo_origem.clear()

        self.combo_origem.addItem(
            "Todas",
            "todos"
        )

        for origem in origens:
            self.combo_origem.addItem(
                origem,
                origem
            )

        indice = self.combo_origem.findData(
            origem_atual
        )

        if indice >= 0:
            self.combo_origem.setCurrentIndex(
                indice
            )

        self.combo_origem.blockSignals(
            False
        )

    def atualizar_resumo(
        self
    ):
        resumo = obter_resumo_hoje()

        agora = datetime.now()

        inicio_dia = agora.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        total_segundos = 0
        abertos = 0

        for item in self.incidentes:
            inicio = self.converter_data(
                item.get(
                    "inicio"
                )
            )

            if inicio is None:
                continue

            if inicio < inicio_dia:
                continue

            if not item.get(
                "encerrado"
            ):
                abertos += 1

                total_segundos += max(
                    0,
                    int(
                        (
                            agora - inicio
                        ).total_seconds()
                    )
                )

            else:
                total_segundos += int(
                    item.get(
                        "duracao_segundos",
                        0
                    )
                    or 0
                )

        self.valor_total.setText(
            str(
                resumo.get(
                    "total",
                    0
                )
            )
        )

        self.valor_criticos.setText(
            str(
                resumo.get(
                    "criticos",
                    0
                )
            )
        )

        self.valor_tempo.setText(
            self.formatar_duracao(
                total_segundos
            )
        )

        self.valor_abertos.setText(
            str(
                abertos
            )
        )

    def aplicar_filtros(
        self
    ):
        periodo = (
            self.combo_periodo.currentData()
            or "hoje"
        )

        tipo = (
            self.combo_tipo.currentData()
            or "todos"
        )

        origem = (
            self.combo_origem.currentData()
            or "todos"
        )

        registros = []

        for item in self.incidentes:
            if not self.incidente_no_periodo(
                item,
                periodo
            ):
                continue

            if (
                tipo != "todos"
                and item.get(
                    "tipo"
                ) != tipo
            ):
                continue

            if (
                origem != "todos"
                and item.get(
                    "origem"
                ) != origem
            ):
                continue

            registros.append(
                item
            )

        self.preencher_tabela(
            registros
        )

    def incidente_no_periodo(
        self,
        item,
        periodo
    ):
        if periodo == "todos":
            return True

        inicio = self.converter_data(
            item.get(
                "inicio"
            )
        )

        if inicio is None:
            return False

        agora = datetime.now()

        if periodo == "hoje":
            return inicio.date() == agora.date()

        if periodo == "24h":
            return inicio >= (
                agora - timedelta(
                    hours=24
                )
            )

        if periodo == "7d":
            return inicio >= (
                agora - timedelta(
                    days=7
                )
            )

        if periodo == "30d":
            return inicio >= (
                agora - timedelta(
                    days=30
                )
            )

        return True

    def obter_cor_estado(
        self,
        texto
    ):
        texto = str(
            texto
            or ""
        ).upper()

        if any(
            termo in texto
            for termo in (
                "SEM RESPOSTA",
                "FALHA HTTP",
                "ERRO",
                "INDISPONIBILIDADE",
                "PERDA GENERALIZADA",
                "REDE LOCAL INSTÁVEL",
                "FALHA GRAVE"
            )
        ):
            return QColor(
                "#ff5c5c"
            )

        if any(
            termo in texto
            for termo in (
                "POSSÍVEL INSTABILIDADE",
                "OSCILAÇÃO",
                "INSTABILIDADE MISTA"
            )
        ):
            return QColor(
                "#f6c344"
            )

        if any(
            termo in texto
            for termo in (
                "LATÊNCIA ALTA",
                "LATÊNCIA GENERALIZADA"
            )
        ):
            return QColor(
                "#ff9f43"
            )

        if any(
            termo in texto
            for termo in (
                "NORMALIZADO",
                "ONLINE",
                "ESTÁVEL"
            )
        ):
            return QColor(
                "#39d98a"
            )

        return QColor(
            "#d7dee8"
        )

    def obter_cor_duracao(
        self,
        incidente
    ):
        if incidente.get(
            "encerrado"
        ):
            segundos = int(
                incidente.get(
                    "duracao_segundos",
                    0
                )
                or 0
            )

        else:
            inicio = self.converter_data(
                incidente.get(
                    "inicio"
                )
            )

            if inicio is None:
                segundos = 0

            else:
                segundos = max(
                    0,
                    int(
                        (
                            datetime.now()
                            - inicio
                        ).total_seconds()
                    )
                )

        if segundos >= 900:
            return QColor(
                "#ff5c5c"
            )

        if segundos >= 300:
            return QColor(
                "#ff9f43"
            )

        if segundos >= 60:
            return QColor(
                "#f6c344"
            )

        return QColor(
            "#d7dee8"
        )

    def preencher_tabela(
        self,
        registros
    ):
        self.tabela.setRowCount(
            0
        )

        for incidente in registros:
            linha = self.tabela.rowCount()

            self.tabela.insertRow(
                linha
            )

            inicio = self.converter_data(
                incidente.get(
                    "inicio"
                )
            )

            texto_inicio = (
                inicio.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
                if inicio is not None
                else "-"
            )

            item_inicio = QTableWidgetItem(
                texto_inicio
            )

            item_inicio.setData(
                Qt.ItemDataRole.UserRole,
                incidente
            )

            item_inicio.setForeground(
                QColor(
                    "#58a6ff"
                )
            )

            self.tabela.setItem(
                linha,
                0,
                item_inicio
            )

            item_origem = QTableWidgetItem(
                incidente.get(
                    "origem",
                    "-"
                )
            )

            self.tabela.setItem(
                linha,
                1,
                item_origem
            )

            evento = incidente.get(
                "status_inicial",
                "-"
            )

            item_evento = QTableWidgetItem(
                evento
            )

            item_evento.setForeground(
                self.obter_cor_estado(
                    evento
                )
            )

            self.tabela.setItem(
                linha,
                2,
                item_evento
            )

            item_duracao = QTableWidgetItem(
                self.obter_duracao_incidente(
                    incidente
                )
            )

            item_duracao.setForeground(
                self.obter_cor_duracao(
                    incidente
                )
            )

            self.tabela.setItem(
                linha,
                3,
                item_duracao
            )

            causa = (
                incidente.get(
                    "causa_provavel",
                    ""
                )
                or "-"
            )

            item_causa = QTableWidgetItem(
                causa
            )

            item_causa.setForeground(
                self.obter_cor_estado(
                    causa
                )
            )

            self.tabela.setItem(
                linha,
                4,
                item_causa
            )

            if incidente.get(
                "encerrado"
            ):
                status = "✓ NORMALIZADO"

            else:
                status = "● EM ANDAMENTO"

            item_status = QTableWidgetItem(
                status
            )

            item_status.setForeground(
                self.obter_cor_estado(
                    status
                )
            )

            self.tabela.setItem(
                linha,
                5,
                item_status
            )

        self.label_resultados.setText(
            (
                f"{len(registros)} registro"
                if len(registros) == 1
                else f"{len(registros)} registros"
            )
        )

    def abrir_detalhes_selecionado(
        self
    ):
        linha = self.tabela.currentRow()

        if linha < 0:
            QMessageBox.information(
                self,
                "Registro de Incidentes",
                "Selecione um incidente."
            )

            return

        item = self.tabela.item(
            linha,
            0
        )

        if item is None:
            return

        incidente = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            incidente,
            dict
        ):
            return

        inicio = self.converter_data(
            incidente.get(
                "inicio"
            )
        )

        fim = self.converter_data(
            incidente.get(
                "fim"
            )
        )

        texto_inicio = (
            inicio.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
            if inicio is not None
            else "-"
        )

        texto_fim = (
            fim.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
            if fim is not None
            else "Em andamento"
        )

        tipo = (
            "Serviço"
            if incidente.get(
                "tipo"
            ) == "SERVICO"
            else "Rede local"
        )

        detalhes = (
            f"Tipo: {tipo}\n"
            f"Origem: {incidente.get('origem', '-')}\n"
            f"Endereço: {incidente.get('endereco') or '-'}\n\n"
            f"Evento: {incidente.get('status_inicial', '-')}\n"
            f"Causa provável: "
            f"{incidente.get('causa_provavel') or '-'}\n\n"
            f"Início: {texto_inicio}\n"
            f"Fim: {texto_fim}\n"
            f"Duração: {self.obter_duracao_incidente(incidente)}\n\n"
            f"Máx. serviços afetados: "
            f"{incidente.get('max_servicos_afetados', 0)}\n"
            f"Máx. perda observada: "
            f"{self.formatar_numero(incidente.get('max_perda', 0))}\n"
            f"Máx. latência: "
            f"{self.formatar_numero(incidente.get('max_latencia', 0))} ms\n"
            f"Máx. oscilação: "
            f"{self.formatar_numero(incidente.get('max_oscilacao', 0))} ms\n\n"
            f"Detalhes:\n"
            f"{incidente.get('detalhes') or '-'}"
        )

        QMessageBox.information(
            self,
            "Detalhes do incidente",
            detalhes
        )

    def obter_duracao_incidente(
        self,
        incidente
    ):
        if incidente.get(
            "encerrado"
        ):
            segundos = int(
                incidente.get(
                    "duracao_segundos",
                    0
                )
                or 0
            )

            return self.formatar_duracao(
                segundos
            )

        inicio = self.converter_data(
            incidente.get(
                "inicio"
            )
        )

        if inicio is None:
            return "-"

        segundos = max(
            0,
            int(
                (
                    datetime.now()
                    - inicio
                ).total_seconds()
            )
        )

        return (
            self.formatar_duracao(
                segundos
            )
            + " +"
        )

    def converter_data(
        self,
        valor
    ):
        if not valor:
            return None

        try:
            return datetime.fromisoformat(
                valor
            )

        except (
            TypeError,
            ValueError
        ):
            return None

    def formatar_duracao(
        self,
        segundos
    ):
        segundos = max(
            0,
            int(
                segundos
            )
        )

        horas, restante = divmod(
            segundos,
            3600
        )

        minutos, segundos = divmod(
            restante,
            60
        )

        if horas:
            return (
                f"{horas}h "
                f"{minutos:02d}m "
                f"{segundos:02d}s"
            )

        if minutos:
            return (
                f"{minutos}m "
                f"{segundos:02d}s"
            )

        return f"{segundos}s"

    def formatar_numero(
        self,
        valor
    ):
        try:
            numero = float(
                valor
            )

        except (
            TypeError,
            ValueError
        ):
            numero = 0.0

        if numero.is_integer():
            return str(
                int(
                    numero
                )
            )

        return f"{numero:.1f}"
