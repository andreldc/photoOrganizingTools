import cv2
import numpy as np

import enhanced_imshow

img1 = cv2.imread('./sample_images/split_scanned_photos_1.jpg')
# img2 = cv2.imread('./sample_images/split_scanned_photos_2.jpg')
img2 = cv2.imread('./sample_images/split_scanned_photos_1 small.jpg')
#img2 = cv2.imread('./sample_images/split_scanned_photos_1 1flip.jpg')
# img2 = cv2.imread('./sample_images/split_scanned_photos_1 small flip.jpg')

gray1= cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
gray2= cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

sift = cv2.SIFT_create()

kp1, des1 = sift.detectAndCompute(gray1,None)
kp2, des2 = sift.detectAndCompute(gray2,None)

img1 = cv2.drawKeypoints(gray1, kp1, img1, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
img2 = cv2.drawKeypoints(gray2, kp2, img2, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

enhanced_imshow.enhanced_imshow("sift1", img1)
enhanced_imshow.enhanced_imshow("sift2", img2)

print(des1.shape)





# BFMatcher with default params
bf = cv2.BFMatcher(cv2.NORM_L2)#, crossCheck=True)
matches = bf.knnMatch(des1, des2, k=2)

print("matches " + str(len(matches)))
# Apply ratio test
good = []
for m, n in matches:
    if m.distance < 0.25*n.distance:
        good.append([m])

good = sorted(good, key = lambda x:x[0].distance)

print("good " + str(len(good)))
img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)


enhanced_imshow.enhanced_imshow("img3", img3)


cv2.waitKey(0)