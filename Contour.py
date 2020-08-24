from Main import *
from ImageProcessing import *
import cv2
import ImageProcessing

def getContours(image):
    ''' 이미지에서 Contour 를 추출하여 반환합니다.
    이미지 처리(Image processing) 단계를 거친 후 contour 를 잘 추출할 수 있습니다.

    :param image: OpenCV의 image 객체 (2 dimension)
    :return: 이미지에서 추출한 co ntours
    '''
    # 이미지로부터 컨투어 찾기
    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def drawContours(imageOrigin, contours): #컨투어 어떻게됐나 보는거
    ''' 이미지에서 찾은 Contour 부분들을 잘라내어 반환합니다.
        각 contour 를 감싸는 외각 사각형에 여유분(padding)을 주어 이미지를 잘라냅니다.

        :param imageOrigin: 원본 이미지
        :param contours: 잘라낼 contour 리스트
        :return: contours 를 기반으로 잘라낸 이미지(OpenCV image 객체) 리스트
        '''
    imageCopy = imageOrigin.copy()  # copy the image to be processed

    sum = 0
    avgCount = 0
    for contoursCount in contours:
        _, _, width, height = cv2.boundingRect(contoursCount)
        if (width < 100 or height < 100) and (width > 20 or height > 20):
            avgCount = avgCount + 1
            sum = sum + width
    avg = sum / avgCount
    print("평균:", avg)

    # avg 값 고쳐주기
    if avg < 30 and avg > 20:
        avg = avg - 10
    elif avg < 40 and avg > 30:
        avg = avg - 20

    for contour in contours:  # Crop the screenshot with on bounding rectangles of contours
        x, y, width, height = cv2.boundingRect(contour)  # top-left vertex coordinates (x,y) , width, height
        # screenshot that are larger than the standard size
        if width > avg - 15 and height > avg - 15 and width < avg + 50 and height < avg + 50:
            cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 2)

    return imageCopy

def croppedContours(imageOrigin, contours): # 실제 자르는거
    ''' 이미지에서 찾은 Contour 부분들을 잘라내어 반환합니다.
    각 contour 를 감싸는 외각 사각형에 여유분(padding)을 주어 이미지를 잘라냅니다.

    :param imageOrigin: 원본 이미지
    :param contours: 잘라낼 contour 리스트
    :return: contours 를 기반으로 잘라낸 이미지(OpenCV image 객체) 리스트
    '''
    imageCopy = imageOrigin.copy()  # copy the image to be processed
    imageGray = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2GRAY)
    dstImg = getThreshold(imageGray)
    # get configs
    padding = 7  # to give the padding when cropping the screenshot
    originHeight, originWidth = imageCopy.shape[:2]  # get image size
    croppedImages = []  # list to save the crop image.
    coordinatesList = []

    sum = 0
    avgCount = 0
    for contoursCount in contours:
        _, _, width, height = cv2.boundingRect(contoursCount)
        if (width < 100 or height < 100) and (width > 20 or height > 20):
            # print(width)
            avgCount = avgCount + 1
            sum = sum + width
    avg = sum / avgCount
    #print("평균:", avg)

    # avg 값 고쳐주기
    if avg < 30 and avg > 20:
        avg = avg - 10
    elif avg < 40 and avg > 30:
        avg = avg - 20


    for contour in contours:  # Crop the screenshot with on bounding rectangles of contours

        x, y, width, height = cv2.boundingRect(contour)  # top-left vertex coordinates (x,y) , width, height
        # screenshot that are larger than the standard size


        if width > avg - 15  and height > avg - 15  and width < avg + 100 and height < avg + 100:
            # ★★★★ 이부분 수정으로 나열해주기 ★★★
            # The range of row to crop (with padding) row 세로 col 가로
            rowFrom = y - padding if (y - padding) > 0 else y
            rowTo = (y + height + padding) if (y + height + padding) < originHeight else y + height
            # The range of column to crop (with padding)
            colFrom = (x - padding) if (x - padding) > 0 else x
            #colFrom = x
            colTo = (x + width + padding) if (x + width + padding) < originWidth else x + width

            coordinatesList.append([x, y, width, height])
            # Crop the image with Numpy Array
            #cropped = imageCopy[rowFrom: rowTo, colFrom: colTo]
            cropped = dstImg[rowFrom: rowTo, colFrom: colTo] #★★★★★
            croppedImages.append(cropped)  # add to the list


    print(coordinatesList)
    return croppedImages, coordinatesList

def getThreshold(imageGray):
    copy = imageGray.copy()

    ret, thresh = cv2.threshold(copy, 127, 255, cv2.THRESH_BINARY_INV)

    return thresh

