# coding=utf8

import thread
import socket
import json
import time

def worker(connection):
    while True:
        try:
            connection.settimeout(60)
            datas = connection.recv(8192)

            if(len(datas) < 1):
                print "close"
                break

            print datas
        except socket.timeout:
            print "time out"
            break
        except Exception as error:
            connection.close()
            print str(error)
            break


        # print "GetMessage "
        # msg = sock.recv(102400) + "..\r\n"
        # if not msg:
        #     sock.close()
        #     print "Close...."
        #     break;
        # print msg



def listen(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = "192.168.199.137"
    s.bind((host, port))
    s.listen(80)

    while True:
        print "Connect..\r\n"
        c, addr = s.accept()
        thread.start_new_thread(worker,(c,))


listen(81)
