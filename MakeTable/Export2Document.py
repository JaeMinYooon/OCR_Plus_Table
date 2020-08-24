import xlsxwriter
from MakeTable.OcrByCell import *

class Export2Document(OcrByCell):
#class Export2Document(Preprocessing):
    def __init__(self, img_file, conf_file=None, verbose='vv', workbook='table.xlsx'):
        OcrByCell.__init__(self, img_file, conf_file=conf_file, verbose=verbose)
        # Create an new Excel file and add a worksheet.
        self.workbook = xlsxwriter.Workbook(workbook)

        self.default_format = dict()
        for key in self.config['xlsx_standard']['default_format']:
            self.default_format[key] = self.config['xlsx_standard']['default_format'][key]

    # ==========================================================================
    def export_to_xlsx(self):
        worksheet = self.workbook.add_worksheet()

        worksheet = self.make_base(worksheet)
        worksheet = self.merge_and_input_text(worksheet)

        self.workbook.close()

    # ==========================================================================
    def make_base(self, worksheet):
        """ 셀의 너비나 높이등 기본적인 틀을 구성합니다.
        :param worksheet: 작업할 worksheet
        :return: 작업후의 worksheet
        """
        default_format = self.workbook.add_format(self.default_format)
        # 인덱스가 다 꼬여있기 때문에 height도 뒤죽박죽, 머지전의 데이터가 필요
        for cols in range(0, len(self.before_merged)):
            worksheet.set_row(cols, self.before_merged[cols][0].height, default_format)  # height
            for rows in range(0, len(self.before_merged[cols])):
                present = self.before_merged[cols][rows]
                worksheet.set_column(rows, rows, present.width / 6.5, default_format)  # width/7
        return worksheet

    # ==========================================================================
    def merge_and_input_text(self, worksheet):
        """ Merge된 정보에 따라 Cell들을 Merge하고 OCR로 읽어낸 text를 입력합니다.
        만약, 현재 Cell의 이름과 merged_info의 이름이 같다면 Cell은 Merge되지 않았음을 의미
        그렇지 않다면 Cell이 Merge 되었음을 의미합니다.
        :param worksheet: 작업할 worksheet
        :return: 작업후의 worksheet
        """
        for cols in range(0, len(self.cells)):
            for rows in range(0, len(self.cells[cols])):
                present = self.cells[cols][rows]
                cell_format = self.get_text_attribute(present)
                cell_format.set_text_wrap()
                # not merged
                if present.cell_name == present.merged_info:
                    if not present.text:
                        worksheet.write_blank(present.cell_name, None, cell_format)
                    else:
                        worksheet.write_rich_string(present.cell_name, present.text, cell_format)
                # merged
                else:
                    worksheet.merge_range(present.cell_name + ':' + present.merged_info, None,
                                          cell_format=cell_format)
                    if not present.text:
                        worksheet.write_blank(present.cell_name, None, cell_format)
                    else:
                        worksheet.write_rich_string(present.cell_name, present.text, cell_format)

        return worksheet

    # ==========================================================================
    def get_text_attribute(self, cell):
        boundary = cell.boundary
        top = 0
        bottom = 0
        left = 0
        right = 0
        if boundary['upper']:  # if boundary['upper'] == True
            top = 1  # 1 == Continuous line
        if boundary['lower']:
            bottom = 1
        if boundary['left']:
            left = 1
        if boundary['right']:
            right = 1
        cell_format = self.workbook.add_format({'font_name': 'Calibri', 'font_color': '#000000',
                                                'align': cell.text_align, 'valign': cell.text_valign,
                                                'top': top, 'bottom': bottom, 'left': left, 'right': right,
                                                'font_size': cell.text_height, 'bg_color': cell.bg_color})
        return cell_format
