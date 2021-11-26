"""
This file is for execute the evaluation

"""

from Haftkraftmessung import HKM


HKM = HKM()

#Here just enter your folder to evaluate with the right folder structure i.e.:
#   PLA_200
#     |>GLAS_60
#     |>GLAS_65
#
# So the folders must be named by the Material and the Nozzle temperature.
# Hence, the subfolders shall be named by the platform followed by the 
# bed temperature all sperated by an underscore (_). 
# The files it self shall be named with "Versuch_01" and so on. 

FolderName = 'PLA_200'

#read the Data from the xlsx files
HKM.readFolder(FolderName)

#get all the Peaks in the Data
HKM.getAllPeaks(height=1)

#If zou want zou can displaz all the peaks
#HKM.plotAll()

#evaluate the mean valueas and standard deviations and save it in a Dataframe
HKM.evaluate()

#We will now show the results and save it as png
HKM.plotResults(save=True)
