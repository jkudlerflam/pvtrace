import numpy as np
import matplotlib.pyplot as plt

x = np.load('/Users/jkudlerflam/Desktop/reflectance3.npy')
plt.plot(np.linspace(0,.95, 98), x[0:98], 'o')
plt.ylabel('External Reflection')
plt.xlabel('Distance y/R')
plt.show()