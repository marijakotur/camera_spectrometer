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
#import time
#import threading
import PyTango as pt
import numpy as np
import pyqtgraph as pq
from scipy.optimize import curve_fit
import scipy as sy

class SpectrometerCamera(QtGui.QWidget):
    def __init__(self, devicename="gunlaser/cameras/blackfly_test01", parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.devicename = devicename
        
        self.scanTimer = QtCore.QTimer()
        self.scanTimer.timeout.connect(self.updateImage)

        #t0 = time.clock()

        #self.lock = threading.Lock()

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
        
        self.image = self.cameraDevice.read_attribute('Image').value.astype(np.double)
        self.bkgndImage = np.zeros(self.image.shape)
        self.attributes['exposure'] = self.cameraDevice.read_attribute('ExposureTime').value
        
        self.setup_layout()
    

    def fitGaussian(self):
        x = np.arange(len(self.lineout1))
        y = self.lineout1
        
        def fitFunc(x, params):
            a = params[0]
            b = params[1]
            c = params[2]
            d = params[3]
            return a*np.exp(-(x-b)**2/c) + d       
        
        a_guess = np.max(self.lineout1) - np.min(self.lineout1)
        p0 = [a_guess, 440, 50, 0]
        p0 = sy.array(p0)
        
        coeffs, matcov = curve_fit(fitFunc, x, y, p0, maxfev=100000)
        print(coeffs)
#         print(matcov)
        
        self.yaj = fitFunc(x, coeffs)
        self.plot22.setData(self.yaj)
        
        self.fitted = fitFunc(x,coeffs)


        
    def setup_layout(self):
        self.layout = QtGui.QHBoxLayout(self) #the whole window, main layout
        self.layout1 = QtGui.QVBoxLayout()
        self.layout2 = QtGui.QVBoxLayout()
        self.layout3 = QtGui.QVBoxLayout()
        self.layout4 = QtGui.QVBoxLayout()
        self.layout5 = QtGui.QVBoxLayout()

        
        self.layout.addLayout(self.layout1)
        self.layout.addLayout(self.layout2)
        self.layout2.addLayout(self.layout3)
        self.layout2.addLayout(self.layout4)
        self.layout1.addLayout(self.layout5)
        
        #layout5 - controls layout
        self.subtractBkgndButton = QtGui.QPushButton('Subtract background')
        self.subtractBkgndButton.clicked.connect(self.subtractBackground)
        self.layout5.addWidget(self.subtractBkgndButton)

   
#        self.plotWidget1 = pq.PlotWidget()
        self.plotWidget1 = pq.PlotWidget()
        #self.plotWidget1.setAspectLocked(1)
        #self.plotWidget1.setVisible(True)
        self.plotWidget1.setMaximumSize(350,250)
        self.plot11 = self.plotWidget1.plot()
        self.layout3.addWidget(self.plotWidget1)
        self.plotWidget1.plotItem.setLabel('bottom', 'wavelength','pixel')

        
        self.plotWidget2 = pq.PlotWidget()
        self.plotWidget2.setMaximumSize(350,250)
        self.plot21 = self.plotWidget2.plot()
        self.plot22 = self.plotWidget2.plot()
        self.layout4.addWidget(self.plotWidget2)
        self.plotWidget2.plotItem.setLabel('bottom', 'pixel')
                
        self.cameraWindow = pq.GraphicsLayoutWidget()
        self.cameraWindow.setMaximumSize(350,250)
        #self.cameraWindow.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.layout1.addWidget(self.cameraWindow)
        self.view = self.cameraWindow.addViewBox()
        self.view.setAspectLocked(True)
        self.img = pq.ImageItem(border='w')
        self.view.addItem(self.img)
        self.img.setImage(self.image)
        self.updateImage()     
        
        self.bkgndBox = self.cameraWindow.addViewBox()
        
        #layout5 - controls layout
        self.fitButton = QtGui.QPushButton('Fit')
        self.fitButton.clicked.connect(self.fitGaussian)

        self.layout5.addWidget(self.fitButton)

        
    def subtractBackground(self):
        self.bkgndImage = self.cameraDevice.read_attribute('Image').value.astype(np.double)

    def updateImage(self):
        #print 'updating image'
        self.image = self.cameraDevice.read_attribute('Image').value.astype(np.double)-self.bkgndImage
        self.img.setImage(self.image) #[425:525,500:600]
        self.lineout0 = np.sum(self.image,axis=0)
        self.plot11.setData(self.lineout0)
        self.lineout1 = np.sum(self.image,axis=1)
        self.plot21.setData(self.lineout1)
        #=======================================================================
        # self.plot21.setData(np.sum(self.image,axis=0))
        # self.plot22.setData(np.sum(self.image,axis=1))
        #=======================================================================
        self.plot21.setPen('r')   
        self.view.update()
        self.cameraWindow.update()
        self.scanTimer.start(100)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

#     splash_pix = QtGui.QPixmap('splash_tangoloading.png')
#     splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
#     splash.setMask(splash_pix.mask())
#     splash.show()
#     splash.showMessage('         Importing modules', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
#                        color=QtGui.QColor('#66cbff'))
#     app.processEvents()
# 
#     splash.showMessage('         Starting GUI', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
#                        color=QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = SpectrometerCamera()
    myapp.show()
    #splash.finish(myapp)
    sys.exit(app.exec_())
