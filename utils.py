from PyQt5.QtCore import QPoint
from typing import List, Tuple
from PyQt5.QtGui import QImage, QPixmap

import cv2
import numpy as np

import matplotlib.pyplot as plt


def convert_ndarray_to_QPixmap(image_matrix: np.ndarray) -> QImage:
    """
    Convert an image loaded from opencv to QImage
    """
    # Convert image_matrix to RGB format first
    image_matrix = cv2.cvtColor(image_matrix, cv2.COLOR_BGR2RGB)

    height, width, _ = image_matrix.shape
    bytesPerLine = 3 * width
    qImg = QImage(image_matrix.data, width, height,
                  bytesPerLine, QImage.Format_RGB888)

    return QPixmap.fromImage(qImg)


def extract(point: QPoint) -> np.ndarray:
    """
    Convert PyQt5.QtCore.QPoint into tuple of (row, column)
    """
    return np.array([point.x(), point.y()])


def transform(image: np.ndarray, qpoints: List[QPoint]):
    """
    Crop document
    Params:
    image 
    """

    for qpoint in qpoints:
        if qpoint is None:
            raise ValueError("Not enough corners to calculate transform")

    # qpoints[0]: top left corner
    # qpoints[1]: top right corner
    # qpoints[2]: bottom right corner
    # qpoints[3]: bottom left corner

    # TODO: Sort corners
    original_corners = np.array([extract(qpoints[0]),
                                 extract(qpoints[1]),
                                 extract(qpoints[2]),
                                 extract(qpoints[3])], dtype=np.float32)

    # TODO: Automatically choose width, height for new_image
    height = np.linalg.norm(original_corners[3] - original_corners[0])
    width = np.linalg.norm(original_corners[1] - original_corners[0])

    new_corners = np.array([[0, 0],
                            [width, 0],
                            [width, height],
                            [0, height]], dtype=np.float32)

    transform_matrix = cv2.getPerspectiveTransform(
        original_corners, new_corners)

    new_image = cv2.warpPerspective(image, transform_matrix, (width, height))
    # TODO: increase contrast of new_image
    return new_image


def auto_transform(image: np.ndarray):
    raise NotImplemented


if __name__ == "__main__":
    img = cv2.imread('demo_papers/paper2.jpg')

    # qpoints = [QPoint(73, 2257),
    #            QPoint(1263, 1901),
    #            QPoint(2046, 3287),
    #            QPoint(573, 4013)]

    # new_img = transform(img, qpoints)
    # new_img_rgb = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB)
    # plt.imshow(new_img_rgb)
    # plt.show()
