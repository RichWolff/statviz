# -*- coding: utf-8 -*-
import numpy as np
import os
import matplotlib.pyplot as plt
from .utils import get_ci_intervals

class PermutationTest:
    def __init__(self,data1,data2,data1Name,data2Name,metric_test=np.mean):
        self.data1 = data1
        self.data1Name = data1Name
        self.data2 = data2
        self.data2Name = data2Name
        self.metric_test = metric_test
        self.observed_metric = self.metric_test(self.data1) - self.metric_test(data2)
        
    def _bs_permutation_samples(self,bs_sample_size):
        self.bs_tests = np.empty(bs_sample_size)

        for i in range(bs_sample_size):
            self._permute_two_arrays()
            self.bs_tests[i] = self.metric_test(self.bs_data1) - self.metric_test(self.bs_data2)

        return self

    def _permute_two_arrays(self):
        """
        Randomly swap entries in two arrays.
        Parameters
        ----------
        a : array_like
            1D array of entries to be swapped.
        b : array_like
            1D array of entries to be swapped. Must have the same lengths
            as `a`.
        Returns
        -------
        self
        """
        #Concat two objects
        data = np.concatenate([self.data1,self.data2])
        
        #Permute objects and return
        permuted = np.random.permutation(data)
        
        self.bs_data1 = permuted[:len(self.data1)]
        self.bs_data2 = permuted[len(self.data1):]
        
        return self
    
    def fit_permuted_metrics(self,bs_sample_size=1000):
        self._bs_permutation_samples(bs_sample_size=bs_sample_size)
        return self
    
    def fit_get_permuted_metrics(self,bs_sample_size=1000):
        self._bs_permutation_samples(bs_sample_size=bs_sample_size)
        return self.bs_tests
    
    def get_permuted_metrics(self,bs_sample_size=1000):
        #Check to see if bs metrics were fitted
        self._test_fit()
        
        return self.bs_tests
    
    def fit_permuted_histogram(self,title_size=14,xlabel_size=12,ylabel_size=12,**kwargs):
        self._test_fit()
        
        if not kwargs.get('ax'):
            fig = plt.figure(figsize=kwargs.get('figsize'),dpi=kwargs.get('dpi'))
            ax = fig.add_axes([0,0,1,1])

        ax.hist(self.bs_tests,bins=kwargs.get('bins'),edgecolor=kwargs.get('edgecolor'),color=kwargs.get('bar_color'));
        
        ylims = ax.get_ylim() # Get chart height

        ax.vlines(x=self.observed_metric,ymin=0,ymax=ylims[1],color='black') # plot observed metric

        # Plot confidence intervals
        confidenceIntervals = get_ci_intervals(self.bs_tests)
  
        for k,v in zip(confidenceIntervals.keys(),confidenceIntervals.values()):
            ylimHigh = ylims[1]/2 if k in (.5,99.5) else ylims[1]
            ax.vlines(x=v, ymin=ylims[0], ymax=ylimHigh, color='red');


        #Plot x and y labels
        ax.set_ylabel(kwargs.get('ylabel','Occurrences'),size=ylabel_size);
        ax.set_xlabel(kwargs.get('xlabel','Metric Change'),size=xlabel_size);
        ax.set_title(kwargs.get('title',f'{self.data1Name} Vs {self.data2Name} Boot Strapped Sample Changes'),size=title_size);
            
        self.histogram = fig;
        return self

    def show_histogram(self,**kwargs):
        self._test_histogram_fit()

        self.histogram.show()
        return self

    def save_figure(self,filename,**kwargs):
        self._test_histogram_fit()

        directory = os.path.dirname(os.path.realpath('__file__'))
        fname = os.path.join(directory,filename)
        savePath = os.path.dirname(fname)

        if not os.path.exists(savePath):
            os.mkdir(savePath)

        self.histogram.savefig(fname=fname, bbox_inches = 'tight',**kwargs)
        return self

    def _test_histogram_fit(self):
        if not hasattr(self,'histogram'):
            raise ValueError("Have not created histogram yet. Please create and try again.")
        return self

    def _test_fit(self):
        if not hasattr(self,'bs_tests'):
            raise ValueError("Permuted metrics not fit, please fit permutations and try again")

        return self

        