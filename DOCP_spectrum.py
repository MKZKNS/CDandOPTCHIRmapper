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
    filename = r"D:\研究データ\20251230_thzBEshift_woBowtie\circle_aperture_Ypol.csv"
    data = np.loadtxt(filename, delimiter=',', skiprows=1)
    head = np.loadtxt(filename, delimiter=',', max_rows=1, dtype=str)
    # pickup frequency unit
    freq_unit = head[0].split('[')[1].split(']')[0]
    frequency = data[:, 0]
    Ex = data[:, 1]
    Ey = data[:, 3]
    Phix = data[:, 2]
    Phiy = data[:, 4]
    DOCP = DOCP_spectrum(Ex, Ey, Phix, Phiy)

    # ディレクトリ名を取得
    dirname = os.path.dirname(filename)
    figname = os.path.join(dirname, 'E_spectrum.png')
    plt.plot(frequency, Ex, label='Ex')
    plt.plot(frequency, Ey, label='Ey')
    plt.xlabel(f'Frequency [{freq_unit}]')
    plt.ylabel('Transmission')
    plt.title('Electric Field Components')
    plt.legend()
    plt.grid()
    # plt.ylim([0,25])
    plt.savefig(figname)
    plt.show()

    figname = os.path.join(dirname, 'Phase_spectrum.png')
    plt.plot(frequency, Phix, label=r'$\phi_x$')
    plt.plot(frequency, Phiy, label=r'$\phi_y$')
    plt.xlabel(f'Frequency [{freq_unit}]')
    plt.ylabel('Phase [degrees]')
    plt.title('Phase of Electric Field Components')
    plt.legend()
    plt.grid()
    plt.ylim(-180, 180)
    plt.savefig(figname)
    plt.show()

    figname = os.path.join(dirname, 'DOCP_spectrum.png')
    plt.plot(frequency, DOCP)
    # max vline
    idx_max_docp = np.argmax(np.abs(DOCP))
    plt.vlines(frequency[idx_max_docp], -1, 1, colors='red', linestyles='dashed', linewidth=3)
    # text box
    plt.text(0.05, 0.05, f'MAX DOCP: {DOCP[idx_max_docp]:.2f}\nFreq: {frequency[idx_max_docp]:.2f} {freq_unit}',
             backgroundcolor='lightblue',
             fontsize="x-large",
             transform=plt.gca().transAxes)
    plt.xlabel(f'Frequency [{freq_unit}]')
    plt.ylabel('DOCP')
    plt.ylim(-1, 1)

    plt.title('Degree of Circular Polarization Spectrum')
    plt.grid()
    plt.savefig(figname)
    plt.show()