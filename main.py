# main.py

import sys
from typing import Callable, List

import cv2
import numpy as np
from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QDockWidget, QFileDialog, QLabel, QMainWindow,
                             QMessageBox, QPushButton, QSizePolicy, QStatusBar,
                             QToolBar, QVBoxLayout, QWidget)

from utils import (convert_ndarray_to_QPixmap, crop, draw_border,
                   flip_horizontal, flip_vertical, rotate_90_clockwise)


class PhotoEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):
        """
        Initialize the window and display its contents to the screen
        """
        self.setMinimumSize(600, 640)
        self.setWindowTitle('Document Scanner')
        self.centerMainWindow()
        self.createToolbar()
        self.createRightDock()
        self.photoEditorWidgets()
        self.show()

    def createToolbar(self):
        """
        Create toolbar for photo editor GUI
        """
        # Create toolbar
        tool_bar = QToolBar("Photo Editor Toolbar")
        tool_bar.setIconSize(QSize(24, 24))
        self.addToolBar(tool_bar)

        # Add actions to toolbar
        open_act = QAction(QIcon('icons/file.svg'), "Open", self)
        open_act.setShortcut('Ctrl+O')
        open_act.setStatusTip('Open a new image')
        open_act.triggered.connect(self.openImage)
        tool_bar.addAction(open_act)

        save_act = QAction(QIcon('icons/save.svg'), "Save", self)
        save_act.setShortcut('Ctrl+S')
        save_act.setStatusTip('Save image')
        save_act.triggered.connect(self.saveImage)
        tool_bar.addAction(save_act)

        clear_act = QAction(QIcon('icons/trash.svg'), "Close image", self)
        clear_act.setShortcut("Ctrl+D")
        clear_act.setStatusTip('Close image')
        clear_act.triggered.connect(self.clearImage)
        tool_bar.addAction(clear_act)

        tool_bar.addSeparator()

        rotate_act = QAction(QIcon('icons/rotate.svg'), "Rotate 90°", self)
        rotate_act.setStatusTip('Rotate image 90° clockwise')
        rotate_act.triggered.connect(self.rotateImage90)
        tool_bar.addAction(rotate_act)

        flip_h_act = QAction(QIcon('icons/fliph.svg'), "Flip Horizontal", self)
        flip_h_act.setStatusTip('Flip image horizontally')
        flip_h_act.triggered.connect(self.flipImageHorizontal)
        tool_bar.addAction(flip_h_act)

        flip_r_act = QAction(QIcon('icons/flipv.svg'), "Flip Vertical", self)
        flip_r_act.setStatusTip('Flip image vertically')
        flip_r_act.triggered.connect(self.flipImageVertical)
        tool_bar.addAction(flip_r_act)

        zoom_act = QAction(QIcon('icons/zoom.svg'), 'Zoom to fit', self)
        zoom_act.setStatusTip('Zoom image to fit the screen')
        zoom_act.triggered.connect(self.showImage)
        tool_bar.addAction(zoom_act)

        tool_bar.addSeparator()

        reset_act = QAction(QIcon('icons/reset.svg'), 'Reset image', self)
        reset_act.setStatusTip("Discard all changes")
        reset_act.triggered.connect(self.resetImage)
        tool_bar.addAction(reset_act)

        tool_bar.addSeparator()

        auto_pick_act = QAction(QIcon('icons/auto.svg'), 'Auto pick', self)
        auto_pick_act.setStatusTip('Auto pick corners')
        auto_pick_act.triggered.connect(lambda: 23)  # TODO
        tool_bar.addAction(auto_pick_act)

        # Display info about tools, menu, and view in the status bar
        self.setStatusBar(QStatusBar(self))

    def createRightDock(self):
        """
        Use View -> Edit Image Tools menu and click the dock widget on or off.
        Tools dock can be placed on the left or right of the main window.
        """
        # Set up vertical layout to contain all the push buttons
        dock_v_box = QVBoxLayout()

        # Add buttons

        # Switch between edit and preview mode
        self.switch_mode_btn = QPushButton("Edit Mode")
        self.switch_mode_btn.setMinimumSize(QSize(130, 40))
        self.switch_mode_btn.setStatusTip("Edit image mode")
        self.switch_mode_btn.clicked.connect(self.switchMode)
        dock_v_box.addWidget(self.switch_mode_btn)

        dock_v_box.addStretch(1)

        # Add select corner buttons and text to display corner's coordinates
        corner_names = ["Top Left", "Top Right", "Bottom Right", "Bottom Left"]
        self.corner_labels: List[QLabel] = []

        for i in range(4):
            corner_btn = QPushButton(corner_names[i])
            corner_btn.setMinimumSize(QSize(130, 40))
            corner_btn.setStatusTip(f'Select {corner_names[i]} corner')
            corner_btn.clicked.connect(self.switchCornerFactory(i))
            dock_v_box.addWidget(corner_btn)

            corner_label = QLabel()
            corner_label.setText("")
            corner_label.setMinimumSize(QSize(130, 20))
            corner_label.setAlignment(Qt.AlignCenter)
            self.corner_labels.append(corner_label)
            dock_v_box.addWidget(corner_label)

        # Set up QDockWidget
        self.dock_tools_view = QDockWidget()
        self.dock_tools_view.setAllowedAreas(Qt.LeftDockWidgetArea |
                                             Qt.RightDockWidgetArea)
        # Create container QWidget to hold all widgets inside dock widget
        self.tools_contents = QWidget()

        # Create tool push buttons
        # Set the main layout for the QWidget, tools_contents,
        # then set the main widget of the dock widget
        self.tools_contents.setLayout(dock_v_box)
        self.dock_tools_view.setWidget(self.tools_contents)

        # Set initial location of dock widget
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_tools_view)

        # Handles the visibility of the dock widget
        # self.toggle_dock_tools_act = self.dock_tools_view.toggleViewAction()

    def photoEditorWidgets(self):
        """
        Set up instances of widgets for photo editor GUI
        """
        self.image = QPixmap()

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignBaseline)
        self.image_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.setCentralWidget(self.image_label)

    def centerMainWindow(self):
        """
        Use QDesktopWidget class to access information about your screen
        and use it to center the application window.
        """
        desktop = QDesktopWidget().screenGeometry()
        screen_width = desktop.width()
        screen_height = desktop.height()
        self.move((screen_width - self.width()) // 2,
                  (screen_height - self.height()) // 2)

    def switchMode(self):
        self.is_edit_mode = not self.is_edit_mode

        if self.is_edit_mode:
            # Change button title
            self.switch_mode_btn.setText("Preview Mode")
            self.switch_mode_btn.setStatusTip("Preview result mode")

            # Enable features
            self.image_label.mousePressEvent = self.selectCorner
        else:
            # Change button title
            self.switch_mode_btn.setText("Edit Mode")
            self.switch_mode_btn.setStatusTip("Edit image mode")

            # Disable features

            self.image_label.mousePressEvent = None

        self.showImage()

    def switchCornerFactory(self, value) -> Callable[[], None]:
        def switchCorner():
            self.corner_idx = value
        return switchCorner

    def selectCorner(self, event):
        tmp_pos: QPoint = event.pos()

        current_idx = self.corner_idx

        original_x = int(round(tmp_pos.x() * self.scale_ratio))
        original_y = int(round(tmp_pos.y() * self.scale_ratio))

        # Set corner coordinates
        self.corners[current_idx] = (original_x, original_y)

        # Set text for current corner
        self.corner_labels[current_idx].setText(str(self.corners[current_idx]))

        # Update image
        self.showImage()

    def initCornersPoint(self):
        h, w = self.image_mat.shape[:2]
        self.corners: np.ndarray = np.array([[0, 0],
                                             [w, 0],
                                             [w, h],
                                             [0, h]], dtype=np.float32)
        self.corner_idx: int = 0

        for i in range(self.corners.shape[0]):
            self.corner_labels[i].setText(str(self.corners[i]))

    def openImage(self):
        """
        Open an image file and display its contents in label widget.
        Display error message if image can't be opened.
        """
        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                    "JPG Files (*.jpeg *jpg);; \
                                                     PNG Files (*.png);; \
                                                     Bitmap Files (*.bmp);; \
                                                     GIF Files (*.gif);; \
                                                     All Files (*.*)")
        if not image_path:
            # If no file is selected then skip
            return

        self.image_mat: np.ndarray = cv2.imread(image_path)

        if self.image_mat is None:
            message = "Unable to open image"
            QMessageBox.information(self, "Error", message, QMessageBox.Ok)
            return

        self.final_mat: np.ndarray = self.image_mat.copy()
        self.initCornersPoint()

        self.is_edit_mode: bool = False
        self.switchMode()

    def saveImage(self):
        """
        Save the image.
        Display error message if image can't be saved.
        """
        filename, extension = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                          "*.jpg;; \
                                                           *.png")
        if filename and self.final_mat is not None:
            cv2.imwrite(filename + extension[1:], self.final_mat)
        else:
            QMessageBox.information(self, "Error",
                                    "Unable to save image.", QMessageBox.Ok)

    def showImage(self):
        display_img_mat = self.final_mat

        if self.is_edit_mode:
            display_img_mat = draw_border(self.image_mat, self.corners)
        else:
            self.final_mat = crop(self.image_mat, self.corners)
            display_img_mat = self.final_mat

        if display_img_mat is None:
            return

        # Convert image_matrix to QPixmap
        self.image = convert_ndarray_to_QPixmap(display_img_mat)

        # scale the image to display
        self.image = self.image.scaled(
            self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # get scale ratio
        original_height: int = display_img_mat.shape[0]
        self.scale_ratio: float = original_height / self.image.height()

        # show the image on screen
        self.image_label.setPixmap(self.image)

        # Update corners
        for i in range(4):
            self.corner_labels[i].setText(str(self.corners[i]))

    def clearImage(self):
        """
        Clears current image in QLabel widget
        """
        self.image_label.clear()
        self.image = QPixmap()  # reset pixmap so that isNull() = True
        self.image_mat = None
        self.final_mat = None
        self.corners = None
        self.corner_idx = None

    def resetImage(self):
        self.final_mat = self.image_mat
        self.initCornersPoint()
        self.showImage()

    def rotateImage90(self):
        """
        Rotate image 90° clockwise
        """
        self.image_mat, self.corners = rotate_90_clockwise(
            self.image_mat, self.corners)

        self.showImage()

    def flipImageHorizontal(self):
        """
        Mirror the image across the horizontal axis
        """
        self.image_mat, self.corners = flip_horizontal(
            self.image_mat, self.corners)

        self.showImage()

    def flipImageVertical(self):
        """
        Mirror the image across the vertical axis
        """
        self.image_mat, self.corners = flip_vertical(
            self.image_mat, self.corners)

        self.showImage()


# Run program
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PhotoEditor()
    sys.exit(app.exec_())
