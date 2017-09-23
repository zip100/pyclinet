# coding=utf8

import thread
import socket
import struct
import serial

x = 0
y = 0

package = "!BBiiB"


class Camera:
    p1 = 1500
    p2 = 1500
    ser = 0;

    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        command = "#9P%(p1)d#15P%(p2)dT100\r\n" % {'p1': self.p1, 'p2': self.p2}
        self.send(command)

    def send(self, command):
        self.ser.write(command.encode())

    def move(self, x, y):
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

        command = "#9P%(p1)d#15P%(p2)dT100\r\n" % {'p1': self.p2, 'p2': self.p1}
        self.send(command)

        return


camera = Camera()


def worker(connection):
    while True:
        try:
            connection.settimeout(3600)
            datas = connection.recv(8192)
            if (len(datas) < 1):
                print "[System] Socket Disconnect..."
                break

            if (len(datas) != struct.calcsize(package)):
                print "[System] Message Not Valid..."
                continue;

            data = struct.unpack(package, datas)

            if (data[4] == 3):
                x = data[2]
                y = data[3]
            if (data[4] == 7):
                moveX = int((data[2] - x) * 0.54)
                moveY = int((data[3] - y) / 0.54)

                if (moveY > 50 or moveY < -50 or moveX > 50 or moveX < -50):
                    camera.move(moveX, moveY)
                    x = data[2]
                    y = data[3]
                    print "------------------------"


        except socket.timeout:
            print "[System] Socket Timeout..."
            break
        except Exception as error:
            print str(error)


def listen(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = "192.168.199.137"
    s.bind((host, port))
    s.listen(80)
    print "[System] Socket Listening..."

    while True:
        c, addr = s.accept()
        print "[System] Socket Connected..."
        thread.start_new_thread(worker, (c,))


listen(81)
