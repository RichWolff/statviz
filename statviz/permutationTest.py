# -*- coding: utf-8 -*-
import numpy as np
import os
import matplotlib.pyplot as plt
from .utils import get_ci_intervals

metric_tests = {
	'mean':np.mean,
	'sum':np.sum,
	'median':np.median
}

class PermutationTest:
	def __init__(self,data1,data2,data1Name,data2Name,equalize_means=False,metric_test='mean'):
		self.concat_data = np.concatenate([data1,data2])
		self.data1Name = data1Name
		self.data2Name = data2Name
		
		if equalize_means:
			self.data1 = data1 - metric_tests[metric_test](data1) + self.concat_data.mean()
			self.data2 = data2 - metric_tests[metric_test](data2) + self.concat_data.mean()
		if not equalize_means:
			self.data1 = data1
			self.data2 = data2

		if not metric_test in metric_tests.keys():
			raise ValueError(f"metric_test of '{metric_test}' not a valid test. Use one of {', '.join(metric_tests.keys())}")


		self.metric_test = metric_test
		self.observed_metric = metric_tests[self.metric_test](self.data1) - metric_tests[self.metric_test](data2)
		
	def _bs_permutation_samples(self,bs_n):
		"""Create n randomly permuted samples of two data sets self.data1 and self.data2

		:param bs_n: Number of random permutations to compute
		:param regex: regular expression used to match tokens using re.findall 
		:return: returns self

		>>> _bs_permutation_samples(1000)
		>>> self.bs_tests
		np.array([1,2,3,4,...,1000])
		"""
		if not type(bs_n) == int:
			raise ValueError('Variable "bs_n" must be of type integer. Please try again with an integer')

		self.bs_tests = np.empty(bs_n)

		for i in range(bs_n):
			self._permute_two_arrays()
			self.bs_tests[i] = metric_tests[self.metric_test](self.bs_data1) - metric_tests[self.metric_test](self.bs_data2)

		return self

	def _permute_two_arrays(self):

		"""Randomly permute two arrays using self.data1 and self.data2

		:return: returns self

		>>> _bs_permutation_samples(1000)
		>>> self.bs_tests
		np.array([1,2,3,4,...,1000])
		"""

		#Concat two objects
		data = np.concatenate([self.data1,self.data2])
		
		#Permute objects and return
		permuted = np.random.permutation(data)
		
		self.bs_data1 = permuted[:len(self.data1)]
		self.bs_data2 = permuted[len(self.data1):]
		
		return self
	
	def fit_permuted_metrics(self,bs_n=1000):
		self._bs_permutation_samples(bs_n=bs_n)
		return self
	
	def fit_get_permuted_metrics(self,bs_n=1000):
		self._bs_permutation_samples(bs_n=bs_n)
		return self.bs_tests
	
	def get_permuted_metrics(self):
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

	def __repr__(self):
		return f"<PermutationTest(data1Name='{self.data1Name}', data2Name='{self.data2Name}', metric_test='{self.metric_test}', observed_metric={self.observed_metric})>"

	def _test_histogram_fit(self):
		if not hasattr(self,'histogram'):
			raise ValueError("Have not created histogram yet. Please create and try again.")
		return self

	def _test_fit(self):
		if not hasattr(self,'bs_tests'):
			raise ValueError("Permuted metrics not fit, please fit permutations and try again")

		return self

	def _is_valid_metric_test(self):
		if not type(self.metric_test) == str:
			raise ValueError(f"metric_test of must be a valid string. Use one of {', '.join(metric_tests.keys())}")

		if not self.metric_test in metric_tests.keys():
			raise ValueError(f"metric_test of '{self.metric_test}' not a valid test. Use one of {', '.join(metric_tests.keys())}")


		