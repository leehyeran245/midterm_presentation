import glob
from glob import glob
import fit_test
import analysis_test

for data in glob('C:/Users/이혜란/OneDrive/바탕 화면/2021-1/공프2/P184640/**/*.xml', recursive=True):
    if data.endswith('LMZC.xml'):
        try:
            fit_test.graph(data)
            analysis_test.data_save(data)
            print(data)
        except:
            None
