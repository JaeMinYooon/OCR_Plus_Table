import cv2

def openImgFile(filePath):
    image = cv2.imread(filePath)  # 파일로부터 이미지 읽기
    return image


def saveImage(image, namePrefix='crop'):
    ''' 이미지(OpenCV image 객체)를 이미지파일(.jpg)로 저장합니다.

    :param image: 저장할 이미지 (OpenCV image 객체)
    :param namePrefix: 파일명을 식별할 접두어 (확장자 제외)
    :return:
    '''
    filePath = namePrefix + ".jpg"
    cv2.imwrite(filePath, image)

def resizeFile(image): # 사진으로 찍은 경우 사이즈가 크기 때문에 수정해주는 함수
    if image.shape[0] > 2000 or image.shape[1] > 2000:
        resizeImage = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    else:
        resizeImage = image

    cv2.imwrite('document.jpg', resizeImage)
