import cv2
import numpy as np
import glob,os
from ImageProcessing import *
from Contour import *
from File import *
from MakeTable import *
from Sort import *
from mExcel import *
#from MakeTable.Preprocessing import *

#from TFOCR.TFmain import *


def Cmain(imagePath, type, model=0):
    #imagePath = './Test/t11.jpg'
    #imagePath = 'test4.jpg'

    image = cv2.imread(imagePath+ type)

    fileList = glob.glob("./TableCrop/*"+ type)
    for f in fileList:
        os.remove(f)
    fileList = glob.glob("./TextCrop/*" + type)
    for f in fileList:
        os.remove(f)


    # 글자따기 ================================================================================
    #croppedImages, coordinateList = processImage(imagePath+'.jpg')  # process the image and get cropped screenshot
    croppedImages, coordinateList = processImage(image)  # process the image and get cropped screenshot
    count = 0
    for cropImage in croppedImages:
        count += 1
        saveImage(cropImage, "./TextCrop/crop_" + str(count))
    # ===================    == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == =

    # 표만들기 ================================================================================
    resizeFile(image)
    main_process = Export2Document.Export2Document('document.jpg', verbose='v')
    main_process.process()
    main_process.ocr_by_box()
    main_process.export_to_xlsx()
    index_list = main_process.get_cell_index()

    # ========================================================================================

    # 정렬하기 ================================================================================

    #xmlP(coordinateList)
    print(index_list)
    #fontsize = getFontsize(coordinateList)
    root = set_base_xml(index_list, coordinateList)
    #TFdata = []
    #TFdata = TFmain(model)
    #root = make_input(root, TFdata)
    #makeExcel(root,fontsize)
    makeExcel(root,imagePath)
    main_process = Preprocessing.Preprocessing('document.jpg', verbose='v')
    main_process.process()
    sortImages = main_process.cal_cell_needed()
    #print(sortImages)
    # ========================================================================================

if __name__ == '__main__':
    #model = load_Model()
    Cmain(imagePath='ete1', type='.png')


