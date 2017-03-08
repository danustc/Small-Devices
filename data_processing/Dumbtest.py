# Created by Dan on 07/21/2016, dumb test of different functions 

from Behavior import Behavioral_test
import glob
import os
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt 



def main():
    dph = '/home/sillycat/Documents/Zebrafish/Behavioral/Data/Behavior_test6/'
    #Please modify the data path above #


    dset_list = glob.glob(dph+'D1*.csv')
    TF_list = glob.glob(dph + 'TF*G*D1*.npy')
    
    
    
    delim = [',',';']
    dset_list.sort(key = os.path.getmtime) # sort the files based on modification time 
    TF_list.sort(key = os.path.getmtime)
    c_list = zip(dset_list, TF_list) # zip is a cool function in python! 
#     nlist = [0, 1, 2, 3]
    ii = 0
    bar_y = {}
    err_y = {}
    for ds_name, tf_name in c_list:
        dset = np.genfromtxt(ds_name,delimiter = delim[ii], skip_header =1)
        dset[:,0]-=dset[0,0]
        dset[:,0]/=29.98
        diff_per = (dset[:,1]-dset[:,2])/10.
        dset = np.append(dset, diff_per[...,None], 1)
        
        tflag = np.load(tf_name)
        tflag-=tflag[0]
        tflag/=1000.
        fig_name = dph+ 'plot_'+os.path.basename(tf_name)[3:-4]
        print(ds_name)
        print(tf_name)
#         print(fig_name)
        print(tflag[29:33]*29.98+338)
        
        
        BT = Behavioral_test(dset,tflag)
        BT.session_split()
        phase_stat = BT.phase_average()
        
       
        fig_3,bar_y[ii], err_y[ii] = BT.phase_barplot([1,2,3], phase_name=['LED', 'LED+para', 'LED'], n_col = 2 )
        fig_3.savefig(fig_name+'_diff')
        
        plt.clf()  
        
        fig_0, ax_0 = plt.subplots(figsize = (8,4))
        ax_0.errorbar(np.arange(BT.n_trial)*3, phase_stat[:, 0], yerr = phase_stat[:,1], color = 'g', linewidth=2)
        ax_0.errorbar(np.arange(BT.n_trial)*3+1, phase_stat[:,2], yerr = phase_stat[:,3], color = 'b', linewidth=2)
        ax_0.set_xticks(np.arange(BT.n_trial, step=3)*3+1.5)
        ax_0.set_xticklabels(np.arange(BT.n_trial, step=3)+1)
        ax_0.set_ylim([0,9])
        ax_0.legend(['+', '-'], fontsize = 12)
        
        fig_0.savefig(fig_name+'_all')
        
        plt.clf()
        
        
        fig_0, ax_0 = plt.subplots(figsize = (8,4))
        ax_0.plot(BT.data[:,1], color = 'g', linewidth=2)
        ax_0.plot(BT.data[:,2], color = 'b', linewidth=2)
#         ax_0.set_xticks(np.arange(BT.n_trial, step=3)*3+1.5)
#         ax_0.set_xticklabels(np.arange(BT.n_trial, step=3)+1)
        ax_0.set_ylim([0,8])
        ax_0.legend(['+', '-'], fontsize = 12)
        
        fig_0.savefig(fig_name+'_raw')
        ii+=1
        

    t_var, p_var = stats.ttest_rel(bar_y[0], bar_y[1])
    fig_comp, ax_comp = plt.subplots(figsize = (8,4))
    ax_comp.bar(np.arange(20)*3, bar_y[0], yerr=err_y[0], color = 'y')
    ax_comp.bar(np.arange(20)*3+1, bar_y[1], yerr = err_y[1], color = 'g')
    ax_comp.set_xlabel('trial')
    ax_comp.set_ylabel('performance index')
    ax_comp.set_ylim([-0.35,0.65])
    ax_comp.set_xlim([-1, 23])
    ax_comp.legend(['control', 'training'])
    ax_comp.set_xticks(np.arange(21)*3+1.)
    ax_comp.set_xticklabels(np.arange(20)+1)
    
    fig_comp.savefig(dph+'bar_compare')
    
    
    
    print(t_var, p_var)
        #         latency = BT.session_latency(1)
#         BT.latency_plot(fig_name, latency)         



if __name__ == '__main__':
    main()
