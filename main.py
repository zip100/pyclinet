# coding=utf8

import thread
import socket
import json
import time
import Camera
import struct

x = 0
y = 0

package = "!BBiiB"


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
                print (data[2] - x) * 5, data[3] - y

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
