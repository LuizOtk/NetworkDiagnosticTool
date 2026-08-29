from datetime import datetime
from math import pi

from PySide6.QtCore import (
    QPointF,
    QRectF,
    QSize,
    QTimer,
    Qt,
    Signal
)

from PySide6.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF
)

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)


# =========================================================
# ÍCONES VETORIAIS DO NDT
# =========================================================

def _ponto(
    rect,
    x,
    y
):
    return QPointF(
        rect.left() + rect.width() * x,
        rect.top() + rect.height() * y
    )


def pintar_icone(
    painter,
    tipo,
    rect,
    cor
):
    painter.save()

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        True
    )

    caneta = QPen(
        QColor(
            cor
        )
    )

    caneta.setWidthF(
        max(
            1.8,
            rect.width() * 0.07
        )
    )

    caneta.setCapStyle(
        Qt.PenCapStyle.RoundCap
    )

    caneta.setJoinStyle(
        Qt.PenJoinStyle.RoundJoin
    )

    painter.setPen(
        caneta
    )

    painter.setBrush(
        Qt.BrushStyle.NoBrush
    )

    if tipo == "shield":
        poligono = QPolygonF([
            _ponto(rect, 0.50, 0.10),
            _ponto(rect, 0.82, 0.22),
            _ponto(rect, 0.78, 0.58),
            _ponto(rect, 0.64, 0.78),
            _ponto(rect, 0.50, 0.90),
            _ponto(rect, 0.36, 0.78),
            _ponto(rect, 0.22, 0.58),
            _ponto(rect, 0.18, 0.22)
        ])

        painter.drawPolygon(
            poligono
        )

        painter.drawLine(
            _ponto(rect, 0.34, 0.50),
            _ponto(rect, 0.46, 0.62)
        )

        painter.drawLine(
            _ponto(rect, 0.46, 0.62),
            _ponto(rect, 0.68, 0.37)
        )

    elif tipo in (
        "server",
        "services"
    ):
        for indice in range(
            3
        ):
            y = 0.16 + indice * 0.27

            caixa = QRectF(
                rect.left() + rect.width() * 0.16,
                rect.top() + rect.height() * y,
                rect.width() * 0.68,
                rect.height() * 0.18
            )

            painter.drawRoundedRect(
                caixa,
                rect.width() * 0.05,
                rect.width() * 0.05
            )

            centro_y = (
                caixa.top()
                + caixa.height() / 2
            )

            painter.drawPoint(
                QPointF(
                    caixa.left()
                    + caixa.width() * 0.12,
                    centro_y
                )
            )

            painter.drawLine(
                QPointF(
                    caixa.right()
                    - caixa.width() * 0.26,
                    centro_y
                ),
                QPointF(
                    caixa.right()
                    - caixa.width() * 0.12,
                    centro_y
                )
            )

    elif tipo == "warning":
        triangulo = QPolygonF([
            _ponto(rect, 0.50, 0.10),
            _ponto(rect, 0.90, 0.84),
            _ponto(rect, 0.10, 0.84)
        ])

        painter.drawPolygon(
            triangulo
        )

        painter.drawLine(
            _ponto(rect, 0.50, 0.34),
            _ponto(rect, 0.50, 0.58)
        )

        painter.drawPoint(
            _ponto(rect, 0.50, 0.71)
        )

    elif tipo == "bell":
        caminho = QPainterPath()

        caminho.moveTo(
            _ponto(rect, 0.28, 0.67)
        )

        caminho.cubicTo(
            _ponto(rect, 0.30, 0.56),
            _ponto(rect, 0.33, 0.43),
            _ponto(rect, 0.34, 0.34)
        )

        caminho.cubicTo(
            _ponto(rect, 0.36, 0.20),
            _ponto(rect, 0.44, 0.15),
            _ponto(rect, 0.50, 0.15)
        )

        caminho.cubicTo(
            _ponto(rect, 0.56, 0.15),
            _ponto(rect, 0.64, 0.20),
            _ponto(rect, 0.66, 0.34)
        )

        caminho.cubicTo(
            _ponto(rect, 0.67, 0.43),
            _ponto(rect, 0.70, 0.56),
            _ponto(rect, 0.72, 0.67)
        )

        painter.drawPath(
            caminho
        )

        painter.drawLine(
            _ponto(rect, 0.23, 0.69),
            _ponto(rect, 0.77, 0.69)
        )

        painter.drawArc(
            QRectF(
                rect.left() + rect.width() * 0.40,
                rect.top() + rect.height() * 0.64,
                rect.width() * 0.20,
                rect.height() * 0.18
            ),
            190 * 16,
            160 * 16
        )

    elif tipo in (
        "pulse",
        "diagnostic"
    ):
        pontos = QPolygonF([
            _ponto(rect, 0.06, 0.55),
            _ponto(rect, 0.24, 0.55),
            _ponto(rect, 0.33, 0.32),
            _ponto(rect, 0.43, 0.78),
            _ponto(rect, 0.55, 0.18),
            _ponto(rect, 0.65, 0.55),
            _ponto(rect, 0.94, 0.55)
        ])

        painter.drawPolyline(
            pontos
        )

    elif tipo == "route":
        pontos = [
            _ponto(rect, 0.22, 0.72),
            _ponto(rect, 0.50, 0.28),
            _ponto(rect, 0.80, 0.66)
        ]

        painter.drawLine(
            pontos[0],
            pontos[1]
        )

        painter.drawLine(
            pontos[1],
            pontos[2]
        )

        raio = rect.width() * 0.08

        for ponto in pontos:
            painter.drawEllipse(
                ponto,
                raio,
                raio
            )

    elif tipo == "plus":
        painter.drawLine(
            _ponto(rect, 0.50, 0.18),
            _ponto(rect, 0.50, 0.82)
        )

        painter.drawLine(
            _ponto(rect, 0.18, 0.50),
            _ponto(rect, 0.82, 0.50)
        )

    elif tipo == "globe":
        painter.drawEllipse(
            QRectF(
                rect.left() + rect.width() * 0.13,
                rect.top() + rect.height() * 0.13,
                rect.width() * 0.74,
                rect.height() * 0.74
            )
        )

        painter.drawArc(
            QRectF(
                rect.left() + rect.width() * 0.30,
                rect.top() + rect.height() * 0.13,
                rect.width() * 0.40,
                rect.height() * 0.74
            ),
            90 * 16,
            180 * 16
        )

        painter.drawArc(
            QRectF(
                rect.left() + rect.width() * 0.30,
                rect.top() + rect.height() * 0.13,
                rect.width() * 0.40,
                rect.height() * 0.74
            ),
            270 * 16,
            180 * 16
        )

        painter.drawLine(
            _ponto(rect, 0.16, 0.50),
            _ponto(rect, 0.84, 0.50)
        )

    elif tipo == "clock":
        painter.drawEllipse(
            QRectF(
                rect.left() + rect.width() * 0.14,
                rect.top() + rect.height() * 0.14,
                rect.width() * 0.72,
                rect.height() * 0.72
            )
        )

        painter.drawLine(
            _ponto(rect, 0.50, 0.50),
            _ponto(rect, 0.50, 0.28)
        )

        painter.drawLine(
            _ponto(rect, 0.50, 0.50),
            _ponto(rect, 0.68, 0.60)
        )

    elif tipo == "home":
        telhado = QPolygonF([
            _ponto(rect, 0.14, 0.47),
            _ponto(rect, 0.50, 0.15),
            _ponto(rect, 0.86, 0.47)
        ])

        painter.drawPolyline(
            telhado
        )

        painter.drawRect(
            QRectF(
                rect.left() + rect.width() * 0.25,
                rect.top() + rect.height() * 0.43,
                rect.width() * 0.50,
                rect.height() * 0.42
            )
        )

        painter.drawLine(
            _ponto(rect, 0.46, 0.85),
            _ponto(rect, 0.46, 0.62)
        )

        painter.drawLine(
            _ponto(rect, 0.46, 0.62),
            _ponto(rect, 0.58, 0.62)
        )

        painter.drawLine(
            _ponto(rect, 0.58, 0.62),
            _ponto(rect, 0.58, 0.85)
        )

    elif tipo == "chart":
        painter.drawLine(
            _ponto(rect, 0.15, 0.80),
            _ponto(rect, 0.15, 0.20)
        )

        painter.drawLine(
            _ponto(rect, 0.15, 0.80),
            _ponto(rect, 0.88, 0.80)
        )

        painter.drawPolyline(
            QPolygonF([
                _ponto(rect, 0.22, 0.67),
                _ponto(rect, 0.38, 0.50),
                _ponto(rect, 0.52, 0.58),
                _ponto(rect, 0.68, 0.31),
                _ponto(rect, 0.84, 0.40)
            ])
        )

    elif tipo == "document":
        painter.drawRoundedRect(
            QRectF(
                rect.left() + rect.width() * 0.22,
                rect.top() + rect.height() * 0.12,
                rect.width() * 0.56,
                rect.height() * 0.76
            ),
            rect.width() * 0.05,
            rect.width() * 0.05
        )

        for y in (
            0.38,
            0.52,
            0.66
        ):
            painter.drawLine(
                _ponto(rect, 0.34, y),
                _ponto(rect, 0.66, y)
            )

    elif tipo == "settings":
        centro = _ponto(
            rect,
            0.50,
            0.50
        )

        raio_externo = rect.width() * 0.28
        raio_interno = rect.width() * 0.10

        painter.drawEllipse(
            centro,
            raio_externo,
            raio_externo
        )

        painter.drawEllipse(
            centro,
            raio_interno,
            raio_interno
        )

        for angulo in range(
            0,
            360,
            45
        ):
            rad = (
                angulo
                * pi
                / 180.0
            )

            x1 = (
                centro.x()
                + raio_externo * 1.05
                * __import__("math").cos(rad)
            )

            y1 = (
                centro.y()
                + raio_externo * 1.05
                * __import__("math").sin(rad)
            )

            x2 = (
                centro.x()
                + raio_externo * 1.35
                * __import__("math").cos(rad)
            )

            y2 = (
                centro.y()
                + raio_externo * 1.35
                * __import__("math").sin(rad)
            )

            painter.drawLine(
                QPointF(
                    x1,
                    y1
                ),
                QPointF(
                    x2,
                    y2
                )
            )

    else:
        painter.drawEllipse(
            QRectF(
                rect.left() + rect.width() * 0.20,
                rect.top() + rect.height() * 0.20,
                rect.width() * 0.60,
                rect.height() * 0.60
            )
        )

    painter.restore()


def criar_icone(
    tipo,
    cor="#8fd3ff",
    tamanho=20,
    com_fundo=False
):
    pixmap = QPixmap(
        tamanho,
        tamanho
    )

    pixmap.fill(
        Qt.GlobalColor.transparent
    )

    painter = QPainter(
        pixmap
    )

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        True
    )

    margem = max(
        2,
        int(
            tamanho * 0.12
        )
    )

    rect = QRectF(
        margem,
        margem,
        tamanho - margem * 2,
        tamanho - margem * 2
    )

    if com_fundo:
        fundo = QColor(
            cor
        )

        fundo.setAlpha(
            42
        )

        painter.setPen(
            QPen(
                QColor(
                    cor
                ),
                1
            )
        )

        painter.setBrush(
            fundo
        )

        painter.drawEllipse(
            QRectF(
                1,
                1,
                tamanho - 2,
                tamanho - 2
            )
        )

        margem = max(
            5,
            int(
                tamanho * 0.24
            )
        )

        rect = QRectF(
            margem,
            margem,
            tamanho - margem * 2,
            tamanho - margem * 2
        )

    pintar_icone(
        painter,
        tipo,
        rect,
        cor
    )

    painter.end()

    return QIcon(
        pixmap
    )


class IconBadge(QWidget):
    def __init__(
        self,
        tipo,
        cor,
        tamanho=58,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.tipo = tipo
        self.cor = QColor(
            cor
        )

        self.setFixedSize(
            tamanho,
            tamanho
        )

        self.efeito = QGraphicsDropShadowEffect(
            self
        )

        self.efeito.setBlurRadius(
            22
        )

        self.efeito.setOffset(
            0,
            0
        )

        self._atualizar_sombra()

        self.setGraphicsEffect(
            self.efeito
        )

    def _atualizar_sombra(
        self
    ):
        cor = QColor(
            self.cor
        )

        cor.setAlpha(
            105
        )

        self.efeito.setColor(
            cor
        )

    def definir_cor(
        self,
        cor
    ):
        self.cor = QColor(
            cor
        )

        self._atualizar_sombra()

        self.update()

    def paintEvent(
        self,
        evento
    ):
        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True
        )

        rect = QRectF(
            3,
            3,
            self.width() - 6,
            self.height() - 6
        )

        fundo = QColor(
            self.cor
        )

        fundo.setAlpha(
            36
        )

        borda = QColor(
            self.cor
        )

        borda.setAlpha(
            180
        )

        painter.setPen(
            QPen(
                borda,
                1.2
            )
        )

        painter.setBrush(
            fundo
        )

        painter.drawEllipse(
            rect
        )

        margem = self.width() * 0.24

        area_icone = QRectF(
            margem,
            margem,
            self.width() - margem * 2,
            self.height() - margem * 2
        )

        pintar_icone(
            painter,
            self.tipo,
            area_icone,
            self.cor
        )

        painter.end()

        super().paintEvent(
            evento
        )


class MetricCard(QFrame):
    CORES_ESTADO = {
        "normal": "#56d364",
        "alerta": "#f0a928",
        "critico": "#ff5c5c",
        "neutro": "#6f8395"
    }

    def __init__(
        self,
        titulo,
        valor="-",
        subtitulo="",
        icone="server",
        cor="#2f81f7",
        cor_dinamica=False,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.cor_base = cor
        self.cor_dinamica = cor_dinamica

        self.setObjectName(
            "dashboardMetricCard"
        )

        self.setProperty(
            "estado",
            "neutro"
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            14,
            12,
            14,
            12
        )

        layout.setSpacing(
            13
        )

        self.badge = IconBadge(
            icone,
            cor,
            60
        )

        bloco_texto = QVBoxLayout()

        bloco_texto.setSpacing(
            2
        )

        self.label_titulo = QLabel(
            titulo
        )

        self.label_titulo.setObjectName(
            "dashboardCardTitle"
        )

        self.label_valor = QLabel(
            valor
        )

        self.label_valor.setObjectName(
            "dashboardCardValue"
        )

        self.label_subtitulo = QLabel(
            subtitulo
        )

        self.label_subtitulo.setObjectName(
            "dashboardCardSub"
        )

        self.label_subtitulo.setWordWrap(
            True
        )

        bloco_texto.addStretch()

        bloco_texto.addWidget(
            self.label_titulo
        )

        bloco_texto.addWidget(
            self.label_valor
        )

        bloco_texto.addWidget(
            self.label_subtitulo
        )

        bloco_texto.addStretch()

        layout.addWidget(
            self.badge
        )

        layout.addLayout(
            bloco_texto,
            1
        )

    def atualizar(
        self,
        valor,
        subtitulo="",
        estado="neutro"
    ):
        self.label_valor.setText(
            str(
                valor
            )
        )

        self.label_subtitulo.setText(
            str(
                subtitulo
            )
        )

        self.setProperty(
            "estado",
            estado
        )

        if self.cor_dinamica:
            self.badge.definir_cor(
                self.CORES_ESTADO.get(
                    estado,
                    self.cor_base
                )
            )

        estilo = self.style()

        estilo.unpolish(
            self
        )

        estilo.polish(
            self
        )


class ServiceRow(QFrame):
    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.setObjectName(
            "dashboardServiceRow"
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            9,
            4,
            10,
            4
        )

        layout.setSpacing(
            10
        )

        self.badge = IconBadge(
            "globe",
            "#2f81f7",
            30
        )

        self.label_nome = QLabel(
            "-"
        )

        self.label_nome.setObjectName(
            "dashboardServiceName"
        )

        self.status_dot = QLabel(
            "●"
        )

        self.status_dot.setObjectName(
            "dashboardServiceDot"
        )

        self.label_resultado = QLabel(
            "-"
        )

        self.label_resultado.setObjectName(
            "dashboardServiceResult"
        )

        layout.addWidget(
            self.badge
        )

        layout.addWidget(
            self.label_nome,
            1
        )

        layout.addWidget(
            self.status_dot
        )

        layout.addWidget(
            self.label_resultado
        )

    def atualizar(
        self,
        nome,
        resultado,
        estado="neutro",
        cor="#2f81f7",
        icone="globe"
    ):
        self.label_nome.setText(
            str(
                nome
            )
        )

        self.label_resultado.setText(
            str(
                resultado
            )
        )

        self.setProperty(
            "estado",
            estado
        )

        self.status_dot.setProperty(
            "estado",
            estado
        )

        self.label_resultado.setProperty(
            "estado",
            estado
        )

        self.badge.tipo = icone

        self.badge.definir_cor(
            cor
        )

        for widget in (
            self,
            self.status_dot,
            self.label_resultado
        ):
            estilo = widget.style()

            estilo.unpolish(
                widget
            )

            estilo.polish(
                widget
            )


class AlertRow(QFrame):
    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.setObjectName(
            "dashboardAlertRow"
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            10,
            5,
            10,
            5
        )

        layout.setSpacing(
            10
        )

        self.icone = QLabel()

        self.icone.setFixedSize(
            24,
            24
        )

        self.label = QLabel(
            "-"
        )

        self.label.setObjectName(
            "dashboardAlertText"
        )

        self.label.setWordWrap(
            True
        )

        layout.addWidget(
            self.icone
        )

        layout.addWidget(
            self.label,
            1
        )

    def atualizar(
        self,
        texto,
        estado="alerta"
    ):
        cor = (
            "#ff5c5c"
            if estado == "critico"
            else "#f0a928"
        )

        self.icone.setPixmap(
            criar_icone(
                "warning",
                cor,
                22
            ).pixmap(
                22,
                22
            )
        )

        self.label.setText(
            str(
                texto
            )
        )

        self.setProperty(
            "estado",
            estado
        )

        estilo = self.style()

        estilo.unpolish(
            self
        )

        estilo.polish(
            self
        )


class ActivityRow(QFrame):
    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.setObjectName(
            "dashboardActivityRow"
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            10,
            6,
            10,
            6
        )

        layout.setSpacing(
            10
        )

        self.timeline = QLabel(
            "●"
        )

        self.timeline.setObjectName(
            "dashboardTimelineDot"
        )

        self.horario = QLabel(
            "-"
        )

        self.horario.setObjectName(
            "dashboardActivityTime"
        )

        self.horario.setFixedWidth(
            66
        )

        self.origem = QLabel(
            "-"
        )

        self.origem.setObjectName(
            "dashboardActivityOrigin"
        )

        self.origem.setMinimumWidth(
            125
        )

        self.evento = QLabel(
            "-"
        )

        self.evento.setObjectName(
            "dashboardActivityEvent"
        )

        self.status = QLabel(
            "NORMALIZADO"
        )

        self.status.setObjectName(
            "dashboardActivityStatus"
        )

        layout.addWidget(
            self.timeline
        )

        layout.addWidget(
            self.horario
        )

        layout.addWidget(
            self.origem
        )

        layout.addWidget(
            self.evento,
            1
        )

        layout.addWidget(
            self.status
        )

    def atualizar(
        self,
        horario,
        origem,
        evento,
        status="NORMALIZADO"
    ):
        self.horario.setText(
            str(
                horario
            )
        )

        self.origem.setText(
            str(
                origem
            )
        )

        self.evento.setText(
            str(
                evento
            )
        )

        self.status.setText(
            str(
                status
            )
        )

        estado = (
            "critico"
            if status == "EM ANDAMENTO"
            else "normal"
        )

        self.status.setProperty(
            "estado",
            estado
        )

        estilo = self.status.style()

        estilo.unpolish(
            self.status
        )

        estilo.polish(
            self.status
        )


class DashboardPage(QWidget):
    solicitar_diagnostico = Signal()
    solicitar_ping = Signal()
    solicitar_rota = Signal()
    solicitar_servicos = Signal()
    solicitar_incidentes = Signal()

    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

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
            11
        )

        # =================================================
        # CABEÇALHO
        # =================================================

        linha_cabecalho = QHBoxLayout()

        icone_globo = QLabel()

        icone_globo.setPixmap(
            criar_icone(
                "globe",
                "#8fbfff",
                30
            ).pixmap(
                30,
                30
            )
        )

        titulo = QLabel(
            "VISÃO GERAL DA REDE"
        )

        titulo.setObjectName(
            "pageTitle"
        )

        linha_cabecalho.addWidget(
            icone_globo
        )

        linha_cabecalho.addWidget(
            titulo
        )

        linha_cabecalho.addStretch()

        icone_relogio = QLabel()

        icone_relogio.setPixmap(
            criar_icone(
                "clock",
                "#91a2b3",
                22
            ).pixmap(
                22,
                22
            )
        )

        self.label_data_hora = QLabel()

        self.label_data_hora.setObjectName(
            "dashboardDateTime"
        )

        linha_cabecalho.addWidget(
            icone_relogio
        )

        linha_cabecalho.addWidget(
            self.label_data_hora
        )

        layout.addLayout(
            linha_cabecalho
        )

        self.timer_relogio = QTimer(
            self
        )

        self.timer_relogio.timeout.connect(
            self.atualizar_relogio
        )

        self.timer_relogio.start(
            1000
        )

        self.atualizar_relogio()

        # =================================================
        # CARDS
        # =================================================

        cards = QGridLayout()

        cards.setHorizontalSpacing(
            10
        )

        self.card_saude = MetricCard(
            "Saúde da Rede",
            "AGUARDANDO",
            "Coletando informações",
            icone="shield",
            cor="#56d364",
            cor_dinamica=True
        )

        self.card_servicos = MetricCard(
            "Serviços",
            "-",
            "Monitor de Serviços",
            icone="server",
            cor="#2f81f7"
        )

        self.card_incidentes = MetricCard(
            "Incidentes Hoje",
            "0",
            "Nenhum registro",
            icone="warning",
            cor="#ff5c5c"
        )

        self.card_alertas = MetricCard(
            "Alertas",
            "0",
            "Nenhum alerta",
            icone="bell",
            cor="#f0a928"
        )

        cards.addWidget(
            self.card_saude,
            0,
            0
        )

        cards.addWidget(
            self.card_servicos,
            0,
            1
        )

        cards.addWidget(
            self.card_incidentes,
            0,
            2
        )

        cards.addWidget(
            self.card_alertas,
            0,
            3
        )

        for coluna in range(
            4
        ):
            cards.setColumnStretch(
                coluna,
                1
            )

        layout.addLayout(
            cards
        )

        # =================================================
        # MONITORAMENTO + ALERTAS
        # =================================================

        linha_centro = QHBoxLayout()

        linha_centro.setSpacing(
            11
        )

        painel_monitoramento = QFrame()

        painel_monitoramento.setObjectName(
            "dashboardSection"
        )

        layout_monitoramento = QVBoxLayout(
            painel_monitoramento
        )

        layout_monitoramento.setContentsMargins(
            14,
            11,
            14,
            11
        )

        layout_monitoramento.setSpacing(
            4
        )

        cabecalho_monitoramento = QHBoxLayout()

        icon_monitor = QLabel()

        icon_monitor.setPixmap(
            criar_icone(
                "pulse",
                "#58a6ff",
                23
            ).pixmap(
                23,
                23
            )
        )

        titulo_monitoramento = QLabel(
            "MONITORAMENTO ATUAL"
        )

        titulo_monitoramento.setObjectName(
            "dashboardSectionTitle"
        )

        cabecalho_monitoramento.addWidget(
            icon_monitor
        )

        cabecalho_monitoramento.addWidget(
            titulo_monitoramento
        )

        cabecalho_monitoramento.addStretch()

        layout_monitoramento.addLayout(
            cabecalho_monitoramento
        )

        layout_monitoramento.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.scroll_servicos = QScrollArea()

        self.scroll_servicos.setObjectName(
            "dashboardScrollArea"
        )

        self.scroll_servicos.setWidgetResizable(
            True
        )

        self.scroll_servicos.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.scroll_servicos.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_servicos.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.scroll_servicos.setMinimumHeight(
            150
        )

        self.conteudo_servicos = QWidget()

        self.conteudo_servicos.setObjectName(
            "dashboardScrollContent"
        )

        self.layout_lista_servicos = QVBoxLayout(
            self.conteudo_servicos
        )

        self.layout_lista_servicos.setContentsMargins(
            0,
            0,
            3,
            0
        )

        self.layout_lista_servicos.setSpacing(
            4
        )

        self.layout_lista_servicos.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.linhas_servicos = []

        self.label_sem_servicos = QLabel(
            "Aguardando o primeiro ciclo do Monitor de Serviços..."
        )

        self.label_sem_servicos.setObjectName(
            "dashboardEmptyState"
        )

        self.label_sem_servicos.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.layout_lista_servicos.addWidget(
            self.label_sem_servicos
        )

        self.scroll_servicos.setWidget(
            self.conteudo_servicos
        )

        layout_monitoramento.addWidget(
            self.scroll_servicos,
            1
        )

        painel_alertas = QFrame()

        painel_alertas.setObjectName(
            "dashboardSection"
        )

        layout_alertas = QVBoxLayout(
            painel_alertas
        )

        layout_alertas.setContentsMargins(
            14,
            11,
            14,
            11
        )

        layout_alertas.setSpacing(
            5
        )

        cabecalho_alertas = QHBoxLayout()

        icon_alerta = QLabel()

        icon_alerta.setPixmap(
            criar_icone(
                "bell",
                "#9fb6ca",
                22
            ).pixmap(
                22,
                22
            )
        )

        titulo_alertas = QLabel(
            "ALERTAS ATIVOS"
        )

        titulo_alertas.setObjectName(
            "dashboardSectionTitle"
        )

        cabecalho_alertas.addWidget(
            icon_alerta
        )

        cabecalho_alertas.addWidget(
            titulo_alertas
        )

        cabecalho_alertas.addStretch()

        layout_alertas.addLayout(
            cabecalho_alertas
        )

        layout_alertas.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.scroll_alertas = QScrollArea()

        self.scroll_alertas.setObjectName(
            "dashboardScrollArea"
        )

        self.scroll_alertas.setWidgetResizable(
            True
        )

        self.scroll_alertas.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.scroll_alertas.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_alertas.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.scroll_alertas.setMinimumHeight(
            126
        )

        self.conteudo_alertas = QWidget()

        self.conteudo_alertas.setObjectName(
            "dashboardScrollContent"
        )

        self.layout_lista_alertas = QVBoxLayout(
            self.conteudo_alertas
        )

        self.layout_lista_alertas.setContentsMargins(
            0,
            0,
            3,
            0
        )

        self.layout_lista_alertas.setSpacing(
            5
        )

        self.layout_lista_alertas.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.linhas_alertas = []

        self.label_sem_alertas = QLabel(
            "✓ Nenhum alerta ativo"
        )

        self.label_sem_alertas.setObjectName(
            "dashboardNoAlerts"
        )

        self.label_sem_alertas.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.layout_lista_alertas.addWidget(
            self.label_sem_alertas
        )

        self.scroll_alertas.setWidget(
            self.conteudo_alertas
        )

        layout_alertas.addWidget(
            self.scroll_alertas,
            1
        )

        self.botao_abrir_servicos = QPushButton(
            "Abrir Monitor de Serviços"
        )

        self.botao_abrir_servicos.setObjectName(
            "dashboardOutlineAction"
        )

        self.botao_abrir_servicos.setIcon(
            criar_icone(
                "chart",
                "#58a6ff",
                22
            )
        )

        self.botao_abrir_servicos.setIconSize(
            QSize(
                22,
                22
            )
        )

        layout_alertas.addWidget(
            self.botao_abrir_servicos
        )

        linha_centro.addWidget(
            painel_monitoramento,
            1
        )

        linha_centro.addWidget(
            painel_alertas,
            1
        )

        layout.addLayout(
            linha_centro,
            2
        )

        # =================================================
        # ATIVIDADE RECENTE
        # =================================================

        painel_atividade = QFrame()

        painel_atividade.setObjectName(
            "dashboardSection"
        )

        layout_atividade = QVBoxLayout(
            painel_atividade
        )

        layout_atividade.setContentsMargins(
            14,
            10,
            14,
            10
        )

        layout_atividade.setSpacing(
            3
        )

        cabecalho_atividade = QHBoxLayout()

        icon_clock = QLabel()

        icon_clock.setPixmap(
            criar_icone(
                "clock",
                "#9fb6ca",
                22
            ).pixmap(
                22,
                22
            )
        )

        titulo_atividade = QLabel(
            "ATIVIDADE RECENTE"
        )

        titulo_atividade.setObjectName(
            "dashboardSectionTitle"
        )

        cabecalho_atividade.addWidget(
            icon_clock
        )

        cabecalho_atividade.addWidget(
            titulo_atividade
        )

        cabecalho_atividade.addStretch()

        layout_atividade.addLayout(
            cabecalho_atividade
        )

        self.linhas_atividade = []

        for _ in range(
            3
        ):
            linha = ActivityRow()

            linha.setVisible(
                False
            )

            self.linhas_atividade.append(
                linha
            )

            layout_atividade.addWidget(
                linha
            )

        self.label_sem_atividade = QLabel(
            "Nenhuma atividade recente registrada."
        )

        self.label_sem_atividade.setObjectName(
            "dashboardEmptyState"
        )

        self.label_sem_atividade.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout_atividade.addWidget(
            self.label_sem_atividade
        )

        layout.addWidget(
            painel_atividade
        )

        # =================================================
        # ATALHOS
        # =================================================

        linha_atalhos = QHBoxLayout()

        linha_atalhos.setSpacing(
            10
        )

        self.botao_diagnostico = self.criar_atalho(
            "Novo Diagnóstico",
            "plus"
        )

        self.botao_ping = self.criar_atalho(
            "Monitor ICMP",
            "pulse"
        )

        self.botao_rota = self.criar_atalho(
            "Monitor de Rota",
            "route"
        )

        self.botao_servicos = self.criar_atalho(
            "Monitor de Serviços",
            "server"
        )

        linha_atalhos.addWidget(
            self.botao_diagnostico,
            1
        )

        linha_atalhos.addWidget(
            self.botao_ping,
            1
        )

        linha_atalhos.addWidget(
            self.botao_rota,
            1
        )

        linha_atalhos.addWidget(
            self.botao_servicos,
            1
        )

        layout.addLayout(
            linha_atalhos
        )

        self.botao_diagnostico.clicked.connect(
            self.solicitar_diagnostico.emit
        )

        self.botao_ping.clicked.connect(
            self.solicitar_ping.emit
        )

        self.botao_rota.clicked.connect(
            self.solicitar_rota.emit
        )

        self.botao_servicos.clicked.connect(
            self.solicitar_servicos.emit
        )

        self.botao_abrir_servicos.clicked.connect(
            self.solicitar_servicos.emit
        )

    def criar_atalho(
        self,
        texto,
        icone
    ):
        botao = QPushButton(
            texto
        )

        botao.setObjectName(
            "dashboardQuickAction"
        )

        botao.setIcon(
            criar_icone(
                icone,
                "#58a6ff",
                44,
                com_fundo=True
            )
        )

        botao.setIconSize(
            QSize(
                44,
                44
            )
        )

        return botao

    def atualizar_relogio(
        self
    ):
        agora = datetime.now()

        self.label_data_hora.setText(
            agora.strftime(
                "%d/%m/%Y  %H:%M:%S"
            )
        )

    def atualizar_servicos(
        self,
        servicos
    ):
        self.label_sem_servicos.setVisible(
            not bool(
                servicos
            )
        )

        while len(
            self.linhas_servicos
        ) < len(
            servicos
        ):
            linha = ServiceRow()

            self.linhas_servicos.append(
                linha
            )

            self.layout_lista_servicos.addWidget(
                linha
            )

        for indice, linha in enumerate(
            self.linhas_servicos
        ):
            if indice >= len(
                servicos
            ):
                linha.setVisible(
                    False
                )
                continue

            servico = servicos[
                indice
            ]

            linha.atualizar(
                servico.get(
                    "nome",
                    "Serviço"
                ),
                servico.get(
                    "resultado",
                    "-"
                ),
                servico.get(
                    "estado",
                    "neutro"
                ),
                servico.get(
                    "cor",
                    "#2f81f7"
                ),
                servico.get(
                    "icone",
                    "globe"
                )
            )

            linha.setVisible(
                True
            )

    def atualizar_alertas(
        self,
        alertas
    ):
        self.label_sem_alertas.setVisible(
            not bool(
                alertas
            )
        )

        while len(
            self.linhas_alertas
        ) < len(
            alertas
        ):
            linha = AlertRow()

            self.linhas_alertas.append(
                linha
            )

            self.layout_lista_alertas.addWidget(
                linha
            )

        for indice, linha in enumerate(
            self.linhas_alertas
        ):
            if indice >= len(
                alertas
            ):
                linha.setVisible(
                    False
                )
                continue

            alerta = alertas[
                indice
            ]

            origem = alerta.get(
                "origem",
                "Serviço"
            )

            status = alerta.get(
                "status",
                "-"
            )

            linha.atualizar(
                f"{origem} — {status}",
                alerta.get(
                    "estado",
                    "alerta"
                )
            )

            linha.setVisible(
                True
            )

    def atualizar_atividade(
        self,
        atividade
    ):
        self.label_sem_atividade.setVisible(
            not bool(
                atividade
            )
        )

        for indice, linha in enumerate(
            self.linhas_atividade
        ):
            if indice >= len(
                atividade
            ):
                linha.setVisible(
                    False
                )
                continue

            item = atividade[
                indice
            ]

            linha.atualizar(
                item.get(
                    "horario",
                    "-"
                ),
                item.get(
                    "origem",
                    "-"
                ),
                item.get(
                    "evento",
                    "-"
                ),
                item.get(
                    "status",
                    "NORMALIZADO"
                )
            )

            linha.setVisible(
                True
            )

    def atualizar(
        self,
        resumo
    ):
        self.card_saude.atualizar(
            resumo.get(
                "saude_texto",
                "AGUARDANDO"
            ),
            resumo.get(
                "saude_subtitulo",
                "Coletando informações"
            ),
            resumo.get(
                "saude_estado",
                "neutro"
            )
        )

        total_servicos = resumo.get(
            "servicos_total",
            0
        )

        online = resumo.get(
            "servicos_online",
            0
        )

        texto_servicos = (
            f"{online} / {total_servicos} ONLINE"
            if total_servicos
            else "-"
        )

        self.card_servicos.atualizar(
            texto_servicos,
            resumo.get(
                "servicos_subtitulo",
                "Aguardando monitoramento"
            ),
            resumo.get(
                "servicos_estado",
                "neutro"
            )
        )

        total_incidentes = resumo.get(
            "incidentes_hoje",
            0
        )

        criticos_hoje = resumo.get(
            "incidentes_criticos_hoje",
            0
        )

        self.card_incidentes.atualizar(
            total_incidentes,
            (
                f"{criticos_hoje} crítico(s)"
                if criticos_hoje
                else "Nenhum crítico hoje"
            ),
            (
                "critico"
                if criticos_hoje
                else (
                    "alerta"
                    if total_incidentes
                    else "normal"
                )
            )
        )

        alertas = resumo.get(
            "alertas_ativos",
            []
        )

        self.card_alertas.atualizar(
            len(
                alertas
            ),
            (
                "ativos"
                if alertas
                else "Nenhum alerta ativo"
            ),
            resumo.get(
                "alertas_estado",
                "normal"
            )
        )

        self.atualizar_servicos(
            resumo.get(
                "servicos_monitoramento",
                []
            )
        )

        self.atualizar_alertas(
            alertas
        )

        self.atualizar_atividade(
            resumo.get(
                "atividade_recente",
                []
            )
        )


class MonitoringPage(QWidget):
    solicitar_ping = Signal()
    solicitar_rota = Signal()
    solicitar_servicos = Signal()

    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

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
            14
        )

        titulo = QLabel(
            "Monitoramento"
        )

        titulo.setObjectName(
            "pageTitle"
        )

        subtitulo = QLabel(
            "Acompanhe disponibilidade, latência e rota em tempo real."
        )

        subtitulo.setObjectName(
            "pageSubtitle"
        )

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            subtitulo
        )

        grade = QGridLayout()

        grade.setSpacing(
            12
        )

        self.painel_servicos = self.criar_painel(
            "Monitor de Serviços",
            "Verificação contínua dos serviços configurados.",
            "Abrir Monitor de Serviços"
        )

        self.painel_ping = self.criar_painel(
            "Monitor ICMP",
            "Acompanhamento contínuo de latência e perda.",
            "Ir para Monitor ICMP"
        )

        self.painel_rota = self.criar_painel(
            "Monitor de Rota",
            "Telemetria por salto com estatísticas acumuladas.",
            "Ir para Monitor de Rota"
        )

        self.botao_servicos = (
            self.painel_servicos[
                "botao"
            ]
        )

        self.botao_ping = (
            self.painel_ping[
                "botao"
            ]
        )

        self.botao_rota = (
            self.painel_rota[
                "botao"
            ]
        )

        grade.addWidget(
            self.painel_servicos[
                "widget"
            ],
            0,
            0
        )

        grade.addWidget(
            self.painel_ping[
                "widget"
            ],
            0,
            1
        )

        grade.addWidget(
            self.painel_rota[
                "widget"
            ],
            1,
            0,
            1,
            2
        )

        grade.setColumnStretch(
            0,
            1
        )

        grade.setColumnStretch(
            1,
            1
        )

        layout.addLayout(
            grade
        )

        layout.addStretch()

        self.botao_servicos.clicked.connect(
            self.solicitar_servicos.emit
        )

        self.botao_ping.clicked.connect(
            self.solicitar_ping.emit
        )

        self.botao_rota.clicked.connect(
            self.solicitar_rota.emit
        )

    def criar_painel(
        self,
        titulo,
        descricao,
        texto_botao
    ):
        painel = QFrame()

        painel.setObjectName(
            "monitorFeatureCard"
        )

        layout = QVBoxLayout(
            painel
        )

        layout.setContentsMargins(
            16,
            14,
            16,
            14
        )

        layout.setSpacing(
            8
        )

        linha_titulo = QHBoxLayout()

        label_titulo = QLabel(
            titulo
        )

        label_titulo.setObjectName(
            "dashboardSectionTitle"
        )

        indicador = QLabel(
            "● AGUARDANDO"
        )

        indicador.setObjectName(
            "featureStatus"
        )

        indicador.setProperty(
            "estado",
            "neutro"
        )

        linha_titulo.addWidget(
            label_titulo
        )

        linha_titulo.addStretch()

        linha_titulo.addWidget(
            indicador
        )

        label_descricao = QLabel(
            descricao
        )

        label_descricao.setObjectName(
            "textoSecundario"
        )

        label_descricao.setWordWrap(
            True
        )

        label_resumo = QLabel(
            "Aguardando informações."
        )

        label_resumo.setObjectName(
            "monitorFeatureSummary"
        )

        botao = QPushButton(
            texto_botao
        )

        botao.setObjectName(
            "monitorFeatureAction"
        )

        layout.addLayout(
            linha_titulo
        )

        layout.addWidget(
            label_descricao
        )

        layout.addSpacing(
            6
        )

        layout.addWidget(
            label_resumo
        )

        layout.addStretch()

        layout.addWidget(
            botao,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        return {
            "widget": painel,
            "status": indicador,
            "resumo": label_resumo,
            "botao": botao
        }

    def _atualizar_painel(
        self,
        painel,
        status,
        resumo,
        estado
    ):
        painel[
            "status"
        ].setText(
            status
        )

        painel[
            "status"
        ].setProperty(
            "estado",
            estado
        )

        painel[
            "resumo"
        ].setText(
            resumo
        )

        estilo = painel[
            "status"
        ].style()

        estilo.unpolish(
            painel[
                "status"
            ]
        )

        estilo.polish(
            painel[
                "status"
            ]
        )

    def atualizar(
        self,
        resumo
    ):
        self._atualizar_painel(
            self.painel_servicos,
            resumo.get(
                "monitor_servicos_badge",
                "● AGUARDANDO"
            ),
            resumo.get(
                "monitor_servicos_texto",
                "Aguardando primeiro ciclo"
            ),
            resumo.get(
                "monitor_servicos_estado",
                "neutro"
            )
        )

        self._atualizar_painel(
            self.painel_ping,
            resumo.get(
                "monitor_ping_badge",
                "○ INATIVO"
            ),
            resumo.get(
                "monitor_ping_texto",
                "Inativo"
            ),
            resumo.get(
                "monitor_ping_estado",
                "neutro"
            )
        )

        self._atualizar_painel(
            self.painel_rota,
            resumo.get(
                "monitor_rota_badge",
                "○ INATIVO"
            ),
            resumo.get(
                "monitor_rota_texto",
                "Inativo"
            ),
            resumo.get(
                "monitor_rota_estado",
                "neutro"
            )
        )


class IncidentsPage(QWidget):
    solicitar_abrir_registro = Signal()

    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

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
            12
        )

        linha_titulo = QHBoxLayout()

        bloco_titulo = QVBoxLayout()

        titulo = QLabel(
            "Incidentes"
        )

        titulo.setObjectName(
            "pageTitle"
        )

        subtitulo = QLabel(
            "Resumo dos eventos registrados pelo Monitor de Serviços."
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

        linha_titulo.addLayout(
            bloco_titulo
        )

        linha_titulo.addStretch()

        self.botao_abrir_registro = QPushButton(
            "Abrir Registro Completo"
        )

        self.botao_abrir_registro.setObjectName(
            "dashboardPrimaryAction"
        )

        linha_titulo.addWidget(
            self.botao_abrir_registro
        )

        layout.addLayout(
            linha_titulo
        )

        cards = QGridLayout()

        self.card_total = MetricCard(
            "Incidentes Hoje",
            "0",
            "Nenhum registro"
        )

        self.card_criticos = MetricCard(
            "Críticos Hoje",
            "0",
            "Nenhum crítico"
        )

        self.card_andamento = MetricCard(
            "Em Andamento",
            "0",
            "Nenhum incidente ativo"
        )

        self.card_tempo = MetricCard(
            "Tempo Afetado Hoje",
            "0 min",
            "Tempo acumulado"
        )

        cards.addWidget(
            self.card_total,
            0,
            0
        )

        cards.addWidget(
            self.card_criticos,
            0,
            1
        )

        cards.addWidget(
            self.card_andamento,
            0,
            2
        )

        cards.addWidget(
            self.card_tempo,
            0,
            3
        )

        for coluna in range(
            4
        ):
            cards.setColumnStretch(
                coluna,
                1
            )

        layout.addLayout(
            cards
        )

        painel = QFrame()

        painel.setObjectName(
            "dashboardSection"
        )

        layout_painel = QVBoxLayout(
            painel
        )

        layout_painel.setContentsMargins(
            14,
            12,
            14,
            12
        )

        titulo_recent = QLabel(
            "Incidentes Recentes"
        )

        titulo_recent.setObjectName(
            "dashboardSectionTitle"
        )

        layout_painel.addWidget(
            titulo_recent
        )

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(
            5
        )

        self.tabela.setHorizontalHeaderLabels([
            "Início",
            "Origem",
            "Evento",
            "Causa provável",
            "Status"
        ])

        self.tabela.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.tabela.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabela.setAlternatingRowColors(
            True
        )

        self.tabela.verticalHeader().setVisible(
            False
        )

        cabecalho = (
            self.tabela
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
            QHeaderView.ResizeMode.ResizeToContents
        )

        cabecalho.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch
        )

        cabecalho.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents
        )

        layout_painel.addWidget(
            self.tabela,
            1
        )

        layout.addWidget(
            painel,
            1
        )

        self.botao_abrir_registro.clicked.connect(
            self.solicitar_abrir_registro.emit
        )

    def atualizar(
        self,
        resumo
    ):
        total = resumo.get(
            "incidentes_hoje",
            0
        )

        criticos = resumo.get(
            "incidentes_criticos_hoje",
            0
        )

        andamento = resumo.get(
            "incidentes_andamento",
            0
        )

        tempo = resumo.get(
            "incidentes_tempo_texto",
            "0 min"
        )

        self.card_total.atualizar(
            total,
            "Registros iniciados hoje",
            (
                "alerta"
                if total
                else "normal"
            )
        )

        self.card_criticos.atualizar(
            criticos,
            "Eventos críticos registrados",
            (
                "critico"
                if criticos
                else "normal"
            )
        )

        self.card_andamento.atualizar(
            andamento,
            "Incidentes ainda abertos",
            (
                "critico"
                if andamento
                else "normal"
            )
        )

        self.card_tempo.atualizar(
            tempo,
            "Duração acumulada dos incidentes de hoje",
            (
                "alerta"
                if total
                else "normal"
            )
        )

        recentes = resumo.get(
            "incidentes_recentes",
            []
        )

        self.tabela.setRowCount(
            len(
                recentes
            )
        )

        for linha, incidente in enumerate(
            recentes
        ):
            valores = [
                incidente.get(
                    "inicio_texto",
                    "-"
                ),
                incidente.get(
                    "origem",
                    "-"
                ),
                incidente.get(
                    "status_inicial",
                    "-"
                ),
                incidente.get(
                    "causa_provavel",
                    "-"
                ),
                incidente.get(
                    "status_texto",
                    "-"
                )
            ]

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(
                        str(
                            valor
                        )
                    )
                )


class ReportsPage(QWidget):
    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

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
            14
        )

        titulo = QLabel(
            "Relatórios"
        )

        titulo.setObjectName(
            "pageTitle"
        )

        subtitulo = QLabel(
            "Exporte diagnósticos, sessões de rota e backups de configuração."
        )

        subtitulo.setObjectName(
            "pageSubtitle"
        )

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            subtitulo
        )

        grade = QGridLayout()

        grade.setSpacing(
            12
        )

        painel_diag = self.criar_painel(
            "Diagnóstico Atual",
            "Relatório completo do último diagnóstico executado."
        )

        self.botao_diagnostico = QPushButton(
            "Exportar TXT"
        )

        self.botao_diagnostico.setObjectName(
            "dashboardPrimaryAction"
        )

        painel_diag[
            "layout"
        ].addWidget(
            self.botao_diagnostico,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        painel_rota = self.criar_painel(
            "Monitor de Rota",
            "Exporte a última sessão concluída em diferentes formatos."
        )

        linha_rota = QHBoxLayout()

        self.botao_rota_txt = QPushButton(
            "TXT"
        )

        self.botao_rota_csv = QPushButton(
            "CSV"
        )

        self.botao_rota_json = QPushButton(
            "JSON"
        )

        linha_rota.addWidget(
            self.botao_rota_txt
        )

        linha_rota.addWidget(
            self.botao_rota_csv
        )

        linha_rota.addWidget(
            self.botao_rota_json
        )

        linha_rota.addStretch()

        painel_rota[
            "layout"
        ].addLayout(
            linha_rota
        )

        painel_config = self.criar_painel(
            "Configurações",
            "Backup e restauração das preferências do NDT."
        )

        linha_config = QHBoxLayout()

        self.botao_config_export = QPushButton(
            "Exportar Backup"
        )

        self.botao_config_import = QPushButton(
            "Importar Backup"
        )

        linha_config.addWidget(
            self.botao_config_export
        )

        linha_config.addWidget(
            self.botao_config_import
        )

        linha_config.addStretch()

        painel_config[
            "layout"
        ].addLayout(
            linha_config
        )

        painel_logs = self.criar_painel(
            "Logs",
            "Consulte eventos, falhas e informações de execução."
        )

        self.botao_logs = QPushButton(
            "Abrir Logs"
        )

        painel_logs[
            "layout"
        ].addWidget(
            self.botao_logs,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        grade.addWidget(
            painel_diag[
                "widget"
            ],
            0,
            0
        )

        grade.addWidget(
            painel_rota[
                "widget"
            ],
            0,
            1
        )

        grade.addWidget(
            painel_config[
                "widget"
            ],
            1,
            0
        )

        grade.addWidget(
            painel_logs[
                "widget"
            ],
            1,
            1
        )

        grade.setColumnStretch(
            0,
            1
        )

        grade.setColumnStretch(
            1,
            1
        )

        layout.addLayout(
            grade
        )

        layout.addStretch()

    def criar_painel(
        self,
        titulo,
        descricao
    ):
        painel = QFrame()

        painel.setObjectName(
            "reportCard"
        )

        layout = QVBoxLayout(
            painel
        )

        layout.setContentsMargins(
            16,
            14,
            16,
            14
        )

        layout.setSpacing(
            8
        )

        label_titulo = QLabel(
            titulo
        )

        label_titulo.setObjectName(
            "dashboardSectionTitle"
        )

        label_descricao = QLabel(
            descricao
        )

        label_descricao.setObjectName(
            "textoSecundario"
        )

        label_descricao.setWordWrap(
            True
        )

        layout.addWidget(
            label_titulo
        )

        layout.addWidget(
            label_descricao
        )

        layout.addStretch()

        return {
            "widget": painel,
            "layout": layout
        }

    def atualizar_exportacoes(
        self,
        diagnostico_disponivel,
        rota_disponivel,
        bloqueado=False
    ):
        self.botao_diagnostico.setEnabled(
            bool(
                diagnostico_disponivel
            )
            and not bloqueado
        )

        for botao in (
            self.botao_rota_txt,
            self.botao_rota_csv,
            self.botao_rota_json
        ):
            botao.setEnabled(
                bool(
                    rota_disponivel
                )
                and not bloqueado
            )

        # Backup/importação e logs continuam utilizáveis
        # enquanto não houver bloqueio explícito da interface.
        self.botao_config_export.setEnabled(
            not bloqueado
        )

        self.botao_config_import.setEnabled(
            not bloqueado
        )

        self.botao_logs.setEnabled(
            True
        )
