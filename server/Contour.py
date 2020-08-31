from Main import *
from ImageProcessing import *
import cv2
import ImageProcessing

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import seaborn as sns
import pandas as pd

def getContours(image):
    ''' 이미지에서 Contour 를 추출하여 반환합니다.
    이미지 처리(Image processing) 단계를 거친 후 contour 를 잘 추출할 수 있습니다.

    :param image: OpenCV의 image 객체 (2 dimension)
    :return: 이미지에서 추출한 co ntours
    '''
    # 이미지로부터 컨투어 찾기
    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def drawTextContours(imageOrigin, contours): #컨투어 어떻게됐나 보는거
    ''' 이미지에서 글자들의 크기 분포를 확인하여 클러스터링 합니다.
    군집별 편차가 비 정상적인 경우 글자가 아니라고 판단합니다.

    :param imageOrigin:
    :param contours:
    :return:
    '''
    imageCopy = imageOrigin.copy()  # copy the image to be processed
    textinfo = {
        'width':[],
        'height':[],
        'x':[],
        'y':[]
    }
    for contour in contours:  # Crop the screenshot with on bounding rectangles of contours
        x, y, width, height = cv2.boundingRect(contour)  # top-left vertex coordinates (x,y) , width, height
        # screenshot that are larger than the standard size
        textinfo['width'].append(width)
        textinfo['height'].append(height)
        textinfo['x'].append(x)
        textinfo['y'].append(y)

        # if width > avg - 15 and height > avg - 15 and width < avg + 50 and height < avg + 50:
        #     cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 2)

        # cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 2)
    df = pd.DataFrame(textinfo, columns=['width', 'height','x','y'])
    data_points = df.values

    # imginfo_df = df[np.logical_and(df['width'] < 150 , df['height']<100)]
    # for i, row in imginfo_df.iterrows():
    #     print(str(df.at[i, 'width'])+"  "+str(df.at[i, 'height']))
    #     cv2.imshow("title", imageCopy[df.at[i,'y']:df.at[i,'y']+df.at[i,'height'], df.at[i,'x']:df.at[i,'x']+df.at[i,'width'] ])
    #     cv2.waitKey(0)

    kmeans = KMeans(n_clusters=2).fit(data_points)
    # print(kmeans.labels_)

    plt.figure()
    plt.scatter(textinfo['width'], textinfo['height'])
    plt.show()
    df['cluster_id'] = kmeans.labels_
    sns.lmplot('width','height', data=df, fit_reg=False, scatter_kws={"s":150}, hue="cluster_id")
    plt.title("kmean plot")
    #
    plt.show()

    return None
def drawContours(imageOrigin, contours,flag): #컨투어 어떻게됐나 보는거
    '''
        전체 컨투어 되는 것에 사각형 그리는 메소드
    '''
    imageCopy = imageOrigin.copy()  # copy the image to be processed

    sum = 0
    avgCount = 0
    for contoursCount in contours:
        _, _, width, height = cv2.boundingRect(contoursCount)
        # if (width < 100 or height < 100) and (width > 20 or height > 20):
        #     avgCount = avgCount + 1
        #     sum = sum + width
        avgCount = avgCount + 1
        sum = sum + width
    avg = sum / avgCount
    print("평균:", avg)
    for contour in contours:  # Crop the screenshot with on bounding rectangles of contours
        x, y, width, height = cv2.boundingRect(contour)  # top-left vertex coordinates (x,y) , width, height
        # screenshot that are larger than the standard size

        # if width > avg - 15 and height > avg - 15 and width < avg + 50 and height < avg + 50:
        #     cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 2)
        if flag==1:
            # if
            if width> avg and height > avg:
                if width > height:
                    if height >= width * 80 / 100 :
                        cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 3)
                    else:
                        if height < avg:
                            continue
                        it_n = int(width / (height*8/10))
                        for it in range(it_n):
                            cv2.rectangle(imageCopy, (x, y), (x + int(width/it_n) , y + height), (127, 25, 10), 3)
                            x += int(width/it_n)
                else:
                    if width >= height * 7 / 10 and width < avg*10 and height < avg*10:
                        cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 3)
            # if width > 35 and height > 35 and width < 70 and height < 70:
            #     cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 3)
        else:
            cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 3)

    return imageCopy,_

def getTextContours(imageOrigin, contours,flag): #컨투어 어떻게됐나 보는거
    '''
        이미지에서 글자 컨투어 부분만 사각형 그리는 메소드

        :param imageOrigin: 원본 이미지
        :param contours: 잘라낼 contour 리스트
        :return: contours 를 기반으로 잘라낸 이미지(OpenCV image 객체) 리스트
        '''
    imageCopy = imageOrigin.copy()  # copy the image to be processed

    sum = 0
    avgCount = 0
    for contoursCount in contours:
        _, _, width, height = cv2.boundingRect(contoursCount)
        # if (width < 100 or height < 100) and (width > 20 or height > 20):
        #     avgCount = avgCount + 1
        #     sum = sum + width
        avgCount = avgCount + 1
        sum = sum + width
    avg = sum / avgCount
    print("평균:", avg)
    avg = 70
    text_contours = {
        'x':[],
        'y':[],
        'w':[],
        'h':[]
    }

    info_for_crop = []

    for contour in contours:  # Crop the screenshot with on bounding rectangles of contours
        x, y, width, height = cv2.boundingRect(contour)  # top-left vertex coordinates (x,y) , width, height
        # screenshot that are larger than the standard size

        # if width > avg - 15 and height > avg - 15 and width < avg + 50 and height < avg + 50:
        #     cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 2)
        if flag==1 or flag==2:
            # if
            if width> avg/2 and height > avg/2 :
                if width > height:
                    if height >= width * 80 / 100 :
                        text_contours['x'].append(x)
                        text_contours['y'].append(y)
                        text_contours['w'].append(width)
                        text_contours['h'].append(height)
                        # cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 3)
                    else:
                        if height < avg/2 or height > avg * 3.5 or width > avg * 10 or (height>avg*2 and width>avg*2):
                        # if height < avg or height > avg*3.5 or width > avg * 10:
                            continue
                        # it_n = int(width / (height*8/10))
                        # for it in range(it_n):
                        #     # cv2.rectangle(imageCopy, (x, y), (x + int(width/it_n) , y + height), (127, 25, 10), 3)
                        text_contours['x'].append(x)
                        text_contours['y'].append(y)
                        text_contours['w'].append(width)
                        text_contours['h'].append(height)
                        #     x += int(width/it_n)
                else:
                    if width >= height * 4 / 10 and (height<avg*3 or width<avg*3):
                    # if width >= height * 7 / 10 and (width < avg*3.5 or height < avg*3.5):
                        # cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 3)
                        text_contours['x'].append(x)
                        text_contours['y'].append(y)
                        text_contours['w'].append(width)
                        text_contours['h'].append(height)


            # if width > 35 and height > 35 and width < 70 and height < 70:
            #     cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 3)
        # else:
        #     cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 3)
    if flag==2:
        for i in range(len(text_contours['x'])):
            x = text_contours['x'][i]
            y = text_contours['y'][i]
            width = text_contours['w'][i]
            height = text_contours['h'][i]
            cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (127, 25, 10), 3)

    if flag ==1:
        remove_list = []
        for i in range(len(text_contours['x'])):
            result = [x for x, y in zip(text_contours['x'], text_contours['y']) if
                        x < (text_contours['x'][i] + text_contours['w'][i]*90/100 ) and x > (text_contours['x'][i]+ text_contours['w'][i]*5/100 ) and y <
                        (text_contours['y'][i] + text_contours['h'][i]*90/100 ) and y > (text_contours['y'][i]+ text_contours['h'][i]*5/100) ]
            if result:
                remove_list.append(i)
        remove_list = sorted(remove_list)
        for i in reversed(remove_list):
            del text_contours['x'][i]
            del text_contours['y'][i]
            del text_contours['w'][i]
            del text_contours['h'][i]

        remove_list.clear()

        for i in range(len(text_contours['x'])):
            x = text_contours['x'][i]
            y = text_contours['y'][i]
            width = text_contours['w'][i]
            height = text_contours['h'][i]

            # 5% 만큼 글자보다 넓게 영역을 확보함
            width_weight = int(width * 3 / 100)
            height_weight = int(height * 3 / 100)

            newX = int(x-width_weight)
            newY = int(y-height_weight)
            if width > avg/2 and height > avg/2:
                if width > height:
                    if height >= width * 90 / 100:
                        cv2.rectangle(imageCopy, (newX, newY), (newX + width+ width_weight*2, newY + height + height_weight*2), (127, 25, 10), 3)
                        cv2.rectangle(imageCopy, (newX, newY), (newX + int(avg), newY + int(avg)), (50, 50, 200), 3)
                        info_for_crop.append((newX,newY,newX + width+ width_weight*2, newY + height + height_weight))
                    else:
                        # if height < avg or height > avg * 3.5 or width > avg * 10:
                        if height < avg/2 or height > avg * 3.5 or width > avg * 10 or (height>avg*2 and width>avg*2):
                            continue
                        it_n = int(width / (height*7/10))
                        if width > height*2.9:
                            it_n = int(width / (height * 8.15 / 10))
                        for it in range(it_n):
                            cv2.rectangle(imageCopy, (newX, newY), (newX + int(width/it_n) +width_weight , newY + height +height_weight), (127, 25, 10), 3)
                            cv2.rectangle(imageCopy, (newX, newY), (newX + int(avg), newY + int(avg)), (50, 50, 200), 3)
                            info_for_crop.append((newX, newY, newX + int(width/it_n) +width_weight , newY + height +height_weight))
                            newX += int(width/it_n)
                else:
                    # if width >= height * 7 / 10 and (width < avg*3.5 or height < avg*3.5):
                    if width >= height * 4 / 10 and (height<avg*3 or width<avg*3):
                        cv2.rectangle(imageCopy, (newX, newY), (newX + width + width_weight*2, newY + height+ height_weight*2), (127, 25, 10), 3)
                        cv2.rectangle(imageCopy, (newX, newY), (newX + int(avg), newY + int(avg)), (50, 50, 200), 3)
                        info_for_crop.append((newX,newY,newX + width+ width_weight*2, newY + height + height_weight))

    return imageCopy, info_for_crop

def getTitleContours(imageOrigin, contours): #컨투어 어떻게됐나 보는거
    '''
        임시 test -> 가장 큰 폰트사이즈 (세금계산서) 따려고 만든 메소드
    '''
    imageCopy = imageOrigin.copy()  # copy the image to be processed

    info_for_crop = []
    max = (1,1,1,1)
    for contour in contours:  # Crop the screenshot with on bounding rectangles of contours
        x, y, width, height = cv2.boundingRect(contour)  # top-left vertex coordinates (x,y) , width, height
        # screenshot that are larger than the standard size
        cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (50, 50, 200), 3)

        if width>height and width> max[2]*9/10 and height>max[3]*9/10:
            if height > width*9/10:
                max = (x,y,width,height)
        elif height>width and width> max[2]*9/10 and height>max[3]*9/10:
            if width> height*9/10:
                max = (x,y,width,height)

    for contour in contours:  # Crop the screenshot with on bounding rectangles of contours
        x, y, width, height = cv2.boundingRect(contour)  # top-left vertex coordinates (x,y) , width, height
        if width>=height and width<=max[2]*2.5:
            if (height>=max[3]*9/10 and height<=max[3]*10.5/10):
                if width>=max[2]*1.8:
                    it_n = int(width / (height * 9 / 10))
                    for it in range(it_n):
                        cv2.rectangle(imageCopy, (x, y), (x + int(width/it_n) , y + height), (50, 200, 50), 3)
                        info_for_crop.append((x, y, int(width/it_n), height))
                        x += int(width/it_n)
                    continue
            # if (height>=max[3]*9/10 and height<=max[3]*10.5/10):
                info_for_crop.append((x, y, width, height))
                cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (50, 200, 50), 3)

        elif height>= width and height<=max[3]*10.3/10:
            if (width>=max[2]*9/10 and width<=max[2]*10.5/10):
                info_for_crop.append((x, y, width, height))
                cv2.rectangle(imageCopy, (x, y), (x + width, y + height), (50, 200, 50), 3)

    return imageCopy,info_for_crop

def testErosion(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    imageErosion = cv2.erode(image, kernel, iterations=1)

    return imageErosion

def croppedContourss(imageOrigin, info_for_crop): # 실제 자르는거
    ''' 이미지에서 찾은 Contour 부분들을 잘라내어 반환합니다.
    각 contour 를 감싸는 외각 사각형에 여유분(padding)을 주어 이미지를 잘라냅니다.

    :param imageOrigin: 원본 이미지
    :param contours: 잘라낼 contour 리스트
    :return: contours 를 기반으로 잘라낸 이미지(OpenCV image 객체) 리스트
    '''
    imageCopy = imageOrigin.copy()  # copy the image to be processed
    imageGray = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2GRAY)
    dstImg = getThreshold(imageGray)
    dstImg = testErosion(dstImg)
    # cv2.imshow("testt", cv2.resize(dstImg, dsize=(0, 0), fx=0.2, fy=0.2, interpolation=cv2.INTER_LINEAR))
    # cv2.waitKey(0)
    # get configs
    padding = 7  # to give the padding when cropping the screenshot
    originHeight, originWidth = imageCopy.shape[:2]  # get image size
    croppedImages = []  # list to save the crop image.
    coordinatesList = []
    i=0
    for info in info_for_crop:  # Crop the screenshot with on bounding rectangles of contours
        i+=1
        x, y, width, height = info  # top-left vertex coordinates (x,y) , width, height
        # print(x,y,width,height)
        cropped = dstImg[y: height, x: width] #★★★★★
        croppedImages.append(cropped)  # add to the list

    # print(coordinatesList)
    return croppedImages, info_for_crop

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


        # if width > avg - 15  and height > avg - 15  and width < avg + 100 and height < avg + 100:
        if width> 35 and height > 35 and width < 70 and height < 70:
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


    # print(coordinatesList)
    return croppedImages, coordinatesList

def deleteInfoInTitleArea(titleInfo, contourInfo):
    remove_list = []
    for title_x,title_y,title_w,title_h in titleInfo:
        fromX = title_x - (title_w*4/10)
        fromY = title_y - (title_h*4/10)
        toX = fromX + (title_w*18/10)
        toY = fromY + (title_h*18/10)
        print("title info ", title_x, title_y, title_w, title_h)
        for i in range(len(contourInfo) ):
            if contourInfo[i][0] < toX and contourInfo[i][0] > fromX and contourInfo[i][1] < toY and contourInfo[i][1] > fromY:
                if i not in remove_list:
                    remove_list.append(i)
    remove_list = sorted(remove_list)
    print(remove_list)
    # for a in remove_list:
    #     print(contourInfo[a])
    for i in reversed(remove_list):
        print(contourInfo[i])
        del contourInfo[i]
        print(len(contourInfo))
    # for a in remove_list:
    #     print(contourInfo[a])

    for x,y,w,h in titleInfo:
        contourInfo.append((x,y,x+w,y+h))
        # print(x,y,w,h)

    return contourInfo

def deleteBlank(img, info):
    imageCopy = img.copy()
    imageGray = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2GRAY)
    dstImg = getThreshold(imageGray)
    print("dstImg")
    print(dstImg.shape)
    removeList = []

    black_list = []
    white_list = []

    for idx, (fromX, fromY, toX, toY) in enumerate(info):
        width = toX - fromX
        height = toY - fromY

        # weight from x // weight to x
        wfx = int(fromX + width*2/10)
        wtx = int(toX - width*2/10)
        wfy = int(fromY + height*2/10)
        wty = int(toY - height*2/10)

        cutImg = dstImg[wfy:wty, wfx:wtx]
        cutWidth = wtx-wfx
        cutHeight = wty-wfy
        black = 0
        white = 0

        for ida in range(len(cutImg)):
            for idb in range(len(cutImg[ida])):
                if cutImg[ida][idb] < 10:
                    black+=1
                elif cutImg[ida][idb] > 245:
                    white +=1
        blackPercent = black/(cutWidth*cutHeight)
        black_list.append(black)
        white_list.append(white)

        if blackPercent >= 0.89:
            # cv2.imshow("bbbbb", cutImg)
            # cv2.waitKey(0)
            removeList.append(idx)
    removeList = sorted(removeList)

    # plt.figure()
    # plt.ylabel('black')
    # plt.xlabel('white')
    # plt.scatter(white_list, black_list)
    # # plt.scatter(textinfo['width'], textinfo['height'])
    # plt.show()

    for idx in reversed(removeList):
        del info[idx]

    return info


def finalDraw(img, info):
    imageCopy = img.copy()
    for x,y,w,h in info:
        cv2.rectangle(imageCopy, (x, y), (w, h), (50, 200, 50), 3)
    return imageCopy

def getThreshold(imageGray):
    copy = imageGray.copy()

    ret, thresh = cv2.threshold(copy, 127, 255, cv2.THRESH_BINARY_INV)

    return thresh

