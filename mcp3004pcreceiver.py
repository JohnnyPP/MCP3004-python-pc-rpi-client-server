from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import socket

HOST = "192.168.1.101"
PORT = 5000

localSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
localSocket.bind((HOST, PORT))
localSocket.settimeout(5)

dataADC = []
maxADCBits = 1023.0
maxVolts = 3.3
voltsPerBit = maxVolts / maxADCBits

app = QtGui.QApplication([])
win = pg.GraphicsWindow()
win.resize(1000,600)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

qtplot = win.addPlot(title="Pyqtgraph ADC MCP3004")
curve = qtplot.plot(pen='y')
qtplot.setXRange(0,4000)
qtplot.setYRange(0,maxVolts)
qtplot.setLabel('left', "Measured voltage [V]")
qtplot.setLabel('bottom', "Number of sample")
qtplot.showGrid(x=True, y=True)

counter = 0


def update():
    global curve, counter, dataNumpy, dataADC

    for i in range(10):                                             # grab ADC data in 10 samples chunks
        try:
            dataReceived = float(localSocket.recv(50))*voltsPerBit  # converts the received data to voltage
            dataADC.append(dataReceived)                            # and appends the data to array
        except socket.timeout:
            print "Socket timeout!"
            localSocket.close()
            print "Socket closed"
            timer.stop()
            print "Qt timer stopped"
        except socket.error:
            print "Socket error"

    dataNumpy = np.array(dataADC)                               # converts dataADC to numpy array required by pyqtgraph
    curve.setData(dataNumpy)
    counter += 1
    if counter == 400:
        dataADC = []                                            # empties the array after 4000 samples
        dataNumpy = np.array(dataADC)
        counter = 0

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()