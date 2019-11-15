'''
Created on 29 Nov 2017

@author: markot
'''
'''
Created on 23 nov. 2017

@author: Marija
'''
from PyQt4 import QtGui, QtCore

#import logging
import sys
import time
import threading
import PyTango as pt
import numpy as np
import pyqtgraph as pq
from scipy.optimize import curve_fit
import scipy as sy

class SpectrometerCamera(QtGui.QWidget):
    def __init__(self, devicename="gunlaser/cameras/blackfly_test01", parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.devicename = devicename
        
        self.lock = threading.Lock()
        
        self.scanTimer = QtCore.QTimer()
        self.scanTimer.timeout.connect(self.updateImage)
        
        self.fittingTimer = QtCore.QTimer()
        self.fittingTimer.timeout.connect(self.fitGaussian)


        #t0 = time.clock()


#         splash.showMessage('         Initializing devices', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
#         app.processEvents()
# 
#         self.devices = dict()
#         self.devices['camera'] = pt.DeviceProxy(self.devicename)
# 
#         splash.showMessage('         Reading startup attributes', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
#         app.processEvents()

        self.cameraName = 'gunlaser/cameras/jai_test'
        self.cameraDevice = pt.DeviceProxy(self.cameraName)
        self.cameraDevice.set_timeout_millis(3000)
        
        self.attributes = dict()
        self.coeffs = [1, 1, 0, 1]
        
        self.image = self.cameraDevice.read_attribute('Image').value.astype(np.double)
        self.bkgndImage = np.zeros(self.image.shape)
        self.frameRate = self.cameraDevice.read_attribute('FrameRate')
        print self.frameRate.value
        self.cameraDevice.write_attribute('ExposureTime',800)
        #self.attributes['exposure'] = self.cameraDevice.read_attribute('ExposureTime').value
        
        self.setup_layout()
    

    def fitGaussian(self):
        
        t0 = time.clock()
        
        def fitFunc(x, a,b,c,d):
#             a = params[0]
#             b = params[1]
#             c = params[2]
#             d = params[3]
            return a*np.exp(-(x-b)**2/c) + d    
        
        with self.lock:
            
            x = np.copy(np.arange(len(self.lineout1)))
            y = np.copy(self.lineout1)
        
        a_guess = np.max(y) - np.min(y)
        b_guess = np.argmax(y, 0)
        c_guess = 20000
        d_guess = np.min(y)
        p0 = [a_guess, b_guess, c_guess, d_guess]
        p0 = sy.array(p0)
        
        try:
            self.coeffs, matcov = curve_fit(fitFunc, x, y, p0, maxfev=1000) #maxfev=100000
        except RuntimeError:
            pass
        
        self.y_fitted = fitFunc(x, self.coeffs[0], self.coeffs[1], self.coeffs[2], self.coeffs[3])
        self.plot22.setData(self.y_fitted)
        self.fittedWidthLabel.setText("{:.2f}".format(self.coeffs[2]))
        
        t1 = time.clock() - t0
        print (t1)
    
        
        if self.fitButton2.isChecked():        
            self.fittingTimer.start(200)
        else:
            self.fittingTimer.stop()
            self.plot22.clear()
            self.fittedWidthLabel.setText('')
            
        
    def setup_layout(self):
        self.layout = QtGui.QHBoxLayout(self) #the whole window, main layout
        self.cameraLayout = QtGui.QHBoxLayout()
        self.plotLayout = QtGui.QVBoxLayout()
        self.controlsLayout = QtGui.QVBoxLayout()
        #self.layout4 = QtGui.QVBoxLayout()
        #self.layout5 = QtGui.QVBoxLayout()

        
        self.layout.addLayout(self.cameraLayout)
        self.layout.addLayout(self.plotLayout)
        self.layout.addLayout(self.controlsLayout)
        #self.layout2.addLayout(self.layout4)
        #self.layout1.addLayout(self.layout5)
        
        #layout5 - controls layout
        self.subtractBkgndButton = QtGui.QPushButton('Subtract background')
        self.subtractBkgndButton.clicked.connect(self.subtractBackground)
        self.controlsLayout.addWidget(self.subtractBkgndButton)

   
#        self.plotWidget1 = pq.PlotWidget()
        self.plotWidget1 = pq.PlotWidget()
        #self.plotWidget1.setAspectLocked(1)
        #self.plotWidget1.setVisible(True)
        self.plotWidget1.setMaximumSize(350,250)
        self.plot11 = self.plotWidget1.plot()
        self.plot12 = self.plotWidget1.plot()
        self.plotLayout.addWidget(self.plotWidget1)
        self.plotWidget1.plotItem.setLabel('bottom', 'wavelength','nm')

        
        self.plotWidget2 = pq.PlotWidget()
        self.plotWidget2.setMaximumSize(350,250)
        self.plot21 = self.plotWidget2.plot()
        self.plot22 = self.plotWidget2.plot()
        self.plotLayout.addWidget(self.plotWidget2)
        self.plotWidget2.plotItem.setLabel('bottom', 'pixel')
        
        #labels
        self.plotWidget2.setLabel('top','imaging quality')
        self.plotWidget1.setLabel('top','spectrum')

                
        self.cameraWindow = pq.GraphicsLayoutWidget()
        #self.cameraWindow.setMaximumSize(350,550)
        self.cameraWindow.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.cameraLayout.addWidget(self.cameraWindow)
        self.view = self.cameraWindow.addViewBox()
        self.view.setAspectLocked(True)

        self.img = pq.ImageItem(border='w')
        self.view.addItem(self.img)
        self.img.setImage(self.image)
        self.updateImage()     
        
        self.bkgndBox = self.cameraWindow.addViewBox()
        
    
        
#         #layout5 - controls layout
#         self.fitButton = QtGui.QPushButton('Fit')
#         self.fitButton.clicked.connect(self.fitGaussian)
#         self.layout5.addWidget(self.fitButton)
        self.fittedWidthLabel = QtGui.QLabel()
        self.fittedWidthLabel.setText("{:.2f}".format(self.coeffs[2]))
        self.controlsLayout.addWidget(self.fittedWidthLabel)
        
        self.fitButton2 = QtGui.QCheckBox('Show fit', self)
        self.controlsLayout.addWidget(self.fitButton2)
        self.fitButton2.stateChanged.connect(self.changeLabel)
        
        self.memoButton = QtGui.QPushButton('Memo trace')
        self.memoButton.clicked.connect(self.showMemo)
        self.clearMemoButton = QtGui.QPushButton('Clear memo')
        self.clearMemoButton.clicked.connect(self.clearMemo)

        self.spectrumButtonGroup = QtGui.QButtonGroup()
        self.spectrumButtonGroup.addButton(self.memoButton)
        self.spectrumButtonGroup.addButton(self.clearMemoButton)
        
        self.controlsLayout.addWidget(self.memoButton)
        self.controlsLayout.addWidget(self.clearMemoButton)

        
    def clearMemo(self):
        self.plot12.clear()
    
    def showMemo(self):
        self.plot12.setData(x=np.arange(len(self.lineout0))/128.0+258,y=self.lineout0)
        self.plot12.setPen('g')
        
        
    def changeLabel(self, state):
        if state == QtCore.Qt.Checked:
            self.fitGaussian()
        else:
            self.plot22.clear()
            self.fittedWidthLabel.setText('')
        
    def subtractBackground(self):
        self.bkgndImage = self.cameraDevice.read_attribute('Image').value.astype(np.double)

    def updateImage(self):
        #print 'updating image'
        with self.lock:
            self.image = (self.cameraDevice.read_attribute('Image').value.astype(np.double)-self.bkgndImage).transpose()
            self.img.setImage(self.image) #[425:525,500:600]
            self.lineout0 = np.sum(self.image,axis=1)
            self.lineout1 = np.sum(self.image,axis=0)
        self.plot11.setData(x=np.arange(len(self.lineout0))/128.0+258,y=self.lineout0)   
        self.plot21.setData(self.lineout1)
        #=======================================================================
        # self.plot21.setData(np.sum(self.image,axis=0))
        # self.plot22.setData(np.sum(self.image,axis=1))
        #=======================================================================
        self.plot21.setPen('r')   
        self.view.update()
        self.cameraWindow.update()
        
        self.scanTimer.start(np.max([100, int(1.0/self.frameRate.value*1000.0)]))
        #print np.max([300, int(1.0/self.frameRate.value*1000.0)])
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)


    app.processEvents()
    myapp = SpectrometerCamera()
    myapp.show()
    #splash.finish(myapp)
    sys.exit(app.exec_())
