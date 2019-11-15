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



d = 0.5 # Inter element spacing [lambda]  (the antennas are 35 mm apart from center-to-center, well bellow a half of a 2.4 GHz wavelength (62.5 mm)
M = 3  # number of antenna elements in the antenna system (ULA)
# theta = 90  # incident angle of the test signal [deg]
# Incident angle of source 1
theta_1 =50

# Incident angle of source 2
theta_2 =80

N = 3*160  # sample size signal received in this pahse
wavelength = 1

# Reading the csv file and extracting the I/Q samples

def read_csv_extract_data(name_of_the_csv_file):
    new_data = pd.read_csv(name_of_the_csv_file)
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
    return ant_final


def DOA_plot_me(DOA_data, incident_angles, log_scale_min=None, alias_highlight=True, d=0.5, axes=None):
    DOA_data = np.divide(np.abs(DOA_data), np.max(np.abs(DOA_data)))  # normalization
    if (log_scale_min != None):
        DOA_data = 10 * np.log10(DOA_data)
        theta_index = 0
        for theta in incident_angles:
            if DOA_data[theta_index] < log_scale_min:
                DOA_data[theta_index] = log_scale_min
            theta_index += 1

    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(111)

    # Plot DOA results
    axes.plot(incident_angles, DOA_data)
    axes.set_title('Direction of Arrival estimation ', fontsize=16)
    axes.set_xlabel('Incident angle [deg]')
    axes.set_ylabel('Amplitude [dB]')

    # Alias highlight
    if alias_highlight:
        (theta_alias_min, theta_alias_max) = alias_border_calc(d)
        # print('Minimum alias angle %2.2f ' % theta_alias_min)
        # print('Maximum alias angle %2.2f ' % theta_alias_max)

        axes.axvspan(theta_alias_min, theta_alias_max, color='red', alpha=0.3)
        axes.axvspan(180 - theta_alias_min, 180, color='red', alpha=0.3)

        axes.axvspan(180 - theta_alias_min, 180 - theta_alias_max, color='blue', alpha=0.3)
        axes.axvspan(0, theta_alias_min, color='blue', alpha=0.3)

    plt.grid()
    return axes


incident_angles= np.arange(0,181,1)
ant_final = read_csv_extract_data('rtls_raw_iq_samples_13.csv')
# Generate scanning vectors with the general purpose function
x = np.arange(0, M, 1) * d  # x coordinates
y = np.zeros(M) # y coordinates
# scanning_vectors = gen_scanning_vectors(M, x, y, incident_angles)

# final list of the complex I/Q numbers
npa_ant_final = np.asarray(ant_final)

# Generate multichannel uncorrelated noise
noise = np.random.normal(0, np.sqrt(10 ** -1), (M, N))


# R_2 = corr_matrix_estimate(npa_ant_final.T, imp="mem_eff")
# Array response vector of the test signal

# Array response vectors of test source 1
a_1 = np.exp(np.arange(0,M,1)*1j*2*np.pi*d*np.cos(np.deg2rad(theta_1)))

# Array response vectors of test source 2
a_2 = np.exp(np.arange(0,M,1)*1j*2*np.pi*d*np.cos(np.deg2rad(theta_2)))

soi_matrix  = ( np.outer( npa_ant_final, a_1) + np.outer( npa_ant_final, a_2)).T

# Create received signal array
rec_signal = soi_matrix + noise

# Estimating the spatial correlation matrix
R = corr_matrix_estimate(rec_signal.T, imp="mem_eff")

# incident_angles= np.arange(0,181,1)

# Generate scanning vectors with the general purpose function
x = np.arange(0, M, 1) * d  # x coordinates
y = np.zeros(M) # y coordinates
scanning_vectors = gen_scanning_vectors(M, x, y, incident_angles)
# R_fb = forward_backward_avg(R)

Bartlett = DOA_Bartlett(R, scanning_vectors)
Capon = DOA_Capon(R, scanning_vectors)
# MEM = DOA_MEM(R, scanning_vectors, column_select = 1)
# LPM = DOA_LPM(R, scanning_vectors, element_select = 0)
MUSIC = DOA_MUSIC(R, scanning_vectors, signal_dimension = 1)

# Get matplotlib axes object
axes = plt.axes()

# Plot results on the same fiugre
DOA_plot(Bartlett, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
DOA_plot(Capon, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# DOA_plot(MEM, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
# DOA_plot(LPM, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)
DOA_plot(MUSIC, incident_angles, log_scale_min = -50, axes=axes, alias_highlight=False)

# axes.legend(("Bartlett","Capon","MEM","LPM","MUSIC"))
axes.legend(("Bartlett","Capon","MUSIC"))
plt.show()

