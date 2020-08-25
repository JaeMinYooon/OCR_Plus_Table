#import pytesseract as ocr
from MakeTable.Preprocessing import *

class OcrByCell(Preprocessing):
    def __init__(self, img_file, conf_file=None, verbose='vv'):
        Preprocessing.__init__(self, img_file, conf_file=conf_file, verbose=verbose)

    # ==========================================================================
    def ocr_by_box(self):
        i = 0
        for cols in range(len(self.cells)):
            for rows in range(len(self.cells[cols])):
                x, y, width, height, _, _ = self.cells[cols][rows]._get_value()
                # separated_img가 원본이미지를 벗어나면 안된다
                if cols == 0 or rows == 0 or cols == len(self.cells) or rows == len(self.cells[cols]):
                    separated_img = self.erased_line[y:y + height, x:x + width]
                else:
                    separated_img = self.erased_line[y - 3:y + height + 3, x - 3:x + width + 3]

                img_for_calculate = self.get_processing_img(separated_img)
                # 분리된 이미지에서 글자영역을 찾아 높이를 계산, 폰트 사이즈를 유추.
                self.cells[cols][rows].text_height = self.get_text_height(img_for_calculate)

                # 분리된 이미지에서 글자영역을 찾아 align, valign을 유추
                self.cells[cols][rows].text_align, self.cells[cols][rows].text_valign \
                    = self.get_text_align(img_for_calculate)

                # 글자영역을 지우고 남은 색상으로 셀 배경색 추출
                self.cells[cols][rows].bg_color = self.get_bg_color(separated_img, img_for_calculate)

                # 잔여 line 및 잡영 제거
                separated_img = self.erase_line_and_noise(separated_img)

                separated_img = self.zoom_image(separated_img)
                separated_img = self.add_white_space(separated_img)
                '''
                Page segmentation modes:
                      0    Orientation and script detection (OSD) only.
                      1    Automatic page segmentation with OSD.
                      2    Automatic page segmentation, but no OSD, or OCR.
                      3    Fully automatic page segmentation, but no OSD. (Default)
                      4    Assume a single column of text of variable sizes.
                      5    Assume a single uniform block of vertically aligned text.
                      6    Assume a single uniform block of text.
                      7    Treat the image as a single text line.
                      8    Treat the image as a single word.
                      9    Treat the image as a single word in a circle.
                     10    Treat the image as a single character.
                     11    Sparse text. Find as much text as possible in no particular order.
                     12    Sparse text with OSD.
                     13    Raw line. Treat the image as a single text line,
                           bypassing hacks that are Tesseract-specific.
                '''
                ''' 재민 수정중
                #★text = ocr.image_to_string(separated_img, lang='kor+eng', config='psm 1')
                text = ocr.image_to_string(separated_img, lang='eng', config='psm 1')
                if not len(text):
                    pass
                else:
                    self.cells[cols][rows].text = text
                    length = len(self.before_merged[cols])
                    for i in range(0, length):
                        temp = self.before_merged[cols][i].central_x
                        if (temp > x and temp < x + width):
                            self.before_merged[cols][i].text = text
                    i += 1
                '''


                ''' 구두점...
                    if not len(text) or (ord(text[0]) < 48 and ord(text[0]) > 32) or (
                        ord(text[0]) < 65 and ord(text[0]) > 57) or (ord(text[0]) < 97 and ord(text[0]) > 90) or (
                        ord(text[0]) < 127 and ord(text[0]) > 122):
                        pass
                '''

        # self.temp_print()

    # ==========================================================================
    def add_white_space(self, img):
        """ OCR 인식률을 높이기 위해 여백을 줍니다.
        만약 분리되고 확대된 이미지가 Orignal_image 의 width, height 보다 크다면
        default값의 여백만 추가해 줍니다.
        :param img: Cell 영역별로 분리되고 확대된 image
        :return: 여백을 추가한 image를 return
        """
        # OCR 인식률을 높이기 위한 여백주기
        h = img.shape[0]
        w = img.shape[1]

        additional_w = self.config['improve_ocr']['additional_width']
        additional_h = self.config['improve_ocr']['additional_height']

        if self.Origin_image.shape[0] > h:
            additional_h = int((self.Origin_image.shape[0] - h) / 2)
        if self.Origin_image.shape[1] > w:
            additional_w = int((self.Origin_image.shape[1] - w) / 2)

        WHITE = [255, 255, 255]
        img = cv2.copyMakeBorder(img, additional_h, additional_h, additional_w,
                                 additional_w, cv2.BORDER_CONSTANT, value=WHITE)

        return img

    # ==========================================================================
    def zoom_image(self, img):
        """ OCR 인식률을 높이기 위해 약간의 확대작업을 수행합니다.
        config.yaml 에서 확대비율을 수정할 수 있습니다.
        :param img: Cell 영역별로 분리된 image
        :return: 확대된 image를 return
        """
        zoom_fx = self.config['improve_ocr']['zoom_fx']
        zoom_fy = self.config['improve_ocr']['zoom_fy']

        img = cv2.resize(img, None, fx=zoom_fx, fy=zoom_fy, interpolation=cv2.INTER_CUBIC)

        return img

    # ==========================================================================
    def get_processing_img(self, img):
        """ 글자영역을 제거하기 위해
        1) Gray-scale 적용
        2) Canny edge 추출 알고리즘 적용
        3) GaussianBlur 적용
        4) dilation 적용
        5) opening 적용
        :param img: Cell 영역별로 분리된 image
        :return: processsed image
        """
        temp_img = img
        imgray = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)

        low_threshold = self.config['canny']['low_threshold']
        high_threshold = self.config['canny']['high_threshold']
        edges = cv2.Canny(imgray, low_threshold, high_threshold)

        blur = cv2.GaussianBlur(edges, (3, 3), 0)

        kernel = np.ones((3, 3), np.uint8)
        dilation = cv2.dilate(blur, kernel, iterations=1)

        opening = cv2.morphologyEx(dilation, cv2.MORPH_OPEN, kernel, iterations=2)
        return opening

    # ==========================================================================
    def get_text_height(self, processed_img):
        """ 글자영역의 contour(윤곽)을 추출하여 높이에 따른 font-size를 유추합니다.
        10px == 7.5pt로 대략적으로 0.75배 처리.
        :param processed_img: 글자영역을 추출하기 위해 처리된 image
        :return: 유추된 font-size 만약 글자영역을 못찾았다면 defalut font-size를 반환
        """
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, _ = cv2.findContours(processed_img, retrieve_mode, approx_method)

        num = 0
        average_h = 0
        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            if (width > 10 and height > 10) and height < processed_img.shape[0] * 0.8:
                average_h += height
                num += 1
        if num:
            return int((average_h / num) * 0.75)  # 10px == 7.5pt
        else:
            return 11

    # ==========================================================================
    def detect_blank(self, processed_img):
        """ 글자영역을 기준으로 상하좌우 여백의 size를 구하여 반환합니다.
        :param processed_img: 글자영역을 추출하기 위해 처리된 image
        :return: 상하좌우의 여백길이
        """
        # todo 최소값을 반환하기 때문에 줄글로 이어져있는 텍스트(text)에 부적합, 개선된 알고리즘 필요
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, _ = cv2.findContours(processed_img, retrieve_mode, approx_method)

        origin_h = processed_img.shape[0]
        origin_w = processed_img.shape[1]

        upper_blank = 1000
        below_blank = 1000
        left_blank = 1000
        right_blank = 1000

        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            if width > 10 and height > 10:
                contour_upper = y
                contour_below = origin_h - (y + height)
                contour_left = x
                contour_right = origin_w - (x + width)

                if upper_blank > contour_upper:
                    upper_blank = contour_upper
                if below_blank > contour_below:
                    below_blank = contour_below
                if left_blank > contour_left:
                    left_blank = contour_left
                if right_blank > contour_right:
                    right_blank = contour_right

        return upper_blank, below_blank, left_blank, right_blank

    # ==========================================================================
    def get_text_align(self, processed_img):
        """ Cell 내부의 텍스트(text)에 대해 좌우 정렬과 상하 정렬을 유추하여 반환합니다.
        :param processed_img: 글자영역을 추출하기 위해 처리된 image
        :return: 유추된 상하, 좌우의 text align
        """
        upper_blank, below_blank, left_blank, right_blank = self.detect_blank(processed_img)

        align = 'center'
        valign = 'vcenter'
        if max(upper_blank, below_blank) > min(upper_blank, below_blank) * 2:
            if min(upper_blank, below_blank) == upper_blank:
                # valign 상단 정렬
                valign = 'top'
            else:
                # valign 하단 정렬
                valign = 'bottom'
        if max(left_blank, right_blank) > min(left_blank, right_blank) * 2:
            if min(left_blank, right_blank) == left_blank:
                # align 좌측 정렬
                align = 'left'
            else:
                # align 우측 정렬
                align = 'right'

        return align, valign

    # ==========================================================================
    def get_bg_color(self, img, processed_img):
        """ Cell에서 글자영역을 찾아 흰색(b,g,r = 255)으로 지우고, Cell의 모든 픽셇의 값을 검사하여,
        배경셀의 색상을 유추합니다.
        :param img: 원본에서 분리된 이미지
        :param processed_img: 글자영역을 추출하기 위해 처리된 image
        :return: HEX COLOR로 변환한 색상값
        """
        temp_image = np.copy(img)
        retrieve_mode = self.config['contour']['retrieve_mode']
        approx_method = self.config['contour']['approx_method']
        contours, _ = cv2.findContours(processed_img, retrieve_mode, approx_method)

        origin_h = temp_image.shape[0]
        origin_w = temp_image.shape[1]

        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            cv2.rectangle(temp_image, (x, y), (x + width, y + height), (255, 255, 255), cv2.FILLED)

        mean_b = 0
        mean_g = 0
        mean_r = 0
        tmp = 0

        ten_percent_h = int(origin_h * 0.1)
        ten_percent_w = int(origin_w * 0.1)

        for y in range(ten_percent_h, origin_h - ten_percent_h):
            for x in range(ten_percent_w, origin_w - ten_percent_w):
                if temp_image.item(y, x, 0) != 255 and temp_image.item(y, x, 1) != 255 \
                        and temp_image.item(y, x, 2) != 255:
                    mean_b += int(temp_image.item(y, x, 0))  # b
                    mean_g += int(temp_image.item(y, x, 1))  # g
                    mean_r += int(temp_image.item(y, x, 2))  # r
                    tmp += 1
        if not tmp:
            return '#ffffff'  # HEX 'WHITE'
        else:
            mean_b = int(np.ceil(mean_b / tmp))
            mean_g = int(np.ceil(mean_g / tmp))
            mean_r = int(np.ceil(mean_r / tmp))
            if mean_b > 245 and mean_g > 245 and mean_r > 245:
                return '#ffffff'

            else:
                # RGB to HEX
                return '#{:02x}{:02x}{:02x}'.format(mean_r, mean_g, mean_b)

    # ==========================================================================
    def erase_line_and_noise(self, img):
        """ HoughlineP 메소드를 이용하여 긴 line을 제거하고,
        Canny edge 추출 알고리즘을 이용하여 필요한 부분(text 영역)을 제외한 부분을 흰색으로 noise 를 지워낸다.
        :param img: 원본에서 Cell 영역별로 분리된 이미지
        :return: 긴 line과 노이즈를 지운 이미지
        """
        line_image = img * 0

        low_threshold = self.config['canny']['low_threshold']
        high_threshold = self.config['canny']['high_threshold']
        edges = cv2.Canny(img, low_threshold, high_threshold)

        rho = self.config['houghline']['rho']  # distance resolution in pixels of the Hough grid
        theta = np.pi / 180  # angular resolution in radians of the Hough grid
        threshold = self.config['houghline']['threshold']  # minimum number of votes (intersections in Hough grid Cell)
        min_line_length = min(img.shape[0], img.shape[1]) * 0.7  # minimum number of pixels making up a line
        max_line_gap = 0  # maximum gap in pixels between connectable line segments

        lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                                min_line_length, max_line_gap)
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), 2)

        kernel = np.ones((3, 3), np.uint8)
        closing = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=4)
        dilation = cv2.dilate(closing, kernel, iterations=2)

        img = cv2.addWeighted(img, 1, line_image, 1, 0)
        dilation = cv2.cvtColor(~dilation, cv2.COLOR_GRAY2BGR)

        img = cv2.addWeighted(img, 1, dilation, 1, 0)

        return img

    # ==========================================================================
    '''
    def temp(self, img):
        ## 글자영역 추출 알고리즘
        temp_img = img

        imgray = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(imgray, 100, 200)

        blur = cv2.GaussianBlur(edges, (3, 3), 0)

        kernel = np.ones((3, 3), np.uint8)
        dilation = cv2.dilate(blur, kernel, iterations=2)

        opening = cv2.morphologyEx(dilation, cv2.MORPH_OPEN, kernel, iterations=2)

        _, contours, hierarchy = cv2.findContours(opening, cv2.RETR_CCOMP, 2)

        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)

            if width > 15 and height > 15:
                opening = cv2.rectangle(opening, (x, y), (x + width, y + height), (255, 0, 0, 50), 1)

                cv2.imshow('contoursssss', opening)
                cv2.waitKey(0)

                separated_img = temp_img[y:y + height, x:x + width]

                separated_img = cv2.resize(separated_img, None, fx=2, fy=3, interpolation=cv2.INTER_CUBIC)

                WHITE = [255, 255, 255]
                separated_img = cv2.copyMakeBorder(separated_img, 100, 100, 100, 100, cv2.BORDER_CONSTANT, value=WHITE)

                text = ocr.image_to_string(separated_img, lang='kor+eng')
                if not len(text):
                    pass
                else:
                    print('temp :\t', text)
                    cv2.imshow('tmp', separated_img)
                    cv2.waitKey(0)
    '''
