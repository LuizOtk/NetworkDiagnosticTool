from collections import deque

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QFontDatabase
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from services.logger import ARQUIVO_APP, ARQUIVO_ERROS, DIRETORIO_LOGS


class LogWindow(QDialog):
    MAXIMO_LINHAS = 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logs do Sistema")
        self.setObjectName("janelaLogs")
        self.resize(900, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        titulo = QLabel("Logs do Sistema")
        titulo.setObjectName("tituloLogs")
        layout.addWidget(titulo)

        self.abas = QTabWidget()
        self.texto_aplicacao = self._criar_visualizador()
        self.texto_erros = self._criar_visualizador()
        self.abas.addTab(self._criar_aba(self.texto_aplicacao), "Aplicação")
        self.abas.addTab(self._criar_aba(self.texto_erros), "Erros")
        layout.addWidget(self.abas, 1)

        linha_botoes = QHBoxLayout()
        linha_botoes.addStretch()

        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.setObjectName("botaoAtualizarLogs")
        botao_atualizar.clicked.connect(self.atualizar)
        linha_botoes.addWidget(botao_atualizar)

        botao_abrir_pasta = QPushButton("Abrir pasta de logs")
        botao_abrir_pasta.clicked.connect(self.abrir_pasta_logs)
        linha_botoes.addWidget(botao_abrir_pasta)
        layout.addLayout(linha_botoes)

        self.atualizar()

    @staticmethod
    def _criar_visualizador():
        visualizador = QPlainTextEdit()
        visualizador.setObjectName("visualizadorLogs")
        visualizador.setReadOnly(True)
        visualizador.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        visualizador.setFont(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        )
        return visualizador

    @staticmethod
    def _criar_aba(visualizador):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(visualizador)
        return aba

    @classmethod
    def _ler_ultimas_linhas(cls, caminho):
        if not caminho.exists():
            return "Nenhum registro encontrado."

        try:
            with caminho.open("r", encoding="utf-8", errors="replace") as arquivo:
                linhas = deque(arquivo, maxlen=cls.MAXIMO_LINHAS)
        except OSError as erro:
            return f"Não foi possível ler o arquivo:\n{erro}"

        conteudo = "".join(linhas).rstrip()
        return conteudo or "Nenhum registro encontrado."

    def atualizar(self):
        self._atualizar_visualizador(self.texto_aplicacao, ARQUIVO_APP)
        self._atualizar_visualizador(self.texto_erros, ARQUIVO_ERROS)

    def _atualizar_visualizador(self, visualizador, caminho):
        visualizador.setPlainText(self._ler_ultimas_linhas(caminho))
        barra = visualizador.verticalScrollBar()
        barra.setValue(barra.maximum())

    def abrir_pasta_logs(self):
        try:
            DIRETORIO_LOGS.mkdir(parents=True, exist_ok=True)
        except OSError as erro:
            QMessageBox.warning(
                self,
                "Logs",
                f"Não foi possível preparar a pasta de logs:\n{erro}",
            )
            return

        if not QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(DIRETORIO_LOGS.resolve()))
        ):
            QMessageBox.warning(
                self,
                "Logs",
                "Não foi possível abrir a pasta de logs.",
            )
