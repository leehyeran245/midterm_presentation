import pandas as pd
import xml.etree.ElementTree as ET
from dateutil.parser import parse
import fit_test
import os


def data_save(path):
    tree = ET.parse(path)
    root = tree.getroot()

    columns = ['Lot', 'Wafer', 'Mask', 'TestSite', 'Name', 'Date', 'Row', 'Column', 'ErrorFlag', 'Error description', 'Analysis Wavelength', 'Rsq of Ref. spectrum (Nth)', 'Max transmission of Ref. spec. (dB)', 'Rsq of 1V', 'I at -1V [A]', 'I at 1V[A]']
    #  'Script ID', 'Script Version', 'Script Owner',
    #  스크립트 정보

    data = []
    values = []

    TestSiteInfo = root.find('TestSiteInfo').attrib
    values.append(TestSiteInfo['Batch'])
    values.append(TestSiteInfo['Wafer'])
    values.append(TestSiteInfo['Maskset'])
    values.append(TestSiteInfo['TestSite'])
    Modulator = root.find('.//Modulator')
    values.append(Modulator.attrib['Name'])
    PortCombo = Modulator.find('PortCombo')
    values.append(parse(PortCombo.attrib['DateStamp']))
    values.append(TestSiteInfo['DieRow'])
    values.append(TestSiteInfo['DieColumn'])

    if fit_test.Ref_max >= 0.99:
        ErrorFlag = 0
        ErrorDescription = 'No Error'
    else:
        ErrorFlag = 1
        ErrorDescription = 'Ref. spec. Error'

    values.append(ErrorFlag)
    values.append(ErrorDescription)
    values.append(root.find(".//DesignParameter[@Name='Design wavelength']").text)
    values.append(fit_test.Max_Rsq)
    values.append(fit_test.max_IL)

    voltage = list(map(float, root.find('.//IVMeasurement/Voltage').text.split(',')))
    current = list(map(float, root.find('.//IVMeasurement/Current').text.split(',')))
    index1 = voltage.index(-1)
    index2 = voltage.index(1)
    values.append(fit_test.max_IV_rsq)
    values.append(current[index1])
    values.append(current[index2])

    # 스크립트 정보 추가 필요

    data.append(values)
    df = pd.DataFrame(data, columns=columns).set_index('Lot')
    if not os.path.exists('sample.csv'):
        df.to_csv('sample.csv', mode='w')
    else:
        df.to_csv('sample.csv', mode='a', header=False)
