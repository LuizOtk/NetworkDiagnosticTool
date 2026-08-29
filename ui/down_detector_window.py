from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout
)


class DownDetectorWindow(QDialog):
    reconhecer_servico = Signal(str)

    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.setWindowTitle(
            "Monitor de Serviços"
        )

        self.resize(
            1150,
            520
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            14,
            14,
            14,
            12
        )

        layout.setSpacing(
            8
        )

        titulo = QLabel(
            "Monitor de Serviços"
        )

        titulo.setObjectName(
            "tituloDownDetector"
        )

        layout.addWidget(
            titulo
        )

        self.resumo = QLabel(
            "Serviços: 0 | Verificados: 0 | Aguardando primeiro ciclo..."
        )

        self.resumo.setObjectName(
            "resumoDownDetector"
        )

        layout.addWidget(
            self.resumo
        )

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(
            10
        )

        self.tabela.setHorizontalHeaderLabels([
            "Serviço",
            "Tipo",
            "Endereço",
            "Latência",
            "HTTP",
            "Variação",
            "Perdas",
            "Status",
            "Verificação",
            "Ação"
        ])

        self.tabela.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        self.tabela.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        self.tabela.verticalHeader().setVisible(
            False
        )

        self.tabela.verticalHeader().setDefaultSectionSize(
            40
        )

        cabecalho = (
            self.tabela
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
            .ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            2,
            QHeaderView
            .ResizeMode
            .Stretch
        )

        for coluna in range(
            3,
            9
        ):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents
            )

        cabecalho.setSectionResizeMode(
            9,
            QHeaderView
            .ResizeMode
            .Fixed
        )

        self.tabela.setColumnWidth(
            9,
            130
        )

        layout.addWidget(
            self.tabela
        )

        self.info = QLabel(
            "Prioridade: Falha crítica > Possível instabilidade > "
            "Latência alta > Online. "
            "Reconhecer remove o aviso da tela principal até o "
            "serviço voltar ao estado ONLINE."
        )

        self.info.setWordWrap(
            True
        )

        self.info.setObjectName(
            "textoSecundario"
        )

        layout.addWidget(
            self.info
        )

    def atualizar_progresso(
        self,
        verificados,
        total
    ):
        if total <= 0:
            self.resumo.setText(
                "Serviços: 0 | Verificados: 0 | Nenhum serviço cadastrado"
            )
            return

        if verificados < total:
            self.resumo.setText(
                f"Serviços: {total} | "
                f"Verificados: {verificados} | "
                "Atualizando..."
            )
            return

        self.resumo.setText(
            f"Serviços: {total} | "
            f"Verificados: {verificados} | "
            "Finalizando ciclo..."
        )

    def atualizar_resumo(
        self,
        total,
        verificados,
        alertas,
        criticos
    ):
        self.resumo.setText(
            f"Serviços: {total} | "
            f"Verificados: {verificados} | "
            f"Alertas: {alertas} | "
            f"Críticos: {criticos}"
        )

    def atualizar_servicos(
        self,
        resultados,
        reconhecidos
    ):
        # A prioridade principal é sempre a gravidade.
        # O reconhecimento só desempata serviços do mesmo nível.
        prioridades = {
            "SEM RESPOSTA": 0,
            "FALHA HTTP": 0,
            "ERRO": 0,
            "POSSÍVEL INSTABILIDADE": 1,
            "LATÊNCIA ALTA": 2,
            "ONLINE": 3,
            "AGUARDANDO": 4
        }

        status_com_alerta = {
            "SEM RESPOSTA",
            "FALHA HTTP",
            "ERRO",
            "POSSÍVEL INSTABILIDADE",
            "LATÊNCIA ALTA"
        }

        def ordenar(
            resultado
        ):
            status = resultado.get(
                "status",
                "AGUARDANDO"
            )

            chave = resultado.get(
                "chave",
                ""
            )

            prioridade = prioridades.get(
                status,
                99
            )

            reconhecido = (
                chave in reconhecidos
            )

            # Dentro da mesma gravidade:
            # não reconhecidos aparecem primeiro.
            prioridade_reconhecimento = (
                1
                if reconhecido
                else 0
            )

            return (
                prioridade,
                prioridade_reconhecimento,
                resultado.get(
                    "nome",
                    ""
                ).casefold()
            )

        resultados_ordenados = sorted(
            resultados,
            key=ordenar
        )

        # Remove inclusive os widgets antigos
        # antes de reconstruir a tabela.
        self.tabela.setRowCount(
            0
        )

        self.tabela.setRowCount(
            len(resultados_ordenados)
        )

        for linha, resultado in enumerate(
            resultados_ordenados
        ):
            chave = resultado.get(
                "chave",
                ""
            )

            status = resultado.get(
                "status",
                "AGUARDANDO"
            )

            latencia = resultado.get(
                "latencia"
            )

            if latencia is None:
                latencia_texto = "-"

            else:
                latencia_texto = (
                    f"{latencia} ms"
                )

            codigo_http = resultado.get(
                "codigo_http"
            )

            if codigo_http is None:
                http_texto = "-"

            else:
                http_texto = str(
                    codigo_http
                )

            valores = [
                resultado.get(
                    "nome",
                    "-"
                ),
                resultado.get(
                    "tipo",
                    "-"
                ),
                resultado.get(
                    "endereco",
                    "-"
                ),
                latencia_texto,
                http_texto,
                (
                    f"{resultado.get('variacao', 0)} ms"
                ),
                resultado.get(
                    "perdas_recentes",
                    0
                ),
                status,
                resultado.get(
                    "ultima_verificacao",
                    "-"
                )
            ]

            for coluna, valor in enumerate(
                valores
            ):
                item = QTableWidgetItem(
                    str(valor)
                )

                if coluna == 7:
                    self.aplicar_cor_status(
                        item,
                        status
                    )

                self.tabela.setItem(
                    linha,
                    coluna,
                    item
                )

            problema = (
                status
                in status_com_alerta
            )

            reconhecido = (
                chave in reconhecidos
            )

            if (
                problema
                and not reconhecido
            ):
                botao = QPushButton(
                    "Reconhecer"
                )

                botao.setObjectName(
                    "botaoReconhecer"
                )

                botao.clicked.connect(
                    lambda
                    checked=False,
                    chave_servico=chave:
                    self.reconhecer_servico.emit(
                        chave_servico
                    )
                )

                self.tabela.setCellWidget(
                    linha,
                    9,
                    botao
                )

            elif (
                problema
                and reconhecido
            ):
                item = QTableWidgetItem(
                    "Reconhecido"
                )

                item.setForeground(
                    QColor(
                        "#8294a5"
                    )
                )

                self.tabela.setItem(
                    linha,
                    9,
                    item
                )

            else:
                self.tabela.setItem(
                    linha,
                    9,
                    QTableWidgetItem(
                        "-"
                    )
                )

    def aplicar_cor_status(
        self,
        item,
        status
    ):
        if status == "ONLINE":
            cor = "#35d07f"

        elif status == (
            "POSSÍVEL INSTABILIDADE"
        ):
            cor = "#ffcc66"

        elif status == (
            "LATÊNCIA ALTA"
        ):
            cor = "#ff9f43"

        elif status in {
            "SEM RESPOSTA",
            "FALHA HTTP",
            "ERRO"
        }:
            cor = "#ff5c5c"

        else:
            cor = "#8294a5"

        item.setForeground(
            QColor(
                cor
            )
        )
