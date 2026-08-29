from collections.abc import Callable

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    Qt,
    Signal
)

from PySide6.QtGui import (
    QColor,
    QFont,
    QTextCharFormat,
    QTextCursor
)

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget
)


class SplashWindow(QWidget):
    solicitar_minimizar = Signal()
    solicitar_fechar = Signal()

    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self._animacao = None
        self._callback_final = None
        self._arrastando = False
        self._posicao_arraste = QPoint()

        self.setWindowTitle(
            "Network Diagnostic Tool"
        )

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_DeleteOnClose,
            False
        )

        self.setFixedSize(
            760,
            485
        )

        self.setObjectName(
            "splashRoot"
        )

        self.setStyleSheet(
            """
            QWidget#splashRoot {
                background-color: #0b1118;
                border: 1px solid #2b3c4d;
                border-radius: 12px;
            }

            QFrame#splashHeader {
                background-color: #101a24;
                border: 1px solid #253545;
                border-radius: 9px;
            }

            QLabel#splashMarca {
                color: #2388ff;
                font-size: 24pt;
                font-weight: 800;
            }

            QLabel#splashNome {
                color: #f3f8fc;
                font-size: 15pt;
                font-weight: 700;
            }

            QLabel#splashSubtitulo {
                color: #8294a5;
                font-size: 9pt;
            }

            QLabel#splashStatus {
                color: #aebdca;
                font-size: 9pt;
            }

            QLabel#splashVersao {
                color: #647688;
                font-size: 9pt;
            }

            QLabel#splashPronto {
                color: #71e3aa;
                font-size: 10pt;
                font-weight: 700;
            }

            QLabel#splashBootBadge {
                color: #39d98a;
                font-size: 9pt;
                font-weight: 700;
            }

            QPlainTextEdit#splashTerminal {
                background-color: #080e14;
                color: #aebdca;
                border: 1px solid #20303e;
                border-radius: 7px;
                padding: 10px;
                selection-background-color: #1e5f91;
            }

            QProgressBar#splashProgress {
                background-color: #111a23;
                border: 1px solid #263646;
                border-radius: 5px;
                min-height: 9px;
                max-height: 9px;
                text-align: center;
            }

            QProgressBar#splashProgress::chunk {
                background-color: #2388ff;
                border-radius: 4px;
            }

            QPushButton#botaoIniciarNdt {
                background-color: #1477dc;
                border: 1px solid #2b91ff;
                border-radius: 8px;
                color: #ffffff;
                font-size: 11pt;
                font-weight: 700;
                padding: 10px 26px;
                min-width: 170px;
            }

            QPushButton#botaoIniciarNdt:hover {
                background-color: #2388ff;
                border-color: #53a7ff;
            }

            QPushButton#botaoIniciarNdt:pressed {
                background-color: #1167be;
            }

            QPushButton#botaoSplashMinimizar,
            QPushButton#botaoSplashFechar {
                background-color: transparent;
                border: none;
                border-radius: 5px;
                color: #8fa2b5;
                font-size: 12pt;
                font-weight: 600;
                min-width: 28px;
                max-width: 28px;
                min-height: 26px;
                max-height: 26px;
                padding: 0px;
            }

            QPushButton#botaoSplashMinimizar:hover {
                background-color: #1c3142;
                color: #ffffff;
            }

            QPushButton#botaoSplashFechar:hover {
                background-color: #7a2e36;
                color: #ffffff;
            }
            """
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            22,
            22,
            22,
            18
        )

        layout.setSpacing(
            14
        )

        # =================================================
        # CABEÇALHO
        # =================================================

        self.cabecalho = QFrame()

        self.cabecalho.setObjectName(
            "splashHeader"
        )

        layout_cabecalho = QHBoxLayout(
            self.cabecalho
        )

        layout_cabecalho.setContentsMargins(
            18,
            14,
            12,
            14
        )

        bloco_marca = QVBoxLayout()

        marca = QLabel(
            "NDT"
        )

        marca.setObjectName(
            "splashMarca"
        )

        nome = QLabel(
            "NETWORK DIAGNOSTIC TOOL"
        )

        nome.setObjectName(
            "splashNome"
        )

        subtitulo = QLabel(
            "Diagnóstico • Monitoramento • Telemetria"
        )

        subtitulo.setObjectName(
            "splashSubtitulo"
        )

        bloco_marca.addWidget(
            marca
        )

        bloco_marca.addWidget(
            nome
        )

        bloco_marca.addWidget(
            subtitulo
        )

        layout_cabecalho.addLayout(
            bloco_marca
        )

        layout_cabecalho.addStretch()

        bloco_controles = QVBoxLayout()

        linha_controles = QHBoxLayout()

        linha_controles.setSpacing(
            3
        )

        self.botao_minimizar = QPushButton(
            "—"
        )

        self.botao_minimizar.setObjectName(
            "botaoSplashMinimizar"
        )

        self.botao_minimizar.setToolTip(
            "Minimizar para a bandeja"
        )

        self.botao_fechar = QPushButton(
            "×"
        )

        self.botao_fechar.setObjectName(
            "botaoSplashFechar"
        )

        self.botao_fechar.setToolTip(
            "Fechar NDT"
        )

        self.botao_minimizar.clicked.connect(
            self.solicitar_minimizar.emit
        )

        self.botao_fechar.clicked.connect(
            self.solicitar_fechar.emit
        )

        linha_controles.addWidget(
            self.botao_minimizar
        )

        linha_controles.addWidget(
            self.botao_fechar
        )

        badge = QLabel(
            "●  SYSTEM BOOT"
        )

        badge.setObjectName(
            "splashBootBadge"
        )

        bloco_controles.addLayout(
            linha_controles
        )

        bloco_controles.addWidget(
            badge,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        bloco_controles.addStretch()

        layout_cabecalho.addLayout(
            bloco_controles
        )

        layout.addWidget(
            self.cabecalho
        )

        # =================================================
        # TERMINAL
        # =================================================

        self.terminal = QPlainTextEdit()

        self.terminal.setObjectName(
            "splashTerminal"
        )

        self.terminal.setReadOnly(
            True
        )

        self.terminal.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        fonte_terminal = QFont(
            "Consolas"
        )

        fonte_terminal.setPointSize(
            9
        )

        self.terminal.setFont(
            fonte_terminal
        )

        layout.addWidget(
            self.terminal,
            1
        )

        self._inserir_boot_inicial()

        # =================================================
        # STATUS
        # =================================================

        linha_status = QHBoxLayout()

        self.status = QLabel(
            "Preparando inicialização..."
        )

        self.status.setObjectName(
            "splashStatus"
        )

        versao = QLabel(
            "Version 1.2"
        )

        versao.setObjectName(
            "splashVersao"
        )

        linha_status.addWidget(
            self.status
        )

        linha_status.addStretch()

        linha_status.addWidget(
            versao
        )

        layout.addLayout(
            linha_status
        )

        self.progresso = QProgressBar()

        self.progresso.setObjectName(
            "splashProgress"
        )

        self.progresso.setRange(
            0,
            100
        )

        self.progresso.setValue(
            0
        )

        self.progresso.setTextVisible(
            False
        )

        layout.addWidget(
            self.progresso
        )

        # =================================================
        # ÁREA DE INÍCIO
        # =================================================

        self.linha_inicio = QHBoxLayout()

        self.label_pronto = QLabel(
            "● SISTEMA PRONTO"
        )

        self.label_pronto.setObjectName(
            "splashPronto"
        )

        self.label_pronto.setVisible(
            False
        )

        self.botao_iniciar = QPushButton(
            "INICIAR NDT"
        )

        self.botao_iniciar.setObjectName(
            "botaoIniciarNdt"
        )

        self.botao_iniciar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.botao_iniciar.setVisible(
            False
        )

        self.botao_iniciar.clicked.connect(
            self.iniciar_ndt
        )

        self.linha_inicio.addWidget(
            self.label_pronto
        )

        self.linha_inicio.addStretch()

        self.linha_inicio.addWidget(
            self.botao_iniciar
        )

        layout.addLayout(
            self.linha_inicio
        )

        self.centralizar()

    # =====================================================
    # TERMINAL COLORIDO
    # =====================================================

    def _formato(
        self,
        cor,
        negrito=False
    ):
        formato = QTextCharFormat()

        formato.setForeground(
            QColor(
                cor
            )
        )

        if negrito:
            formato.setFontWeight(
                QFont.Weight.Bold
            )

        return formato

    def _inserir_segmento(
        self,
        cursor,
        texto,
        cor,
        negrito=False
    ):
        cursor.insertText(
            texto,
            self._formato(
                cor,
                negrito
            )
        )

    def _inserir_boot_inicial(
        self
    ):
        cursor = self.terminal.textCursor()

        cursor.movePosition(
            QTextCursor.MoveOperation.End
        )

        self._inserir_segmento(
            cursor,
            "> ",
            "#2388ff",
            True
        )

        self._inserir_segmento(
            cursor,
            "NDT",
            "#58a6ff",
            True
        )

        self._inserir_segmento(
            cursor,
            " BOOT SEQUENCE",
            "#dce6ee",
            True
        )

        cursor.insertText(
            "\n"
        )

        self.terminal.setTextCursor(
            cursor
        )

    def adicionar_etapa(
        self,
        texto,
        progresso,
        ok=True
    ):
        cursor = self.terminal.textCursor()

        cursor.movePosition(
            QTextCursor.MoveOperation.End
        )

        self._inserir_segmento(
            cursor,
            "> ",
            "#2388ff",
            True
        )

        cor_texto = (
            "#71e3aa"
            if texto == "Sistema pronto"
            else "#8fd3ff"
        )

        self._inserir_segmento(
            cursor,
            texto,
            cor_texto,
            texto == "Sistema pronto"
        )

        largura = 54

        tamanho_atual = (
            2
            + len(
                texto
            )
        )

        quantidade_pontos = max(
            3,
            largura
            - tamanho_atual
        )

        self._inserir_segmento(
            cursor,
            "." * quantidade_pontos,
            "#405264"
        )

        if ok:
            self._inserir_segmento(
                cursor,
                " [ OK ]",
                "#39d98a",
                True
            )

        else:
            self._inserir_segmento(
                cursor,
                " [ .. ]",
                "#ffcc66",
                True
            )

        cursor.insertText(
            "\n"
        )

        self.terminal.setTextCursor(
            cursor
        )

        self.terminal.ensureCursorVisible()

        self.status.setText(
            texto
        )

        self.progresso.setValue(
            int(
                max(
                    0,
                    min(
                        100,
                        progresso
                    )
                )
            )
        )

    # =====================================================
    # JANELA
    # =====================================================

    def centralizar(
        self
    ):
        tela = QApplication.primaryScreen()

        if tela is None:
            return

        area = tela.availableGeometry()

        geometria = self.frameGeometry()

        geometria.moveCenter(
            area.center()
        )

        self.move(
            geometria.topLeft()
        )

    def mousePressEvent(
        self,
        evento
    ):
        if (
            evento.button()
            == Qt.MouseButton.LeftButton
        ):
            self._arrastando = True

            self._posicao_arraste = (
                evento.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            evento.accept()
            return

        super().mousePressEvent(
            evento
        )

    def mouseMoveEvent(
        self,
        evento
    ):
        if (
            self._arrastando
            and evento.buttons()
            & Qt.MouseButton.LeftButton
        ):
            self.move(
                evento.globalPosition().toPoint()
                - self._posicao_arraste
            )

            evento.accept()
            return

        super().mouseMoveEvent(
            evento
        )

    def mouseReleaseEvent(
        self,
        evento
    ):
        self._arrastando = False

        super().mouseReleaseEvent(
            evento
        )

    # =====================================================
    # ESTADOS
    # =====================================================

    def definir_status(
        self,
        texto,
        progresso=None
    ):
        self.status.setText(
            texto
        )

        if progresso is not None:
            self.progresso.setValue(
                int(
                    max(
                        0,
                        min(
                            100,
                            progresso
                        )
                    )
                )
            )

    def concluir(
        self,
        callback: Callable[[], None] | None = None
    ):
        self._callback_final = callback

        self.adicionar_etapa(
            "Sistema pronto",
            100,
            True
        )

        self.status.setText(
            "Inicialização concluída. Clique em INICIAR NDT."
        )

        self.progresso.setStyleSheet(
            """
            QProgressBar#splashProgress {
                background-color: #111a23;
                border: 1px solid #263646;
                border-radius: 5px;
                min-height: 9px;
                max-height: 9px;
            }

            QProgressBar#splashProgress::chunk {
                background-color: #39d98a;
                border-radius: 4px;
            }
            """
        )

        self.label_pronto.setVisible(
            True
        )

        self.botao_iniciar.setVisible(
            True
        )

        self.botao_iniciar.setFocus()

    def iniciar_ndt(
        self
    ):
        self.botao_iniciar.setEnabled(
            False
        )

        self.status.setText(
            "Abrindo Network Diagnostic Tool..."
        )

        self._animacao = QPropertyAnimation(
            self,
            b"windowOpacity"
        )

        self._animacao.setDuration(
            380
        )

        self._animacao.setStartValue(
            1.0
        )

        self._animacao.setEndValue(
            0.0
        )

        self._animacao.setEasingCurve(
            QEasingCurve.Type.InOutCubic
        )

        self._animacao.finished.connect(
            self._finalizar_fade
        )

        self._animacao.start()

    def _finalizar_fade(
        self
    ):
        self.hide()

        self.setWindowOpacity(
            1.0
        )

        callback = self._callback_final

        self._callback_final = None

        if callback is not None:
            callback()
