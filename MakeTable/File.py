from Main import *
import cv2
# ★★★★★★★★★★★★★★★★★★★★★★★ 내가만든함수
def imageSave(image, namePrefix='crop'):
    filePath = namePrefix + ".jpg"
    cv2.imwrite(filePath, image)

def resizeFile(image): # 사진으로 찍은 경우 사이즈가 크기 때문에 수정해주는 함수
    if image.shape[0] > 2000 or image.shape[1] > 2000:
        resizeImage = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    else:
        resizeImage = image

    cv2.imwrite('document.jpg', resizeImage)

''' 다시돌려줄려고 '일단 만들었는데 ㅈ 같네 ^^
def resizeFIle(image): # 사진으로 찍은 경우 사이즈가 크기 때문에 수정해주는 함수
    image = cv2.imread('document.jpg')
    if image.shape[0] > 0 or image.shape[1] > 0:
        resizeImage = cv2.resize(image, (0, 0), fx=10, fy=5)
    else:
        resizeImage = image

    cv2.imwrite('document1.jpg', resizeImage)
'''
