class Cell(object):
    """ Form에서 이루어지는 각각의 cell들의 대한 정보를 저장합니다. """

    def __init__(self):
        ##print('Cell')
        # cells matrix
        self.x = None
        self.y = None
        self.width = None
        self.height = None

        self.central_x = None
        self.central_y = None

        # text info
        self.text = None
        self.text_height = None
        self.text_align = 'center'
        self.text_valign = 'vcenter'

        self.cell_name = None
        self.merged_info = None
        self.bg_color = '#ffffff'

        self.boundary = {
            'left': False,
            'right': False,
            'upper': False,
            'lower': False
        }

    # ==========================================================================
    def _set_value(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.central_x = x + int(width / 2)
        self.central_y = y + int(height / 2)

        #print('test')

    # 재원
    def _get_cell_name(self):
        return self.cell_name

    # 재원
    def _get_cell_value(self):
        return self.x * 4, self.y * 4, self.width * 4, self.height * 4

    # ==========================================================================
    def _get_value(self):
        return self.x, self.y, self.width, self.height, self.central_x, self.central_y

    # ==========================================================================
    def _set_text(self, text, text_height, text_align, text_valign):
        self.text = text
        self.text_height = text_height
        self.text_align = text_align
        self.text_valign = text_valign

    # ==========================================================================
    def _merge_horizontal(self, right_cell):
        """ 가로로 정렬된 Cell들을 merge합니다.
        :param right_cell: 현재 Cell을 기준으로 우측에 위치한 Cell
        """
        self.width += right_cell.width
        self.central_x = self.x + int(self.width / 2)
        self.boundary['right'] = right_cell.boundary['right']
        self.merged_info = right_cell.merged_info

    # ==========================================================================
    def _merge_vertical(self, lower_cell):
        """ 가로로 정렬된 Cell들을 merge합니다.
        :param lower_cell: 현재 Cell을 기준으로 하단에 위치한 Cell
        """


        self.height += lower_cell.height
        self.central_y = self.y + int(self.height / 2)
        self.boundary['lower'] = lower_cell.boundary['lower']
        self.merged_info = lower_cell.merged_info

    # ==========================================================================

    def __repr__(self):
        """ Console로 Cell이 지닌 속성들을 print합니다. """
        s = str()
        s += 'x %d y %d\t|\t' % (self.x, self.y)
        s += 'w %d h %d\t|\t' % (self.width, self.height)

        s += self.cell_name + '\t|\t'

        if self.text is not None:
            s += self.text
        else:
            s += 'None'

        s += '\t\theight: ' + str(self.text_height)
        s += '\talign/valign: ' + self.text_align + '/' + self.text_valign

        s += '\t\t'
        s += str(self.boundary)

        return s
