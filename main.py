import sys
from pathlib import Path

import cv2
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QAction, QColor, QPixmap, QImage
from imageProcessor import imageProcessor
from recipes import MealDBAPI
from ui_components import ImageStageCard, InfoCard, TitleBar, ZoomTableDialog
from styles import MODERN_STYLE

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

class SmartPantryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.original_pixmap = QPixmap()
        self.processed_img_cv = None
        self.detected_items = []

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
        splitter.setSizes([240,1120, 300])
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
        self.run_processing_btn.clicked.connect(self.run_processing)
        self.run_detection_btn = QPushButton("Run Detection")
        self.run_detection_btn.clicked.connect(self.run_detection)
        self.run_full_btn = QPushButton("Run Full Pipeline")
        self.run_full_btn.clicked.connect(self.run_full_pipeline)
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

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1) 

        self.original_card = ImageStageCard(
           "Input Layer",
           "Uploaded image and validation preview.",
        )

        self.processed_card = ImageStageCard(
           "Image Processing Layer",
           "Enhanced image used for detection.",
        )
       
        self.analysis_card = ImageStageCard(
           "Feature / Analysis Layer",
           "Detected items and extracted ingredients.",
        )
       
        self.output_card = ImageStageCard(
           "Output Layer",
           "Final detection and recommendation result.",
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
        self.features_table.horizontalHeader().setMinimumHeight(38)
        self.features_table.verticalHeader().setVisible(False)
        self.features_table.setAlternatingRowColors(True)
        self.features_table.setShowGrid(True)
        self.features_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.features_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.features_table.setFocusPolicy(Qt.ClickFocus)
        self.features_table.verticalHeader().setDefaultSectionSize(36)
        self.features_table.setMinimumHeight(180)
        self.features_card.body_layout.addWidget(self.features_table)

        expand_features_btn = QPushButton("⤢  Expand Table")
        expand_features_btn.setObjectName("ghostButton")
        expand_features_btn.setCursor(Qt.PointingHandCursor)
        expand_features_btn.setMaximumWidth(160)
        expand_features_btn.clicked.connect(lambda: self._open_table_zoom(self.features_table, "Detected Items"))
        self.features_card.body_layout.addWidget(expand_features_btn)
        layout.addWidget(self.features_card)

        self.decision_card = InfoCard("Decision Layer")
        self.recipe_table = QTableWidget(0, 3)
        self.recipe_table.setHorizontalHeaderLabels(["Recipe", "Match %", "Missing"])
        self.recipe_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recipe_table.horizontalHeader().setMinimumHeight(38)
        self.recipe_table.verticalHeader().setVisible(False)
        self.recipe_table.setAlternatingRowColors(True)
        self.recipe_table.setShowGrid(True)
        self.recipe_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recipe_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recipe_table.setFocusPolicy(Qt.ClickFocus)
        self.recipe_table.verticalHeader().setDefaultSectionSize(36)
        self.recipe_table.setMinimumHeight(180)
        self.decision_card.body_layout.addWidget(self.recipe_table)

        expand_recipe_btn = QPushButton("⤢  Expand Table")
        expand_recipe_btn.setObjectName("ghostButton")
        expand_recipe_btn.setCursor(Qt.PointingHandCursor)
        expand_recipe_btn.setMaximumWidth(160)
        expand_recipe_btn.clicked.connect(lambda: self._open_table_zoom(self.recipe_table, "Recipe Recommendations"))
        self.decision_card.body_layout.addWidget(expand_recipe_btn)
        layout.addWidget(self.decision_card)

        return container

    def _open_table_zoom(self, table, title):
        dialog = ZoomTableDialog(table, title, self)
        dialog.exec()

    def _apply_styles(self):
        self.setStyleSheet(MODERN_STYLE)

    def _apply_window_effects(self):
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
            shadow.setBlurRadius(16)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 45))
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

        self.features_table.setRowCount(0)
        self.recipe_table.setRowCount(0)

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

        self.original_card.set_pixmap(pixmap)

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

    def cv2_to_qpixmap(self, cv_img):
        height, width, channel = cv_img.shape
        bytes_per_line = 3 * width
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        q_img = QImage(rgb_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_img)

    def run_processing(self):
        if not self.current_image_path:
            self.statusBar().showMessage("Please open an image first.")
            return

        img = cv2.imread(self.current_image_path)
        if img is None:
            self.statusBar().showMessage("Failed to load image for processing.")
            return

        # denoised = imageProcessor.apply_median_blur(img)
        # blur = imageProcessor.apply_gaussian_blur(denoised)
        # enhanced_bgr = imageProcessor.apply_clahe(blur)
        # final_img = imageProcessor.apply_unsharp_masking(enhanced_bgr)
        final, logs = imageProcessor.enhance_image_pipeline(img)
        self.processed_img_cv = final

        final_pixmap = self.cv2_to_qpixmap(final)
        self.processed_card.set_pixmap(final_pixmap)

        self.processing_log.setPlainText("\n".join(logs))
        self.progress.setValue(33)
        self.stage_list.setCurrentRow(2)
        self.statusBar().showMessage("Preprocessing complete.")

    def run_detection(self):
        if self.processed_img_cv is None:
            self.statusBar().showMessage("Please run preprocessing first.")
            return

        plotted_img, items = imageProcessor.detect_ingredients(self.processed_img_cv, 'best.pt')
        
        final_pixmap = self.cv2_to_qpixmap(plotted_img)
        self.analysis_card.set_pixmap(final_pixmap)
        self.output_card.set_pixmap(final_pixmap)

        # Aggregate items
        item_counts = {}
        item_confidences = {}
        for item in items:
            name = item['name']
            item_counts[name] = item_counts.get(name, 0) + 1
            if name not in item_confidences or item['confidence'] > item_confidences[name]:
                item_confidences[name] = item['confidence']

        self.detected_items = list(item_counts.keys())
        self.features_table.setRowCount(len(self.detected_items))
        for row, name in enumerate(self.detected_items):
            self.features_table.setItem(row, 0, QTableWidgetItem(name))
            self.features_table.setItem(row, 1, QTableWidgetItem(f"{item_confidences[name]:.2f}"))
            self.features_table.setItem(row, 2, QTableWidgetItem(str(item_counts[name])))

        self.progress.setValue(66)
        self.stage_list.setCurrentRow(3)
        self.statusBar().showMessage("Detection complete.")

    def run_recommendations(self):
        if not self.detected_items:
            self.statusBar().showMessage("No ingredients detected for recommendations.")
            return
            
        recipes = MealDBAPI.search_by_multiple_ingredients(self.detected_items)
        self.recipe_table.setRowCount(len(recipes))
        for row, r in enumerate(recipes):
            self.recipe_table.setItem(row, 0, QTableWidgetItem(r['name']))
            self.recipe_table.setItem(row, 1, QTableWidgetItem(f"{r['match_percentage']}%"))
            self.recipe_table.setItem(row, 2, QTableWidgetItem(', '.join(r['missing_ingredients'])))

        self.progress.setValue(100)
        self.stage_list.setCurrentRow(4)
        self.statusBar().showMessage("Recommendations fetched.")

    def run_full_pipeline(self):
        self.run_processing()
        if self.processed_img_cv is not None:
            self.run_detection()
            self.run_recommendations()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartPantryWindow()
    window.show()
    sys.exit(app.exec())
