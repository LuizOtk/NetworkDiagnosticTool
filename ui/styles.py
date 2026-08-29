DARK_STYLE = """
/* =====================================================
   BASE
   ===================================================== */

QMainWindow,
QDialog,
QWidget {
    background-color: #0b1118;
    color: #e5edf5;
    font-family: "Segoe UI";
    font-size: 10pt;
}

QMainWindow {
    background-color: #0b1118;
}

QLabel {
    background: transparent;
}

QToolTip {
    background-color: #162330;
    color: #eef6fc;
    border: 1px solid #365269;
    padding: 6px 8px;
    border-radius: 5px;
}


/* =====================================================
   CAMPOS DE ENTRADA
   ===================================================== */

QLineEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    background-color: #101923;
    border: 1px solid #2b3c4d;
    border-radius: 7px;
    padding: 7px 10px;
    color: #ffffff;
    min-height: 22px;
}

QLineEdit:hover,
QComboBox:hover,
QSpinBox:hover,
QDoubleSpinBox:hover {
    border-color: #40586d;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 1px solid #2388ff;
    background-color: #12202c;
}

QLineEdit:disabled,
QComboBox:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled {
    background-color: #0e151d;
    border-color: #202b35;
    color: #65707c;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #152330;
    color: #eef5fb;
    border: 1px solid #365269;
    selection-background-color: #1e5f91;
    selection-color: #ffffff;
    outline: none;
}


/* =====================================================
   BOTÕES
   ===================================================== */

QPushButton {
    background-color: #172331;
    border: 1px solid #304153;
    border-radius: 7px;
    padding: 8px 14px;
    color: #e5edf5;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #213247;
    border-color: #40566c;
}

QPushButton:pressed {
    background-color: #29405a;
}

QPushButton:focus {
    border-color: #3b8eea;
}

QPushButton:disabled {
    background-color: #111820;
    border-color: #202b35;
    color: #65707c;
}

/* Usado pelos seletores Tabela | Telemetria */
QPushButton:checked {
    background-color: #173a58;
    border: 1px solid #2f81d7;
    color: #a9dcff;
    font-weight: 600;
}

QPushButton:checked:hover {
    background-color: #1c4669;
}

QPushButton#botaoPrincipal,
QPushButton#botaoSalvarConfiguracoes {
    background-color: #1477dc;
    border: 1px solid #2b91ff;
    color: #ffffff;
    font-weight: 700;
}

QPushButton#botaoPrincipal:hover,
QPushButton#botaoSalvarConfiguracoes:hover {
    background-color: #2388ff;
}

QPushButton#botaoMonitorIcmp,
QPushButton#botaoMonitorRota {
    background-color: #173449;
    border: 1px solid #285a79;
    color: #8fd3ff;
    font-weight: 600;
}

QPushButton#botaoMonitorIcmp:hover,
QPushButton#botaoMonitorRota:hover {
    background-color: #204963;
    border-color: #3b7192;
}

QPushButton#botaoIncidentes,
QPushButton#botaoLogs {
    background-color: #172b3d;
    border: 1px solid #365269;
    color: #dff2ff;
    font-weight: 600;
}

QPushButton#botaoIncidentes:hover,
QPushButton#botaoLogs:hover {
    background-color: #203f57;
    border-color: #4d7593;
}

QPushButton#botaoDownDetector {
    min-width: 150px;
    font-weight: 600;
}

QPushButton#botaoDownDetector[estado="vazio"] {
    background-color: #172331;
    border-color: #304153;
}

QPushButton#botaoDownDetector[estado="ok"] {
    background-color: #173c2d;
    border: 1px solid #2c7655;
    color: #71e3aa;
}

QPushButton#botaoDownDetector[estado="alerta"] {
    background-color: #493b17;
    border: 1px solid #8b7027;
    color: #ffcc66;
}

QPushButton#botaoDownDetector[estado="critico"] {
    background-color: #4a2024;
    border: 1px solid #8d3840;
    color: #ff8088;
}

QPushButton#botaoDownDetector[estado="reconhecido"] {
    background-color: #1b2732;
    border: 1px solid #344757;
    color: #8fa2b5;
}

QPushButton#botaoAbrirWeb {
    background-color: #173c2d;
    border: 1px solid #2c7655;
    color: #71e3aa;
    padding: 5px 11px;
    font-weight: 600;
}

QPushButton#botaoAbrirWeb:hover {
    background-color: #1d4b37;
    border-color: #3a946c;
}

QPushButton#botaoReconhecer {
    background-color: #493b17;
    border: 1px solid #8b7027;
    color: #ffcc66;
    padding: 5px 10px;
    font-weight: 600;
}

QPushButton#botaoReconhecer:hover {
    background-color: #5b491c;
}

QPushButton#botaoTestarNavegador,
QPushButton#botaoAtualizarLogs {
    background-color: #17354a;
    border: 1px solid #2d6b94;
    color: #dff2ff;
    font-weight: 600;
}

QPushButton#botaoTestarNavegador:hover,
QPushButton#botaoAtualizarLogs:hover {
    background-color: #1d4965;
    border-color: #3f8fc2;
}

QPushButton#botaoLimparHistorico {
    background-color: #3b2024;
    border: 1px solid #74353c;
    color: #ffb1b7;
    font-weight: 600;
}

QPushButton#botaoLimparHistorico:hover {
    background-color: #51272d;
    border-color: #98434c;
}


/* =====================================================
   CAMPO DE IP PRINCIPAL
   ===================================================== */

QFrame#campoIpContainer {
    background-color: #101923;
    border: 1px solid #263646;
    border-radius: 8px;
}

QLineEdit#campoIpInterno {
    background-color: transparent;
    border: none;
    padding: 0px 5px;
    color: #ffffff;
    font-size: 11pt;
    min-height: 0px;
}

QLineEdit#campoIpInterno:focus {
    border: none;
    background-color: transparent;
}

QPushButton#botaoExecutarIp {
    background-color: #1477dc;
    border: 1px solid #2b91ff;
    border-radius: 6px;
    padding: 0px;
    color: #ffffff;
    font-size: 15pt;
    font-weight: 700;
}

QPushButton#botaoExecutarIp:hover {
    background-color: #2388ff;
}

QPushButton#botaoExecutarIp:pressed {
    background-color: #1167be;
}

QPushButton#botaoExecutarIp:disabled {
    background-color: #172331;
    border: 1px solid #263646;
    color: #65707c;
}


/* =====================================================
   GROUP BOX / PAINÉIS
   ===================================================== */

QGroupBox {
    background-color: #0f1822;
    border: 1px solid #253545;
    border-radius: 9px;
    margin-top: 14px;
    padding-top: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #f0f5fa;
}

QFrame#cardPing {
    background-color: #14202c;
    border: 1px solid #293b4d;
    border-radius: 8px;
}

QFrame#painelStatusPing {
    background-color: #0c141d;
    border: 1px solid #233342;
    border-radius: 8px;
}

QFrame#painelConfiguracaoInfo {
    background-color: #14212c;
    border: 1px solid #30485a;
    border-radius: 8px;
}


/* =====================================================
   TEXTOS / CARDS
   ===================================================== */

QLabel#cardTitulo {
    color: #91a2b3;
    font-size: 9pt;
}

QLabel#cardValor {
    color: #f5f8fb;
    font-size: 16pt;
    font-weight: 700;
}

QLabel#pingStatus {
    font-size: 15pt;
    font-weight: 700;
}

QLabel#pingDetalhes {
    color: #aebdca;
    padding-top: 6px;
}

QLabel#statusBar {
    color: #8fa2b5;
    padding: 4px;
}

QLabel#versaoApp {
    color: #647688;
    padding: 4px;
}

QLabel#tituloDownDetector {
    font-size: 14pt;
    font-weight: 700;
    color: #f5f9fd;
}

QLabel#textoSecundario {
    color: #8294a5;
}

QLabel#tituloConfiguracaoInfo {
    color: #ffffff;
    font-size: 11pt;
    font-weight: 700;
}

QLabel#subtituloConfiguracaoInfo {
    color: #6eb6ff;
    font-size: 10pt;
    font-weight: 600;
}


/* =====================================================
   TABELAS
   ===================================================== */

QTableWidget {
    background-color: #0c141d;
    alternate-background-color: #0f1923;
    border: 1px solid #263847;
    border-radius: 7px;
    gridline-color: #20303e;
    color: #dce6ee;
    selection-background-color: #1c4f7d;
    selection-color: #ffffff;
    outline: none;
}

QTableWidget::item {
    padding: 7px 8px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #1e5f91;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #162633;
    color: #d6e1ea;
    border: none;
    border-right: 1px solid #2b3d4d;
    border-bottom: 1px solid #2b3d4d;
    padding: 8px 9px;
    font-weight: 600;
}

QHeaderView::section:hover {
    background-color: #1b2f3f;
}

QTableCornerButton::section {
    background-color: #162633;
    border: none;
    border-right: 1px solid #2b3d4d;
    border-bottom: 1px solid #2b3d4d;
}


/* =====================================================
   CHECKBOX
   ===================================================== */

QCheckBox {
    color: #e6eef5;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
}

QCheckBox::indicator:unchecked {
    background-color: #13202b;
    border: 1px solid #4c6578;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #2388ff;
    border: 1px solid #2388ff;
    border-radius: 3px;
}

QCheckBox:disabled {
    color: #65707c;
}


/* =====================================================
   NAVEGAÇÃO / ABAS / LISTAS
   ===================================================== */

QTabWidget::pane {
    border: 1px solid #253545;
    border-radius: 6px;
    background-color: #0f1822;
}

QTabBar::tab {
    background-color: #111b25;
    border: 1px solid #253545;
    padding: 8px 16px;
    color: #91a2b3;
}

QTabBar::tab:hover {
    background-color: #172735;
    color: #dbe8f2;
}

QTabBar::tab:selected {
    background-color: #172b3d;
    color: #ffffff;
    border-bottom: 2px solid #2388ff;
}

QListWidget#menuConfiguracoes {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#menuConfiguracoes::item {
    padding: 11px 13px;
    margin: 2px 0px;
    border-radius: 6px;
    color: #aebdca;
}

QListWidget#menuConfiguracoes::item:hover {
    background-color: #152a3a;
    color: #e7f3fc;
}

QListWidget#menuConfiguracoes::item:selected {
    background-color: #17324a;
    color: #8ecbff;
    border-left: 3px solid #2f81f7;
    font-weight: 600;
}

QStackedWidget {
    background: transparent;
    border: none;
}


/* =====================================================
   MENUS
   ===================================================== */

QMenu {
    background-color: #121d27;
    color: #e5edf5;
    border: 1px solid #304153;
    border-radius: 6px;
    padding: 5px;
}

QMenu::item {
    padding: 7px 28px 7px 10px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #1e5f91;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #2a3a49;
    margin: 5px 8px;
}


/* =====================================================
   SPLITTER
   ===================================================== */

QSplitter::handle:vertical {
    background-color: #15222e;
    height: 6px;
    margin: 2px 0px;
    border-radius: 3px;
}

QSplitter::handle:vertical:hover {
    background-color: #2388ff;
}

QSplitter::handle:horizontal {
    background-color: #15222e;
    width: 6px;
    margin: 0px 2px;
    border-radius: 3px;
}

QSplitter::handle:horizontal:hover {
    background-color: #2388ff;
}


/* =====================================================
   SCROLLBARS
   ===================================================== */

QScrollBar:vertical {
    background: #0c141d;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #35485a;
    min-height: 30px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #465e73;
}

QScrollBar::horizontal {
    background: #0c141d;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #35485a;
    min-width: 30px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background: #465e73;
}

QScrollBar::add-line,
QScrollBar::sub-line {
    width: 0px;
    height: 0px;
}

QScrollBar::add-page,
QScrollBar::sub-page {
    background: transparent;
}


/* =====================================================
   JANELA DE LOGS
   ===================================================== */

QDialog#janelaLogs {
    background-color: #0f1822;
}

QLabel#tituloLogs {
    color: #ffffff;
    font-size: 14pt;
    font-weight: 700;
}

QPlainTextEdit#visualizadorLogs {
    background-color: #091119;
    color: #dce6ee;
    border: 1px solid #2f4658;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #1e5f91;
    selection-color: #ffffff;
}


/* =====================================================
   DIÁLOGOS
   ===================================================== */

QDialog {
    background-color: #0f1822;
}

QDialog QLabel {
    color: #dce6f0;
}

QDialog QPushButton {
    min-height: 20px;
}

QDialog QTableWidget {
    background-color: #0d1720;
    alternate-background-color: #111f2b;
    color: #e8f0f7;
    border: 1px solid #2f4658;
    border-radius: 6px;
    gridline-color: #263b4b;
}

QDialog QHeaderView::section {
    background-color: #1a2b39;
    color: #edf5fb;
    border: none;
    border-right: 1px solid #304858;
    border-bottom: 1px solid #304858;
    padding: 8px;
}

/* =====================================================
   NAVEGAÇÃO PRINCIPAL / DASHBOARD
   ===================================================== */

QFrame#topNavigation {
    background-color: #0f1822;
    border: 1px solid #253545;
    border-radius: 9px;
}

QLabel#brandNdt {
    color: #2388ff;
    font-size: 16pt;
    font-weight: 800;
    padding: 0px 6px;
}

QPushButton#navButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    color: #91a2b3;
    font-weight: 600;
    padding: 7px 12px;
    min-height: 18px;
}

QPushButton#navButton:hover {
    background-color: #152735;
    border-color: #253d50;
    color: #dce9f3;
}

QPushButton#navButton:checked {
    background-color: #17324a;
    border: 1px solid #2c5f87;
    color: #8fd3ff;
}

QPushButton#navSettingsButton {
    background-color: #152330;
    border: 1px solid #304153;
    border-radius: 7px;
    color: #aebdca;
    font-size: 13pt;
    font-weight: 700;
    padding: 4px 10px;
    min-width: 34px;
}

QPushButton#navSettingsButton:hover {
    background-color: #20384b;
    border-color: #4d7593;
    color: #ffffff;
}

QLabel#pageTitle {
    color: #f5f9fd;
    font-size: 17pt;
    font-weight: 800;
}

QLabel#pageSubtitle {
    color: #8294a5;
    font-size: 9pt;
}

QLabel#dashboardDateTime {
    color: #6f8395;
    font-size: 9pt;
    padding-top: 4px;
}

QFrame#dashboardMetricCard {
    background-color: #111c26;
    border: 1px solid #283a4a;
    border-radius: 9px;
}

QFrame#dashboardMetricCard[estado="normal"] {
    border-color: #2c7655;
}

QFrame#dashboardMetricCard[estado="alerta"] {
    border-color: #8b7027;
}

QFrame#dashboardMetricCard[estado="critico"] {
    border-color: #8d3840;
}

QLabel#dashboardCardTitle {
    color: #91a2b3;
    font-size: 9pt;
    font-weight: 600;
}

QLabel#dashboardCardValue {
    color: #f5f8fb;
    font-size: 18pt;
    font-weight: 800;
}

QLabel#dashboardCardSub {
    color: #8294a5;
    font-size: 8pt;
}

QFrame#dashboardSection,
QFrame#monitorFeatureCard,
QFrame#reportCard {
    background-color: #0f1822;
    border: 1px solid #253545;
    border-radius: 9px;
}

QLabel#dashboardSectionTitle {
    color: #eef5fb;
    font-size: 11pt;
    font-weight: 700;
}

QFrame#monitorStatusRow {
    background-color: #111c26;
    border: 1px solid #263847;
    border-radius: 7px;
}

QFrame#monitorStatusRow[estado="normal"] {
    border-color: #2c7655;
}

QFrame#monitorStatusRow[estado="alerta"] {
    border-color: #8b7027;
}

QFrame#monitorStatusRow[estado="critico"] {
    border-color: #8d3840;
}

QLabel#monitorStatusDot {
    color: #667786;
    font-size: 11pt;
    font-weight: 800;
}

QLabel#monitorStatusDot[estado="normal"] {
    color: #39d98a;
}

QLabel#monitorStatusDot[estado="alerta"] {
    color: #ffcc66;
}

QLabel#monitorStatusDot[estado="critico"] {
    color: #ff6b74;
}

QLabel#monitorStatusTitle {
    color: #e8f0f7;
    font-weight: 700;
}

QLabel#featureStatus {
    color: #8294a5;
    font-size: 9pt;
    font-weight: 700;
}

QLabel#featureStatus[estado="normal"] {
    color: #71e3aa;
}

QLabel#featureStatus[estado="alerta"] {
    color: #ffcc66;
}

QLabel#featureStatus[estado="critico"] {
    color: #ff8088;
}

QLabel#monitorFeatureSummary {
    color: #dce6ee;
    font-size: 11pt;
    font-weight: 600;
}

QPushButton#monitorFeatureAction {
    background-color: #173449;
    border: 1px solid #285a79;
    color: #8fd3ff;
    font-weight: 600;
}

QPushButton#monitorFeatureAction:hover {
    background-color: #204963;
    border-color: #3b7192;
}

QPushButton#dashboardPrimaryAction {
    background-color: #1477dc;
    border: 1px solid #2b91ff;
    color: #ffffff;
    font-weight: 700;
}

QPushButton#dashboardPrimaryAction:hover {
    background-color: #2388ff;
}


/* =====================================================
   DASHBOARD VISUAL V1.2
   ===================================================== */

QFrame#topNavigation {
    background-color: #08131f;
    border: 1px solid #1d3144;
    border-radius: 8px;
}

QLabel#brandNdt {
    color: #f4f8fc;
    font-size: 19pt;
    font-weight: 800;
    padding: 0px 4px 0px 0px;
}

QPushButton#navButton {
    background-color: transparent;
    border: none;
    border-radius: 5px;
    color: #a8b7c5;
    font-size: 10pt;
    font-weight: 600;
    padding: 8px 13px;
    min-height: 22px;
}

QPushButton#navButton:hover {
    background-color: #10263a;
    color: #eaf3fa;
}

QPushButton#navButton:checked {
    background-color: #102b46;
    border-bottom: 2px solid #2388ff;
    color: #ffffff;
}

QPushButton#navSettingsButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 7px;
    padding: 5px;
    min-width: 32px;
    max-width: 32px;
}

QPushButton#navSettingsButton:hover {
    background-color: #142b3d;
    border-color: #2b4f69;
}

QLabel#pageTitle {
    color: #f4f8fc;
    font-size: 17pt;
    font-weight: 800;
}

QLabel#dashboardDateTime {
    color: #9fb0bf;
    font-size: 10pt;
}

QFrame#dashboardMetricCard {
    background-color: #0d1a27;
    border: 1px solid #294258;
    border-radius: 10px;
}

QFrame#dashboardMetricCard[estado="normal"] {
    border-color: #2f7d4f;
}

QFrame#dashboardMetricCard[estado="alerta"] {
    border-color: #294258;
}

QFrame#dashboardMetricCard[estado="critico"] {
    border-color: #5f3340;
}

QLabel#dashboardCardTitle {
    color: #c2cfda;
    font-size: 10pt;
    font-weight: 600;
}

QLabel#dashboardCardValue {
    color: #f7fbff;
    font-size: 18pt;
    font-weight: 800;
}

QLabel#dashboardCardSub {
    color: #8ea0af;
    font-size: 9pt;
}

QFrame#dashboardSection {
    background-color: #0b1825;
    border: 1px solid #28435b;
    border-radius: 10px;
}

QLabel#dashboardSectionTitle {
    color: #dce7f0;
    font-size: 11pt;
    font-weight: 750;
}

QFrame#dashboardServiceRow,
QFrame#dashboardAlertRow,
QFrame#dashboardActivityRow {
    background-color: #0c1926;
    border: 1px solid #1b3042;
    border-radius: 5px;
}

QFrame#dashboardServiceRow[estado="alerta"],
QFrame#dashboardAlertRow[estado="alerta"] {
    border-color: #1e3448;
}

QFrame#dashboardServiceRow[estado="critico"],
QFrame#dashboardAlertRow[estado="critico"] {
    border-color: #263b4d;
}

QLabel#dashboardServiceName,
QLabel#dashboardActivityOrigin {
    color: #eef5fb;
    font-size: 10pt;
    font-weight: 600;
}

QLabel#dashboardServiceDot {
    color: #6f8395;
    font-size: 10pt;
}

QLabel#dashboardServiceDot[estado="normal"] {
    color: #56d364;
}

QLabel#dashboardServiceDot[estado="alerta"] {
    color: #f0a928;
}

QLabel#dashboardServiceDot[estado="critico"] {
    color: #ff5c5c;
}

QLabel#dashboardServiceResult {
    color: #9aabba;
    font-size: 10pt;
    font-weight: 700;
}

QLabel#dashboardServiceResult[estado="normal"] {
    color: #dce6ee;
}

QLabel#dashboardServiceResult[estado="alerta"] {
    color: #f0a928;
}

QLabel#dashboardServiceResult[estado="critico"] {
    color: #ff7078;
}

QLabel#dashboardAlertText {
    color: #e9f0f6;
    font-size: 10pt;
    font-weight: 600;
}

QLabel#dashboardNoAlerts {
    color: #71e3aa;
    font-size: 10pt;
    font-weight: 700;
}

QLabel#dashboardEmptyState {
    color: #718394;
    font-size: 9pt;
    padding: 12px;
}

QPushButton#dashboardOutlineAction {
    background-color: transparent;
    border: 1px solid #2f81d7;
    border-radius: 7px;
    color: #71b7ff;
    font-size: 10pt;
    font-weight: 600;
    padding: 8px 14px;
}

QPushButton#dashboardOutlineAction:hover {
    background-color: #102b46;
    border-color: #58a6ff;
    color: #a9d5ff;
}

QLabel#dashboardTimelineDot {
    color: #2f81f7;
    font-size: 12pt;
    min-width: 18px;
}

QLabel#dashboardActivityTime {
    color: #58a6ff;
    font-size: 10pt;
    font-weight: 700;
}

QLabel#dashboardActivityEvent {
    color: #b7c4cf;
    font-size: 10pt;
}

QLabel#dashboardActivityStatus {
    color: #8294a5;
    font-size: 9pt;
    font-weight: 700;
}

QLabel#dashboardActivityStatus[estado="normal"] {
    color: #71e35e;
}

QLabel#dashboardActivityStatus[estado="critico"] {
    color: #ff7078;
}

QPushButton#dashboardQuickAction {
    background-color: #0c1b2a;
    border: 1px solid #2b5e8a;
    border-radius: 9px;
    color: #f0f6fb;
    font-size: 10pt;
    font-weight: 650;
    padding: 8px 16px;
    text-align: left;
    min-height: 50px;
}

QPushButton#dashboardQuickAction:hover {
    background-color: #102a43;
    border-color: #3d8bd3;
}


/* =====================================================
   REFINO FINAL DO DASHBOARD
   ===================================================== */

QFrame#dashboardServiceRow {
    min-height: 30px;
    max-height: 38px;
}

QFrame#dashboardAlertRow {
    min-height: 32px;
    max-height: 42px;
}

QFrame#dashboardActivityRow {
    min-height: 28px;
    max-height: 34px;
}

QLabel#dashboardServiceName {
    font-size: 9pt;
}

QLabel#dashboardServiceResult {
    font-size: 9pt;
}

QLabel#dashboardAlertText {
    font-size: 9pt;
}

QLabel#dashboardActivityTime,
QLabel#dashboardActivityOrigin,
QLabel#dashboardActivityEvent {
    font-size: 9pt;
}

QPushButton#dashboardQuickAction {
    min-height: 46px;
}


/* =====================================================
   SCROLL INTERNO DO DASHBOARD
   ===================================================== */

QScrollArea#dashboardScrollArea {
    background-color: transparent;
    border: none;
}

QScrollArea#dashboardScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QWidget#dashboardScrollContent {
    background-color: transparent;
}

QScrollArea#dashboardScrollArea QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 2px 0px;
}

QScrollArea#dashboardScrollArea QScrollBar::handle:vertical {
    background-color: #31485c;
    min-height: 28px;
    border-radius: 4px;
}

QScrollArea#dashboardScrollArea QScrollBar::handle:vertical:hover {
    background-color: #49677f;
}

QScrollArea#dashboardScrollArea QScrollBar::add-line:vertical,
QScrollArea#dashboardScrollArea QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollArea#dashboardScrollArea QScrollBar::add-page:vertical,
QScrollArea#dashboardScrollArea QScrollBar::sub-page:vertical {
    background-color: transparent;
}

"""
