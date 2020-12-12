from PyQt5.QtCore import QPoint
from typing import List
from PyQt5.QtGui import QImage, QPixmap

import cv2
import numpy as np


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


def manhattan(a, b):
    return np.abs(b - a).sum()


def add_z_coordinates(pts: np.ndarray):
    nrow, ncol = pts.shape[:2]

    assert(ncol == 2)

    return np.hstack([pts, np.ones((nrow, 1))]).astype(pts.dtype)


def rotate_corners_90_clockwise(corners: np.ndarray, height: int) -> None:
    rotate_matrix = np.array([[0, -1, height],
                              [1,  0,      0]], dtype=corners.dtype)

    # Add third coordinate in order to apply translate transformation corners after rotation
    tmp_corners = add_z_coordinates(corners).T

    return (rotate_matrix @ tmp_corners).T


def rotate_90_clockwise(image: np.ndarray, corners: np.ndarray) -> List[np.ndarray]:
    height, width = image.shape[:2]
    # rotate_corners_90_clockwise(corners, image.shape[0])
    return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE), rotate_corners_90_clockwise(corners, height)


def flip_horizontal(image: np.ndarray) -> np.ndarray:
    raise NotImplemented
    return cv2.flip(image, 1)


def flip_vertical(image: np.ndarray) -> np.ndarray:
    raise NotImplemented
    return cv2.flip(image, 0)


def draw_border(image: np.ndarray, corners: np.ndarray):
    thickness = 20
    color = (53, 57, 229)
    isClosed = True
    tmp_image = image.copy()

    cv2.polylines(tmp_image, np.int32([corners]), isClosed, color, thickness)

    return tmp_image


def crop(image: np.ndarray, corners: np.ndarray):
    """
    Crop document out of background
    """
    # qpoints[0]: top left corner
    # qpoints[1]: top right corner
    # qpoints[2]: bottom right corner
    # qpoints[3]: bottom left corner

    # TODO: Sort corners

    # height = np.linalg.norm(corners[3] - corners[0])
    # width = np.linalg.norm(corners[1] - corners[0])
    height = manhattan(corners[3], corners[0])
    width = manhattan(corners[1], corners[0])

    new_corners = np.array([[0, 0],
                            [width, 0],
                            [width, height],
                            [0, height]], dtype=np.float32)

    transform_mat = cv2.getPerspectiveTransform(corners, new_corners)
    new_image = cv2.warpPerspective(image, transform_mat, (width, height))

    # TODO: increase contrast of new_image
    return new_image


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    img = cv2.cvtColor(cv2.imread('demo_papers/paper2.jpg'), cv2.COLOR_BGR2RGB)
    height, width = img.shape[:2]
    # img = rotate_90_clockwise(img, None)[0]

    # M = cv2.getRotationMatrix2D((width//2, height//2), -90, 1)
    # N = cv2.getRotationMatrix2D((width//2, height//2), -90, 2)

    # im1 = cv2.warpAffine(img, M, (height, width))
    # im2 = cv2.warpAffine(img, N, (width*2, height*2))

    # plt.subplot(1, 2, 1)
    # plt.imshow(im1)
    # plt.subplot(1, 2, 2)
    # plt.imshow(im2)
    # plt.show()
    pts1 = np.array([[1, 1]])
    pts2 = rotate_corners_90_clockwise(pts1, 1)
    print(pts2)
