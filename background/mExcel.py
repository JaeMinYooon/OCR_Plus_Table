from xml.etree.ElementTree import dump
import openpyxl

def make_input(root,data):
    '''data = {
        'name': ['crop_193.jpg','crop_194.jpg','crop_195.jpg' , 'crop_192.jpg','crop_191.jpg','crop_190.jpg','crop_179.jpg','crop_178.jpg','crop_177.jpg'],
        'label': ['독','후','감','지','은','이','김','지','훈']
    }'''
    sheet_heads = root.find('./head').text.split(',')
    #sheet_heads = ['A1','A2','B2','C2','D2','A3','B3','C3','D3']

    # -----------------------------------------------------------------------------
    for cell_name in sheet_heads:
        cell_heads = root.find(cell_name + '/head').text.split(',')
        for text_name in cell_heads:
            if text_name:
                img_list = root.find(cell_name + '/' + text_name).text.split(',')
                replace_list = []
                for img in img_list:
                    if img in data['name']:
                        index = data['name'].index(img)
                        replace_list.append(data['label'][index])
                        #print(replace_list)
                    if img not in data['name']:
                        replace_list.append(" ")
                root.find(cell_name+ '/' + text_name).text = ",".join(replace_list)
    # -----------------------------------------------------------------------------
    dump(root)

    return root

def makeExcel(root, imagePath):
    wb = openpyxl.load_workbook('table.xlsx')
    sheet = wb.active
    sheet.title = "첫번째"
    sheet_heads = root.find('./head').text.split(',')
    #폰트사이즈 좌표평균 인데 적절히 나누기 하면될듯
    #fsize = fontSize / 4)
    for cell_node in sheet_heads:
        cell_heads = root.find(cell_node + '/head').text.split(',')
        text_list = []
        for text_node in cell_heads:
            if text_node:
                img_list = root.find(cell_node + '/' + text_node).text.split(',')
                for img in img_list:
                    if img :
                        text_list.append(img)
            if text_node != cell_heads[len(cell_heads)-1]:
                text_list.append('\n')
            # if not text_node: 셀에 추가 안해도됨 걍 냅두면됨.
        sheet[cell_node] = "".join(text_list)
        cell = sheet[cell_node]
        cell.font = openpyxl.styles.Font(size=16)
        cell.number_format = cell.number_format
        cell.alignment = openpyxl.styles.Alignment(horizontal='center',vertical='center', wrapText=True)
    wb.save(imagePath+'.xlsx')
