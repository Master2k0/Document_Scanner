# main.py

import sys
from typing import List
from utils import convert_ndarray_to_QPixmap, draw_circle_around_corners, flip_horizontal, flip_vertical, rotate_left_90, crop

import numpy as np
import cv2

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QAction, QFileDialog, QDesktopWidget, QMessageBox, QSizePolicy, QToolBar,
                             QStatusBar, QDockWidget, QVBoxLayout, QPushButton)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QPoint, Qt, QSize, qsrand


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
        tool_bar.addAction(zoom_act)  # TODO

        tool_bar.addSeparator()

        restore_act = QAction(QIcon('icons/reset.svg'), 'Reset image', self)
        restore_act.setStatusTip("Discard all changes to the image")
        restore_act.triggered.connect(self.restoreImage)
        tool_bar.addAction(restore_act)  # TODO

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

        edit_btn = QPushButton("Edit Mode")
        edit_btn.setMinimumSize(QSize(130, 40))
        edit_btn.setStatusTip("Edit image mode")
        edit_btn.clicked.connect(lambda: 2)  # TODO
        dock_v_box.addWidget(edit_btn)

        crop_btn = QPushButton("Preview Mode")
        crop_btn.setMinimumSize(QSize(130, 40))
        crop_btn.setStatusTip("Document image")
        crop_btn.clicked.connect(lambda: 2)  # TODO
        dock_v_box.addWidget(crop_btn)

        dock_v_box.addStretch(1)

        # Select top left corner
        corner1_btn = QPushButton("Top Left")
        corner1_btn.setMinimumSize(QSize(130, 40))
        corner1_btn.setStatusTip('Choose top left corner')
        corner1_btn.clicked.connect(self.switchToFirstCorner)
        dock_v_box.addWidget(corner1_btn)

        corner1_text = QLabel()
        corner1_text.setText("")
        corner1_text.setMinimumSize(QSize(130, 20))
        dock_v_box.addWidget(corner1_text)

        # Select top right corner
        corner2_btn = QPushButton("Top Right")
        corner2_btn.setMinimumSize(QSize(130, 40))
        corner2_btn.setStatusTip('Choose top right corner')
        corner2_btn.clicked.connect(self.switchToSecondCorner)
        dock_v_box.addWidget(corner2_btn)

        corner2_text = QLabel()
        corner2_text.setText("")
        corner2_text.setMinimumSize(QSize(130, 20))
        dock_v_box.addWidget(corner2_text)

        # Select bottom right corner
        corner3_btn = QPushButton("Bottom Right")
        corner3_btn.setMinimumSize(QSize(130, 40))
        corner3_btn.setStatusTip('Choose bottom right corner')
        corner3_btn.clicked.connect(self.switchToThirdCorner)
        dock_v_box.addWidget(corner3_btn)

        corner3_text = QLabel()
        corner3_text.setText("")
        corner3_text.setMinimumSize(QSize(130, 20))
        dock_v_box.addWidget(corner3_text)

        # Select bottom left corner
        corner4_btn = QPushButton("Bottom Left")
        corner4_btn.setMinimumSize(QSize(130, 40))
        corner4_btn.setStatusTip('Choose bottom left corner')
        corner4_btn.clicked.connect(self.switchToFourthCorner)
        dock_v_box.addWidget(corner4_btn)

        corner4_text = QLabel()
        corner4_text.setText("")
        corner4_text.setMinimumSize(QSize(130, 20))
        dock_v_box.addWidget(corner4_text)

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

    def openImage(self):
        """
        Open an image file and display its contents in label widget.
        Display error message if image can't be opened.
        """
        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                    "JPG Files (*.jpeg *jpg);; \
                                                     PNG Files (*.png);; \
                                                     Bitmap Files (*.bmp);; \
                                                     GIF Files(*.gif) \
                                                     All Files (*.*)")
        if not image_path:
            return

        self.image_mat: np.ndarray = cv2.imread(image_path)
        self.final_mat: np.ndarray = self.image_mat.copy()
        self.initCornersPoint()

        if self.image_mat is None:
            QMessageBox.information(self, "Error",
                                    "Unable to open image", QMessageBox.Ok)

        self.showImage()

    def saveImage(self):
        """
        Save the image.
        Display error message if image can't be saved.
        """
        # TODO: Implement this shit
        raise NotImplemented

        image_file, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                    "JPG Files (*.jpeg * .jpg); ; PNG Files (*.png); ; Bitmap Files (*.bmp); ; GIF Files(*.gif)")
        if image_file and self.image.isNull() == False:
            self.image.save(image_file)
        else:
            QMessageBox.information(self, "Error",
                                    "Unable to save image.", QMessageBox.Ok)

    def showImage(self):
        return
        image_matrix = self.image_mat if self.show_original else self.final_mat

        image_matrix = draw_circle_around_corners(
            image_matrix, self.corner_points)

        # scale the image to display
        self.image = convert_ndarray_to_QPixmap(image_matrix)
        self.image = self.image.scaled(
            self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # get scale ratio
        original_height: int = image_matrix.shape[0]
        self.scale_ratio: float = original_height / self.image.height()

        # show the image on screen
        self.image_label.setPixmap(self.image)

        self.image_label.mousePressEvent = self.selectCorner

    def clearImage(self):
        """
        Clears current image in QLabel widget
        """
        self.image_label.clear()
        self.image = QPixmap()  # reset pixmap so that isNull() = True

    def initCornersPoint(self):
        self.corner_points: List[QPoint] = [None] * 4
        self.corner_idx: int = 0

    def restoreImage(self):
        self.final_mat = self.image_mat
        self.showImage()
        self.initCornersPoint()

    def rotateImage90(self):
        """
        Rotate image 90° clockwise
        """
        if self.final_mat is None:
            return

        self.final_mat = rotate_left_90(self.final_mat)

        self.showImage()

        self.initCornersPoint()

    def flipImageHorizontal(self):
        """
        Mirror the image across the horizontal axis
        """
        self.final_mat = flip_horizontal(self.final_mat)

        self.showImage()

        self.initCornersPoint()

    def flipImageVertical(self):
        """
        Mirror the image across the vertical axis
        """
        self.final_mat = flip_vertical(self.final_mat)

        self.showImage()

        self.initCornersPoint()

    def switchToFirstCorner(self):
        self.corner_idx = 0

    def switchToSecondCorner(self):
        self.corner_idx = 1

    def switchToThirdCorner(self):
        self.corner_idx = 2

    def switchToFourthCorner(self):
        self.corner_idx = 3

    def selectCorner(self, event):
        tmp_pos: QPoint = event.pos()
        original_x = int(round(tmp_pos.x() * self.scale_ratio))
        original_y = int(round(tmp_pos.y() * self.scale_ratio))
        self.corner_points[self.corner_idx] = QPoint(original_x, original_y)
        print(self.corner_points[self.corner_idx])
        self.showImage()

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


# Run program
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PhotoEditor()
    sys.exit(app.exec_())
