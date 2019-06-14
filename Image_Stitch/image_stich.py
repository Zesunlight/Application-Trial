import numpy as np
import cv2

"""
opencv-python==3.4.2.17
opencv-contrib-python==3.4.2.17
"""

if __name__ == "__main__":
    img1 = cv2.imread('Your Lie in April(2).jpg') # left below
    img2 = cv2.imread('Your Lie in April(5).jpg') # right below
    img3 = cv2.imread("Your Lie in April(3).jpg") # left top
    img4 = cv2.imread("Your Lie in April(4).jpg") # right top

    stitcher = cv2.createStitcher(False)
    # stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)

    (_result, stitched_image) = stitcher.stitch((img4, img2, img3, img1))
    cv2.imwrite("1res.png", stitched_image)

    (_result, stitched_image) = stitcher.stitch((img4, img2, img3))
    cv2.imwrite("2res.png", stitched_image)

    (_result, stitched_image) = stitcher.stitch((img2, img1))
    cv2.imwrite("3res.png", stitched_image)

    (_result, stitched_image) = stitcher.stitch((img3, img1))
    cv2.imwrite("4res.png", stitched_image)

    (_result, stitched_image) = stitcher.stitch((img4, img1))
    cv2.imwrite("4res.png", stitched_image)
