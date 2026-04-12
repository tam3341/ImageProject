MODERN_STYLE = """
QWidget {
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
    color: #eef9f9;
}

QWidget#root {
    background: transparent;
}

QFrame#windowShell {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #0b1f2b,
        stop: 0.32 #0f2d3a,
        stop: 0.66 #113943,
        stop: 1 #144b4b
    );
    border: none;
    border-radius: 0px;
}

QFrame#topBar, QFrame#panel, QFrame#card, QFrame#sideCard {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(22, 48, 62, 0.85),
        stop: 1 rgba(16, 38, 50, 0.75)
    );
    border: 1px solid rgba(140, 235, 220, 0.05);
    border-radius: 20px;
}

QLabel#appTitle {
    font-size: 24px;
    font-weight: 700;
    color: #f5ffff;
    letter-spacing: 0.2px;
}

QLabel#appSubtitle {
    color: rgba(226, 246, 247, 0.68);
    font-size: 12px;
}

QLabel#panelTitle {
    font-size: 18px;
    font-weight: 650;
    color: #f3ffff;
}

QLabel#sectionTitle {
    font-size: 15px;
    font-weight: 650;
    color: #dffbfb;
}

QLabel#cardTitle {
    font-size: 16px;
    font-weight: 650;
    color: #f3ffff;
}

QLabel#cardSubtitle, QLabel#mutedText {
    color: rgba(230, 250, 250, 0.75);
    line-height: 1.35em;
}

QLabel#pill {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #18a8ff,
        stop: 1 #22d59a
    );
    color: white;
    padding: 8px 14px;
    border-radius: 14px;
    font-weight: 700;
}

QLabel#imageViewport {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(28, 60, 72, 0.88),
        stop: 1 rgba(24, 68, 74, 0.86)
    );
    border: 1px solid rgba(150, 240, 220, 0.08);
    border-radius: 18px;
    color: rgba(230, 250, 250, 0.50);
    font-size: 14px;
}

QPushButton, QToolButton {
    border: none;
    border-radius: 14px;
    padding: 11px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#primaryButton {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #0ea5ff,
        stop: 1 #18cc90
    );
    color: white;
}

QPushButton#primaryButton:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #2ab6ff,
        stop: 1 #36dba1
    );
}

QPushButton#secondaryButton {
    background: rgba(18, 45, 61, 0.92);
    color: #efffff;
    border: 1px solid rgba(100, 206, 232, 0.26);
}

QPushButton#secondaryButton:hover,
QPushButton#ghostButton:hover,
QToolButton#windowButton:hover {
    background: rgba(29, 67, 84, 0.92);
}

QPushButton#ghostButton {
    background: rgba(18, 42, 55, 0.82);
    color: #e6fbfb;
    border: 1px solid rgba(140, 235, 220, 0.08);
}

QToolButton#windowButton, QToolButton#closeButton {
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    padding: 0;
    border-radius: 17px;
    background: rgba(18, 39, 51, 0.88);
    color: #e9f6f7;
    font-size: 14px;
    font-weight: 700;
}

QToolButton#closeButton:hover {
    background: rgba(220, 68, 88, 0.95);
    color: white;
}

QTextEdit, QListWidget, QTableWidget {
    background: rgba(16, 36, 48, 0.78);
    border: 1px solid rgba(140, 235, 220, 0.08);
    border-radius: 16px;
    color: #eefcfc;
    padding: 8px;
    selection-background-color: rgba(40, 200, 170, 0.25);
    gridline-color: rgba(140, 235, 220, 0.06);
}

QListWidget::item {
    padding: 8px 10px;
    margin: 2px 0;
    border-radius: 10px;
}

QListWidget::item:selected {
    background: rgba(26, 160, 183, 0.28);
    color: #f5ffff;
}

QHeaderView::section {
    background: rgba(15, 40, 52, 0.92);
    color: #dbffff;
    border: none;
    padding: 8px;
    font-weight: 600;
}

QProgressBar {
    background: rgba(14, 30, 40, 0.75);
    border: 1px solid rgba(140, 235, 220, 0.08);
    border-radius: 10px;
    height: 22px;
    text-align: center;
    color: white;
    font-weight: 700;
}

QProgressBar::chunk {
    border-radius: 9px;
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #10a9ff,
        stop: 1 #20d596
    );
}

QSplitter::handle {
    background: transparent;
}

QStatusBar {
    background: rgba(8, 19, 28, 0.82);
    color: rgba(233, 246, 247, 0.78);
    border-top: 1px solid rgba(120, 220, 210, 0.08);
    border-radius: 12px;
}
"""
