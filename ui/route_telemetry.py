import math
import statistics
import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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


class RouteTelemetryWidget(QWidget):
    def __init__(
        self,
        max_amostras=1800,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.max_amostras = int(
            max(
                60,
                max_amostras
            )
        )

        self.historico_por_salto = {}
        self.info_por_salto = {}
        self.ultimo_ciclo = None

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
        # SELETOR
        # =================================================

        linha_seletor = QHBoxLayout()

        label_salto = QLabel(
            "Salto:"
        )

        label_salto.setObjectName(
            "textoSecundario"
        )

        self.combo_salto = QComboBox()

        self.combo_salto.setMinimumWidth(
            240
        )

        self.combo_salto.addItem(
            "Aguardando rota...",
            None
        )

        self.combo_salto.currentIndexChanged.connect(
            self.atualizar_grafico
        )

        linha_seletor.addWidget(
            label_salto
        )

        linha_seletor.addWidget(
            self.combo_salto
        )

        linha_seletor.addStretch()

        layout.addLayout(
            linha_seletor
        )

        # =================================================
        # CARDS DE RESUMO
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

        # =================================================
        # STATUS + LEGENDA
        # =================================================

        linha_status = QHBoxLayout()

        self.status = QLabel(
            "Aguardando amostras..."
        )

        self.status.setObjectName(
            "textoSecundario"
        )

        self.legenda = QLabel(
            "— Latência   ● Pico   × Perda"
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
            self.pontos_pico = None
            self.pontos_perda = None
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

        # Linha limpa, sem preenchimento.
        self.curva = self.grafico.plot(
            [],
            [],
            pen=pg.mkPen(
                "#58a6ff",
                width=2
            ),
            connect="finite"
        )

        self.pontos_pico = pg.ScatterPlotItem(
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
            self.pontos_pico
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

    def limpar(
        self
    ):
        self.historico_por_salto = {}
        self.info_por_salto = {}
        self.ultimo_ciclo = None

        self.combo_salto.blockSignals(
            True
        )

        self.combo_salto.clear()

        self.combo_salto.addItem(
            "Aguardando rota...",
            None
        )

        self.combo_salto.blockSignals(
            False
        )

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

        if self.pontos_pico is not None:
            self.pontos_pico.setData(
                [],
                []
            )

        if self.pontos_perda is not None:
            self.pontos_perda.setData(
                [],
                []
            )

    def atualizar_ciclo(
        self,
        resultados,
        ciclos,
        timestamp=None
    ):
        if timestamp is None:
            timestamp = time.time()

        try:
            ciclo_atual = int(
                ciclos
            )

        except (
            TypeError,
            ValueError
        ):
            ciclo_atual = 0

        if (
            self.ultimo_ciclo is not None
            and ciclo_atual == self.ultimo_ciclo
        ):
            self.atualizar_info_saltos(
                resultados
            )

            self.atualizar_seletor_saltos()
            self.atualizar_grafico()
            return

        self.ultimo_ciclo = ciclo_atual

        for resultado in resultados:
            try:
                salto = int(
                    resultado.get(
                        "salto"
                    )
                )

            except (
                TypeError,
                ValueError
            ):
                continue

            ip = str(
                resultado.get(
                    "ip",
                    "-"
                )
            )

            status = str(
                resultado.get(
                    "status",
                    ""
                )
            )

            latencia = resultado.get(
                "ultimo"
            )

            if latencia is not None:
                try:
                    latencia = float(
                        latencia
                    )

                except (
                    TypeError,
                    ValueError
                ):
                    latencia = None

            historico = self.historico_por_salto.setdefault(
                salto,
                []
            )

            historico.append({
                "timestamp": float(
                    timestamp
                ),
                "latencia": latencia,
                "status": status,
                "ip": ip
            })

            excesso = (
                len(
                    historico
                )
                - self.max_amostras
            )

            if excesso > 0:
                del historico[
                    :excesso
                ]

            self.info_por_salto[
                salto
            ] = {
                "ip": ip,
                "status": status
            }

        self.atualizar_seletor_saltos()
        self.atualizar_grafico()

    def atualizar_info_saltos(
        self,
        resultados
    ):
        for resultado in resultados:
            try:
                salto = int(
                    resultado.get(
                        "salto"
                    )
                )

            except (
                TypeError,
                ValueError
            ):
                continue

            self.info_por_salto[
                salto
            ] = {
                "ip": str(
                    resultado.get(
                        "ip",
                        "-"
                    )
                ),
                "status": str(
                    resultado.get(
                        "status",
                        ""
                    )
                )
            }

    def atualizar_seletor_saltos(
        self
    ):
        saltos = sorted(
            self.info_por_salto
        )

        if not saltos:
            return

        selecionado = self.combo_salto.currentData()

        self.combo_salto.blockSignals(
            True
        )

        self.combo_salto.clear()

        for salto in saltos:
            info = self.info_por_salto.get(
                salto,
                {}
            )

            ip = info.get(
                "ip",
                "-"
            )

            self.combo_salto.addItem(
                f"{salto} — {ip}",
                salto
            )

        indice = self.combo_salto.findData(
            selecionado
        )

        if indice < 0:
            indice = (
                self.combo_salto.count()
                - 1
            )

        if indice >= 0:
            self.combo_salto.setCurrentIndex(
                indice
            )

        self.combo_salto.blockSignals(
            False
        )

    def calcular_picos(
        self,
        historico
    ):
        """
        Marca somente picos realmente relevantes.

        Usamos uma janela local de até 20 amostras anteriores e
        comparamos a latência atual com a mediana dessa janela.

        Para ser considerado pico:
        - precisa estar pelo menos 10 ms acima da mediana; e
        - precisa ser pelo menos 50% maior que a mediana.

        Isso evita transformar cada resposta normal em ponto laranja.
        """
        picos = set()
        anteriores = []

        for indice, item in enumerate(
            historico
        ):
            latencia = item[
                "latencia"
            ]

            if latencia is None:
                continue

            janela = anteriores[
                -20:
            ]

            if len(
                janela
            ) >= 5:
                mediana = statistics.median(
                    janela
                )

                limite_absoluto = (
                    mediana
                    + 10.0
                )

                limite_relativo = (
                    mediana
                    * 1.5
                )

                limite = max(
                    limite_absoluto,
                    limite_relativo
                )

                if latencia >= limite:
                    picos.add(
                        indice
                    )

            anteriores.append(
                latencia
            )

        return picos

    def atualizar_grafico(
        self
    ):
        salto = self.combo_salto.currentData()

        if salto is None:
            return

        historico = self.historico_por_salto.get(
            salto,
            []
        )

        if not historico:
            self.status.setText(
                "Aguardando amostras deste salto..."
            )
            return

        latencias_validas = [
            item[
                "latencia"
            ]
            for item in historico
            if item[
                "latencia"
            ] is not None
        ]

        total = len(
            historico
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

        info = self.info_por_salto.get(
            salto,
            {}
        )

        ip = info.get(
            "ip",
            "-"
        )

        status_atual = info.get(
            "status",
            "-"
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
            f"Salto {salto} — {ip}   |   "
            f"Amostras: {total}   |   "
            f"Status: {status_atual}"
        )

        if (
            self.grafico is None
            or self.curva is None
            or self.pontos_pico is None
            or self.pontos_perda is None
        ):
            return

        xs = []
        ys = []
        xs_pico = []
        ys_pico = []
        xs_perda = []

        indices_pico = self.calcular_picos(
            historico
        )

        for indice, item in enumerate(
            historico
        ):
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

            if indice in indices_pico:
                xs_pico.append(
                    x
                )

                ys_pico.append(
                    latencia
                )

        self.curva.setData(
            xs,
            ys
        )

        self.pontos_pico.setData(
            xs_pico,
            ys_pico
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
                20.0
            )

            self.grafico.setYRange(
                0,
                teto
            )
