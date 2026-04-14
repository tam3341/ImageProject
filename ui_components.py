from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QAction, QColor, QPixmap, QImage, QWheelEvent
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
    QDialog,
    QScrollArea,
)
from matplotlib.pyplot import title

class ImageStageCard(QFrame):
    def __init__(self, title: str, subtitle: str):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(380)

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

        self.image_label = ClickableImageLabel()
        self.image_label.setText("Click to enlarge")
        self.image_label.dialog_title = title
        self.image_label.setObjectName("imageViewport")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(300)
        layout.addWidget(self.image_label)

    def set_pixmap(self, pixmap: QPixmap):
         if pixmap.isNull():
             return

         self.image_label.set_full_pixmap(pixmap)

         scaled = pixmap.scaled(
             self.image_label.size() - QSize(12, 12),
             Qt.KeepAspectRatio,
             Qt.SmoothTransformation,
       )
         self.image_label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.image_label.full_pixmap.isNull():
           self.set_pixmap(self.image_label.full_pixmap)



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

class ZoomImageDialog(QDialog):
    def __init__(self, pixmap: QPixmap, title: str = "Image Preview", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1100, 800)
        self.original_pixmap = pixmap
        self.scale_factor = 1.0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background: #102a36;
                border-radius: 12px;
                padding: 8px;
            }
        """)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)

        button_row = QHBoxLayout()
        button_row.addStretch()

        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_out_btn = QPushButton("Zoom Out")
        self.reset_btn = QPushButton("Reset")
        self.close_btn = QPushButton("Close")

        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_btn.clicked.connect(self.reset_zoom)
        self.close_btn.clicked.connect(self.accept)

        button_row.addWidget(self.zoom_in_btn)
        button_row.addWidget(self.zoom_out_btn)
        button_row.addWidget(self.reset_btn)
        button_row.addWidget(self.close_btn)

        layout.addWidget(self.scroll_area)
        layout.addLayout(button_row)

        self.update_image()

    def update_image(self):
        if self.original_pixmap.isNull():
            return

        scaled_size = self.original_pixmap.size() * self.scale_factor
        scaled = self.original_pixmap.scaled(
            scaled_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        self.image_label.resize(scaled.size())

    def zoom_in(self):
        self.scale_factor *= 1.2
        self.update_image()

    def zoom_out(self):
        self.scale_factor /= 1.2
        self.update_image()

    def reset_zoom(self):
        self.scale_factor = 1.0
        self.update_image()

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()


class ClickableImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.full_pixmap = QPixmap()
        self.dialog_title = "Image Preview"
        self.setCursor(Qt.PointingHandCursor)

    def set_full_pixmap(self, pixmap: QPixmap):
        self.full_pixmap = pixmap

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.full_pixmap.isNull():
            dialog = ZoomImageDialog(self.full_pixmap, self.dialog_title, self)
            dialog.exec()
        super().mousePressEvent(event)
