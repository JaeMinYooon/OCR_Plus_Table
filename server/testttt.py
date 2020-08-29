
text_contours = {
    'x':[],
    'y':[],
    'w':[],
    'h':[]
}
# 1
text_contours['x'].append(50)
text_contours['y'].append(2000)
text_contours['w'].append(100)
text_contours['h'].append(100)
# 2
text_contours['x'].append(75)
text_contours['y'].append(2075)
text_contours['w'].append(30)
text_contours['h'].append(30)
# 3
text_contours['x'].append(150)
text_contours['y'].append(150)
text_contours['w'].append(100)
text_contours['h'].append(100)
# 4
text_contours['x'].append(175)
text_contours['y'].append(175)
text_contours['w'].append(40)
text_contours['h'].append(40)
# 5
text_contours['x'].append(250)
text_contours['y'].append(250)
text_contours['w'].append(100)
text_contours['h'].append(100)
# 6
text_contours['x'].append(275)
text_contours['y'].append(275)
text_contours['w'].append(100)
text_contours['h'].append(100)
# 7
text_contours['x'].append(374)
text_contours['y'].append(2000)
text_contours['w'].append(100)
text_contours['h'].append(100)
# 8
text_contours['x'].append(2000)
text_contours['y'].append(374)
text_contours['w'].append(100)
text_contours['h'].append(100)

remove_list = []

for i in range(len(text_contours['x'])):
    result = [x for x, y in zip(text_contours['x'], text_contours['y']) if
              x < (text_contours['x'][i] + text_contours['w'][i] * 8 / 10) and x > (
                          text_contours['x'][i] * 11 / 10) and y <
              (text_contours['y'][i] + text_contours['h'][i] * 8 / 10) and y > (text_contours['y'][i] * 11 / 10)]
    # result_y = [x for x in text_contours['y'] if
    #             x < text_contours['y'][i] + text_contours['h'][i] and x > text_contours['y'][i]]
    # if result_x and result_y:
    if result:
        # print(result_x, result_y)
        print(result)
        remove_list.append(i)

print(remove_list)

temp = []
temp.append((1,1,1,1))
temp.append((1,1,2,2))
temp.append((1,1,3,3))
print(len(temp))

for x,y,w,h in temp:
    print(x,y,w,h)

