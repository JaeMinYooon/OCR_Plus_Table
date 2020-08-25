import cv2
import numpy as np
import glob,os
from Main import *
from MakeTable.File import *
from Contour import *
def processImage(image):
    ''' 다섯 단계의 이미지 처리(Image precessing)를 힙니다.
    현재 함수에서 순서를 변경하여 적용할 수 있습니다.
    1) Gray-scale 적용
    2) Morph Gradient 적용
    3) Threshold 적용
    4) Long Line Removal 적용
    5) Close 적용
    6) Contour 추출

    :param image_file: 이미지 처리(Image precessing)를 적용할 이미지 파일
    :return: 이미지 처리 후 글자로 추정되는 부분을 잘라낸 이미지 리스트
    '''
    #image = openImgFile(imageFile)
    wrappingImg = image_warping(image) # 이미지 wrapping 해주는것 => 표만 딱 잘라주기
    imageGray = getGrayImage(wrappingImg) # 이미지 회색으로 바꿔주는 것
    imageThreshold = getAdaptiveThreshold(imageGray) # 이미지를 검은색 아니면 흰색을 바꿔주기 + 블러 처리
    # Long line remove
    ##imageLineRemoved = removeLongLine(imageThreshold)
    # Morph Close
    ##imageClose = getClosing(imageLineRemoved)
    imageDilation = getDilation(imageThreshold)
    imageErosion = getErosion(imageDilation)

    contours = getContours(imageErosion)
    cv2.imwrite("result.jpg", imageErosion)
    cv2.imwrite("contour.jpg", drawContours(wrappingImg, contours))

    return croppedContours(wrappingImg, contours)  # 글자로 추정되는 부분을 잘라낸 이미지들을 반환

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)

    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect
def image_warping(imageFile):
    orig = imageFile.copy()
    r = 800.0 / imageFile.shape[0]
    dim = (int(imageFile.shape[1] * r), 800)
    imageFile = cv2.resize(imageFile, dim, interpolation=cv2.INTER_AREA)

    imgray = cv2.cvtColor(imageFile, cv2.COLOR_BGR2GRAY)
    imgray = cv2.GaussianBlur(imgray, (3, 3), 0)
    edged = cv2.Canny(imgray, 75, 200)

    contours, hierarchy = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:3]

    image = np.copy(imageFile)

    for contour in contours:
        perl = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perl, True)

        if len(approx) == 4:
            screenCnt = approx
            break

    cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)

    rect = order_points(screenCnt.reshape(4, 2) / r)

    (topLeft, topRight, bottomRight, bottomLeft) = rect
    w1 = abs(bottomRight[0] - bottomLeft[0])
    w2 = abs(topRight[0] - topLeft[0])
    h1 = abs(topRight[1] - bottomRight[1])
    h2 = abs(topLeft[1] - bottomLeft[1])

    maxWidth = max([w1, w2])
    maxHeight = max([h1, h2])

    dst = np.float32([[0, 0], [maxWidth, 0], [maxWidth, maxHeight - 1], [0, maxHeight - 1]])
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))

    return warped

def getGrayImage(image):
    copyGray = image.copy()
    imageGray = cv2.cvtColor(copyGray, cv2.COLOR_BGR2GRAY)

    return imageGray


def getAdaptiveThreshold(imageGray):
    ''' 이미지에 Threshold 를 적용해서 흑백(Binary) 이미지객체를 반환합니다.
    이 때 인자로 입력되는 이미지는 Gray-scale 이 적용된 2차원 이미지여야 합니다.
    gaussian을 이용
    '''
    copy = imageGray.copy()
    imgBlurred = cv2.GaussianBlur(copy, ksize=(3, 7), sigmaX=0)
    # adaptive threshold - gaussian
    imageThreshold = cv2.adaptiveThreshold(imgBlurred, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C, thresholdType=cv2.THRESH_BINARY_INV, blockSize=29, C=6)

    return imageThreshold  # 임계 값이 적용된 이미지를 반환

def removeLongLine(imageBinary):
    ''' 이미지에서 직선을 찾아서 삭제합니다.
    글자 경계를 찾을 때 방해가 되는 직선을 찾아서 삭제합니다.
    이 때 인자로 입력되는 이미지 2 차원(2 dimension) 흑백(Binary) 이미지여야 합니다.
    직선을 삭제할 때는 해당 라인을 검정색으로 그려 덮어 씌웁니다.

    :param imageBinary: 흑백(Binary) OpenCV image (2 dimension)
    :return: 라인이 삭제된 이미지 (OpenCV image)
    '''
    # 이거 안쓰면 글자에 선이 생김

    copy = imageBinary.copy()

    lines = cv2.HoughLinesP(copy, 1, np.pi / 180, 600, np.array([]), 53, 300)  # 라인 지우기 인데 600이란 수치를 형이 바꿔가면서 하면 뭔지 바로 감이 올거야 그 뒤에 어래이는 나도 뭔지 모르게따
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]  # get end point of line : ( (x1, y1) , (x2, y2) )
            # slop = 0
            # if x2 != x1:
            #     slop = abs((y2-y1) / (x2-x1))
            # if slop < 0.5 or slop > 50 or x2 == x1:  # only vertical or parallel lines.
            # remove line drawing black line
            cv2.line(copy, (x1, y1), (x2, y2), (0, 0, 0), 2)
    return copy

def getClosing(imageGray):
    ''' 이미지에 Morph Close 를 적용한 이미지객체를 반환합니다.
    이미지에 Dilation 수행을 한 후 Erosion 을 수행한 것입니다.
    이 때 인자로 입력되는 이미지는 Gray-scale 이 적용된 2차원 이미지여야 합니다.
    configs 에 의해 kernel size 값을 설정할 수 있습니다.

    :param imageGray: Gray-scale 이 적용된 OpenCV image (2 dimension)
    :return: Morph Close 를 적용한 흑백(Binary) 이미지
    '''
    copy = imageGray.copy()

    # make kernel matrix for dilation and erosion
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # closing (dilation and erosion)
    imageClose = cv2.morphologyEx(copy, cv2.MORPH_CLOSE, kernel, iterations=2) #iterations가 반복 but 현재는 안쓰는게 good

    return imageClose

def getDilation(image):

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    imageDilation = cv2.dilate(image, kernel, iterations=2)

    return imageDilation

def getErosion(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    imageErosion = cv2.erode(image, kernel, iterations=0)

    return imageErosion

def getGradient(imageGray): #일단 안씀
    ''' 이미지에 Dilation 과 Erosion 을 적용한 것을 바탕으로 차이를 이용해 윤곽선을 추출합니다.
    이 때 인자로 입력되는 이미지는 Gray scale 이 적용된 2차원 이미지여야 합니다.

    :param imageGray: Gray-scale 이 적용된 OpenCV image (2 dimension)
    :return: 윤곽선을 추출한 결과 이미지 (OpenCV image)
    '''
    copy = imageGray.copy()  # 가공된 이미지 복사하기
    # 팽창과 침식을 위한 커널 만들기
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # 커널 부분도 5,5로 생성하느냐 3,3이냐 하면 그림이 계속 바뀌더라 한번 해봐
    # morph gradient
    imageGradient = cv2.morphologyEx(copy, cv2.MORPH_GRADIENT, kernel)
    print("getGradient")

    return imageGradient

