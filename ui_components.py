from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QAction, QColor, QPixmap, QImage
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

class ImageStageCard(QFrame):
    def __init__(self, title: str, subtitle: str):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("cardSubtitle")
        subtitle_label.setWordWrap(True)

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)

        self.image_label = QLabel("Preview will appear here")
        self.image_label.setObjectName("imageViewport")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(180)
        layout.addWidget(self.image_label)

    def set_pixmap(self, pixmap: QPixmap):
        if pixmap.isNull():
            return
        scaled = pixmap.scaled(
            self.image_label.size() - QSize(12, 12),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        current = self.image_label.pixmap()
        if current and not current.isNull():
            self.set_pixmap(current)


class InfoCard(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setObjectName("sideCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        self.body_layout = layout


class TitleBar(QFrame):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.drag_pos = None
        self.setObjectName("topBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 14, 16, 14)
        layout.setSpacing(14)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        app_title = QLabel("Smart Pantry Assistant")
        app_title.setObjectName("appTitle")
        app_subtitle = QLabel(
            "Interactive image-processing pipeline for food detection and recipe recommendation"
        )
        app_subtitle.setObjectName("appSubtitle")
        title_col.addWidget(app_title)
        title_col.addWidget(app_subtitle)

        layout.addLayout(title_col)
        layout.addStretch()

        self.min_btn = QToolButton()
        self.min_btn.setText("–")
        self.min_btn.setObjectName("windowButton")
        self.min_btn.clicked.connect(self.parent_window.showMinimized)

        self.max_btn = QToolButton()
        self.max_btn.setText("□")
        self.max_btn.setObjectName("windowButton")
        self.max_btn.clicked.connect(self.toggle_max_restore)

        self.close_btn = QToolButton()
        self.close_btn.setText("✕")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.parent_window.close)

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

    def toggle_max_restore(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.max_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self.max_btn.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None and not self.parent_window.isMaximized():
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.parent_window.move(self.parent_window.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_max_restore()
            event.accept()
