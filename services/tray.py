from PySide6.QtCore import (
    QObject,
    QEvent
)

from PySide6.QtGui import QAction

from PySide6.QtWidgets import (
    QApplication,
    QMenu,
    QStyle,
    QSystemTrayIcon
)

from services.logger import logger


class SystemTrayController(QObject):
    def __init__(
        self,
        app: QApplication,
        janela
    ):
        super().__init__(
            app
        )

        self.app = app
        self.janela = janela

        self.encerrar_realmente = False
        self.encerramento_em_andamento = False
        self.aviso_exibido = False

        self.criar_bandeja()

        self.janela.installEventFilter(
            self
        )

    def criar_bandeja(
        self
    ):
        icone = (
            self.janela
            .style()
            .standardIcon(
                QStyle
                .StandardPixmap
                .SP_ComputerIcon
            )
        )

        self.tray = QSystemTrayIcon(
            icone,
            self
        )

        self.tray.setToolTip(
            "Network Diagnostic Tool"
        )

        menu = QMenu(
            self.janela
        )

        acao_abrir = QAction(
            "Abrir Network Diagnostic Tool",
            self
        )

        self.acao_status = QAction(
            "DownDetector ativo",
            self
        )

        self.acao_status.setEnabled(
            False
        )

        acao_sair = QAction(
            "Sair",
            self
        )

        acao_abrir.triggered.connect(
            self.mostrar_janela
        )

        acao_sair.triggered.connect(
            self.sair
        )

        menu.addAction(
            acao_abrir
        )

        menu.addAction(
            self.acao_status
        )

        menu.addSeparator()

        menu.addAction(
            acao_sair
        )

        self.tray.setContextMenu(
            menu
        )

        self.tray.activated.connect(
            self.tray_ativado
        )

        self.tray.show()

        logger.info(
            "Ícone da bandeja iniciado."
        )

    def eventFilter(
        self,
        objeto,
        evento
    ):
        if (
            objeto is self.janela
            and evento.type()
            == QEvent.Type.Close
            and not self.encerrar_realmente
        ):
            evento.ignore()

            self.janela.hide()

            logger.info(
                "Janela ocultada na bandeja."
            )

            if not self.aviso_exibido:
                self.tray.showMessage(
                    "Network Diagnostic Tool",
                    "O programa continua executando "
                    "em segundo plano.",
                    QSystemTrayIcon
                    .MessageIcon
                    .Information,
                    3000
                )

                self.aviso_exibido = True

            return True

        return super().eventFilter(
            objeto,
            evento
        )

    def mostrar_janela(
        self
    ):
        if self.encerramento_em_andamento:
            return

        self.janela.show()

        self.janela.showNormal()

        self.janela.raise_()

        self.janela.activateWindow()

        logger.info(
            "Janela restaurada da bandeja."
        )

    def tray_ativado(
        self,
        motivo
    ):
        if motivo == (
            QSystemTrayIcon
            .ActivationReason
            .Trigger
        ):
            self.mostrar_janela()

    def sair(
        self
    ):
        if self.encerramento_em_andamento:
            return

        self.encerramento_em_andamento = True
        self.encerrar_realmente = True

        logger.info(
            "Encerramento solicitado "
            "pela bandeja."
        )

        self.tray.hide()

        # IMPORTANTE:
        # Não chamamos simplesmente janela.close() + app.quit().
        # MainWindow.encerrar_aplicacao() marca o fechamento como real,
        # encerra todas as threads e só depois fecha a janela.
        if hasattr(
            self.janela,
            "encerrar_aplicacao"
        ):
            self.janela.encerrar_aplicacao()

        else:
            # Fallback de segurança.
            self.janela.encerramento_real = True

            if hasattr(
                self.janela,
                "parar_threads"
            ):
                self.janela.parar_threads()

            self.janela.close()

        # Neste ponto as threads do NDT já receberam o encerramento
        # adequado. Agora o loop do Qt pode ser finalizado com segurança.
        self.app.quit()
