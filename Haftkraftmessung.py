import os, glob
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import find_peaks
import pandas as pd
import matplotlib.pyplot as plt

import json


PATH = os.path.dirname(os.path.abspath(__file__))


class HKM:

    def __init__(self):
        self.dataDict = dict()
        self.peakDict = dict()
        id = pd.MultiIndex.from_tuples([],
                           names=('Material', 'Nozzle Temperature',
                                  'Buildplatform', 'Bed Temperature'))
        self.col = pd.MultiIndex(levels=[['Force', 'Temperature'], ['mean','std']],
                                 codes=[[0,0,1,1], [0,1,0,1]])
        #from_tuples([('Force','mean'), ('Force','std'),('Temperature','mean'), ('Temperature','std')])
        self.df=pd.DataFrame(columns=self.col, index=id)
        print(self.df)
        pass

    def readFile(self, file, skip=48):
        """
        This function raeds one data file, from the Adhesion tester

        Parameters
        ----------
        file : path rting 
            path variable to file

        Returns
        -------
        data : pandas dataframe
            read data in dataframe form.

        """
        df = pd.read_excel(file, skiprows=skip)
        data = df.drop(columns=df.columns[1]).to_numpy()
        data[:,0]=data[:,0]-data[0,0]
        return data
        

    def readFolder(self, folder):
        """
        This functions reads the data files structured by Material and the 
        nozzle temperature as folder name.
        The subfolders are structured by the built platform and the bed temperature.

        Data is saved as a dictonary
        """            
            
        key = folder.split('/')[-1]
        for root, dirs, files in os.walk(folder):
            if files:
                subKey=root.split('/')[-1]
                data=dict()
                for fn in  files:
                    if fn.endswith('.xlsx'):
                        name = fn.split('/')[-1].split('.')[0]
                        data.update({name:self.readFile(os.path.join(root,fn))})
                #print(data)
                self.dataDict.update({key+'_'+subKey : data})                        
        pass


    def getPeaks(self, data=False, height=1, distance=500):
        """
        returns the peaks in the data curves passed by the data variable
        """
        x = data[:,0]
        y = data[:,-1]
        peaks,_=find_peaks(y, height=height, distance=distance)

        return [x[peaks], y[peaks]]


    def getAllPeaks(self, height=1, distance=500):
        """
        Evaluation of all peaks in the Data dictonary
        """
        for key, subDict in self.dataDict.items():
            subPeaks=dict()
            for subKey, data in subDict.items():
                subPeaks.update({subKey:self.getPeaks(data=data, 
                                                      height=height, 
                                                      distance=distance)})
            self.peakDict.update({key:subPeaks})
        pass
    
    def plotData(self, data, peaks):
        """
        Plot the diagramm of the measured data points, bed temperature and evaluated peaks
        """
        fig, ax = plt.subplots()

        ax.plot(data[:,0], data[:,-1], 'black')
        ax2=ax.twinx()
        ax2.plot(data[:,0],data[:,1], 'r')

        ylim2=[int(np.mean(data[:,1])-15), int(np.mean(data[:,1])+15)]
        ax2.set(ylim=ylim2)

        if peaks:
            ax.scatter(peaks[0], peaks[1])
      
        plt.show()
        plt.close()


    def plotAll(self):
        """
        visualization of the raw data and the peaks avaliable in the data and peaks dictonary
        """
        for (dataDict, peaksDict) in zip(self.dataDict.values(), self.peakDict.values()):
            
            for (data, peaks) in zip(dataDict.values(), peaksDict.values()):
                
                self.plotData(data, peaks)


    def save(self):
        #Save the pandas Dataframe!
        pass

    def evaluate(self):
        """
        Evaluation of the mean values of the measured points of the data dictonary 
        and saving the results in a pandas DataFrame
        """
        for ((key, subPeaks),(subData)) in zip(self.peakDict.items(),self.dataDict.values()):
            m, nt, b, bt = key.split('_')
            peaks=np.empty((0,0))
            bedTemp=np.empty((0,0))
            for p,t in zip(subPeaks.values(),subData.values()):
                peaks=np.append(p[1], peaks)
                bedTemp=np.append(t[:,1], bedTemp)

            df= pd.DataFrame([[np.mean(peaks), np.std(peaks), np.mean(bedTemp),
                              np.std(bedTemp)]], columns=self.col,index=[[m],[nt],[b],[bt]])
            self.df=self.df.append(df, sort=True)
        #print(self.df)
        pass
    
    def plotResults(self, save=False):
        fig, axs = plt.subplots()
        label=''
        for mat in self.df.index.unique(level=0):
            label+=mat+' '
            subdf=self.df.loc[mat]
            for nt in subdf.index.unique(level=0):
                label+=nt+' '
                subdf=subdf.loc[nt]
                for b in subdf.index.unique(level=0):
                    label+=b+' '
                    subdf=subdf.loc[b]
                    data = []
                    for bt in subdf.index.unique(level=0):
                        row=(subdf.loc[bt].values.tolist())
                        row.append(float(bt))
                        data.append(row)
                    data=np.array(data)

                    axs.errorbar(data[:,-1], data[:,0], yerr=data[:,1], 
                                 fmt='o--', capsize=4)
                    label.replace(b+' ', '')
                label.replace(nt+' ', '')
            label.replace(mat+' ', '')
        
        axs.set_xlabel('Bed temperature in degree C')
        axs.set_ylabel('Adhesion Force in N')
        axs.legend(loc='best')
        plt.tight_layout
        plt.show()
        if save:
            plt.savefig(label+'_results.png', dpi=150)
        return fig, axs
        
        
    def returnPeaks(self,name):
        return self.peakDict.get(name)

    def returnNames(self):
        return list(self.dataDict.keys())

if __name__ == '__main__':
    
    HKM = HKM()
    HKM.readFolder(PATH+'/PLA_200')
    HKM.getAllPeaks()
    #HKM.plotAll()
    HKM.evaluate()
    #HKM.load(PATH)
    HKM.plotResults()
    """
    for fname in glob.glob(PATH+'/*.txt'):
        
        data, name=HKM.readFile(fname)
        N.append(name)
        HKM.getPeaks(name=name)
        print(HKM.returnPeaks(name)[1])
    #HKM.plotData(name=N)
    """

