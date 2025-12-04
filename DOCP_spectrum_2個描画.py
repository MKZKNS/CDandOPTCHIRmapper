import numpy as np
import matplotlib.pyplot as plt
import os

def DOCP_spectrum(Ex, Ey, Phix, Phiy):
    """
    Calculate the Degree of Circular Polarization (DOCP) spectrum.

    Parameters:
    Ex : array_like
        Electric field component in the x-direction.
    Ey : array_like
        Electric field component in the y-direction.
    Phix : array_like
        Phase of the electric field component in the x-direction.(degrees)
    Phiy : array_like
        Phase of the electric field component in the y-direction.(degrees)

    Returns:
    DOCP : array_like
        Degree of Circular Polarization spectrum.
    """
    # Convert inputs to numpy arrays for element-wise operations
    Ex = np.array(Ex)
    Ey = np.array(Ey)
    Phix = np.array(Phix)
    Phiy = np.array(Phiy)

    Phix = np.deg2rad(Phix)
    Phiy = np.deg2rad(Phiy)

    # Calculate the numerator and denominator for DOCP
    numerator = 2 * Ex * Ey * np.sin(Phiy - Phix)
    denominator = Ex**2 + Ey**2

    # Avoid division by zero by setting DOCP to zero where denominator is zero
    with np.errstate(divide='ignore', invalid='ignore'):
        DOCP = np.where(denominator != 0, numerator / denominator, 0)

    return DOCP


if __name__ == "__main__":
    # import E, Phi from csv files
    filename90 = r'Lambda_39um\1G38p7um\Xincident\Transmission1G38p7umXincident.csv'
    filename0 = r'Lambda_39um\1G38p7um\Yincident\Transmission1G38p7um.csv'
    data = np.loadtxt(filename0, delimiter=',', skiprows=1)
    frequency = data[:, 0]
    Ex0 = data[:, 1]
    Ey0 = data[:, 3]
    Phix0 = data[:, 2]
    Phiy0 = data[:, 4]
    DOCP0 = DOCP_spectrum(Ex0, Ey0, Phix0, Phiy0)

    data = np.loadtxt(filename90, delimiter=',', skiprows=1)
    Ex90 = data[:, 1]
    Ey90 = data[:, 3]
    Phix90 = data[:, 2]
    Phiy90 = data[:, 4]
    DOCP90 = DOCP_spectrum(Ex90, Ey90, Phix90, Phiy90)

    # ディレクトリ名を取得
    figname = 'E_spectrum.png'
    plt.plot(frequency, Ex0, label='Ex 0deg')
    plt.plot(frequency, Ey0, label='Ey 0deg')
    plt.plot(frequency, Ex90, label='Ex 90deg')
    plt.plot(frequency, Ey90, label='Ey 90deg')
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Electric Field Amplitude')
    plt.title('Electric Field Components')
    plt.legend()
    plt.grid()
    plt.savefig(figname)
    plt.show()

    figname = 'Phase_spectrum.png'
    plt.plot(frequency, Phix0, label=r'$\phi_x$ 0deg')
    plt.plot(frequency, Phiy0, label=r'$\phi_y$ 0deg')
    plt.plot(frequency, Phix90, label=r'$\phi_x$ 90deg')
    plt.plot(frequency, Phiy90, label=r'$\phi_y$ 90deg')
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Phase (degrees)')
    plt.title('Phase of Electric Field Components')
    plt.legend()
    plt.grid()
    plt.ylim(-180, 180)
    plt.savefig(figname)
    plt.show()

    figname = 'DOCP_spectrum.png'
    plt.plot(frequency, DOCP0, label='0deg')
    plt.plot(frequency, DOCP90, label='90deg')
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('DOCP')
    plt.ylim(-1, 1)
    plt.title('Degree of Circular Polarization Spectrum')
    plt.grid()
    plt.legend()
    plt.savefig(figname)
    plt.show()