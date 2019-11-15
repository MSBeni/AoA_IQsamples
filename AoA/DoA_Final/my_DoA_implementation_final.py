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

d = 0.5  # Inter element spacing [lambda]  (the antennas are 35 mm apart from center-to-center, well bellow a half of a 2.4 GHz wavelength (62.5 mm)
M = 3  # number of antenna elements in the antenna system (ULA)
# theta = 90  # incident angle of the test signal [deg]
# N = 160  # sample size signal received in this pahse
wavelength = 1


# Reading the csv file and extracting the I/Q samples

def read_csv_extract_data(name_of_the_csv_file):
    new_data = pd.read_csv(name_of_the_csv_file)
    ant_1 = []
    ant_2 = []
    ant_3 = []
    ant_final = []
    calc = 0
    for j in range(0, len(new_data['pkt'].unique()), 2):
        for i in range(j * 511 + 16, j * 511 + 496, 16):
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


# sample size signal received in this pahse
def calculating_N(name_of_the_csv_file):
    new_data = pd.read_csv(name_of_the_csv_file)
    return (int((len(new_data['pkt'].unique()) / 2)) * 160)


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


def DOA_Bartlett(R, scanning_vectors):
    #     """
    #                     Fourier(Bartlett) - DIRECTION OF ARRIVAL ESTIMATION

    #         Description:
    #         ------------
    #            The function implements the Bartlett method for direction estimation

    #            Calculation method :
    # 		                                                  H
    # 		                PAD(theta) = S(theta) * R_xx * S(theta)

    #         Parameters:
    #         -----------

    #             :param R: spatial correlation matrix
    #             :param scanning_vectors : Generated using the array alignment and the incident angles

    #             :type R: 2D numpy array with size of M x M, where M is the number of antennas in the antenna system
    #             :tpye scanning vectors: 2D numpy array with size: M x P, where P is the number of incident angles

    #        Return values:
    #        --------------

    #             :return PAD: Angular distribution of the power ("Power angular densitiy"- not normalized to 1 deg)
    # 	        :rtype PAD: numpy array

    #             :return -1, -1: Input spatial correlation matrix is not quadratic
    #             :return -2, -2: dimension of R not equal with dimension of the antenna array

    # """

    # --- Parameters ---

    # --> Input check
    if np.size(R, 0) != np.size(R, 1):
        print("ERROR: Correlation matrix is not quadratic")
        return -1, -1

    if np.size(R, 0) != np.size(scanning_vectors, 0):
        print("ERROR: Correlation matrix dimension does not match with the antenna array dimension")
        return -2, -2

    PAD = np.zeros(np.size(scanning_vectors, 1), dtype=complex)

    # --- Calculation ---
    theta_index = 0
    for i in range(np.size(scanning_vectors, 1)):
        S_theta_ = scanning_vectors[:, i]
        PAD[theta_index] = np.dot(np.conj(S_theta_), np.dot(R, S_theta_))
        theta_index += 1

    return PAD


def forward_backward_avg(R):
    #     """
    #         Calculates the forward-backward averaging of the input correlation matrix

    #     Parameters:
    #     -----------
    #         :param R : Spatial correlation matrix
    #         :type  R : M x M complex numpy array, M is the number of antenna elements.

    #     Return values:
    #     -------------

    #         :return R_fb : Forward-backward averaged correlation matrix
    #         :rtype R_fb: M x M complex numpy array

    #         :return -1, -1: Input spatial correlation matrix is not quadratic

    #     """
    # --> Input check
    if np.size(R, 0) != np.size(R, 1):
        print("ERROR: Correlation matrix is not quadratic")
        return -1, -1

        # --> Calculation
    M = np.size(R, 0)  # Number of antenna elements
    R = np.matrix(R)

    # Create exchange matrix
    J = np.eye(M)
    J = np.fliplr(J)
    J = np.matrix(J)

    R_fb = 0.5 * (R + J * np.conjugate(R) * J)

    return np.array(R_fb)


incident_angles = np.arange(0, 181, 1)
data_file = 'rtls_raw_iq_samples_9.csv'
ant_final = read_csv_extract_data(data_file)
N = calculating_N(data_file)
# N = int((len(datafile['pkt'].unique())/2))*160


# Generate scanning vectors with the general purpose function
x = np.arange(0, M, 1) * d  # x coordinates
y = np.zeros(M)  # y coordinates
# scanning_vectors = gen_scanning_vectors(M, x, y, incident_angles)

# final list of the complex I/Q numbers
npa_ant_final = np.asarray(ant_final)
# print(len(npa_ant_final),len(npa_ant_final[0]) )


# Generate multichannel uncorrelated noise
noise = np.random.normal(0, np.sqrt(10 ** -1), (M, N))
# print(noise)
# print(len(noise),len(noise[0]) )

# Create received signal array
rec_signal = npa_ant_final + noise
# print(rec_signal)

signal_dimension = 1

# Estimating the spatial correlation matrix
R = corr_matrix_estimate(rec_signal.T, imp="mem_eff")
R = forward_backward_avg(R)
R_inv = np.linalg.inv(R)  # invert the cross correlation matrix

# Determine eigenvectors and eigenvalues
sigmai, vi = lin.eig(R)
eig_array = []
for i in range(M):
    eig_array.append([np.abs(sigmai[i]), vi[:, i]])
eig_array = sorted(eig_array, key=lambda eig_array: eig_array[0], reverse=False)

# Generate noise subspace matrix
noise_dimension = M - signal_dimension
E = np.zeros((M, noise_dimension), dtype=complex)
for i in range(noise_dimension):
    E[:, i] = eig_array[i][1]

E = np.matrix(E)

# a = np.exp(np.arange(0,M,1)*1j*2*np.pi*d*np.cos(np.deg2rad(60)))
# a_H = np.asarray(a_matrix.getH())

# print(len(a.T),len(a_H.T), len(E*E.getH()),len(E*E.getH()[0]) )

# a = np.exp(np.arange(0,M,1)*1j*2*np.pi*d*np.cos(np.deg2rad(60)))
# a_matrix_ = np.matrix(a).getT()
# s = np.abs(a_matrix_.getH()*(E*E.getH())*a_matrix_)
# print(s)
# print(float(s[0].real))

# soi_matrix = np.zeros((M, N), dtype=complex)
p_BF_Bartlett = []
p_BF_Capon = []
p_BF_MUSIC = []
x_axis = []
for el in range(0, 181):
    x_axis.append(el)
    a = np.exp(np.arange(0, M, 1) * 1j * 2 * np.pi * d * np.cos(np.deg2rad(el)))
    a_matrix = np.matrix(a)
    a_H = np.asarray(a_matrix.getH())
    p_BF_Bartlett_final = (np.dot(a_H.T, np.dot(R, a.T))) / (np.dot(a_H.T, a.T))
    p_BF_Bartlett.append(p_BF_Bartlett_final)
    p_BF_Capon_final = 1 / ((np.dot(a_H.T, np.dot(R_inv, a.T))))
    p_BF_Capon.append(p_BF_Capon_final)
    a_matrix_ = np.matrix(a).getT()
    p_BF_MUSIC_final = (np.dot(a_H.T, a.T)) / (np.abs(a_matrix_.getH() * (E * E.getH()) * a_matrix_))
    p_BF_MUSIC.append(float(p_BF_MUSIC_final[0].real))

axes = plt.axes()

# fig, ax = plt.subplots(figsize=(20,10))
# ax = fig.add_axes([0,0,1,1])
# ax.plot(x_axis, p_BF_TETA, color="red", linewidth=1, marker = 'o', )
# ax.plot(x_axis, p_BF_CAP, color="blue", linewidth=1, marker = '>', )
# ax.plot(x_axis, p_BF_MUSIC, color="green", linewidth=1, marker = 'o', )
DOA_plot_me(p_BF_MUSIC, incident_angles, log_scale_min=-50, axes=axes, alias_highlight=False)
DOA_plot_me(p_BF_Bartlett, incident_angles, log_scale_min=-50, axes=axes, alias_highlight=False)
DOA_plot_me(p_BF_Capon, incident_angles, log_scale_min=-50, axes=axes, alias_highlight=False)

plt.show()
# ax = fig.add_axes([0,0,1,1])
# ax.plot(x,x**2)
# ax.plot(x,x**3)

# p_BF_CAP = []
# x_axis_ = []
# for el in range(0,181):
#     x_axis.append(el)
#     a = np.exp(np.arange(0,M,1)*1j*2*np.pi*d*np.cos(np.deg2rad(el)))
#     a_matrix = np.matrix(a)
#     a_H = np.asarray(a_matrix.getH())
# #     p_BF_TETA = np.dot(a_H, np.dot(R,a))
#     p_BF_CAP_final = 1/((np.dot(a_H.T, np.dot(R_inv,a.T)))
#     p_BF_CAP.append(p_BF_CAP_final)


# print(R)
# print(len(R),len(R[0]) )
