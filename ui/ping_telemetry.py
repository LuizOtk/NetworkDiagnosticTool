import math
import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget
)

try:
    import pyqtgraph as pg
except ImportError:
    pg = None


class PingTelemetryWidget(QWidget):
    def __init__(
        self,
        limite_latencia=100,
        max_amostras=1800,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.limite_latencia = float(
            limite_latencia
        )

        self.max_amostras = int(
            max(
                60,
                max_amostras
            )
        )

        self.amostras = []

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            8
        )

        # =================================================
        # RESUMO
        # =================================================

        linha_resumo = QHBoxLayout()

        (
            self.card_minimo,
            self.valor_minimo
        ) = self.criar_card(
            "Mínimo",
            "-"
        )

        (
            self.card_media,
            self.valor_media
        ) = self.criar_card(
            "Média",
            "-"
        )

        (
            self.card_maximo,
            self.valor_maximo
        ) = self.criar_card(
            "Máximo",
            "-"
        )

        (
            self.card_perda,
            self.valor_perda
        ) = self.criar_card(
            "Perda",
            "-"
        )

        linha_resumo.addWidget(
            self.card_minimo,
            1
        )

        linha_resumo.addWidget(
            self.card_media,
            1
        )

        linha_resumo.addWidget(
            self.card_maximo,
            1
        )

        linha_resumo.addWidget(
            self.card_perda,
            1
        )

        layout.addLayout(
            linha_resumo
        )

        linha_status = QHBoxLayout()

        self.status = QLabel(
            "Aguardando amostras..."
        )

        self.status.setObjectName(
            "textoSecundario"
        )

        self.legenda = QLabel(
            "— Latência   ● Acima do limite   × Perda"
        )

        self.legenda.setObjectName(
            "textoSecundario"
        )

        linha_status.addWidget(
            self.status
        )

        linha_status.addStretch()

        linha_status.addWidget(
            self.legenda
        )

        layout.addLayout(
            linha_status
        )

        # =================================================
        # GRÁFICO
        # =================================================

        if pg is None:
            aviso = QLabel(
                "A telemetria requer o pacote pyqtgraph.\n\n"
                "Instale no ambiente virtual com:\n"
                "pip install pyqtgraph"
            )

            aviso.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            aviso.setWordWrap(
                True
            )

            layout.addWidget(
                aviso,
                1
            )

            self.grafico = None
            self.curva = None
            self.pontos_latencia_alta = None
            self.pontos_perda = None
            self.linha_limite = None
            return

        eixo_tempo = pg.DateAxisItem(
            orientation="bottom"
        )

        self.grafico = pg.PlotWidget(
            axisItems={
                "bottom": eixo_tempo
            }
        )

        self.grafico.setBackground(
            None
        )

        self.grafico.showGrid(
            x=True,
            y=True,
            alpha=0.12
        )

        self.grafico.setLabel(
            "left",
            "Latência",
            units="ms"
        )

        self.grafico.setLabel(
            "bottom",
            "Horário"
        )

        self.grafico.setMouseEnabled(
            x=True,
            y=False
        )

        self.grafico.setMenuEnabled(
            False
        )

        # Linha simples: sem preenchimento de área.
        self.curva = self.grafico.plot(
            [],
            [],
            pen=pg.mkPen(
                "#58a6ff",
                width=2
            ),
            connect="finite"
        )

        self.pontos_latencia_alta = pg.ScatterPlotItem(
            [],
            [],
            symbol="o",
            size=7,
            pen=pg.mkPen(
                "#ff9f43",
                width=1
            ),
            brush=pg.mkBrush(
                "#ff9f43"
            )
        )

        self.grafico.addItem(
            self.pontos_latencia_alta
        )

        self.pontos_perda = pg.ScatterPlotItem(
            [],
            [],
            symbol="x",
            size=10,
            pen=pg.mkPen(
                "#ff5c5c",
                width=2
            )
        )

        self.grafico.addItem(
            self.pontos_perda
        )

        self.linha_limite = pg.InfiniteLine(
            pos=self.limite_latencia,
            angle=0,
            pen=pg.mkPen(
                "#ff9f43",
                width=1,
                style=Qt.PenStyle.DashLine
            )
        )

        self.grafico.addItem(
            self.linha_limite
        )

        layout.addWidget(
            self.grafico,
            1
        )

    def criar_card(
        self,
        titulo,
        valor
    ):
        card = QFrame()

        card.setObjectName(
            "painelConfiguracaoInfo"
        )

        card.setMaximumHeight(
            58
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            10,
            6,
            10,
            6
        )

        layout.setSpacing(
            2
        )

        label_titulo = QLabel(
            titulo
        )

        label_titulo.setObjectName(
            "textoSecundario"
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

    def definir_limite_latencia(
        self,
        limite
    ):
        try:
            self.limite_latencia = float(
                limite
            )

        except (
            TypeError,
            ValueError
        ):
            self.limite_latencia = 100.0

        if self.linha_limite is not None:
            self.linha_limite.setValue(
                self.limite_latencia
            )

        self.atualizar_grafico()

    def limpar(
        self
    ):
        self.amostras = []

        self.valor_minimo.setText(
            "-"
        )

        self.valor_media.setText(
            "-"
        )

        self.valor_maximo.setText(
            "-"
        )

        self.valor_perda.setText(
            "-"
        )

        self.status.setText(
            "Aguardando amostras..."
        )

        if self.curva is not None:
            self.curva.setData(
                [],
                []
            )

        if self.pontos_latencia_alta is not None:
            self.pontos_latencia_alta.setData(
                [],
                []
            )

        if self.pontos_perda is not None:
            self.pontos_perda.setData(
                [],
                []
            )

    def adicionar_amostra(
        self,
        latencia,
        timestamp=None
    ):
        if timestamp is None:
            timestamp = time.time()

        valor = None

        if latencia is not None:
            try:
                valor = float(
                    latencia
                )

            except (
                TypeError,
                ValueError
            ):
                valor = None

        self.amostras.append({
            "timestamp": float(
                timestamp
            ),
            "latencia": valor
        })

        excesso = (
            len(
                self.amostras
            )
            - self.max_amostras
        )

        if excesso > 0:
            del self.amostras[
                :excesso
            ]

        self.atualizar_grafico()

    def atualizar_grafico(
        self
    ):
        if not self.amostras:
            return

        latencias_validas = [
            item[
                "latencia"
            ]
            for item in self.amostras
            if item[
                "latencia"
            ] is not None
        ]

        total = len(
            self.amostras
        )

        perdas = (
            total
            - len(
                latencias_validas
            )
        )

        perda_percentual = (
            (
                perdas
                / total
            )
            * 100
            if total
            else 0.0
        )

        if latencias_validas:
            minimo = min(
                latencias_validas
            )

            maximo = max(
                latencias_validas
            )

            media = (
                sum(
                    latencias_validas
                )
                / len(
                    latencias_validas
                )
            )

            self.valor_minimo.setText(
                f"{minimo:.0f} ms"
            )

            self.valor_media.setText(
                f"{media:.1f} ms"
            )

            self.valor_maximo.setText(
                f"{maximo:.0f} ms"
            )

        else:
            self.valor_minimo.setText(
                "-"
            )

            self.valor_media.setText(
                "-"
            )

            self.valor_maximo.setText(
                "-"
            )

        self.valor_perda.setText(
            f"{perda_percentual:.1f}%"
        )

        self.status.setText(
            f"Amostras: {total}   |   "
            f"Limite de latência: "
            f"{self.limite_latencia:g} ms"
        )

        if (
            self.grafico is None
            or self.curva is None
            or self.pontos_latencia_alta is None
            or self.pontos_perda is None
        ):
            return

        xs = []
        ys = []
        xs_altas = []
        ys_altas = []
        xs_perda = []

        for item in self.amostras:
            x = item[
                "timestamp"
            ]

            latencia = item[
                "latencia"
            ]

            xs.append(
                x
            )

            if latencia is None:
                ys.append(
                    math.nan
                )

                xs_perda.append(
                    x
                )
                continue

            ys.append(
                latencia
            )

            if (
                latencia
                >= self.limite_latencia
            ):
                xs_altas.append(
                    x
                )

                ys_altas.append(
                    latencia
                )

        self.curva.setData(
            xs,
            ys
        )

        self.pontos_latencia_alta.setData(
            xs_altas,
            ys_altas
        )

        referencia_perda = 0.0

        if latencias_validas:
            referencia_perda = max(
                0.0,
                min(
                    latencias_validas
                )
                * 0.15
            )

        self.pontos_perda.setData(
            xs_perda,
            [
                referencia_perda
                for _ in xs_perda
            ]
        )

        if len(
            xs
        ) >= 2:
            self.grafico.setXRange(
                xs[
                    0
                ],
                xs[
                    -1
                ]
            )

        if latencias_validas:
            teto = max(
                max(
                    latencias_validas
                )
                * 1.15,
                self.limite_latencia
                * 1.15,
                20.0
            )

            self.grafico.setYRange(
                0,
                teto
            )
