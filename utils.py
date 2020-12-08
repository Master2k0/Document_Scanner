from PyQt5.QtCore import QPoint
from typing import List, Tuple

import cv2
import numpy as np

import matplotlib.pyplot as plt

def extract(point: QPoint) -> Tuple:
    """
    Convert PyQt5.QtCore.QPoint into tuple of (row, column)
    """
    return point.x(), point.y()


def transform(image: np.ndarray, qpoints: List[QPoint]):
    for qpoint in qpoints:
        if qpoint is None:
            raise ValueError("Not enough corners to calculate transform")

    # qpoints[0]: top left corner
    # qpoints[1]: top right corner
    # qpoints[2]: bottom right corner
    # qpoints[3]: bottom left corner

    original_corners = np.array([extract(qpoints[0]),
                                 extract(qpoints[1]),
                                 extract(qpoints[2]),
                                 extract(qpoints[3])], dtype=np.float32)

    height = 1000   
    width = 700

    new_corners = np.array([[0, 0],
                            [width, 0],
                            [width, height],
                            [0, height]], dtype=np.float32)

    transform_matrix = cv2.getPerspectiveTransform(original_corners, new_corners)    

    new_image = cv2.warpPerspective(image, transform_matrix, (width, height))

    return new_image

# if __name__ == "__main__":
#     img = cv2.imread('demo_papers/paper2.jpg')

#     qpoints = [QPoint(73, 2257),
#                QPoint(1263, 1901),
#                QPoint(2046, 3287),
#                QPoint(573, 4013)]

#     new_img = transform(img, qpoints)
#     new_img_rgb = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB)
#     plt.imshow(new_img_rgb)
#     plt.show()
