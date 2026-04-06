import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QAction, QColor, QPixmap
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


class SmartPantryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.original_pixmap = QPixmap()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self.setWindowTitle("Smart Pantry Assistant")
        self.resize(1580, 920)
        self.setMinimumSize(1360, 800)

        self._build_ui()
        self._apply_styles()
        self._apply_window_effects()
        self._add_demo_data()

    def _build_ui(self):
        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.window_shell = QFrame()
        self.window_shell.setObjectName("windowShell")
        shell_layout = QVBoxLayout(self.window_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(14)

        self.title_bar = TitleBar(self)
        shell_layout.addWidget(self.title_bar)

        central = QWidget()
        central.setObjectName("root")
        shell_layout.addWidget(central)

        outer_layout.addWidget(self.window_shell)
        self.setCentralWidget(outer)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(14)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        splitter.addWidget(self._build_left_sidebar())
        splitter.addWidget(self._build_pipeline_area())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([280, 920, 360])
        root_layout.addWidget(splitter)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready — build the interface first, then connect the pipeline.")

        open_action = QAction("Open Image", self)
        open_action.triggered.connect(self.open_image)
        self.addAction(open_action)

    def _build_left_sidebar(self) -> QWidget:
        container = QFrame()
        container.setObjectName("panel")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        title = QLabel("Controls")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.clicked.connect(self.open_image)

        self.run_input_btn = QPushButton("Run Input Check")
        self.run_processing_btn = QPushButton("Run Preprocessing")
        self.run_detection_btn = QPushButton("Run Detection")
        self.run_full_btn = QPushButton("Run Full Pipeline")
        self.reset_btn = QPushButton("Reset")

        self.run_full_btn.setObjectName("primaryButton")
        self.upload_btn.setObjectName("secondaryButton")
        self.run_input_btn.setObjectName("ghostButton")
        self.run_processing_btn.setObjectName("ghostButton")
        self.run_detection_btn.setObjectName("ghostButton")
        self.reset_btn.setObjectName("ghostButton")

        for btn in [
            self.upload_btn,
            self.run_input_btn,
            self.run_processing_btn,
            self.run_detection_btn,
            self.run_full_btn,
            self.reset_btn,
        ]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(44)
            layout.addWidget(btn)

        progress_card = InfoCard("Pipeline Progress")
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p% complete")
        progress_card.body_layout.addWidget(self.progress)

        self.stage_list = QListWidget()
        self.stage_list.addItems(
            [
                "1. User Interface Layer",
                "2. Input Layer",
                "3. Image Processing Layer",
                "4. Feature / Analysis Layer",
                "5. Decision Layer",
                "6. Output Layer",
            ]
        )
        progress_card.body_layout.addWidget(self.stage_list)
        layout.addWidget(progress_card)

        tips_card = InfoCard("Presentation Tip")
        tip_label = QLabel(
            "Do not hide the pipeline. Each layer should show what it receives, what it does, and what it returns."
        )
        tip_label.setWordWrap(True)
        tip_label.setObjectName("mutedText")
        tips_card.body_layout.addWidget(tip_label)
        layout.addWidget(tips_card)

        layout.addStretch()
        return container

    def _build_pipeline_area(self) -> QWidget:
        container = QFrame()
        container.setObjectName("panel")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        panel_title = QLabel("Pipeline View")
        panel_title.setObjectName("panelTitle")
        panel_note = QLabel("Show intermediate stages clearly")
        panel_note.setObjectName("mutedText")
        header_layout.addWidget(panel_title)
        header_layout.addStretch()
        header_layout.addWidget(panel_note)
        layout.addLayout(header_layout)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

        self.original_card = ImageStageCard(
            "Input Layer",
            "Original uploaded image and basic validation preview.",
        )
        self.processed_card = ImageStageCard(
            "Image Processing Layer",
            "Enhanced / resized / filtered image output.",
        )
        self.analysis_card = ImageStageCard(
            "Feature / Analysis Layer",
            "Detections, extracted ingredients, and useful representations.",
        )
        self.output_card = ImageStageCard(
            "Output Layer",
            "Final visual result with decision-ready output.",
        )

        grid.addWidget(self.original_card, 0, 0)
        grid.addWidget(self.processed_card, 0, 1)
        grid.addWidget(self.analysis_card, 1, 0)
        grid.addWidget(self.output_card, 1, 1)

        layout.addLayout(grid)
        return container

    def _build_right_panel(self) -> QWidget:
        container = QFrame()
        container.setObjectName("panel")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        panel_title = QLabel("Layer Details")
        panel_title.setObjectName("panelTitle")
        layout.addWidget(panel_title)

        self.input_card = InfoCard("Input Layer")
        self.input_log = QTextEdit()
        self.input_log.setReadOnly(True)
        self.input_card.body_layout.addWidget(self.input_log)
        layout.addWidget(self.input_card)

        self.processing_card = InfoCard("Image Processing Layer")
        self.processing_log = QTextEdit()
        self.processing_log.setReadOnly(True)
        self.processing_card.body_layout.addWidget(self.processing_log)
        layout.addWidget(self.processing_card)

        self.features_card = InfoCard("Feature / Analysis Layer")
        self.features_table = QTableWidget(0, 3)
        self.features_table.setHorizontalHeaderLabels(["Item", "Confidence", "Count"])
        self.features_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.features_table.verticalHeader().setVisible(False)
        self.features_card.body_layout.addWidget(self.features_table)
        layout.addWidget(self.features_card)

        self.decision_card = InfoCard("Decision Layer")
        self.recipe_table = QTableWidget(0, 3)
        self.recipe_table.setHorizontalHeaderLabels(["Recipe", "Match %", "Missing"])
        self.recipe_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recipe_table.verticalHeader().setVisible(False)
        self.decision_card.body_layout.addWidget(self.recipe_table)
        layout.addWidget(self.decision_card)

        return container

    def _apply_styles(self):
        self.setStyleSheet(
            """
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
                border: 1px solid rgba(140, 235, 220, 0.08);
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
                    stop: 0 rgba(24, 55, 70, 0.92),
                    stop: 1 rgba(18, 65, 72, 0.9)
                );
                border: 1px dashed rgba(150, 240, 220, 0.22);
                border-radius: 16px;
                color: rgba(230, 250, 250, 0.55);
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
        )

    def _apply_window_effects(self):
        # Removed outer window shadow to eliminate glowing outline
        # shell_shadow = QGraphicsDropShadowEffect(self)
        # shell_shadow.setBlurRadius(42)
        # shell_shadow.setOffset(0, 12)
        # shell_shadow.setColor(QColor(0, 0, 0, 120))
        # self.window_shell.setGraphicsEffect(shell_shadow)

        for card in [
            self.original_card,
            self.processed_card,
            self.analysis_card,
            self.output_card,
            self.input_card,
            self.processing_card,
            self.features_card,
            self.decision_card,
        ]:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(26)
            shadow.setOffset(0, 8)
            shadow.setColor(QColor(0, 0, 0, 70))
            card.setGraphicsEffect(shadow)

    def _add_demo_data(self):
        self.input_log.setPlainText(
            "No image uploaded yet.\n\n"
            "This panel should later show:\n"
            "- file name\n"
            "- image format\n"
            "- width and height\n"
            "- quality/validation result"
        )

        self.processing_log.setPlainText(
            "Waiting for preprocessing stage.\n\n"
            "Later show:\n"
            "- resize operation\n"
            "- denoising/filtering\n"
            "- normalization\n"
            "- any intermediate notes"
        )

        sample_items = [
            ("egg", "0.94", "4"),
            ("milk", "0.89", "1"),
            ("tomato", "0.91", "3"),
        ]
        self.features_table.setRowCount(len(sample_items))
        for row, values in enumerate(sample_items):
            for col, value in enumerate(values):
                self.features_table.setItem(row, col, QTableWidgetItem(value))

        sample_recipes = [
            ("Omelette", "100", "-") ,
            ("Tomato Egg Skillet", "100", "-") ,
            ("Creamy Pasta", "67", "pasta") ,
        ]
        self.recipe_table.setRowCount(len(sample_recipes))
        for row, values in enumerate(sample_recipes):
            for col, value in enumerate(values):
                self.recipe_table.setItem(row, col, QTableWidgetItem(value))

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select pantry or fridge image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)",
        )
        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.statusBar().showMessage("Could not load the selected image.")
            return

        self.current_image_path = file_path
        self.original_pixmap = pixmap

        for card in [self.original_card, self.processed_card, self.analysis_card, self.output_card]:
            card.set_pixmap(pixmap)

        image_path = Path(file_path)
        self.input_log.setPlainText(
            f"File name: {image_path.name}\n"
            f"File type: {image_path.suffix.lower()}\n"
            f"Image size: {pixmap.width()} × {pixmap.height()} px\n"
            f"Validation: Passed\n\n"
            "Next step:\n"
            "Run the input check and preprocessing pipeline, then replace the placeholder previews with real intermediate outputs."
        )

        self.processing_log.setPlainText(
            "Image loaded successfully.\n\n"
            "Planned preprocessing preview:\n"
            "- resize to model input size\n"
            "- denoise if needed\n"
            "- normalize color/brightness\n"
            "- save processed frame for YOLO input"
        )

        self.progress.setValue(18)
        self.stage_list.setCurrentRow(1)
        self.statusBar().showMessage(f"Loaded image: {image_path.name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartPantryWindow()
    window.show()
    sys.exit(app.exec())
