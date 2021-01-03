from typing import Tuple

import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap


def convert_ndarray_to_QPixmap(image_matrix: np.ndarray) -> QPixmap:
    """
    Convert an image loaded from opencv to QImage
    """
    # Convert image_matrix to RGB format first
    image_matrix = cv2.cvtColor(image_matrix, cv2.COLOR_BGR2RGB)

    height, width, _ = image_matrix.shape
    bytesPerLine = 3 * width
    qImg = QImage(image_matrix.data, width, height, bytesPerLine, QImage.Format_RGB888)

    return QPixmap.fromImage(qImg)


def manhattan(a: np.ndarray, b: np.ndarray) -> float:
    return np.abs(b - a).sum()


def add_z_coordinates(pts: np.ndarray) -> np.ndarray:
    nrow, ncol = pts.shape[:2]

    assert ncol == 2

    return np.hstack([pts, np.ones((nrow, 1))]).astype(pts.dtype)


def rotate_90_clockwise(
        image: np.ndarray, corners: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return rotated images and corners
    """
    height, width = image.shape[:2]

    # create 90 clockwise rotation matrix
    rotation_mat = np.array([[0, -1, height], [1, 0, 0]], dtype=corners.dtype)

    # Rotate the image
    rotated_image = cv2.warpAffine(image, rotation_mat, (height, width))

    # Add third coordinates in order to use with rotation_mat
    tmp_corners = add_z_coordinates(corners).T
    # Rotate corners' coordinates
    rotated_corner_coordinates = (rotation_mat @ tmp_corners).T

    # Rearrange corners' order (bottom-left -> top-left -> top-right -> bottom-right)
    rotated_corners = np.empty_like(rotated_corner_coordinates)
    for i in range(rotated_corners.shape[0]):
        rotated_corners[i] = rotated_corner_coordinates[i - 1]

    return rotated_image, rotated_corners


def flip_horizontal(
        image: np.ndarray, corners: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    height, width = image.shape[:2]

    # Create flip matrix
    flip_h_mat = np.array([[-1, 0, width], [0, 1, 0]], dtype=corners.dtype)

    # Flip the image
    flipped_image = cv2.warpAffine(image, flip_h_mat, (width, height))

    # Add third coordinates in order to use with flip_h_mat
    tmp_corners = add_z_coordinates(corners).T
    # Flip corners' coordinates
    flipped_corner_coordinates = (flip_h_mat @ tmp_corners).T

    # Rearrange corners' order (top-right -> top-left -> bottom-left -> bottom-right)
    flipped_corners = np.array(
        [
            flipped_corner_coordinates[1],
            flipped_corner_coordinates[0],
            flipped_corner_coordinates[2],
            flipped_corner_coordinates[3],
        ]
    )

    return flipped_image, flipped_corners


def flip_vertical(
        image: np.ndarray, corners: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    height, width = image.shape[:2]

    # Create flip matrix
    flip_v_mat = np.array([[1, 0, 0], [0, -1, height]], dtype=corners.dtype)

    # Flip the image
    flipped_image = cv2.warpAffine(image, flip_v_mat, (width, height))

    # Add third coordinates in order to use with flip_v_mat
    tmp_corners = add_z_coordinates(corners).T
    # Flip corners' coordinates
    flipped_corner_coordinates = (flip_v_mat @ tmp_corners).T

    # Rearrange corners' order (bottom-left -> bottom-right -> top-right -> top-left)
    flipped_corners = np.array(
        [
            flipped_corner_coordinates[3],
            flipped_corner_coordinates[2],
            flipped_corner_coordinates[1],
            flipped_corner_coordinates[0],
        ]
    )

    return flipped_image, flipped_corners


def draw_border(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    """Draw border of the document in image using corners' coordinates without changing the original image

    Args:
        image: input image matrix
        corners: array of size (4, 2) stores coordinates of 4 corners

    Returns:
        New image with border in it
    """
    thickness = 20
    color = (0, 255, 0)
    isClosed = True
    radius = 5
    tmp_image = image.copy()

    cv2.polylines(tmp_image, np.int32([corners]), isClosed, color, thickness)

    for corner in corners:
        tmp_image = cv2.circle(tmp_image, tuple(corner), radius * 8, color, -1)

    return tmp_image


def crop(image: np.ndarray, corners: np.ndarray):
    """
    Crop document out of background
    """
    # corners[0]: top left corner
    # corners[1]: top right corner
    # corners[2]: bottom right corner
    # corners[3]: bottom left corner

    height = np.linalg.norm(corners[3] - corners[0])
    width = np.linalg.norm(corners[1] - corners[0])

    new_corners = np.array(
        [[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32
    )

    transform_mat = cv2.getPerspectiveTransform(corners, new_corners)
    new_image = cv2.warpPerspective(image, transform_mat, (width, height))

    # TODO: increase contrast of new_image
    return new_image


def sort_corners(corners: np.ndarray) -> np.ndarray:
    """Sort corners in this order: top-left top-right bottom-right bottom-left

    Args:
        corners: ndarray of shape (4, 2) corresponding to 4 corners' coordinates of the document

    Returns:
        ndarray of shape (4, 2) corresponding to sorted corners

    References:
        .. [1] https://bretahajek.com/
    """
    diff = np.diff(corners, axis=1)
    total = corners.sum(axis=1)
    # Top-left point has smallest sum...
    return np.array([corners[np.argmin(total)],
                     corners[np.argmin(diff)],
                     corners[np.argmax(total)],
                     corners[np.argmax(diff)]])


def auto_select_corners(image: np.ndarray) -> np.ndarray:
    """Automatically select top-left top-right bottom-right bottom-left corners

    Args:
        image: ndarray of image

    Returns:
        ndarray of shape (4, 2) corresponding to sorted corners
    """
    raise NotImplemented
