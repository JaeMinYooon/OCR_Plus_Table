# TCP server

from socket import *
import socket
import os
import time
import sys
from TextExtract3 import Main

# 이미지 파일 저장경로
src = 'C:/Users/030mp/image/'


def fileName():
    dte = time.localtime()
    Year = dte.tm_year
    Mon = dte.tm_mon
    Day = dte.tm_mday
    WDay = dte.tm_wday
    Hour = dte.tm_hour
    Min = dte.tm_min
    Sec = dte.tm_sec
    imgFileName = src + str(Year) + '_' + str(Mon) + '_' + str(Day) + '_' + str(Hour) + '_' + str(Min) + '_' + str(
        Sec) + '.jpg'
    return imgFileName


model = Main.myMain.load()  # 모델 미리 로딩시켜놓음.

# 서버 소켓 오픈
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("223.194.134.64", 5003))
server_socket.listen(5)

print("TCPServer Waiting for client on port 5010")

while True:

    # 클라이언트 요청 대기중 .
    client_socket, address = server_socket.accept()
    # 연결 요청 성공
    print("I got a connection from ", address)

    data = None

    # Data 수신
    while True:
        img_data = client_socket.recv(1024)
        data = img_data
        if img_data:
            while img_data:
                print("recving Img...")
                img_data = client_socket.recv(6000000)
                data += img_data
                Main.main(model=model, image=data)
            else:
                break

    # 받은 데이터 저장
    # 이미지 파일 이름은 현재날짜/시간/분/초.jpg
    img_fileName = fileName()
    img_file = open(img_fileName, "wb")
    print("finish img recv")
    print(sys.getsizeof(data))
    img_file.write(data)
    img_file.close()
    print("Finish ")



client_socket.close()
print("SOCKET closed... END")