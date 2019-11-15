from pyargus.directionEstimation import *
import matplotlib.pyplot as plt
import numpy as np
# %matplotlib inline

d = 0.5  # Inter element spacing [lambda]
M = 4  # number of antenna elements in the antenna system (ULA)
N = 2 ** 12  # sample size used for the simulation
theta = 60  # incident angle of the test signal [deg]

# Change the interelement sapcing.
# ! Spatial aliasing will occur !
d= 0.8
incident_angles= np.arange(0,181,1)

# Generate scanning vectors with the general purpose function
x = np.arange(0, M, 1) * d  # x coordinates
y = np.zeros(M) # y coordinates
scanning_vectors = gen_scanning_vectors(M, x, y, incident_angles)
# print('scanning_vectors: ','\n',scanning_vectors,'\n')
#
# print(len(scanning_vectors))
# print(len(scanning_vectors[0]))

# Array response vector of the test signal
a = np.exp(np.arange(0,M,1)*1j*2*np.pi*d*np.cos(np.deg2rad(theta)))
# print('a: ','\n',a,'\n')
# Generate multichannel test signal
soi = np.random.normal(0,1,N)  # Signal of Interest
# print('soi: ','\n',soi,'\n')
# print(len(soi))
soi_matrix  = np.outer(soi, a).T
#print('soi_matrix: ','\n',soi_matrix,'\n',len(soi_matrix[0]))


# Generate multichannel uncorrelated noise
noise = np.random.normal(0,np.sqrt(10**-1),(M,N))

# Create received signal array
rec_signal = soi_matrix + noise

# Estimating the spatial correlation matrix
R = corr_matrix_estimate(rec_signal.T, imp="mem_eff")
print(len(R))
print(len(R[0]))
# Estimate DOA with the Bartlett method
Bartlett = DOA_Bartlett(R, scanning_vectors)

DOA_plot(Bartlett, incident_angles, log_scale_min = -50, alias_highlight=True, d=d)
plt.show()