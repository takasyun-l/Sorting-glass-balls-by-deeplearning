import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtCore import QObject, pyqtSignal
from Ui_server import Ui_MainWindow
import threading
import server
from deepLearning.Detecter import Detecter


class MyMainWindow(QMainWindow, Ui_MainWindow):
    recvmsg = pyqtSignal(object)

    def __init__(self, parent=None):

        # 计数器初始化
        self.server_switch_count = 0
        self.getID_switch_count = 0
        self.recv_switch_count = 0
        self.deepLearning_count = 0

        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.server_switch_init()
        self.getID_switch_init()
        self.recv_switch_init()
        self.meso_textBrowser_init()
        self.clear_button_init()
        self.recvmsg_init()
        self.send_button_init()
        self.ready_button_init()
        self.deepLearning_start_init()
        self.deepLearning_open_init()

    def server_switch_init(self):
        self.server_switch.clicked.connect(self._push1)

    def getID_switch_init(self):
        self.getID_switch.clicked.connect(self._push2)

    def recv_switch_init(self):
        self.recv_switch.clicked.connect(self._push3)

    def meso_textBrowser_init(self):
        # self.meso_textBrowser.setText('写入小柠檬')
        # self.meso_textBrowser.append('写入小柠檬')
        self.meso_textBrowser.ensureCursorVisible()

    def clear_button_init(self):
        self.clear_button.clicked.connect(self._push4)

    def recvmsg_init(self):
        self.recvmsg.connect(self._push5)

    def send_button_init(self):
        self.send_button.clicked.connect(self._push6)

    def ready_button_init(self):
        self.ready_button.clicked.connect(self._push7)
        
    def deepLearning_start_init(self):
        self.deepLearning_start.clicked.connect(self._push8)
        
    def deepLearning_open_init(self):
        self.deepLearning_open.clicked.connect(self._push9)
        
    def _push1(self):
        if self.server_switch_count % 2 == 0:
            # self.server_switch.setStyleSheet("color: rgb(255, 0, 0); background-color: rgb(255, 255, 255);")
            self.server_switch.setText("OFF")
            self.server_switch_count = self.server_switch_count + 1
            self.server_start_thread = threading.Thread(target=self.start_server)
            self.server_start_thread.start()

        elif self.server_switch_count % 2 == 1:
            if hasattr(self, 'link'):
                # 删除服务器连接对象
                del self.link
            if hasattr(self, 'server_start_thread'):
                # 等待服务器线程结束
                self.server_start_thread.join()
            # self.server_switch.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(255, 0, 0);")
            self.server_switch.setText("ON")
            self.server_switch_count = self.server_switch_count + 1

    def _push2(self):
        if self.getID_switch_count % 2 == 0:
            # self.getID_switch.setStyleSheet("color: rgb(255, 0, 0); background-color: rgb(255, 255, 255);")
            self.getID_switch.setText("OFF")
            self.getID_switch_count = self.getID_switch_count + 1
            self.getID_server()

        elif self.getID_switch_count % 2 == 1:
            # self.getID_switch.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(255, 0, 0);")
            self.getID_switch.setText("ON")
            self.getID_switch_count = self.getID_switch_count + 1

    def _push3(self):
        if self.recv_switch_count % 2 == 0:
            # self.recv_switch.setStyleSheet("color: rgb(255, 0, 0); background-color: rgb(255, 255, 255);")
            self.recv_switch.setText("OFF")
            self.recv_switch_count = self.recv_switch_count + 1
            self.server_recv_thread = threading.Thread(target=self.recv_server)
            self.server_recv_thread.start()

        elif self.recv_switch_count % 2 == 1:
            # self.recv_switch.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(255, 0, 0);")
            self.recv_switch.setText("ON")
            self.recv_switch_count = self.recv_switch_count + 1
            self.recv_terminate_server()

    def _push4(self):
        self.meso_textBrowser.clear()

    def _push5(self, message):
        print(message)
        print(len(self.labels), len(self.positions))
        self.meso_textBrowser.append(message.decode('utf-8'))
        if len(self.labels) == 0 and len(self.positions) == 0:
            self.send_server(u"10")
        else:
            if message.decode('utf-8') == u"1":
                medium = self.labels.pop()
                print(1)
                self.send_server(str(medium))
        
            elif message.decode('utf-8') == u"2":
                mediumarr = self.positions.pop()
                medium = str('{:.3f}'.format(mediumarr[0])) + u"," + str('{:.3f}'.format(mediumarr[1])) + u"," \
                    + str('{:.3f}'.format(mediumarr[2])) + u"," + str('{:.3f}'.format(mediumarr[3])) + u"," \
                        + str('{:.3f}'.format(mediumarr[4])) + u"," + str('{:.3f}'.format(mediumarr[5]))                                                                                 
                print(2)
                self.send_server(medium)
            
    def _push6(self):
        self.med = self.send_lineEdit.text()
        self.link.send(self.med)

    def _push7(self):
        self.addr = self.addr_lineEdit.text()
        self.com = int(self.com_lineEdit.text())
        self.address = (self.addr, self.com)
        
    def _push8(self):            
        self.img, self.result = self.visual.Detect(100)
        self.labels = []
        self.positions = []
        for res in self.result:
            self.labels.append(res[0])
            pos = [0, 0, 0, 180, 0, 0]
            pos[0] = res[1]
            pos[1] = res[2]
            if res[0] <= 5:
                pos[2] = 133 + 50
            elif res[0] > 5:
                pos[2] = 140 + 50
            self.positions.append(pos)
            print(self.result)
        self.send_server(u"0")

    def _push9(self):
        if self.deepLearning_count % 2 == 0:
            self.visual = Detecter()
            self.deepLearning_open.setText("dCLOSE")
            self.deepLearning_count = self.deepLearning_count + 1
        elif self.deepLearning_count % 2 == 1:
            del self.visual
            self.deepLearning_open.setText("dOPEN")
            self.deepLearning_count = self.deepLearning_count + 1

    def start_server(self):
        self.link = server.SocketServer(self.address, self)

    def getID_server(self):
        self.link.getID()

    def recv_server(self):
        self.link.receive()
        
    def send_server(self, mes):
        self.link.send(mes)

    def recv_terminate_server(self):
        self.link.terminate()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
