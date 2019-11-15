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


d = 0.35 # Inter element spacing [lambda]
M = 3  # number of antenna elements in the antenna system (ULA)
theta = 60  # incident angle of the test signal [deg]
N = 160  # sample size signal received in this pahse

new_data = pd.read_csv('rtls_raw_iq_samples_11.csv')

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
npa_ant_final = np.asarray(ant_final)
N = len(ant_final[0])
noise = np.random.normal(0,np.sqrt(10**-1),(M,N))

R = corr_matrix_estimate(npa_ant_final.T, imp="mem_eff")


final_angle_teta = []
for i in range(len(ant_final)):
    angle_teta = []
    for j in range(len(ant_final[i])):
        angle_teta.append(np.arctan2(ant_final[i][j].imag, ant_final[i][j].real)*180 / np.pi)
    final_angle_teta.append(angle_teta)


angle_teta_list = []

for j in range(len(ant_final[0])):
    angle_teta_list.append(np.arctan2(ant_final[0][j].imag, ant_final[i][j].real)*180 / np.pi)
    angle_teta_list.append(np.arctan2(ant_final[1][j].imag, ant_final[i][j].real)*180 / np.pi)
    angle_teta_list.append(np.arctan2(ant_final[2][j].imag, ant_final[i][j].real)*180 / np.pi)

final_angle_teta_one_list = []
for i in range(len(ant_final)):
    for j in range(len(ant_final[i])):
        final_angle_teta_one_list.append(np.arctan2(ant_final[i][j].imag, ant_final[i][j].real)*180 / np.pi)

# incident_angles = np.asarray(final_angle_teta)
incident_angles = np.asarray(final_angle_teta_one_list)
print(len(incident_angles))
array_alignment = np.arange(0, M, 1)* d

ula_scanning_vectors = gen_ula_scanning_vectors(array_alignment, final_angle_teta_one_list)

#
# Bartlett = DOA_Bartlett(R,ula_scanning_vectors)
# DOA_plot(Bartlett, incident_angles, log_scale_min = -50)

print(ula_scanning_vectors)
print(len(ula_scanning_vectors))
print(len(ula_scanning_vectors[0]))
# print(ula_scanning_vectors[1])
# print(ula_scanning_vectors[2])

# print(R)
# print(len(R))
# print(len(R[0]),'\n')
#
# print(final_angle_teta)
# print(len(final_angle_teta))
# print(len(final_angle_teta[2]),'\n')
# print(array_alignment)

Bartlett = DOA_Bartlett(R, ula_scanning_vectors)

DOA_plot(Bartlett, incident_angles, log_scale_min = -50, alias_highlight=True, d=d)
plt.show()