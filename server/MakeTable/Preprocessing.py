import os
import cv2
import yaml
import numpy as np
from string import ascii_uppercase
from MakeTable.Cell import *
from MakeTable.File import *

class Preprocessing(object):
    def __init__(self, img_file, conf_file=None, verbose='v'):
        if img_file:
            if not os.path.exists(img_file):
                raise IOError('Cannot find image file "%s"' % img_file)
        self.img_file = img_file
        self.img = cv2.imread(img_file)  # 작업용 이미지

        # self.img = resizeFile(self.img)
        # self.img = img_file  # 작업용 이미지
        #★self.img = cv2.imread('hi.png')
        ####### image_warping 전처리 ############
        #self.img = self.image_warping()
        #self.img = self.resize_image(self.img)
        #######################################

        #self.Origin_image = cv2.imread(img_file)
        self.Origin_image = self.img.copy()
        self.line_image = self.img * 0  # image that only lines will be drawn
        self.erased_line = None  # image that will be erased  with white color
        self.closing_line = None

        # original image's width & height
        self.origin_height, self.origin_width = self.Origin_image.shape[:2]

        if not conf_file:
            # 디폴트는 현재 패키지 위치의 config.yaml 파일을 읽음
            conf_file = '%s/config.yaml' \
                        % os.path.abspath(os.path.dirname(__file__))
            if not os.path.exists(conf_file):
                raise IOError('Cannot find config file "%s"' % conf_file)
        self.config_str = None
        self.config = self._read_config(conf_file)

        # 꼭 필요한 row, col에 대한 리스트
        self.final_x = None
        self.final_y = None

        # 추출된 셀들 사이 가장 작은 width, height
        self.find_min_width = None
        self.find_min_height = None

        # cell의 정보를 가지고 있음
        self.cells = None
        self.before_merged = None

        self.verbose = verbose

    # ==========================================================================
    def image_warping(self):
        orig = self.img.copy()
        r = 800.0 / self.img.shape[0]
        dim = (int(self.img.shape[1] * r), 800)
        self.img = cv2.resize(self.img, dim, interpolation=cv2.INTER_AREA)

        imgray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        imgray = cv2.GaussianBlur(imgray, (3, 3), 0)
        edged = cv2.Canny(imgray, 75, 200)

        contours, hierarchy = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:3]

        image = np.copy(self.img)

        for contour in contours:
            perl = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perl, True)

            if len(approx) == 4:
                screenCnt = approx
                break

        cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)

        rect = self.order_points(screenCnt.reshape(4, 2) / r)

        (topLeft, topRight, bottomRight, bottomLeft) = rect

        w1 = abs(bottomRight[0] - bottomLeft[0])
        w2 = abs(topRight[0] - topLeft[0])
        h1 = abs(topRight[1] - bottomRight[1])
        h2 = abs(topLeft[1] - bottomLeft[1])

        maxWidth = max([w1, w2])
        maxHeight = max([h1, h2])

        # dst = np.float32([[0, 0], [maxWidth + 10, 0], [maxWidth + 10, maxHeight - 1], [0, maxHeight - 1]])
        # 맨 오른쪽 칸
        dst = np.float32([[0, 0], [maxWidth -1, 0], [maxWidth-1, maxHeight - 1], [0, maxHeight - 1]])
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))

        self.img = warped
        return warped

    # ==========================================================================
    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)

        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    # ==========================================================================
    '''
    def resize_image(self, img):
        """ 촬영된 이미지는 사이즈가 큼 """
        if img.shape[0] > 2000 or img.shape[1] > 2000:
            r = 600.0 / self.img.shape[0]
            dim = (int(self.img.shape[1] * r), 600)
            img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

            cv2.imshow('resize', img)
            cv2.waitKey(0)
        print('resize되는가?')
        return img
    '''

    def resize_image(self):
        """ 촬영된 이미지는 사이즈가 큼 """
        img = cv2.imread(self.img_file)
        if img.shape[0] > 2000 or img.shape[1] > 2000:
            r = 600.0 / img.shape[0]
            dim = (int(img.shape[1] * r), 600)
            img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            self.img = img
            # cv2.imshow('resize', img)
            # cv2.waitKey(0)
        print('resize되는가?')
    # ==========================================================================
    def _read_config(self, config_file):
        """ .yaml file 을 읽어서 configuration 값의 객체를 갖습니다.

        :param config_file:
        :return: 읽은 configuration 을 담고있는 dictionary 형태로 반환
        """
        # read contents from .yam config file
        with open(config_file, 'r', encoding='UTF-8') as ifp:
            self.config_str = ifp.read()
        with open(config_file, 'r', encoding='UTF-8') as ifp:
            return yaml.safe_load(ifp)

    # ==========================================================================
    def _show_img(self, title, target_img):
        temp_img = np.copy(target_img)
        if self.verbose.startswith('v'):
            if self.origin_width > 1000 or self.origin_height > 1000:
               temp_img = cv2.resize(temp_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            # cv2.imshow(title, temp_img)
            # cv2.waitKey(0)
            cv2.imwrite('./data/result/' + title + '.png', temp_img)

    # ==========================================================================
    def _get_threshold(self, imgray, mode):
        """ 이미지에 Threshold 를 적용해서 이진(Binary) 이미지 객체를 반환합니다.
        이미지의 글자와 line이 적절히 나누어 지도록 mode에 따라 parameter값이 달라집니다.
        :param mode: mode에 따라서 low, high_threshold의 값이 달라집니다.
        """

        low_threshold = self.config[mode]['low_threshold']
        high_threshold = self.config[mode]['high_threshold']
        thr_type = self.config[mode]['thr_type']

        ret, thr = cv2.threshold(imgray, low_threshold, high_threshold, thr_type)
        # th2 = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 2)
        # th3 = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
        return thr

    # ==========================================================================
    def boxing_ambiguous(self):
        """ 이미지에서 line이 위아래만 적용되어 있거나, 경계선이 그려져 있지 않고 색상으로 경계된 Cell등의
        모호한 경계에 대해 강제로 경계를 그려줍니다.
        """
        imgray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        mode = 'boxing'
        thr = self._get_threshold(imgray, mode)

        min_width = self.config['contour']['min_width']
        min_height = self.config['contour']['min_height']
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, hierarchy = cv2.findContours(thr, retrieve_mode, approx_method)

        i = 0
        # first contour detection for making line clarify
        for contour in contours:
            # top-left vertex coordinates (x,y) , width, height
            x, y, width, height = cv2.boundingRect(contour)

            # adjacent pixels bgr median, darkness++
            mid_b = 0
            mid_g = 0
            mid_r = 0
            j = 0
            for my in range(y - 2, y + 3):
                for mx in range(x - 2, x + 3):
                    if (my and mx) >= 0 and (my < self.img.shape[0]) and (mx < self.img.shape[1]):
                        mid_b += int(self.img.item(my, mx, 0))  # b
                        mid_g += int(self.img.item(my, mx, 1))  # g
                        mid_r += int(self.img.item(my, mx, 2))  # r
                        j += 1
            mid_b = (mid_b / j) * 0.7  # strengthen darkness
            mid_g = (mid_g / j) * 0.7
            mid_r = (mid_r / j) * 0.7

            # Draw rectangle with median bgr
            # larger than the half of original image size
            if width > self.origin_width * 0.5 or height > self.origin_height * 0.5:
                self.img = cv2.rectangle(self.img, (x + 1, y + 1), (x + width - 1, y + height - 1),
                                         (mid_b, mid_g, mid_r, 50), 2)
                i += 1
                continue
            if (width > min_width and height > min_height) and ((hierarchy[0, i, 2] != -1 or hierarchy[0, i, 3] == (
                    len(hierarchy) - 2 or len(hierarchy) - 1)) or cv2.arcLength(contour, True) > 1000):
                # child가 없는 contour(최내곽)이 아니거나 parent가 최외곽 or 최외곽-1인 contour
                # 또는 arc length > 1000 이상
                self.img = cv2.rectangle(self.img, (x - 1, y - 1), (x + width + 1, y + height + 1),
                                         (mid_b, mid_g, mid_r, 50), 2)
            i += 1
        self._show_img('_strengthen_img', self.img)

    # ==========================================================================
    def detect_contours(self):
        """ 경계선이 강화된 이미지에 다시 한 번 Contour(윤곽)을 찾아 표에 대한 경계를 찾아냅니다.
        찾아낸 경계를 까만(b,g,r = 0)이미지에 흰색(b,g,r = 255)의 사각형을 그려 line만 있는 line_image를 만듭니다.
        """
        # repeat contour detection
        imgray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        mode = 'detect'
        thr = self._get_threshold(imgray, mode)

        min_width = self.config['contour']['min_width']
        min_height = self.config['contour']['min_height']
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, hierarchy = cv2.findContours(thr, retrieve_mode, approx_method)

        i = 0
        # Draw rectangle with white color
        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)

            if width > self.origin_width * 0.5 or height > self.origin_height * 0.5:
                self.line_image = cv2.rectangle(self.line_image, (x, y), (x + width, y + height), (255, 255, 255, 50),
                                                2)
            if (width > min_width and height > min_height) and ((hierarchy[0, i, 2] != -1 or hierarchy[0, i, 3] == (
                    len(hierarchy) - 2 or len(hierarchy) - 1)) or cv2.arcLength(contour, True) > 1000):
                self.line_image = cv2.rectangle(self.line_image, (x, y), (x + width, y + height), (255, 255, 255, 50),
                                                2)
            i += 1

        self._show_img('_line_img', self.line_image)

    # ==========================================================================
    def erase_line(self):
        """ 흰색으로 그려진 Line_image를 Original_imgae에 덮어 씌워 경계를 지워줍니다."""
        # image that will be erased with white color
        # self.closing_line = cv2.cvtColor(self.closing_line, cv2.COLOR_GRAY2BGR)
        self.erased_line = cv2.addWeighted(self.Origin_image, 1, self.closing_line, 1, 0)
        self._show_img('_erased_img', self.erased_line)
        x,y,_ = self.img.shape
        wrap_line_image = self.closing_line[:x, :y]
        wrap_line_image = cv2.resize(wrap_line_image, (y*4, x*4), interpolation=cv2.INTER_AREA )
        # self.erased_line = cv2.addWeighted(self.img, 1, self.closing_line, 1, 0)
        self._show_img('_wrap_erased_img', wrap_line_image)

    # ==========================================================================
    '''
    def detect_line(self):
        img = self.line_image

        low_threshold = self.config['canny']['low_threshold']
        high_threshold = self.config['canny']['high_threshold']
        edges = cv2.Canny(img, low_threshold, high_threshold)

        rho = self.config['houghline']['rho']  # distance resolution in pixels of the Hough grid
        theta = np.pi / 180  # angular resolution in radians of the Hough grid
        threshold = self.config['houghline']['threshold']  # minimum number of votes (intersections in Hough grid Cell)
        min_line_length = min(self.origin_height, self.origin_width) * 0.2  # minimum number of pixels making up a line
        max_line_gap = min(self.origin_height,
                           self.origin_width) * 0.08  # maximum gap in pixels between connectable line segments

        lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                                min_line_length, max_line_gap)

        for line in lines:
            for x1, y1, x2, y2 in line:
                if x1 == x2 or y1 == y2:
                    cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 1)

        self._show_img('detect_line', self.line_image)
    '''
    # ==========================================================================
    def brightness(self): #지금 0.4 - 60 완벽 0.3 - 50 까지 완벽.
        image = self.img

        '''
        # RGB 영상은 [0,255] 범위에 해당하는 픽셀이 존재, 우리가 생각하는 연산과 다름.
        # 연산 후 0보다 작은 것은 0으로, 255보다 큰것은 255로 바꿔주게 됨.
        print("max of 255: {}".format(cv2.add(np.uint8([200]), np.uint8([100]))))
        print("min of 0: {}".format(cv2.subtract(np.uint8([50]), np.uint8([100]))))

        # numpy는 255보다 커지면 0부터 다시 세기 시작, 0보다 작아지면 255부터 다시 세기 시작.
        print("wrap around: {}".format(np.uint8([200]) + np.uint8([100])))
        print("wrap around: {}".format(np.uint8([50]) - np.uint8([100])))
        '''
        # 밝게하기(원본보다 100만큼 밝게(최대 255))
        control = np.ones(image.shape, dtype="uint8") * 60
        brightnessImage = cv2.add(image, control)
        self.img = brightnessImage


    # ==========================================================================
    def morph_closing(self):
        """ Line_image에서 Line과 Line사이에 존재하는 공간을 Morph Close기법을 이용하여 매꿔줍니다.
        Line과 Line사이에 존재하는 공간은 실제 라인이 존재하는 공간이기 때문에 필요한 Cell들을 계산할 때 필요하지 않습니다.
        """
        # for line_image
        kernel_row = self.config['closing']['kernel_size_row']
        kernel_col = self.config['closing']['kernel_size_col']
        kernel = np.ones((kernel_row, kernel_col), np.uint8)

        closing_iter = self.config['closing']['iteration']

        self.closing_line = cv2.morphologyEx(self.line_image, cv2.MORPH_CLOSE, kernel, iterations=closing_iter)

        self._show_img('_closing_line_img', self.closing_line)

    # ==========================================================================
    def cal_cell_needed(self):
        """ Closing 된 line_image에서 다시 한 번 cv2.findContour()를 적용하여 필요한 x,y axis 들을 계산합니다.
        """
        # 재민 도전중 ★★★★★★★★★★★★★★★★★★★★
        croppedImages = []
        sortImages = []
        image = cv2.imread(self.img_file)

        imgray = cv2.cvtColor(self.closing_line, cv2.COLOR_BGR2GRAY)
        mode = 'default_threshold'
        thr = self._get_threshold(imgray, mode)

        min_width = self.config['contour']['min_width']
        min_height = self.config['contour']['min_height']
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, hierarchy = cv2.findContours(thr, retrieve_mode, approx_method)

        needed_x = []
        needed_y = []
        find_min_width = self.config['num_of_needed_cell']['find_min_width']
        find_min_height = self.config['num_of_needed_cell']['find_min_height']

        for contour in contours:
            # top-left vertex coordinates (x,y) , width, height
            x, y, width, height = cv2.boundingRect(contour)
            if find_min_width > width and width > min_width:
                find_min_width = width
            if find_min_height > height and height > min_height:
                find_min_height = height
            # Draw screenshot that are larger than the standard size
            if width > min_width or height > min_height:
                #self.line_image = cv2.rectangle(self.line_image, (x, y), (x + width, y + height), (255, 0, 0, 50), 2)
                needed_x.append(x)
                needed_x.append(x + width)
                needed_y.append(y)
                needed_y.append(y + height)
                ## 여기서부터 자르기 도전 ★★★★★★★★★★★★★★★★★★★★★★★★★★
                cropped = self.img[y: y+height, x: x+width]
                sortImages.append([x * 4, y * 4, width * 4, height * 4])
                croppedImages.append(cropped)
        count = 0
        #print('표')
        #print(sortImages)

        ## 이것도 도전중인 포문★★★★★★★★★★★★★★
        for cropImage in croppedImages:
            count += 1
            imageSave(cropImage, "./TableCrop/crop_" + str(count))


        # num of needed cells
        needed_x = sorted(list(set(needed_x)))  # list(set(my_list)) --> 중복제거
        needed_y = sorted(list(set(needed_y)))

        self.find_min_width = find_min_width
        self.find_min_height = find_min_height

        # contour와 contour사이의 선은 cell로 취급할 필요가 없음
        # 가장 작은 contour rectangle의 width와 height를 기준으로 유사한 값을 압축
        # print("***")
        # print(needed_x, ", ", needed_y)
        self.final_x = self.approx_axis(needed_x, int(find_min_width * 0.5), 0)
        self.final_y = self.approx_axis(needed_y, int(find_min_height * 0.5), 1)

        self.draw_axis()

        return sortImages
    '''
    # ★★★★★★★★★★★★★★★★★★★★★★★ 내가만든함수
    def imageSave(image, namePrefix='crop'):
        filePath = namePrefix + ".jpg"
        cv2.imwrite(filePath, image)
    '''
    # ==========================================================================


    def draw_axis(self):
        if self.verbose.startswith('vv'):

            #tmp_img1 = np.copy(self.line_image) 재민 도전중 사이즈 맞추기
            #tmp_img2 = np.copy(self.erased_line) 재민 도전중 사이즈 맞추기
            tmp_img1 = np.copy(self.img)
            tmp_img2 = np.copy(self.img)

            for x in self.final_x:
                cv2.line(tmp_img1, (x, 0), (x, self.origin_height), (0, 0, 255), 2)
            for y in self.final_y:
                cv2.line(tmp_img1, (0, y), (self.origin_width, y), (0, 0, 255), 2)
            self._show_img('_draw_axis', tmp_img1)

            for x in self.final_x:
                cv2.line(tmp_img2, (x, 0), (x, self.origin_height), (0, 0, 255), 2)
            for y in self.final_y:
                cv2.line(tmp_img2, (0, y), (self.origin_width, y), (0, 0, 255), 2)
            self._show_img('_draw_axis', tmp_img2)

    # ==========================================================================
    # if self.origin_width 부분 수정 - 재원
    def approx_axis(self, needed_axis, find_min_axis, flag):

        """ 효율적으로 필요한 axis의 개수를 구하기 위해 list의 값들을 압축합니다.
        :param needed_axis: cal_cell_needed 메소드에서 구한 필요한 x 또는 y axis의 list
        :param find_min_axis: x, y axis list를 압축하기 위한 임계 값
        :return: 압축된 x,y axis list
        """
        h,w,_ = self.img.shape
        final_axis = set()
        temp_int = needed_axis[0]
        num_temp_int = 1
        for a in range(1, len(needed_axis)):
            if needed_axis[a] - needed_axis[a - 1] < find_min_axis:
                temp_int += needed_axis[a]
                num_temp_int += 1
            else:
                final_axis.add(int(temp_int / num_temp_int))
                num_temp_int = 1
                temp_int = needed_axis[a]
        final_axis.add(int(temp_int / num_temp_int))
        if min(final_axis) > find_min_axis:
            final_axis.add(0)
        if self.origin_width - max(final_axis) > find_min_axis:
            if(flag==0):
                if(self.origin_width<w and self.origin_width>=0):
                    final_axis.add(self.origin_width)
            else:
                if(self.origin_width<h and self.origin_width>=0):
                    final_axis.add(self.origin_width)

        final_axis = sorted(list(final_axis))  # len(final_axis) - 1 개의 셀이 필요함
        return final_axis

    # ==========================================================================
    def save_cell_value(self):

        """ 현재까지 추출해낸 각각의 Cell들의 x, y, width, height 의 값들과
        Excel(엑셀)로 게워내기 좀 더 편리하도록 각 Cell에 알파벳과 숫자로 이루어진 이름을 입력합니다.
        """
        self.cells = [[Cell() for rows in range(len(self.final_x) - 1)] for cols in
                      range(len(self.final_y) - 1)]
        # for rows in range(len(self.final_x) - 1):
        #     for cols in range(len(self.final_y) - 1):
        #
        #         self.cells.add(Cell())
        h,w,_ = self.img.shape
        # print("%%%"+str(h)+" "+str(w))
        h,w,_ = self.line_image.shape
        # print("%%%"+str(h)+" "+str(w))
        self.before_merged = [[Cell() for rows in range(len(self.final_x) - 1)] for cols in
                              range(len(self.final_y) - 1)]

        for cols in range(len(self.final_y)-1):
            for rows in range(len(self.final_x) - 1):
                x = self.final_x[rows]
                y = self.final_y[cols]

                width = self.final_x[rows + 1] - self.final_x[rows]
                height = self.final_y[cols + 1] - self.final_y[cols]

                self.cells[cols][rows]._set_value(x, y, width, height)

                self.before_merged[cols][rows]._set_value(x, y, width, height)
                if rows < 26:
                    self.cells[cols][rows].cell_name = ascii_uppercase[rows] + "%d" % (cols + 1)
                    self.cells[cols][rows].merged_info = ascii_uppercase[rows] + "%d" % (cols + 1)
                    self.before_merged[cols][rows].cell_name = ascii_uppercase[rows] + "%d" % (cols + 1)
                else:
                    self.cells[cols][rows].cell_name = ascii_uppercase[int(rows/26)-1] + ascii_uppercase[rows%26] + "%d" % (cols + 1)
                    self.cells[cols][rows].merged_info = ascii_uppercase[int(rows/26)-1] + ascii_uppercase[rows%26] + "%d" % (cols + 1)

                # 본인의 cell_name과 merged_info가 같으면 머지 되지 않은 것


    # ==========================================================================
    def find_cell_boundary(self):
        """ line_image를 기준으로 각 Cell의 중심 좌표에서 상하좌우로 흰색(b,g,r = 255)값이 있는지 판별합니다.
        만약 흰색값이 있다면 경계(boundary)가 있는 것으로 판별합니다.
        """
        for cols in range(len(self.final_y) - 1):
            for rows in range(len(self.final_x) - 1):
                x, y, width, height, central_x, central_y = self.cells[cols][rows]._get_value()
                if rows == 0:
                    self.cells[cols][rows].boundary['left'] = True
                if rows == len(self.final_x) - 1:
                    self.cells[cols][rows].boundary['right'] = True
                if cols == 0:
                    self.cells[cols][rows].boundary['upper'] = True
                if cols == len(self.final_y) - 1:
                    self.cells[cols][rows].boundary['lower'] = True

                # 'white'의 b != 0
                for left in range(x + 1, central_x):
                    if self.line_image.item(central_y, left, 0) != 0:
                        self.cells[cols][rows].boundary['left'] = True
                        break
                for right in range(x + width - 1, central_x, -1):
                    if self.line_image.item(central_y, right, 0) != 0:
                        self.cells[cols][rows].boundary['right'] = True
                        break
                for upper in range(y + 1, central_y):
                    if self.line_image.item(upper, central_x, 0) != 0:
                        self.cells[cols][rows].boundary['upper'] = True
                        break
                for lower in range(y + height - 1, central_y, -1):
                    if self.line_image.item(lower, central_x, 0) != 0:
                        self.cells[cols][rows].boundary['lower'] = True
                        break

    # ==========================================================================
    def merge_cell(self):
        self.merge_cell_horizontal()
        self.merge_cell_vertical()

        if self.verbose.startswith('vv'):
            #tmp_img = np.copy(self.erased_line) 재민 도전중 사이즈 맞추기
            tmp_img = np.copy(self.img)
            cols_range = len(self.cells)
            for cols in range(cols_range):
                rows_range = len(self.cells[cols])
                for rows in range(rows_range):
                    x, y, width, height, _, _ = self.cells[cols][rows]._get_value()
                    cv2.rectangle(tmp_img, (x, y), (x + width, y + height),
                                  (255, 0, 0, 50), 2)

            self._show_img('_cell_merged', tmp_img)

    # ==========================================================================
    def merge_cell_horizontal(self):
        """ 좌우로 열거된 Cell들에 대해 merge 작업을 수행합니다.
        만약 현재 Cell의 우측 경계가 있거나, 우측 Cell의 좌측 경계가 있다면 경계가 있는 것으로 인식하고,
        그렇지 않다면 경계가 없는 것으로 인식, merge 작업을 수행합니다.
        """
        cols_range = len(self.cells)
        for cols in range(cols_range):
            rows_range = len(self.cells[cols])
            rows_flag = 0
            for rows in range(rows_range - 1):
                rows -= rows_flag

                now_b = self.cells[cols][rows].boundary
                right_b = self.cells[cols][rows + 1].boundary

                # todo 경계가 명확하지 않은 Cell에 대해 좌우 양 끝단에 있는 Cell을 나누어 줘야함
                if now_b['right'] or right_b['left']:
                    # 오른쪽 경계 있음
                    continue
                else:
                    if (now_b['upper'] == right_b['upper']) or (now_b['lower'] == right_b['lower']):
                        # merge horizontal
                        self.cells[cols][rows]._merge_horizontal(self.cells[cols][rows + 1])
                        del self.cells[cols][rows + 1]
                        rows_flag += 1
                        rows_range -= 1

                    else:
                        continue

                ''' 이건 셀 안의 셀의 경계를 나눠버림....
                                elif ((not now_b['lower']) and right_b['lower']) or (now_b['lower'] and (not right_b['lower'])):
                                    # 아래 경계가 없으면서 우측 셀은 아래 경계를 지닐 때
                                    continue
                                elif ((not now_b['upper']) and right_b['upper']) or (now_b['upper'] and (not right_b['upper'])):
                                    # 위 경계가 없으면서 우측 셀은 위 경계를 지닐 때
                                    continue
                                '''

    # ==========================================================================
    def merge_cell_vertical(self):
        """ 상하로 열거된 Cell들에 대해 merge 작업을 수행합니다.
        만약 현재 Cell의 하단 경계가 있거나, 하단 Cell의 상단 경계가 있다면 경계가 있는 것으로 인식하고,
        그렇지 않다면 경계가 없는 것으로 인식, merge 작업을 수행합니다.
        """
        # todo 현재 merge algorithm(알고리즘)은 merge_horizontal 이후 인덱스 다 꼬이게 됨
        # 고민해서 더 나은 algorithm(알고리즘)을 설계해야함

        for cols in range(len(self.cells)):
            for rows in range(len(self.cells[cols])):
                now = self.cells[cols][rows]
                merge_flag = False

                for tmp_col in range(cols + 1, len(self.cells)):
                    for tmp_row in range(len(self.cells[tmp_col])):
                        if tmp_col == cols + 1 or (tmp_col != cols + 1 and merge_flag):
                            tmp_cell = self.cells[tmp_col][tmp_row]
                            if (now.x == tmp_cell.x) and (now.width == tmp_cell.width) and (
                                    now.y + now.height == tmp_cell.y):
                                if now.boundary['lower'] or tmp_cell.boundary['upper']:
                                    continue
                                else:
                                    now._merge_vertical(tmp_cell)
                                    del self.cells[tmp_col][tmp_row]
                                    merge_flag = True
                                    break
                            else:
                                continue
                    if tmp_col == cols + 1 and not merge_flag:
                        break

    # 재원
    '''
    def get_cell_index(self):
        cell_index_list = {
            'index': [],
            'value': []
        }
        for cols in range(len(self.cells) - 1):
            cell_index_list['index'].append([])
            cell_index_list['value'].append([])
            for rows in range(len(self.cells[cols])):
                if rows == len(self.cells[cols]) - 1:
                    if self.cells[cols][rows].boundary['right'] == False:
                        continue
                if cols == len(self.cells) - 1:
                    if self.cells[cols][rows].boundary['lower'] == False:
                        continue
                if self.cells[cols][rows]._get_cell_name() is not None:
                    cell_index_list['index'][cols].append(self.cells[cols][rows]._get_cell_name())
                    cell_index_list['value'][cols].append(self.cells[cols][rows]._get_cell_value())
        return cell_index_list
        '''

    def get_cell_index(self):
        cell_index_list = {
            'index': [],
            'value': []
        }
        for cols in range(len(self.cells)):
            for rows in range(len(self.cells[cols])):
                if rows == len(self.cells[cols]) - 1:
                    if self.cells[cols][rows].boundary['right'] == False:
                        continue
                if cols == len(self.cells) - 1:
                    if self.cells[cols][rows].boundary['lower'] == False:
                        continue

                if self.cells[cols][rows]._get_cell_name() is not None:
                    cell_index_list['index'].append(self.cells[cols][rows]._get_cell_name())
                    cell_index_list['value'].append(self.cells[cols][rows]._get_cell_value())
        return cell_index_list
    # ==========================================================================

    def process(self):
        #img = cv2.imread(self.img_file)
        #self.resize_image(img)
        #self.resize_image()
        # cv2.imshow("tt", self.img)

        self.image_warping()
        self.brightness()

        self.boxing_ambiguous()
        self.detect_contours()
        self.morph_closing()
        self.erase_line()
        #self.detect_line()
        self.cal_cell_needed()
        self.save_cell_value()
        self.find_cell_boundary()
        self.merge_cell()

    # ==========================================================================
    def temp_print(self):
        """ cell's info printing method for debugging
        """
        for cols in range(len(self.cells)):
            for rows in range(len(self.cells[cols])):
                print(self.cells[cols][rows])