# Always import whatever libraries you need before writing functions and r
# Last update: 07/21/16


from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import os



ccode = ['g', 'b', 'y', 'm', 'c', 'r']



class Behavioral_test(object):
    def __init__(self, dset, tflag, ntotal = 10):
        # time offset corrected. 
        # self.data can have multiple columns, but tflag is only one column.
        
        self.data = dset 
        self.tflag = tflag - tflag[0] 
        self.ds_total = None
        self.trial_phase = {} 
        self.n_trial = len(tflag) 
        self.n_total = ntotal
        
        
    def session_split(self):
        # assume data is already corrected by the time offset. The result is saved in trial_phase  
        # take out the first column of behavior data. Assume that the tflag and tbehave are sharing unit
        t_behave = self.data[:,0] #
        t_idx = np.searchsorted(t_behave, self.tflag)
        nsta = 0 
        
        for idx in np.arange(1, self.n_trial):
            nend = t_idx[idx]
            self.trial_phase[idx-1] = self.data[nsta:nend, :]
            nsta = nend 
        
        # for the last trial, directly append one more 
        self.trial_phase[idx] = self.data[nsta:] # directly to the end
        return self.trial_phase

    def phase_average(self):
        # calculate phase average from the well-spliteed trial_phase 
        # output: phase average
        phase_mean = np.zeros([self.n_trial, self.data.shape[1]-1])
        phase_std = np.zeros_like(phase_mean)
        
        for itrial in np.arange(self.n_trial):
            phase_mean[itrial, :] = np.mean(self.trial_phase[itrial][:,1:], axis = 0)
            phase_std[itrial, :] = np.std(self.trial_phase[itrial][:,1:], axis = 0)
            # update phase_average
        # interleave two arrays
        self.phase_stat = np.empty((phase_mean.shape[0], phase_mean.shape[1]+phase_std.shape[1]))
        self.phase_stat[:,::2] = phase_mean
        self.phase_stat[:,1::2] = phase_std 
        return self.phase_stat

    def phase_barplot(self, n_display, phase_name, n_col, n_period = 4, n_offset = 1):
        # plot the bar chart of the same group, starting from n_offset 
        # n_display: which phase will be plotted?  
        # self.phase_stat is saved 
        # n_col: which column of the data should be plotted, just a number
        # return bar_y
        n_rep = int((self.n_trial-n_offset)/n_period)
        ind = np.arange(n_rep)*(len(n_display)+1)
        fig, ax = plt.subplots(figsize = (8,5))
        bar_ax = {}
        for idis in np.arange(len(n_display)): # nd start from 1 instead of 0
            p_offset = n_offset + (n_display[idis]-1) # phase offset 
            bar_y = self.phase_stat[p_offset::n_period, 2*n_col]
            err_y = self.phase_stat[p_offset::n_period, 2*n_col+1]
            bar_ax[idis] = ax.bar(ind+idis, bar_y, color = ccode[idis], yerr = err_y) 
            
        ax.legend(phase_name, fontsize = 10)
        ax.set_ylim([0,9])
            
        ax.set_xticks(ind+(len(n_display)+1)/2)
        ax.set_xticklabels(np.arange(n_rep)+1)
        
        return fig, bar_y, err_y
        
        
        
    def phase_barplot_diff(self, n_display, phase_name, n_1, n_2,  n_period = 4, n_offset = 1):
        # plot the bar chart of the same group, starting from n_offset 
        # n_display: which phase will be plotted?  
        # self.phase_stat is saved 
        # n_col: which column of the data should be plotted, just a number
        n_rep = int((self.n_trial-n_offset)/n_period)
        ind = np.arange(n_rep)*(len(n_display)+1)
        fig, ax = plt.subplots(figsize = (8,5))
        
        bar_y = self.phase_stat[n_offset::n_period, 2*n_1] - self.phase_stat[n_offset::n_period, 2*n_2]
        
        for idis in np.arange(1,len(n_display)): # nd start from 1 instead of 0
            p_offset = n_offset + (n_display[idis]-1) # phase offset 
            bar_y += self.phase_stat[p_offset::n_period, 2*n_1] - self.phase_stat[p_offset::n_period, 2*n_2]
        
        
        ax.bar(ind+idis, bar_y, color = ccode[0]) 
        ax.legend(phase_name, fontsize = 10)
        ax.set_ylim([-10,15])
            
        ax.set_xticks(ind+(len(n_display)+1)/2)
        ax.set_xticklabels(np.arange(n_rep)+1)
        
        
        return fig, bar_y
        

    
    def session_merge(self, tflag):
        # merge the counting data with the time flags. The time offset is corrected.
        # 
        
        NL = len(tflag)
        tflag = np.column_stack((tflag, np.zeros(NL)))
        ds_total = np.concatenate((self.data, tflag), axis  = 0)
        self.ds_total = ds_total[ds_total[:,0].argsort()] # self.ds_total
        self.flag = np.where(self.ds_total[:,1] == 0)[0]  # mark the flag position
        return self.ds_total
    
    
    def session_latency(self, ev = 1, offset = 1):
        
        NL = len(self.flag)-1 - offset
        latency = np.zeros([NL, 3])
        for ii in np.arange(NL): 
            nsta = self.flag[ii+offset]
            nend = self.flag[ii+1+offset]
            data_section = self.ds_total[nsta:nend]
            t0 = data_section[0,0] # the time offset of the trial
            event_mark = np.where(data_section[:,1] == ev)[0]
            if len(event_mark) == 0:
                print("This session does not have the required event.")
            else:
                latency[ii,0]=data_section[event_mark[0], 0] - t0
                latency[ii,1]=data_section[event_mark, 0].mean() - t0
                latency[ii,2]=data_section[event_mark, 0].std()
                
        return latency
    
    def latency_plot(self, fname, data, nphase = 4):
        fig_init = plt.figure()
        fig_mean = plt.figure()
        ax_init = fig_init.add_subplot(111)
        ax_mean = fig_mean.add_subplot(111)
        NR = data.shape[0]
        
        session_ind = np.arange(0, NR, nphase)
        ind = np.arange(len(session_ind))*(nphase+1)
        
        width = 1.0
        for iphase in np.arange(nphase):
            ax_init.bar(ind+iphase*width, data[session_ind + iphase, 0], color = ccode[iphase])
            ax_mean.bar(ind+iphase*width, data[session_ind + iphase, 1], color = ccode[iphase], yerr = data[session_ind + iphase, 2])
             
            ax_init.set_xticks(ind + 2.0*width)
            ax_mean.set_xticks(ind + 2.0*width)
#             ax.set_xticklabels(keylist, rotation = 0)
        path, ti=os.path.split(fname)
        
        fname_init = ti+'_init'
        fname_mean = ti+'_mean'     
        
        fig_init.savefig(path+'/'+fname_init)
        fig_mean.savefig(path+'/'+fname_mean)
        
        # calculate the latency of the sessions
    
        
    
    
def session_split(dset, tflag, NI, n_offset = 1):
    # dset: dataset 
    # tflag: time flag
    # NI: Initially, how many larvae are on the positive side? 
    NL = len(tflag)-n_offset
    tflag = np.column_stack((tflag[n_offset:], np.zeros(NL)))
    dset[0,1] = NI
    ds_total = np.concatenate((dset, tflag), axis  = 0)
    ds_total = ds_total[ds_total[:,0].argsort()]
    flags = np.where(ds_total[:,1] == 0)[0] # the position of flags
    ds_total[:,1] = ds_total[:,1].cumsum()

    t0 = ds_total[0,0]
    ds_total[:,0] -= t0
    
    NSec = len(flags)
    print(NSec)
    gcount = np.zeros([NSec-n_offset, 2])


    for ii in np.arange(NSec-n_offset):
        nsta = flags[ii] # Find where the session begins
        nend = flags[ii+1] # Find where the session ends
        
        dsection = ds_total[nsta:nend+1] # Take out the session from the dataset
        tdiff = np.diff(dsection[:,0]) # Calculate how long does each state (between two events) last
        gcount[ii,0] = np.inner(tdiff, dsection[:-1, 1]) # Inner product!
        gcount[ii,1] = ds_total[nend,0]-ds_total[nsta,0] # calculate how long does each session last (in miliseconds)
        
    gcount[:,0]/=gcount[:,1]   
        
    return gcount
    
    




def plot_sessions(gcount, pname, keylist):
    LG = len(gcount)
    session_ind = np.arange(0, LG, 4)
    
    g_LED = gcount[session_ind, 0]
    g_FEED = gcount[session_ind+1, 0]
    g_POST = gcount[session_ind+2, 0]
    g_REST = gcount[session_ind+3, 0]
    
    ind = np.arange(len(g_LED))*5
    fig = plt.figure()
    ax = fig.add_subplot(111)
    width = 1.0
    recs1 = ax.bar(ind, g_LED, width, color = 'g')
    recs2 = ax.bar(ind+width, g_FEED, color = 'y')
    recs3 = ax.bar(ind+2*width, g_POST, color = 'b')
    recs4 = ax.bar(ind+3*width, g_REST, color = 'm')
    
    ax.set_xticks(ind + 2.0*width)
    ax.set_xticklabels(keylist, rotation = 0)
    
    ptitle=os.path.split(pname)[1]
    ax.set_title(ptitle)
    ax.set_ylim([0,14])
#     ax.legend((recs1[0], recs2[0], recs3[0]), ('LED', 'LED+para', 'Rest'))
    ax.legend((recs1[0], recs2[0], recs3[0], recs4[0]), ('LED', 'LED+para', 'Post-feeding', 'Rest'))
    plt.savefig(pname) # save the figure 




def session_ttest(gcount, nlist, nsess = 4 ):
    # n1: the session label
    # n2: the session label 
    # return: two matrices of t-values and p-values
    nl = len(nlist) # The length of sessions that 
    t_val = np.zeros([nl,nl])
    p_val = np.identity(nl)
    
    for ii in np.arange(nl):
        ni = nlist[ii]
        X1 = gcount[ni::nsess, 0]
        for jj in np.arange(ii):
            nj = nlist[jj]
            
            X2 = gcount[nj::nsess, 0]
            
            t_val[ii,jj], p_val[ii,jj] = stats.ttest_ind(X1, X2)
            t_val[jj,ii] = t_val[ii,jj]
            p_val[jj,ii] = p_val[ii,jj]
 
    return t_val, p_val
