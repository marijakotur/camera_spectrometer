'''
Created on 4 Feb 2019

@author: markot
'''

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

def func(x, a, b, c):
    return a * np.exp(-x**2/(2*b)) + c

x = np.linspace(-10, 10, 50) 
noise = np.random.normal(0,1,x.shape)/25
sigma = 4
y = np.exp(-x**2/(2*sigma))
y+=noise

yfunc = func(x,1,3,0)



popt, pcov = curve_fit(func, x, y, bounds = ([0, 0, -1],[10,10,10]))
print 'fit', popt
plt.plot(x, func(x, *popt), 'r-',label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))


plt.plot(x,y)
plt.show()