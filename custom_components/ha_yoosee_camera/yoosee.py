import socket
import time

class Yoosee():

    def __init__(self, ip):
        self.ip = ip

    async def move(self, host, ptzCmd):
        MaxBytes = 1024 * 1024
        port = 554

        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.settimeout(30)
        client.connect((host,port))

        print('Connected')

        def send(inputData):
            client.send(inputData.encode())

        send("SETUP rtsp://" + host + "/onvif1/track1 RTSP/1.0\r\n" + \
            "CSeq: 1\r\n" + \
            "User-Agent: LibVLC/2.2.6 (LIVE555 Streaming Media v2016.02.22)\r\n" + \
            "Transport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n\r\n")

        while True:
            recvData = client.recv(MaxBytes)
            if not recvData:
                print('接收数据为空，我要退出了')
                break
            localTime = time.asctime( time.localtime(time.time()))
            print(localTime, ' 接收到数据字节数:',len(recvData))
            recvDataStr = recvData.decode()
            print(recvDataStr)
            # 命令发送成功，则退出
            if 'Session: 12345678' in recvDataStr:
                break
            # 发送PTZ命令
            send("SET_PARAMETER rtsp://" + host + "/onvif1 RTSP/1.0\r\n" + \
                "Content-type: ptzCmd: " + ptzCmd + "\r\n" + \
                "CSeq: 2\r\n" + \
                "Session: 12345678\r\n\r\n")
        client.close()
        print("我已经退出了，后会无期")