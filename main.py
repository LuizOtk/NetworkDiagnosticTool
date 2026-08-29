import sys
from typing import Any

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMenu,
    QStyle,
    QSystemTrayIcon
)

from config.settings import (
    carregar_configuracoes
)

from services.logger import (
    instalar_captura_global,
    logger
)

from ui.splash_window import SplashWindow
from ui.styles import DARK_STYLE


instalar_captura_global()

logger.info(
    "========================================"
)

logger.info(
    "Network Diagnostic Tool iniciado."
)

logger.info(
    "Versão 1.2 em desenvolvimento."
)


app = QApplication(
    sys.argv
)

app.setQuitOnLastWindowClosed(
    False
)

app.setStyleSheet(
    DARK_STYLE
)


estado_aplicacao: dict[str, Any] = {
    "janela": None,
    "tray": None,
    "splash": None,
    "tray_splash": None
}


configuracoes_iniciais = (
    carregar_configuracoes()
)


def preparar_encerramento():
    janela = estado_aplicacao.get(
        "janela"
    )

    if janela is None:
        return

    if not janela.encerramento_real:
        logger.info(
            "Qt solicitou encerramento geral."
        )

        janela.encerramento_real = True

        janela.parar_threads()


def registrar_encerramento():
    logger.info(
        "Aplicação encerrada."
    )


app.aboutToQuit.connect(
    preparar_encerramento
)

app.aboutToQuit.connect(
    registrar_encerramento
)


# =========================================================
# TRAY TEMPORÁRIO DA TELA DE BOOT
# =========================================================

def restaurar_splash():
    splash = estado_aplicacao.get(
        "splash"
    )

    if splash is None:
        return

    splash.showNormal()
    splash.setWindowOpacity(
        1.0
    )
    splash.raise_()
    splash.activateWindow()


def ocultar_splash_na_bandeja():
    splash = estado_aplicacao.get(
        "splash"
    )

    tray_splash = estado_aplicacao.get(
        "tray_splash"
    )

    if splash is None:
        return

    if tray_splash is not None:
        tray_splash.show()

        tray_splash.showMessage(
            "Network Diagnostic Tool",
            "A tela de inicialização continua disponível na bandeja.",
            QSystemTrayIcon.MessageIcon.Information,
            1800
        )

    splash.hide()


def encerrar_pelo_splash():
    logger.info(
        "Encerramento solicitado pela tela de inicialização."
    )

    app.quit()


def criar_tray_splash():
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None

    estilo = app.style()

    icone = estilo.standardIcon(
        QStyle.StandardPixmap.SP_ComputerIcon
    )

    tray = QSystemTrayIcon(
        icone,
        app
    )

    tray.setToolTip(
        "Network Diagnostic Tool — Inicialização"
    )

    menu = QMenu()

    acao_abrir = QAction(
        "Abrir inicialização",
        menu
    )

    acao_sair = QAction(
        "Sair",
        menu
    )

    acao_abrir.triggered.connect(
        restaurar_splash
    )

    acao_sair.triggered.connect(
        encerrar_pelo_splash
    )

    menu.addAction(
        acao_abrir
    )

    menu.addSeparator()

    menu.addAction(
        acao_sair
    )

    tray.setContextMenu(
        menu
    )

    def ativado(
        motivo
    ):
        if motivo in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick
        ):
            restaurar_splash()

    tray.activated.connect(
        ativado
    )

    return tray


# =========================================================
# INTERFACE PRINCIPAL
# =========================================================

def construir_interface():
    from ui.main_window import (
        MainWindow
    )

    splash = estado_aplicacao.get(
        "splash"
    )

    if splash is not None:
        splash.definir_status(
            "Inicializando interface principal...",
            45
        )

        app.processEvents()

    janela = MainWindow()

    estado_aplicacao[
        "janela"
    ] = janela

    return janela


def ativar_tray_principal():
    if estado_aplicacao.get(
        "tray"
    ) is not None:
        return

    janela = estado_aplicacao.get(
        "janela"
    )

    if janela is None:
        return

    from services.tray import (
        SystemTrayController
    )

    controlador_bandeja = (
        SystemTrayController(
            app,
            janela
        )
    )

    estado_aplicacao[
        "tray"
    ] = controlador_bandeja


def mostrar_interface():
    tray_splash = estado_aplicacao.get(
        "tray_splash"
    )

    if tray_splash is not None:
        tray_splash.hide()

    ativar_tray_principal()

    janela = estado_aplicacao.get(
        "janela"
    )

    if janela is None:
        return

    janela.show()
    janela.raise_()
    janela.activateWindow()


# =========================================================
# INICIALIZAÇÃO
# =========================================================

def iniciar_com_splash():
    splash = SplashWindow()

    estado_aplicacao[
        "splash"
    ] = splash

    tray_splash = criar_tray_splash()

    estado_aplicacao[
        "tray_splash"
    ] = tray_splash

    splash.solicitar_minimizar.connect(
        ocultar_splash_na_bandeja
    )

    splash.solicitar_fechar.connect(
        encerrar_pelo_splash
    )

    splash.show()
    splash.raise_()

    app.processEvents()

    def etapa_configuracoes():
        splash.adicionar_etapa(
            "Configurações carregadas",
            18
        )

        QTimer.singleShot(
            220,
            etapa_componentes
        )

    def etapa_componentes():
        splash.adicionar_etapa(
            "Preparando componentes de rede",
            34
        )

        QTimer.singleShot(
            180,
            etapa_interface
        )

    def etapa_interface():
        construir_interface()

        splash.adicionar_etapa(
            "Interface principal inicializada",
            62
        )

        QTimer.singleShot(
            220,
            etapa_monitoramento
        )

    def etapa_monitoramento():
        splash.adicionar_etapa(
            "Monitor de Serviços preparado",
            76
        )

        QTimer.singleShot(
            200,
            etapa_incidentes
        )

    def etapa_incidentes():
        splash.adicionar_etapa(
            "Registro de Incidentes disponível",
            88
        )

        QTimer.singleShot(
            180,
            etapa_telemetria
        )

    def etapa_telemetria():
        splash.adicionar_etapa(
            "Telemetria carregada",
            96
        )

        QTimer.singleShot(
            220,
            finalizar
        )

    def finalizar():
        splash.concluir(
            mostrar_interface
        )

    QTimer.singleShot(
        120,
        etapa_configuracoes
    )


def iniciar_sem_splash():
    construir_interface()
    mostrar_interface()


if configuracoes_iniciais.get(
    "exibir_tela_inicializacao",
    True
):
    QTimer.singleShot(
        0,
        iniciar_com_splash
    )

else:
    QTimer.singleShot(
        0,
        iniciar_sem_splash
    )


codigo_saida = app.exec()


logger.info(
    "Qt finalizado com código %s.",
    codigo_saida
)


sys.exit(
    codigo_saida
)
