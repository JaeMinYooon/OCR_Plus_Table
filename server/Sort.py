import pandas as pd
from xml.etree.ElementTree import Element, dump, SubElement
import numpy as np

def getFontsize(coordinateList):
    df = pd.DataFrame(coordinateList)
    fsize = df.iloc[:,2].mean(axis=0)
    return fsize

def set_base_xml(index_list, all_text_list):
    root = Element("Sheet")
    df = pd.DataFrame(all_text_list)
    SubElement(root, 'head').text = ",".join(index_list['index'])
    for i, i_name in enumerate(index_list['index']):

        #if i_name == 'B5':
        sort_text, df = sort_in_cell(index_list['value'][i],df)

        #셀 노드 추가
        cell_element = Element("".join(map(str, i_name)))
        root.append(cell_element)
        head_list = []
        for i in range(len(sort_text)):
            head_list.append(i+1)
        #if sort_text:
        SubElement(cell_element,'head').text = ",".join(map(str, head_list))
        #셀노드의 텍스트 노드 추가 없으면 빈 노드가 됨.
        for i in range(len(sort_text)):
            SubElement(cell_element, str(i+1)).text = ",".join(sort_text[i])
        #SubElement(root, "".join(map(str, i_name))).text = ",".join(sorted_text[i])

    indent(root)
    dump(root)
    return root

def judge_linebreak(slice_df):
    lineCtrl_for_Y = 50
    sameline_range = 30
    minY = 0
    line_num = 1

    if slice_df.empty == False:
        df_for_Ysort = pd.DataFrame(slice_df[slice_df.iloc[:, 1] > minY])
        df_for_Ysort = df_for_Ysort.sort_values(by=df_for_Ysort.columns.values[1], axis=0)
        #if len(df_for_Ysort.values) != 1:
        if df_for_Ysort[df_for_Ysort.iloc[:, 1] > df_for_Ysort.iloc[0, 1] + 30].empty == False:
            avg_height = round(df_for_Ysort.iloc[:, 3].mean())
            allow_range = avg_height + lineCtrl_for_Y
            minY = int(df_for_Ysort.iloc[0, 1])
            next_minY = int(df_for_Ysort[df_for_Ysort.iloc[:, 1] > minY + sameline_range].iloc[:,1].min(axis=0))

            if next_minY - minY <= allow_range:
                while (True):
                    if next_minY - minY > allow_range or next_minY == minY:
                        break
                    else:
                        minY = next_minY
                        if df_for_Ysort[df_for_Ysort.iloc[:, 1] > next_minY + sameline_range].empty == True:
                            next_minY = minY
                        else:
                            next_minY = int(df_for_Ysort[df_for_Ysort.iloc[:, 1] > minY + sameline_range].iloc[:, 1].min(axis=0))
                        line_num += 1
    return line_num

def judge_spacebreak(df_for_Xsort):
    # [연 감 공 문 상] 이라 쳤을때 공연, 감상문 이여야 하는데 명백히 연 & 감 사이에는 공백이 큼
    # 그 공백을 알아내려는 while문임 --  공연ㅁ감상문 이라 표현하겠음 ㅁ 은 공백
    # 글자수가 (공연 = 2 이고) ==  (공연ㅁ 도 2잖아?) 그럼 break해서 뒤에 글자가 더 없구나? 확인
    # 근데 그럼 [공연감상문]으로 돼 있다 생각하면 (공연 = 2) != (공연감 =3 ) 이니까 2개로 끝날게 아니라 뒤에 글자가 더 있구나? 생각하는거
    word_num = 1
    if len(df_for_Xsort.values) != 1:
        avg_width = round(df_for_Xsort.iloc[:, 2].mean())
        allow_range = avg_width + 25
        if allow_range < 90:
            allow_range += 5
        if allow_range > 100:
            allow_range -= 5
        minX = int(df_for_Xsort.iloc[0, 0])
        next_minX = int(df_for_Xsort.iloc[1, 0])
        if next_minX - minX <= allow_range:
            while (True):
                if next_minX - minX > allow_range or next_minX == minX:
                    break
                else:
                    # minX = int(df_for_Xsort.iloc[word_num, 0].min(axis=0))
                    minX = next_minX
                    if len(df_for_Xsort.values) == word_num + 1:
                        next_minX = minX
                        # next_minX = int(df_for_Xsort.iloc[word_num, 0].min(axis=0))
                    else:
                        next_minX = int(df_for_Xsort.iloc[word_num + 1, 0].min(axis=0))
                    word_num += 1
    else:
        minX = int(df_for_Xsort.iloc[0, 0])
    return minX

def slice_dataframe(x,y,w,h,df):
    sliced_df = pd.DataFrame(df[np.logical_and(df.iloc[:, 0] > x, df.iloc[:, 0] < x + w)])
    sliced_df = pd.DataFrame(sliced_df[np.logical_and(sliced_df.iloc[:, 1] > y, sliced_df.iloc[:, 1] < y + h)])

    return sliced_df

def sort_in_cell(cell_info, df):
    x,y,w,h = cell_info
    slice_df = slice_dataframe(x,y,w,h, df)
    line_num = judge_linebreak(slice_df)

    sameline_range = 30
    cols = 0
    minY = 0
    # 이 while문이 Y값 내려가는건데 지금 맨밑에 break 걸어놔서 첫번째꺼만 돌려봤음 2번째부터 되는지는 모름.
    sort_List = []
    #sort_List.append([])
    while (True):
        if slice_df.empty == True:
            break

        minX = 0
        #수정 df -> slice_df

        sort_List.append([])
        # 컨투어에서 받아온 리스트에서 Y제일작은값 부터 돌리는거
        # 다음 줄로 넘어갈 때 다음 줄에 대해서 Y 정렬해야하니까 ' > minY ' 이렇게 주고 계속 minY값이 바뀌는거.
        #수정
        df_for_Ysort = pd.DataFrame(slice_df[slice_df.iloc[:, 1] > minY])
        df_for_Ysort = df_for_Ysort.sort_values(by=df_for_Ysort.columns.values[1], axis=0)

        # minY 값이 계속 바뀌는거임 그 줄의 최소 Y값
        minY = df_for_Ysort.iloc[0,1]

        # 얘는 같은 줄이더라도 Y값이 좀 다르잖아? 보정치를 넣은 리스트라고 보면됨.  지금은 spaceCtrl로 보정치 주는데 X랑 같은 변수 쓰는데
        # 나중에 따로 만들어야함 X랑 Y는 오차 범위가 확연히 다르니까
        df_sortedY = pd.DataFrame(slice_df[slice_df.iloc[:, 1] <= minY+ sameline_range])
        df_for_Xsort = pd.DataFrame(df_sortedY[df_sortedY.iloc[:, 0] >= minX])

        while (True):
            # 줄넘겨야하는 cols면 줄넘김.
            if cols == line_num and line_num != 1:
                #sort_List[cols].append("Line")
                break
            # 한 줄에 [연 감 공 문 상]있다 쳤을때 공연 꺼내고 리스트를 [감 문 상]으로 만들고 다시 재배치
            # 다 꺼냈을때 empty면 그 줄 멈춤
            if df_for_Xsort.empty == True:
                sort_List[cols].pop()
                break
            # 줄넘김 했으면, 새로운 list줄 만들어줘야함
            if cols == line_num and line_num != 1:
                sort_List.append([])


            df_for_Xsort = df_for_Xsort.sort_values(by=df_for_Xsort.columns.values[0], axis=0)
            minX = judge_spacebreak(df_for_Xsort)

            # 1 2 3 -> 1,2? ㅇㅋ
            # 얘는 붙어있는 글자만 뽑아쓰는 리스트임
            df_sortedX = pd.DataFrame(df_for_Xsort[df_for_Xsort.iloc[:, 0] <= minX])

            # 여기 for문에서 글자수 만큼 xml에 파싱하는거 rowList에 crop뒤에 숫자담고 xml의 root의 하위 노드로 넣는거
            # 그리고 나는 지금 글자를 추출하면 삭제하는 방식으로 한댔잖아? 그래서 전체 리스트, x에 관한리스트에서 하나씩 뽑음
            # 내가 Y를 밑줄로 내려가면서 하는건 아직 안돌려봤는데 Y도 이 작업이 필요하다고 생각함.
            for i in range(len(df_sortedX.values)):
                xIndex = df_sortedX.iloc[:, 0].idxmin()
                sort_List[cols].append("crop_"+str(xIndex+1)+".jpg")
                #sort_List[cols].append(str(xIndex + 1))
                df = df.drop(int(xIndex))
                slice_df = slice_df.drop(int(xIndex))
                df_sortedX = df_sortedX.drop(int(xIndex))
                df_for_Xsort = df_for_Xsort.drop(int(xIndex))

            sort_List[cols].append(" ")

        cols += 1
    return sort_List,df


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i