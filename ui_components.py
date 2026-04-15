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


class ZoomTableDialog(QDialog):
    """Full-screen zoomable dialog for viewing table data."""

    DIALOG_STYLE = """
        QDialog {
            background: #0b1f2b;
        }
        QTableWidget {
            background: rgba(12, 30, 42, 0.95);
            alternate-background-color: rgba(20, 45, 60, 0.90);
            border: 1px solid rgba(140, 235, 220, 0.15);
            border-radius: 14px;
            color: #eefcfc;
            padding: 4px;
            selection-background-color: rgba(40, 200, 170, 0.30);
            gridline-color: rgba(140, 235, 220, 0.12);
            outline: 0;
        }
        QTableWidget::item {
            padding: 8px 14px;
            border-bottom: 1px solid rgba(140, 235, 220, 0.08);
        }
        QTableWidget::item:selected {
            background: rgba(26, 160, 183, 0.30);
            color: #ffffff;
        }
        QTableWidget::item:hover {
            background: rgba(40, 120, 150, 0.22);
        }
        QHeaderView {
            background: transparent;
        }
        QHeaderView::section {
            background: rgba(10, 32, 46, 0.96);
            color: #8cecdc;
            border: none;
            border-bottom: 2px solid rgba(140, 235, 220, 0.22);
            border-right: 1px solid rgba(140, 235, 220, 0.06);
            padding: 12px 16px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        QHeaderView::section:last {
            border-right: none;
        }
        QLabel {
            color: #eefcfc;
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }
        QLabel#dialogTitle {
            font-size: 20px;
            font-weight: 700;
            color: #f3ffff;
        }
        QLabel#zoomLabel {
            font-size: 13px;
            color: rgba(230, 250, 250, 0.75);
        }
        QPushButton {
            border: none;
            border-radius: 12px;
            padding: 10px 18px;
            font-size: 13px;
            font-weight: 600;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            color: #efffff;
            background: rgba(18, 42, 55, 0.82);
            border: 1px solid rgba(140, 235, 220, 0.08);
        }
        QPushButton:hover {
            background: rgba(29, 67, 84, 0.92);
        }
        QPushButton#closeBtn {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #0ea5ff,
                stop: 1 #18cc90
            );
            color: white;
        }
        QPushButton#closeBtn:hover {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #2ab6ff,
                stop: 1 #36dba1
            );
        }
        QScrollBar:vertical {
            background: rgba(14, 30, 40, 0.5);
            width: 8px;
            border-radius: 4px;
            margin: 2px;
        }
        QScrollBar::handle:vertical {
            background: rgba(140, 235, 220, 0.18);
            border-radius: 4px;
            min-height: 28px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(140, 235, 220, 0.32);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """

    def __init__(self, source_table: QTableWidget, dialog_title: str = "Table View", parent=None):
        super().__init__(parent)
        self.setWindowTitle(dialog_title)
        self.resize(900, 650)
        self.base_font_size = 14
        self.current_font_size = self.base_font_size
        self.setStyleSheet(self.DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header row
        header_row = QHBoxLayout()
        title_label = QLabel(dialog_title)
        title_label.setObjectName("dialogTitle")
        header_row.addWidget(title_label)
        header_row.addStretch()

        self.zoom_label = QLabel(f"{self.current_font_size}px")
        self.zoom_label.setObjectName("zoomLabel")

        zoom_out_btn = QPushButton("A−")
        zoom_out_btn.setFixedSize(40, 40)
        zoom_out_btn.clicked.connect(self.zoom_out)

        zoom_in_btn = QPushButton("A+")
        zoom_in_btn.setFixedSize(40, 40)
        zoom_in_btn.clicked.connect(self.zoom_in)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_zoom)

        header_row.addWidget(zoom_out_btn)
        header_row.addWidget(self.zoom_label)
        header_row.addWidget(zoom_in_btn)
        header_row.addWidget(reset_btn)
        layout.addLayout(header_row)

        # Build the zoomed table
        col_count = source_table.columnCount()
        row_count = source_table.rowCount()

        self.table = QTableWidget(row_count, col_count)
        headers = []
        for c in range(col_count):
            header_item = source_table.horizontalHeaderItem(c)
            headers.append(header_item.text() if header_item else f"Col {c + 1}")
        self.table.setHorizontalHeaderLabels(headers)

        for r in range(row_count):
            for c in range(col_count):
                src_item = source_table.item(r, c)
                text = src_item.text() if src_item else ""
                self.table.setItem(r, c, QTableWidgetItem(text))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setMinimumHeight(44)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setDefaultSectionSize(42)
        layout.addWidget(self.table)

        # Bottom buttons
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(self.accept)
        bottom_row.addWidget(close_btn)
        layout.addLayout(bottom_row)

        self._apply_font_size()

    def _apply_font_size(self):
        font = self.table.font()
        font.setPixelSize(self.current_font_size)
        self.table.setFont(font)

        header_font = self.table.horizontalHeader().font()
        header_font.setPixelSize(max(12, self.current_font_size - 1))
        header_font.setBold(True)
        self.table.horizontalHeader().setFont(header_font)

        row_height = self.current_font_size + 24
        self.table.verticalHeader().setDefaultSectionSize(row_height)
        self.table.horizontalHeader().setMinimumHeight(row_height + 4)

        self.zoom_label.setText(f"{self.current_font_size}px")

    def zoom_in(self):
        if self.current_font_size < 32:
            self.current_font_size += 2
            self._apply_font_size()

    def zoom_out(self):
        if self.current_font_size > 10:
            self.current_font_size -= 2
            self._apply_font_size()

    def reset_zoom(self):
        self.current_font_size = self.base_font_size
        self._apply_font_size()

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

