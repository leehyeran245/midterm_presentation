from lmfit import Parameters, fit_report, minimize, Model
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import parse
import matplotlib.pyplot as plt
import numpy as np
from numpy import exp
import warnings


def polyfit(x, y, degree):
    results = {}
    coeffs = np.polyfit(x, y, degree)
    results['polynomial'] = coeffs.tolist()
    p = np.poly1d(coeffs)
    yhat = p(x)
    ybar = np.sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)
    sstot = np.sum((y - ybar)**2)
    results['determination'] = ssreg / sstot
    return results


def IV(x, Is, vt):
    return Is * (exp(x / vt) - 1)


def graph(path):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', np.RankWarning)
        tree = parse(str(path))
        root = tree.getroot()
        plt.figure(figsize=(16, 10))
        # IV Measurement
        plt.subplot(2, 3, 4)
        voltage = list(map(float, root.find('.//IVMeasurement/Voltage').text.split(',')))
        current = list(map(float, root.find('.//IVMeasurement/Current').text.split(',')))
        v = np.array(voltage)
        c = np.array(current)
        gmodel = Model(IV)
        params = gmodel.make_params(Is=1, vt=0.026)
        result = gmodel.fit(c, params, x=v)

        c2 = c - result.best_fit
        r_square = {}
        for i in range(1, 20):
            poly = polyfit(v, c2, i)
            r_square[i] = poly['determination']
        max_key = max(r_square, key=lambda key: r_square[key])
        global max_IV_rsq
        max_IV_rsq = r_square[max_key]
        polyIV = np.poly1d(np.polyfit(v, c2, max_key))(v)

        plt.plot(v, abs(c), 'ok')
        plt.plot(v, abs(result.best_fit + polyIV), '--', label='Highest order term = {}'.format(max_key))
        plt.legend(loc='best')
        plt.xlabel('Voltage[V]')
        plt.ylabel('Current[A]')
        plt.title('IV-analysis')
        plt.yscale('log')

        # Raw Spectrum
        plt.subplot(2, 3, 1)
        ref_L = list(map(float, root.findtext(".//*[@Name='DCM_LMZC_ALIGN']//L").split(',')))
        ref_IL = list(map(float, root.findtext(".//*[@Name='DCM_LMZC_ALIGN']//IL").split(',')))
        global max_IL
        max_IL = max(ref_IL)
        for wavelengthsweep in root.iter('WavelengthSweep'):
            L = list(map(float, wavelengthsweep.findtext('L').split(',')))
            IL = list(map(float, wavelengthsweep.findtext('IL').split(',')))
            if IL == ref_IL:
                name = 'Reference'
            else:
                name = 'DCBias=' + str(wavelengthsweep.attrib['DCBias']) + 'V'
            plt.plot(L, IL, 'o', label=name)

        plt.legend(loc='lower right')
        plt.xlabel('Wavelength[nm]')
        plt.ylabel('Measured transmissions[dB]')
        plt.title('Transmission spectra - as measured')

        # Fitting
        plt.subplot(2, 3, 3)
        x = np.array(ref_L)
        y = np.array(ref_IL)

        plt.scatter(x, y, facecolor='none', edgecolor='r', alpha=0.06, label='Reference')
        Ref_Rsq = {}
        for i in range(4, 7):
            poly = polyfit(x, y, i)
            Ref_Rsq[i] = poly['determination']
            fit = np.poly1d(poly['polynomial'])(x)
            plt.plot(x, fit, label='Highest order term =' + str(i) + '\nR^2 = ' + str(poly['determination']))

        global Ref_max
        Ref_max = max(Ref_Rsq, key=lambda key: Ref_Rsq[key])
        global Max_Rsq
        Max_Rsq = Ref_Rsq[Ref_max]
        plt.legend(loc='lower right')
        plt.xlabel('Wavelength[nm]')
        plt.ylabel('Measured transmissions[dB]')
        plt.title('Fitting Function')

        # Modeling
        plt.subplot(2, 3, 2)
        ref = np.poly1d(np.polyfit(x, y, Ref_max))
        for wavelengthsweep in root.iter('WavelengthSweep'):
            L = list(map(float, wavelengthsweep.findtext('L').split(',')))
            IL = list(map(float, wavelengthsweep.findtext('IL').split(',')))
            l = np.array(L)
            il = np.array(IL)
            if IL == ref_IL:
                name = 'Reference'
            else:
                name = 'DCBias=' + str(wavelengthsweep.attrib['DCBias']) + 'V'
            plt.plot(l, il - ref(l), label=name)

        plt.legend(loc='lower right')
        plt.xlabel('Wavelength[nm]')
        plt.ylabel('Transmissions[dB]')
        plt.title('Transmission spectra - fitted')
        plt.savefig(r'C:/Users/이혜란/OneDrive/바탕 화면/graph/' + path[-40:-5] +'.png')
        plt.clf()
