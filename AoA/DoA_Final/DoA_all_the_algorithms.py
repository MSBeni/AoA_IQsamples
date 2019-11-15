from pyargus.directionEstimation import *
import pandas as pd
import csv
import matplotlib.pyplot as plt
import numpy as np
# %matplotlib inline
import seaborn as sns
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import cufflinks as cf
import plotly
from IPython.display import IFrame
init_notebook_mode(connected=True)
import math
cf.go_offline()



d = 0.5 # Inter element spacing [lambda]
M = 3  # number of antenna elements in the antenna system (ULA)
theta = 60  # incident angle of the test signal [deg]
N = 3*160  # sample size signal received in this pahse
Landa = 1

# Reading the csv  file and extracting the I/Q samples
new_data = pd.read_csv('rtls_raw_iq_samples_13.csv')

ant_1 = []
ant_2 = []
ant_3 = []
ant_final = []
calc = 0
for i in range(16, 496, 16):
    if (calc == 0) or (calc % 3 == 0):
        for j in range(i - 16, i):
            ant_1.append(complex(new_data['i'][j], new_data['q'][j]))
            calc += 1

    elif (calc % 3 == 1):
        for j in range(i - 16, i):
            ant_2.append(complex(new_data['i'][j], new_data['q'][j]))
            calc += 1

    elif (calc % 3 == 2):
        for j in range(i - 16, i):
            ant_3.append(complex(new_data['i'][j], new_data['q'][j]))
            calc += 1

ant_final.append(ant_1)
ant_final.append(ant_2)
ant_final.append(ant_3)

# print(len(ant_final[0]))

# angle_teta_list = []
#
# for j in range(len(ant_final[0])):
#     angle_teta_list.append(np.arctan2(ant_final[0][j].imag, ant_final[0][j].real)*180 / np.pi)
#     angle_teta_list.append(np.arctan2(ant_final[1][j].imag, ant_final[1][j].real)*180 / np.pi)
#     angle_teta_list.append(np.arctan2(ant_final[2][j].imag, ant_final[2][j].real)*180 / np.pi)
#
#
# # final_angle_teta_one_list = []
# # for i in range(len(ant_final)):
# #     for j in range(len(ant_final[i])):
# #         final_angle_teta_one_list.append(np.arctan2(ant_final[i][j].imag, ant_final[i][j].real)*180 / np.pi)
#
# # incident_angles = np.asarray(final_angle_teta)
# incident_angles = np.asarray(angle_teta_list)
incident_angles= np.arange(0,181,1)

# Generate scanning vectors with the general purpose function
x = np.arange(0, M, 1) * d  # x coordinates
y = np.zeros(M) # y coordinates
# scanning_vectors = gen_scanning_vectors(M, x, y, incident_angles)

# final list of the complex I/Q numbers
npa_ant_final = np.asarray(ant_final)

# R_2 = corr_matrix_estimate(npa_ant_final.T, imp="mem_eff")
# Array response vector of the test signal
a = np.exp(np.arange(0,M,1)*1j*2*np.pi*d*(1/Landa)*np.cos(np.deg2rad(theta)))
# a_2 = np.exp(np.arange(0,M,1)*1j*2*np.pi*d*(1/Landa)*np.cos(np.deg2rad(theta+10)))
# a_3 = np.exp(np.arange(0,M,1)*1j*2*np.pi*d*(1/Landa)*np.cos(np.deg2rad(theta+20)))

print(a)
# Generate multichannel test signal
# soi = np.random.normal(0,1,N)  # Signal of Interest

soi_matrix  = np.outer(npa_ant_final, a).T

# soi_matrix_2  = np.outer(npa_ant_final, a_2).T
# soi_matrix_3  = np.outer(npa_ant_final, a_3).T

# Generate multichannel uncorrelated noise
noise = np.random.normal(0,np.sqrt(10**-1),(M,N))

# Create received signal array
rec_signal = soi_matrix + noise

# rec_signal_2 = soi_matrix_2 + noise
# rec_signal_3 = soi_matrix_3 + noise

# Estimating the spatial correlation matrix
R = corr_matrix_estimate(rec_signal.T, imp="mem_eff")

# R_2 = corr_matrix_estimate(rec_signal_2.T, imp="mem_eff")
# R_3 = corr_matrix_estimate(rec_signal_3.T, imp="mem_eff")

# incident_angles= np.arange(0,181,1)

# Generate scanning vectors with the general purpose function
x = np.arange(0, M, 1) * d  # x coordinates
y = np.zeros(M) # y coordinates
scanning_vectors = gen_scanning_vectors(M, x, y, incident_angles)


Bartlett = DOA_Bartlett(R, scanning_vectors)
Capon = DOA_Capon(R, scanning_vectors)
# MEM = DOA_MEM(R, scanning_vectors, column_select = 1)
# LPM = DOA_LPM(R, scanning_vectors, element_select = 0)
MUSIC = DOA_MUSIC(R, scanning_vectors, signal_dimension = 1)

# Bartlett_2 = DOA_Bartlett(R_2, scanning_vectors)
# Capon_2 = DOA_Capon(R_2, scanning_vectors)
# MEM = DOA_MEM(R, scanning_vectors, column_select = 1)
# LPM = DOA_LPM(R, scanning_vectors, element_select = 0)
# MUSIC_2 = DOA_MUSIC(R_2, scanning_vectors, signal_dimension = 1)
# Bartlett_3 = DOA_Bartlett(R_3, scanning_vectors)
# Capon_3 = DOA_Capon(R_3, scanning_vectors)
# MEM = DOA_MEM(R, scanning_vectors, column_select = 1)
# LPM = DOA_LPM(R, scanning_vectors, element_select = 0)
# MUSIC_3 = DOA_MUSIC(R_3, scanning_vectors, signal_dimension = 1)

# Get matplotlib axes object
axes = plt.axes()

# Plot results on the same fiugre
DOA_plot(Bartlett, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
DOA_plot(Capon, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# DOA_plot(MEM, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# DOA_plot(LPM, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
DOA_plot(MUSIC, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)


# DOA_plot(Bartlett_2, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# DOA_plot(Capon_2, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# # DOA_plot(MEM, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# # DOA_plot(LPM, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# DOA_plot(MUSIC_2, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# DOA_plot(Bartlett_3, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# DOA_plot(Capon_3, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# # DOA_plot(MEM, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# # DOA_plot(LPM, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# DOA_plot(MUSIC_3, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)

# axes.legend(("Bartlett","Capon","MEM","LPM","MUSIC"))
axes.legend(("Bartlett","Capon","MUSIC"))
plt.show()
