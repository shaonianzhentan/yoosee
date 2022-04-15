import socket
import time
from threading import Thread

class Yoosee():

    def __init__(self, host):
        self.host = host
        self.port = 554
        self.connected = False
        self.ticks = None
        self.client = None
    
    def ptz(self, cmd):
        cmd = cmd.upper()
        if ['UP', 'DOWN', 'LEFT', 'RIGHT'].count(cmd) != 1:
            return
        # 上下翻转，符合操作逻辑
        if cmd == 'UP':
            cmd = 'DOWN'
        elif cmd == 'DOWN':
            cmd = 'UP'
        # 协议命令为DWON，所以要转一下，不知道为啥
        if cmd == 'DOWN':
            cmd = 'DWON'
        # 5秒重置
        if(self.ticks is not None and int(time.time()) - self.ticks > 3) and self.connected == True:
            self.connected = False

        t = Thread(target=self.move, args=(cmd,))
        t.start()

    # 发送数据
    def send(self, data):
        try:
            if self.client is not None:
                self.client.send(data.encode())
        except Exception as ex:
            print(ex)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(30)
        client.connect((self.host, self.port))
        self.client = client
        # 初始数据
        init_data = "SETUP rtsp://" + self.host + "/onvif1/track1 RTSP/1.0\r\n" + \
            "CSeq: 1\r\n" + \
            "User-Agent: LibVLC/2.2.6 (LIVE555 Streaming Media v2016.02.22)\r\n" + \
            "Transport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n\r\n"        
        client.send(init_data.encode())
        time.sleep(2)
        client.send(data.encode())

    def move(self, ptzCmd):
        if self.connected:
            print('正在操作中')
            return
        self.connected = True
        print('Connected', self.host, ptzCmd)
        self.ticks = int(time.time())
        # 发送PTZ命令
        self.send("SET_PARAMETER rtsp://" + self.host + "/onvif1 RTSP/1.0\r\n" + \
            "Content-type: ptzCmd: " + ptzCmd + "\r\n" + \
            "CSeq: 2\r\n" + \
            "Session: 12345678\r\n\r\n")
        # client.close()
        print("我已经退出了，后会无期")
        self.connected = False