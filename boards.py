import threading
import socket
import serial
import time

class Raspi(object):
    def __init__(self, parent=None):
        self.onMsg = None   
    
    def connect(self, ip, port):
        self._exit = False
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        try:
            self.soc.connect((ip, port))
            self.th = threading.Thread(target = self._th_read)
            self.th.start()
            return True            
        except Exception,e:
            print str(e)
            return False
  
    def sendCmd(self, cmd):
        try:
            self.soc.sendall(cmd + '\r\n')
        except AttributeError:
            print('Not connected yet!')
        except socket.error:
            print('Lost connection!')        

    def _th_read(self):
        buf = ""
        self.soc.settimeout(1)
        while not self._exit:
            try:
                dat = self.soc.recv(1024)
                if dat == "":
                    print("Disconnected")
                    break # if conn lost get out!
                buf = buf + dat
                while "\r\n" in buf: # PuTTY send CR+LF per each "Enter" key
                    (msg, buf) = buf.split("\r\n", 1)
                    if self.onMsg and msg<>"":
                        self.onMsg(msg)                        
            except socket.timeout:
                #print("timeout")
                continue
            except socket.error:
                print('Lost connection!')
                break            

    def disconnect(self):
        self._exit = True
        self.th.join()
        self.soc.close()
    
class Duino(object):
    def __init__(self, parent=None):
        self.onMsg = None   
    
    def connect(self, port):
        self._exit = False
        self.ser = serial.Serial()
        try:
            self.ser.port = port
            self.ser.baudrate = 115200
            self.ser.timeout = 0 # non-blocking read 
            self.ser.open()
            self.th = threading.Thread(target = self._th_read)
            self.th.start()
            return True            
        except Exception,e:
            print str(e)
            return False
  
    def sendCmd(self, cmd):
        print("cmd= {0}".format(cmd))
        try:
            self.ser.write(cmd + "\r")
        except serial.SerialException as e:
            print(e)                 

    def _th_read(self):
        buf = ""         
        while not self._exit:
            time.sleep(0.1)
            try:
                dat = self.ser.read(1024)
                if dat <> "":
                    buf = buf + dat
                    while "\r\n" in buf: # PuTTY send CR+LF per each "Enter" key
                        (msg, buf) = buf.split("\r\n", 1)
                        if self.onMsg and msg <> "":
                            print("msg= {0}".format(msg))
                            self.onMsg(msg)                        
            except serial.SerialException as e:
                print(e)
                break

    def disconnect(self):
        self._exit = True
        self.th.join()
        self.ser.close()
    