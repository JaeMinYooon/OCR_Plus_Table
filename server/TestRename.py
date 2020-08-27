import os

path = './TestCase/'

file_list = os.listdir(path)

print(file_list)
num = 1
for file in file_list:
    if 'jpg' in file:
        os.rename(path+file, path+'testcase'+str(num)+'.jpg')
        num+=1
    if 'png' in file:
        os.rename(path + file, path + 'testcase' + str(num) + '.png')
        num+=1