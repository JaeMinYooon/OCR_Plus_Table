#import pyserver.gray as gray
# TCP server example

import socket
import os
import time
import sys
from Main import *
from TFOCR.TFmain import load_Model
# 이미지 파일 저장경로
src = "D:\\jaewon\\TextExtract3\\"

def fileName():
    dte = time.localtime()
    Year = dte.tm_year
    Mon = dte.tm_mon
    Day = dte.tm_mday
    WDay = dte.tm_wday
    Hour = dte.tm_hour
    Min = dte.tm_min
    Sec = dte.tm_sec
    imgFileName = str(Year) + str(Mon) + str(Day) + str(Hour) + str(Min) + str(Sec) + '.jpg'
    #imgFileName = src + str(Year)+ str(Mon) + str(Day) + str(Hour) + str(Min) + str(Sec) + '.jpg'
    toMain = str(Year)+ str(Mon) + str(Day) + str(Hour) + str(Min) + str(Sec)
    return imgFileName,toMain

def getFileData(fileName, directory):
    with open(directory + "\\" + fileName, 'r', encoding="UTF-8") as f:
        data = ""
        ## 파일이 매번 각 라인을 읽어 리턴할 수 있기 때문에 라인마다 끊어서 저장
        for line in f:
            data += line
    return data
model = load_Model()

# 서버 소켓 오픈
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("223.194.131.27", 5801))
server_socket.listen(5)
print("TCPServer Waiting for client on port 5000")

while True:

    # 클라이언트 요청 대기중 .
    client_socket, address = server_socket.accept()
    # 클라이언트 호스트네임
    # 연결 요청 성공
    print("I got a connection from ", address)

    data = None
    #img_data = client_socket.recv(1024)

    excetionCtrl = False
    # Data 수신
    while True:
        img_data = client_socket.recv(1024)
        data = img_data
        if img_data:
            while img_data:
                print("recving Img...")
                img_data = client_socket.recv(1024)
                data += img_data
            else:
                break

    # 받은 데이터 저장
    # 이미지 파일 이름은 현재날짜/시간/분/초.jpg
    img_fileName, toMain = fileName()
    img_file = open(img_fileName, "wb")
    print("finish img recv")
    print(sys.getsizeof(data))
    img_file.write(data)
    img_file.close()

    print("Finish ")
    #print(toMain)
    #client_socket.send("ok".encode())
    try:
        Cmain(imagePath= toMain ,model=model)
        excetionCtrl = True
        print("성공!")
    except:
        excetionCtrl = False
        print("실패!")
    client_socket.shutdown(socket.SHUT_RD)
    #client_socket.sendall(getFileData(toMain+'.jpg', src))
    if excetionCtrl == True:
        #client_socket.send("ok".encode())
        excel_file = open(toMain+'.xlsx', 'rb')
        l = excel_file.read(1024)
        while(l):
            client_socket.send(l)
            print('sending....')
            l = excel_file.read(1024)
        excel_file.close()

    client_socket.shutdown(socket.SHUT_WR)
    print("보냈는데?")

    #client_socket.shutdown(SHUT_RD)
client_socket.close()
print("SOCKET closed... END")