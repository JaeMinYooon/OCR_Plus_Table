import os
import cv2
import numpy as np
import collections
import matplotlib.pyplot as plt

def main():
    dirPath = './TextCrop/'
    flist = os.listdir(dirPath)
    toPath = './delNoise/'
    print(flist)
    i=0
    white_list = []
    black_list = []
    name_list = []
    for file in flist:
        if 'txt' in file:
            continue
        img = cv2.imread(dirPath+file)
        w,h,_ = img.shape
        x = int(w*2/10)
        y = int(h*2/10)
        cutImg = img[x:w-x,y:h-y]

        black = 0
        white = 0
        for ida in range(len(cutImg)):
            for idb in range(len(cutImg[ida])):
                for idc in range(len(cutImg[ida][idb])):
                    if cutImg[ida][idb][idc] < 10:
                        black+=1
                    elif cutImg[ida][idb][idc] > 245:
                        white +=1
        # print("white : ", white)
        # print("black : ", black)
        white_list.append(white)
        black_list.append(black)
        name_list.append(dirPath+file)
        # black_list.append(0)
        # cv2.imshow("test", cutImg)
        # cv2.waitKey(0)

    for idx in range(len(white_list)):
        # if white_list[idx] < 6000 and black_list[idx] > 7000:
        # if white_list[idx] < 6000 and black_list[idx] < 2200:
        iimg = cv2.imread(name_list[idx])

        w, h, c = iimg.shape
        x = int(w * 2 / 10)
        y = int(h * 2 / 10)
        cutImg = iimg[x:w - x, y:h - y]
        w, h ,c = cutImg.shape
        percent = black_list[idx]/(w*h*c)
        if percent >=0.89:
            print(name_list[idx])
            print(white_list[idx], black_list[idx])
            print("percent => ", percent)
            cv2.imshow("test", cutImg)
            cv2.waitKey(0)

    plt.figure()
    plt.ylabel('black')
    plt.xlabel('white')
    plt.scatter(white_list, black_list)
    # plt.scatter(textinfo['width'], textinfo['height'])
    plt.show()

if __name__=='__main__':
    main()