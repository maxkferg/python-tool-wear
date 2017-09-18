import numpy as np
from .utils import rmse
from sklearn.svm import SVR
from lib.data import ToolData
from lib.errors import FFTException
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
import matplotlib.pyplot as plt


AUDIO_SCALE = 5e10
ACCEL_SCALE = 1e4


def difference(a,b):
	"""Return the positive difference between a and b"""
	return abs(a-b)


def get_audio_vibration_vector(cut,nfft=128):
	"""Return the joined audio and vibration vectors"""
	f,audio = cut.get_audio_power_spectrum(nfft=nfft)
	f,vibration = cut.get_vibration_power_spectrum(nfft=nfft)
	audio = AUDIO_SCALE*audio.flatten()
	vibration = ACCEL_SCALE*np.sum(vibration,axis=1).flatten()
	return np.concatenate([vibration]).flatten()


def featurize_cuts(cuts,cuttype):
	"""Return a list of tool x and tool y pairs"""
	reference = get_audio_vibration_vector(cuts[1])
	xlist = []
	ylist = []

	for i,cut in enumerate(cuts):
		if i==0:
			continue
		# Boolean feature to separate climb and conventional cuts
		try:
			spectra = get_audio_vibration_vector(cut)
			features = spectra-reference
			cut.plot_vibration()
			cut.plot_audio()
			plot_against_reference(reference,features)
			plt.show()

			features = np.append(features,cuttype)
			features = np.append(features,cuts[i-1].toolwear)
			xlist.append(features)
			ylist.append(cut.toolwear)
		except FFTException:
			print("Skipping cut {0}".format(i))
	plt.figure()
	return xlist,ylist


def featurize_tools(tools):
	"""Featurize a list of tools"""
	X = []
	Y = []
	for tool in tools:
		td = ToolData(tool)
		climb = [cut for cut in td.iter_cuts() if cut.cuttype=="CL"]
		# conv = [cut for cut in td.iter_cuts() if cut.cuttype=="CO"]
		# Featurize climb and conventional separately and combine
		xclimb, yclimb = featurize_cuts(climb,cuttype=1)
		#xconv, yconv = featurize_cuts(conv,cuttype=0)
		X = X + xclimb #+ xconv
		Y = Y + yclimb #+ yconv
	# Stack the arrays into well-formed matrices
	X = np.array(X)
	Y = np.array(Y)
	return X,Y



def plot_against_reference(reference,features):
	x = range(len(reference))
	plt.figure()
	plt.plot(x,reference,'r--')
	plt.plot(x,features,'b')
