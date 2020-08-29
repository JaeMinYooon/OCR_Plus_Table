import os
import cv2
import numpy as np

def main():
    dirPath = './TextCrop/'
    flist = os.listdir(dirPath)
    toPath = './delNoise/'
    print(flist)
    i=0
    for file in flist:
        if 'txt' in file:
            continue
        if i==0:
            i+=1
            continue
        img = cv2.imread(dirPath+file)
        # cv2.imshow("before", img)
        # cv2.waitKey(0)

        img = getBrightness(img)
        # cv2.imshow("getBrightness", img)
        # cv2.waitKey(0)

        img = getGrayImage(img)
        # cv2.imshow("getGrayImage", img)
        # cv2.waitKey(0)

        img = getAdaptiveThreshold(img)
        # cv2.imshow("getAdaptiveThreshold", img)
        # cv2.waitKey(0)

        img = getErosion(img)
        # cv2.imshow("erosion", cv2.resize(img, dsize=(0, 0), fx=2, fy=2, interpolation=cv2.INTER_LINEAR))
        # cv2.waitKey(0)

        # img = getOpening(img)
        # cv2.imshow("getOpening", cv2.resize(img, dsize=(0, 0), fx=3, fy=3, interpolation=cv2.INTER_LINEAR))
        # cv2.waitKey(0)

        cv2.imwrite(toPath+file, img)

        # img = getErosion(img)
        # cv2.imshow("erosion", cv2.resize(img, dsize=(0, 0), fx=3, fy=3, interpolation=cv2.INTER_LINEAR))
        # cv2.waitKey(0)
        #
        # img = getClosing(img)
        # cv2.imshow("getClosing", cv2.resize(img, dsize=(0, 0), fx=3, fy=3, interpolation=cv2.INTER_LINEAR))
        # cv2.waitKey(0)

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

def getGrayImage(image):
    copyGray = image.copy()
    imageGray = cv2.cvtColor(copyGray, cv2.COLOR_BGR2GRAY)

    return imageGray

def getBrightness(image):
    # 밝게하기(원본보다 100만큼 밝게(최대 255))
    control = np.ones(image.shape, dtype="uint8") * 80
    brightnessImage = cv2.add(image, control)
    return brightnessImage

def getDilation(image, ksize=(5,5)):
    #  3,3 으로 설정하면 작은글자 나옴
    #  5,5 = 엥간한 작은 글자들 // testcase9(5,5하면 다나옴)
    #  8,8 이상에 정사각형 잡으면 세금계산서만 나옴 // testcase9(8,8이상) testcase7(8,8만)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize)
    imageDilation = cv2.dilate(image, kernel, iterations=2)

    return imageDilation

def getErosion(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    imageErosion = cv2.erode(image, kernel, iterations=0)

    return imageErosion

def getOpening(imageGray):
    ''' 이미지에 Morph Close 를 적용한 이미지객체를 반환합니다.
    이미지에 Dilation 수행을 한 후 Erosion 을 수행한 것입니다.
    이 때 인자로 입력되는 이미지는 Gray-scale 이 적용된 2차원 이미지여야 합니다.
    configs 에 의해 kernel size 값을 설정할 수 있습니다.

    :param imageGray: Gray-scale 이 적용된 OpenCV image (2 dimension)
    :return: Morph Close 를 적용한 흑백(Binary) 이미지
    '''
    copy = imageGray.copy()

    # make kernel matrix for dilation and erosion
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    # closing (dilation and erosion)
    imageOpen = cv2.morphologyEx(copy, cv2.MORPH_OPEN, kernel, iterations=2) #iterations가 반복 but 현재는 안쓰는게 good

    return imageOpen

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
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    # closing (dilation and erosion)
    imageClose = cv2.morphologyEx(copy, cv2.MORPH_CLOSE, kernel, iterations=2) #iterations가 반복 but 현재는 안쓰는게 good

    return imageClose

if __name__=='__main__':
    main()