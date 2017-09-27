# coding=utf8

import thread
import socket
import struct
import serial
import wiringpi as wiringpi
from time import sleep;

x = 0
y = 0

# 二进制数据包格式
package = "!BBiiB"

# 16路舵机控制板物理设备
steering_engine_device = "/dev/ttyACM0"

# 舵机控制命令模板
steering_engine_command = "#9P%(p1)d#15P%(p2)dT1000\r\n"

# 监听端口
listen_port = 1500

# 监听地址
listen_address = "192.168.199.121"

# 左边马达 GPIO 编号
left_motor_pin = 18

# 右边马达 GPIO 编号
right_motor_pin = 18


class Camera:
    p1 = 1500
    p2 = 1500
    ser = 0;

    def __init__(self):
        self.ser = serial.Serial(steering_engine_device, 9600, timeout=1)

        # 初始化云台动作
        command = steering_engine_command % {'p1': 2400, 'p2': 600}
        self.send(command)
        sleep(2)

        # 云台移动到默认位置
        command = steering_engine_command % {'p1': self.p1, 'p2': self.p2}
        self.send(command)

    def send(self, command):
        self.ser.write(command.encode())

    def move(self, x, y):
        x = 0 - x

        # 舵机位置限定（上下左右各预留100防止碰撞）
        pp1 = self.p1 - x
        if (pp1 > 2400):
            pp1 = 2400
        if (pp1 < 600):
            pp1 = 600
        self.p1 = pp1

        pp2 = self.p2 - y
        if (pp2 > 2400):
            pp2 = 2400
        if (pp2 < 600):
            pp2 = 600
        self.p2 = pp2

        command = steering_engine_command % {'p1': self.p2, 'p2': self.p1}
        print command
        self.send(command)

        return


class Montor:
    pin = 0

    def __init__(self, pin):
        self.pin = pin
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(self.pin, 1)
        wiringpi.digitalWrite(self.pin, 0)
        wiringpi.pwmSetClock(2)
        wiringpi.softPwmCreate(self.pin, 0, 200)

        # 马达电调油门中间位置
        self.set(15)

    def set(self, speed):
        wiringpi.softPwmWrite(self.pin, int(speed))


# 实例化摄像头云台
camera = Camera()

# 实例化左马达对象
leftMotor = Montor(left_motor_pin)

# 实例化右马达对象
rightMotor = Montor(right_motor_pin)


# 解包函数
def unpck(data, format):
    data_len = len(data)
    per_len = struct.calcsize(format)
    pos = 0
    end = per_len
    bag = {'list': [], 'foot': ''}

    if (data_len < per_len):
        bag['foot'] = data
        return bag

    while (pos < data_len):
        if (end - pos < per_len):
            bag['foot'] = data[pos:end]
        else:
            bag['list'].append(struct.unpack(package, "".join(data[pos:end])))
        pos += per_len
        end += per_len
        if (end > data_len):
            end = data_len
    return bag


# 工作线程
def worker(connection):
    head = ""
    connection.settimeout(3600)
    while True:
        try:
            raw = connection.recv(8192)
            if (len(raw) < 1):
                print "[System] Socket Disconnect..."
                break

            if (len(raw) % struct.calcsize(package) == 0):
                ret = unpck(raw, package)
            else:
                ret = unpck(head + raw, package)

            head = ret['foot']
            for data in ret['list']:
                print data
                if (data[4] == 3):
                    x = data[2]
                    y = data[3]
                if (data[4] == 7):
                    moveX = int(data[2] - x * 1)
                    moveY = int((data[3] - y) / 0.54)

                    if (moveY > 10 or moveY < -10 or moveX > 10 or moveX < -10):
                        camera.move(moveX, moveY)
                        x = data[2]
                        y = data[3]
                        print "Camer Move:", moveX, moveY
                if (data[4] == 1 or data[4] == 6 or data[4] == 5):
                    leftMotor.set(data[0])
                    rightMotor.set(data[1])
                    print "Motor Set:", data[0], data[1]

        except socket.timeout:
            print "[System] Socket Timeout..."
            break
        except Exception as error:
            print str(error)


def listen(address, port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 绑定地址和端口
    s.bind((address, port))

    # 最大排队数量
    s.listen(80)
    print "[System] Socket Listening..."

    while True:
        c, addr = s.accept()
        print "[System] Socket Connected..."
        # 给新的连接启动线程
        thread.start_new_thread(worker, (c,))


# 程序入口
listen(listen_address, listen_port)
