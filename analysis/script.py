import numpy as np 
import scipy as sp 
import matplotlib.pyplot as plt
import tools.load_data as load_data
import pandas as pd 
import glob
from os.path import join, dirname, abspath
#--------------------------------The main function------------------------------
def main():
    """
    this is the first script I wrote in vim! 
    The data processing pipeline: 
        0. Read the xls. 
        1. Identify the zones and the essential zones. 
        2. Draw the bar diagram and add labels, save as eps, jpeg or png. 
        3. Happy! 
    """
    data_folder = "/home/sillycat/Documents/Zebrafish/Behavioral/Social_Behavior/Feb22Control_1/"
    xls_folder =data_folder+'Export Files/' 
    xls_list = glob.glob(xls_folder+'*stat*.xls')
    for fxls in xls_list:
        print(fxls)
        load_data.parse_xls(fxls)
#----------------------------The Execution part---------------------------------
if __name__ == '__main__':
    main()
    
