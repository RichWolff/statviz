import numpy as np
import matplotlib.pyplot as plt

class ECDF:
	def __init__(self,data):

		if not type(data) == dict:
			raise ValueError('Data variable must be a dictionary with Key being the data title and value being an array of data')

		self.data = {k:{'data':v} for k,v in zip(data.keys(),data.values())}

		self.fit_ecdf()

	def fit_ecdf(self):
		for k in self.data.keys():
			data = self.data[k]
			data['x'] = sorted(data['data'])
			data['n'] = len(data['x'])
			data['y'] = np.arange(1,data['n']+1)/data['n']

	def get_ecdf(self,dataName=None):
		if dataName:
			return self.data[dataName]
		return data
	
	def plot_ecdf(self,plotKeys=[],title_size=14,xlabel_size=12,ylabel_size=12,**kwargs):
		if not kwargs.get('ax'):
			fig = plt.figure(figsize=kwargs.get('figsize'),dpi=kwargs.get('dpi'))
			ax = fig.add_axes([0,0,1,1])

		for k,v in zip(self.data.keys(),self.data.values()):
			if not k in plotKeys or len(plotKeys) == 0:
					ax.plot(self.data[k]['x'], self.data[k]['y'], marker='.', linestyle='none',label=k)

		#Plot x and y labels
		ax.set_ylabel(kwargs.get('ylabel','ECDF'),size=ylabel_size);
		ax.set_xlabel(kwargs.get('xlabel','Metric'),size=xlabel_size);
		ax.set_title(kwargs.get('title',f'Metric ECDF'),size=title_size);

		plt.legend();

		return self

	def test_ecdf_fit(self):
		if not hasattr(self,'x'):
			raise ValueError("Have not fit ECDF yet. Please run fit_ecdf() and try again.")
		return self