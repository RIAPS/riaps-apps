from pyqtgraph import QtCore, QtGui
import csv
import pyqtgraph as pg
from datetime import datetime
import sys
import numpy as np
import sched, time
import threading
import socket


NORMAL_FILE = "../Data/cs01_no_ls.csv"
RAS_FILE = "../Data/cs01_with_dufls_[VR].csv"

NORMAL_IMAGE = "../Data/normal_state.png"
ALERT_IMAGE = "../Data/alert_state.png"

WSU_LOGO = "Arpa_demo_nodes/Logos/All_Logo.png"
GRAPH_IMAGE = "Arpa_demo_nodes/UFLS_Graph.png"

GA1_IMAGE = "Arpa_demo_nodes/Node1.PNG"
SA1_IMAGE = "Arpa_demo_nodes/Node2.PNG"
SA2_IMAGE = "Arpa_demo_nodes/Node3.PNG"

GA1_NORMAL = "Arpa_demo_nodes/Slide1.PNG"
GA1_ALERT = "Arpa_demo_nodes/Slide2.PNG"
GA1_STABLE = "Arpa_demo_nodes/Slide3.PNG"
SA1_NORMAL = "Arpa_demo_nodes/Slide4.PNG"
SA1_ALERT = "Arpa_demo_nodes/Slide5.PNG"
SA1_STABLE = "Arpa_demo_nodes/Slide6.PNG"
SA2_NORMAL = "Arpa_demo_nodes/Slide7.PNG"
SA2_ALERT = "Arpa_demo_nodes/Slide8.PNG"
SA2_STABLE = "Arpa_demo_nodes/Slide9.PNG"

LINE_DIAGRAM = "Arpa_demo_nodes/14-bus-jing-hi.png"

PLOT_SIZE = 5000
TIMEOUT = 5

INITIAL_VALUE = 60.0

EMERGENCY_LIMIT = 59.78

RANGE_START = 0
RANGE_END = 500
RANGE_LIMIT = 10000000

NORMAL_STATE = 0
DETECTED_STATE = 1
GA_CUT_STATE = 2
SA_CUT_STATE = 3
STABLE_STATE = 4


NORMAL_START = 750
RAS_START = 8530


def parse_files():

        normalFile = open(NORMAL_FILE, 'r') 
        rasFile = open(RAS_FILE, 'r')

        normalReader = csv.reader(normalFile)
        rasReader = csv.reader(rasFile)

        normalReadings = list()
        rasReadings = list()

        normalTimes = list()
        rasTimes = list()


        for row in normalReader:
            normalReadings.append(float(row[1].strip()))
            #Get all the dates and times and then display them
            #normalTimes.append(datetime.strptime(row[0].strip(), '%m/%d/%Y %X.%f'))
        
        for row in rasReader:
            rasReadings.append(float(row[1].strip()))
            #rasTimes.append(datetime.strptime(row[0].strip(), '%m/%d/%Y %X.%f'))


        normalFile.close()
        rasFile.close()


        return normalReadings[NORMAL_START:], rasReadings[RAS_START:]

def sockThread(normalReadings, e, port=7571):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

    s.bind(("192.168.1.155", port))

    s.listen(1)
    sock, addr = s.accept()

    print("CONNECTION ON PORT " + str(port))

    with open(NORMAL_FILE, 'r') as f:

        normalReadings = f.readlines()

        for i in range(NORMAL_START, len(normalReadings)):
            recv_str = sock.recv(64)
            if 'lider' in recv_str:
                print recv_str
                recv_str = sock.recv(64)

            recv_str = sock.recv(64)
            if 'lider' in recv_str:
                print recv_str
                recv_str = sock.recv(64)

            recv_str = sock.recv(64)
            if 'lider' in recv_str:
                print recv_str
                recv_str = sock.recv(64)

            if not e.isSet():
                i = NORMAL_START + 50
            sock.send(normalReadings[i].replace(',', ''))

    sock.close()            


class DataGenerator():
    def __init__(self):
        self.normalReadings, self.rasReadings = parse_files()
        self.index = 0
        self.isContingency = False

        self.contingencyEvent = threading.Event()

        thread1 = threading.Thread(target=self.sockThread, args=(self.normalReadings, self.contingencyEvent, 7571))
        thread2 = threading.Thread(target=self.sockThread, args=(self.normalReadings, self.contingencyEvent, 7572))
        thread3 = threading.Thread(target=self.sockThread, args=(self.normalReadings, self.contingencyEvent, 7573))

        #thread1.start()
        #thread2.start()
        #thread3.start()


    def start(self):
        self.isContingency = True
        self.contingencyEvent.set()

    def stop(self):
        self.isContingency = False
        self.index = 0

    def get(self):
        normalReading = INITIAL_VALUE
        rasReading = INITIAL_VALUE

        if (self.isContingency):
            normalReading = self.normalReadings[self.index]
            rasReading = self.rasReadings[self.index]

            self.index += 1

            if self.index >= len(self.normalReadings):
                self.index = 0

        return normalReading, rasReading

    def sockThread(self, normalReadings, e, port=7571):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

        s.bind(("192.168.1.155", port))

        s.listen(1)
        sock, addr = s.accept()

        print("CONNECTION ON PORT " + str(port))

        with open(RAS_FILE, 'r') as f:

            normalReadings = f.readlines()
            i = RAS_START

            while True:
                recv_str = sock.recv(64)
                if 'SetSlider' in recv_str:
                    print recv_str
                    recv_str = sock.recv(64)

                recv_str = sock.recv(64)
                if 'SetSlider' in recv_str:
                    print recv_str
                    recv_str = sock.recv(64)

                recv_str = sock.recv(64)
                if 'SetSlider' in recv_str:
                    print recv_str
                    recv_str = sock.recv(64)

                if not e.isSet():
                    i = RAS_START
                else:
                    i = RAS_START + self.index
                sock.send(normalReadings[i].replace(',', ''))

        sock.close()            





class SpeedButton(QtGui.QWidget):
    def __init__(self, dataGenerator, parent=None):
        super(SpeedButton, self).__init__(parent=parent)


        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.speed = 0.25
        self.label = QtGui.QLabel(self)
        self.label.setText("Speed Control")
        self.label.setFixedHeight(25)
        self.label.setAlignment(QtCore.Qt.AlignCenter)


        self.startButton = QtGui.QPushButton('Apply Contingency', self)
        self.startButton.clicked.connect(dataGenerator.start)

        self.stopButton = QtGui.QPushButton('Reset', self)
        #self.stopButton.clicked.connect(dataGenerator.stop)

        self.fullPlotButton = QtGui.QPushButton("View Full Plot", self)

        self.zoomButton = QtGui.QPushButton("Zoom Out", self)

        self.sb1 = QtGui.QRadioButton("x1")
        self.sb1.toggled.connect(lambda: self.setSpeed(1))
        self.sb2 = QtGui.QRadioButton("x0.5")
        self.sb2.toggled.connect(lambda: self.setSpeed(0.5))
        self.sb3 = QtGui.QRadioButton("x0.25")
        self.sb3.toggled.connect(lambda: self.setSpeed(0.25))
        self.sb3.setChecked(True)
        self.sb4 = QtGui.QRadioButton("x0.10")
        self.sb4.toggled.connect(lambda: self.setSpeed(0.1))

        #self.speedLayout = QtGui.QVBoxLayout()
        #self.speedLayout.addWidget(self.label)
        #self.speedLayout.addWidget(self.sb1)
        

        self.verticalLayout.setAlignment(QtCore.Qt.AlignTop)
        self.checkboxLayout = QtGui.QHBoxLayout()

        self.hl1 = QtGui.QHBoxLayout()
        self.hl2 = QtGui.QHBoxLayout() 

        self.hl1.addWidget(self.startButton)
        self.hl1.addWidget(self.stopButton)
        self.hl2.addWidget(self.fullPlotButton)
        self.hl2.addWidget(self.zoomButton)

        self.verticalLayout.addLayout(self.hl1)
        self.verticalLayout.addLayout(self.hl2)
        self.verticalLayout.addWidget(self.label)

        self.checkboxLayout.addWidget(self.sb1)
        self.checkboxLayout.addWidget(self.sb2)
        self.checkboxLayout.addWidget(self.sb3)
        self.checkboxLayout.addWidget(self.sb4)
        
        self.verticalLayout.addLayout(self.checkboxLayout)


    def setSpeed(self, speed):
        self.speed = speed

    def getSpeed(self):
        return self.speed

class BBInfo(QtGui.QWidget):
    def __init__(self, parent=None):
        super(BBInfo, self).__init__(parent=parent)
        
        self.label1text = ""
        self.label2text = ""
        self.label3text = "Normal Operation"

        self.layout = QtGui.QVBoxLayout(self)
        self.label1 = QtGui.QLabel(self)

        self.label2 = QtGui.QLabel(self)
#        self.label2.setText("Issue detected")

        self.label3 = QtGui.QLabel(self)
        self.label3.setStyleSheet("QLabel { color : green; font-size:20px}") 
        self.label3.setText(self.label3text)

        self.label1.setFixedWidth(100)

        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.label3)

    def update(self, text):
        self.label1text = self.label2text
        self.label2text = self.label3text
        self.label3text = text

        self.label1.setText(self.label1text)
        self.label2.setText(self.label2text)
        self.label3.setText(self.label3text)

    def setRed(self):
        self.label3.setStyleSheet("QLabel { color : red; font-size:20px}")

    def setGreen(self):
        self.label3.setStyleSheet("QLabel { color : green; font-size:20px}")

   
class SystemState(QtGui.QWidget):
    def __init__(self, image, parent=None):
        super(SystemState, self).__init__(parent=parent)
        self.layout = QtGui.QHBoxLayout(self)

        self.image = QtGui.QPixmap(image).scaledToHeight(120)
        self.imageLabel = QtGui.QLabel(self)
        self.imageLabel.setPixmap(self.image)
        self.bbinfo = BBInfo()

        self.layout.addWidget(self.imageLabel)
        self.layout.addWidget(self.bbinfo)

    def updateText(self, text):
        self.bbinfo.update(text)
        
class SystemStateWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SystemStateWidget, self).__init__(parent=parent)
        self.systemStateLayout = QtGui.QVBoxLayout(self)

        height = 200

        if (parent):
            height = parent.frameGeometry().height() * 1.0
            print height

        self.isAlert = False

        self.ga1_state = SystemState(GA1_IMAGE)
        self.sa1_state = SystemState(SA1_IMAGE)
        self.sa2_state = SystemState(SA2_IMAGE)

        self.systemStateLayout.addWidget(self.ga1_state)
        self.systemStateLayout.addWidget(self.sa1_state)
        self.systemStateLayout.addWidget(self.sa2_state)
        #self.systemStateLayout.addWidget(self.ga1Label)
        #self.systemStateLayout.addWidget(self.sa1Label)
        #self.systemStateLayout.addWidget(self.sa2Label)


    def ga1_update(self, text):
        self.ga1_state.updateText(text)

    def sa1_update(self, text):
        self.sa1_state.updateText(text)

    def sa2_update(self, text):
        self.sa2_state.updateText(text)

    def setRed(self):
        self.ga1_state.bbinfo.setRed()
        self.sa1_state.bbinfo.setRed()
        self.sa2_state.bbinfo.setRed()

    def setGreen(self):
        self.ga1_state.bbinfo.setGreen()
        self.sa1_state.bbinfo.setGreen()
        self.sa2_state.bbinfo.setGreen()



class GraphWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent=parent)

        self.speed = 1
        self.index = 0

        self.plotSize = 500

        self.isZoomed = True

        self.state = NORMAL_STATE

        self.horizontalLayout = QtGui.QHBoxLayout(self)

        self.dataGenerator = DataGenerator()
        self.w1 = SpeedButton(self.dataGenerator)
        self.w1.fullPlotButton.clicked.connect(self.showFullPlot)
        self.w1.zoomButton.clicked.connect(self.toggleZoom)
        self.w1.stopButton.clicked.connect(self.reset)

#        self.w2 = Slider(-1, 1)
#        self.horizontalLayout.addWidget(self.w2)

#        self.w3 = Slider(-10, 10)
#        self.horizontalLayout.addWidget(self.w3)

#        self.w4 = Slider(-10, 10)
#        self.horizontalLayout.addWidget(self.w4)



        self.win = pg.GraphicsWindow(title="UFLS Demo")
        self.win2 = pg.GraphicsWindow(title="UFLS Demo")
        #self.update()

        #self.w1.slider.valueChanged.connect(self.setInterval)

        self.normalReadings = [60.0 for _ in range(PLOT_SIZE)]
        self.rasReadings = [60.0 for _ in range(PLOT_SIZE)]


        #Print the difference between times and see if there's any hope, or else take the average of times

        #time_list = [(self.normalTimes[i+1] - self.normalTimes[i]).microseconds for i in range(len(self.normalTimes) - 1) ]
        #print float(sum(time_list)/1000)/float(len(time_list))

        #self.win.resize(1000, 600)

        pg.setConfigOptions(antialias = True)

        self.vlayout = QtGui.QVBoxLayout()
        self.vlayout.addWidget(self.win)
        self.vlayout.addWidget(self.win2)
        self.horizontalLayout.addLayout(self.vlayout)

        self.rangeStart = 0
        self.rangeEnd = 500
        self.rangeCount = 1

        self.tickList = [(x, x) for x in range(0, 500, 200)]

        self.normalPlot = self.win.addPlot(title = "<h2>Without RAS</h2>")
        self.normalCurve = self.normalPlot.plot(pen = pg.mkPen('r', width = 6))
        self.normalPlot.setYRange(49, 60, padding = 0.1, update = False)
        self.normalPlot.setLabel("left", "Frequency", units = "Hz")
        self.normalPlot.setLabel("bottom", "Time (ms) ")

        self.rasPlot = self.win.addPlot(title = "<h2>With RAS</h2>")

        self.rasPlot.getAxis('bottom').setTicks([self.tickList])

        self.rasCurve = self.rasPlot.plot(pen = pg.mkPen('g', width = 5))
        self.rasPlot.setYRange(58.1, 60, padding = 0.1, update = False)
        self.rasPlot.setLabel("left", "Frequency", units = "Hz")
        self.rasPlot.setLabel("bottom", "Time (ms)")

        self.bothPlot = self.win2.addPlot(title = "<h2>Comparison</h2>")
        self.bothPlot.setYRange(49, 60, padding = 0.1, update = False)
        self.bothPlot.setLabel("left", "Frequency", units = "Hz")
        self.bothPlot.setLabel("bottom", "Time (ms)")
        self.bothPlot.getAxis('bottom').setTicks([self.tickList])
        

        self.bothPlot.getAxis('bottom').setGrid(120)
        self.bothPlot.getAxis('left').setGrid(200)

        self.normalPlot.getAxis('bottom').setGrid(120)
        self.normalPlot.getAxis('left').setGrid(200)

        self.rasPlot.getAxis('bottom').setGrid(120)
        self.rasPlot.getAxis('left').setGrid(200)

        
        self.bothNormalCurve = pg.PlotCurveItem()
        self.bothNormalCurve.setPen(pg.mkPen('r', width = 8))
        self.bothRasCurve = pg.PlotCurveItem()
        self.bothRasCurve.setPen(pg.mkPen('g', width = 5))
        self.bothRasCurve.setPen(pg.mkPen('g', width = 5))
        

        self.bothPlot.addItem(self.bothNormalCurve)
        self.bothPlot.addItem(self.bothRasCurve)


        self.systemStateLayout = SystemStateWidget(self) 
        self.horizontalLayout.addWidget(self.systemStateLayout)

        #self.horizontalLayout.addWidget(self.w1)

        #self.lineDiagramLabel = QtGui.QLabel(self)
        #self.lineDiagramPixmap = QtGui.QPixmap(LINE_DIAGRAM)
        #self.lineDiagramLabel.setPixmap(self.lineDiagramPixmap.scaledToHeight(550))

        #self.horizontalLayout.addWidget(self.lineDiagramLabel)


        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(TIMEOUT)


    def update(self):
        normalReading, rasReading = self.dataGenerator.get()
        self.normalReadings = self.normalReadings[-PLOT_SIZE:] + [normalReading]
        self.rasReadings = self.rasReadings[-PLOT_SIZE:] + [rasReading]
        self.normalCurve.setData(self.normalReadings[-self.plotSize:])
        self.rasCurve.setData(self.rasReadings[-self.plotSize:])
        
        self.bothNormalCurve.setData(self.normalReadings[-self.plotSize:])
        self.bothRasCurve.setData(self.rasReadings[-self.plotSize:])


        self.rangeStart = self.rangeStart + 1
        self.rangeEnd = self.rangeEnd + 1
        if (self.rangeStart > 200):
            self.rangeStart = RANGE_START
            self.rangeEnd = RANGE_END
            self.rangeCount += 1

        if self.isZoomed:
            tickList = [(200 -self.rangeStart, 200 * self.rangeCount), (400-self.rangeStart, 200 * (self.rangeCount + 1)), (600 - self.rangeStart, 200 * (self.rangeCount + 2))]
        else:
            tickList = [(2000 -self.rangeStart, 2000 * self.rangeCount), (4000-self.rangeStart, 2000 * (self.rangeCount + 1)), (6000 - self.rangeStart, 2000 * (self.rangeCount + 2))]

        self.rasPlot.getAxis('bottom').setTicks([tickList])
        self.normalPlot.getAxis('bottom').setTicks([tickList])
        self.bothPlot.getAxis('bottom').setTicks([tickList])

        #self.rasPlot.setXRange(self.rangeStart, self.rangeEnd)

        if (self.speed != self.w1.getSpeed()):
            self.speed = self.w1.getSpeed()
            self.timer.setInterval(int(TIMEOUT/self.speed))

#HANDLE STATE CHANGES

        if self.state == NORMAL_STATE:
            if self.rasReadings[-1] < EMERGENCY_LIMIT:
                self.systemStateLayout.ga1_update("Frequency Issue\nDetected")
                self.systemStateLayout.setRed()
                self.delay_count = 50
                self.state = DETECTED_STATE

        if self.state == DETECTED_STATE:
            self.delay_count -= 1
            if self.delay_count == 0:
                self.state = GA_CUT_STATE
                self.delay_count = 160

                self.systemStateLayout.ga1_update("Active Power deficiency \nestimated - 19.37 MW")
                self.systemStateLayout.sa1_update("Informed of Issue")
                self.systemStateLayout.sa2_update("Informed of Issue")

        if self.state == GA_CUT_STATE:
            self.delay_count -= 1
            if self.delay_count == 0:
                self.delay_count = 250
                self.state = SA_CUT_STATE
                self.systemStateLayout.ga1_update("GA1 cuts 6.456 MW,\n3.874 MVAR (32.27%)")
                self.systemStateLayout.sa1_update("SA1 cuts 6.456 MW,\n2.483 MVAR (24.83%)")
                self.systemStateLayout.sa2_update("SA2 cuts 6.456 MW,\n3.228 MVAR (32.27%)")

        if self.state == SA_CUT_STATE:
            self.delay_count -= 1
            if self.delay_count == 0:
                self.state = STABLE_STATE
                self.systemStateLayout.ga1_update("Frequency Drop Stops")
                self.systemStateLayout.sa1_update("Frequency Drop Stops")
                self.systemStateLayout.sa2_update("Frequency Drop Stops")
                self.systemStateLayout.setGreen()

        if self.state == STABLE_STATE:
            if self.rasReadings[-1] >= 60.0:
                self.state = NORMAL_STATE
                self.systemStateLayout.ga1_update("Normal Operation")
                self.systemStateLayout.sa1_update("Normal Operation")
                self.systemStateLayout.sa2_update("Normal Operation")

            
        
    def showFullPlot(self):
        self.timer.setInterval(5000)
        self.speed = 0.2
        normalReadings, rasReadings = parse_files()
        self.normalCurve.setData(normalReadings)
        self.rasCurve.setData(rasReadings[:len(normalReadings)])

    def setInterval(self):
        self.interval = self.w1.x

    def reset(self):
        self.dataGenerator.stop()
        self.state = NORMAL_STATE

        self.systemStateLayout.ga1_update("Normal Operation")
        self.systemStateLayout.sa1_update("Normal Operation")
        self.systemStateLayout.sa2_update("Normal Operation")
        self.systemStateLayout.setGreen()


    def toggleZoom(self):
        self.isZoomed = not self.isZoomed
        if self.isZoomed:
            self.w1.zoomButton.setText("Zoom Out")
            self.plotSize = 500
        else:
            self.w1.zoomButton.setText("Zoom In")
            self.plotSize = 5000



class StaticInfo(QtGui.QWidget):
    def __init__(self, parent = None):
        super(StaticInfo, self).__init__(parent = parent)

        self.layout = QtGui.QHBoxLayout(self)

        self.logoPixmap = QtGui.QPixmap(WSU_LOGO)
        self.logoLabel = QtGui.QLabel(self)
        self.logoLabel.setPixmap(self.logoPixmap.scaledToWidth(900))

        #self.graphPixmap = QtGui.QPixmap(GRAPH_IMAGE)
        #self.graphLabel = QtGui.QLabel(self)
        #self.graphLabel.setPixmap(self.graphPixmap.scaledToWidth(550))

        self.layout.addWidget(self.logoLabel)
        #self.layout.addWidget(self.graphLabel)


class LineDiagram(QtGui.QWidget):
    def __init__(self, parent = None):
        super(LineDiagram, self).__init__(parent = parent)

        self.layout = QtGui.QVBoxLayout(self)

        self.lineLabel = QtGui.QLabel(self)
        self.linePixmap = QtGui.QPixmap(LINE_DIAGRAM)
        self.lineLabel.setPixmap(self.linePixmap.scaledToHeight(400))

#        self.graphLabel = QtGui.QLabel(self)
#        self.graphPixmap = QtGui.QPixmap(GRAPH_IMAGE)
#        self.graphLabel.setPixmap(self.graphPixmap.scaledToHeight(300))

        self.layout.addWidget(self.parent().demoWindow.graph.w1)
        self.layout.addWidget(self.lineLabel)
#        self.layout.addWidget(self.graphLabel)


class DemoWindow(QtGui.QWidget):
    def __init__(self, parent = None):
        super(DemoWindow, self).__init__(parent = parent)
        #self.showMaximized()

        self.graph = GraphWidget(self)

        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.graph)


        self.verticalLayout.addWidget(StaticInfo(self))


class AppWindow(QtGui.QWidget):
    def __init__(self, parent = None):
        super(AppWindow, self).__init__(parent = parent)
        self.showMaximized()

        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor('white'))
        self.setPalette(p)


        self.layout = QtGui.QHBoxLayout(self)

        self.demoWindow = DemoWindow(self)

        self.lineDiagram = LineDiagram(self)

        self.layout.addWidget(self.demoWindow)
        self.layout.addWidget(self.lineDiagram)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())


