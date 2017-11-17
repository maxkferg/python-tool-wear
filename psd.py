"""
Plot all of the PSD for a given signal
PSD are plotted on subplots depending on their cutting type
"""
import sys
import numpy as np
from lib.data import ToolData
from lib.colors import SIZE
import matplotlib.pyplot as plt
from colour import Color
from numpy import log

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def plot_psd_for_all_cuts(tooldata):
	plt.figure(1)
	cuts = list(td.iter_cuts())
	ncuts = len(cuts)
	colors = Color("green").range_to(Color("red"),ncuts)
	plt.figure()
	for cut in cuts:
		f,pxx = cut.get_audio_power_spectrum()
		color = colors.next()
		# Conventional cuts
		if cut.cuttype=="CO":
			plt.subplot(211)
			plt.plot(f, pxx, color=color.rgb)
		# climb cuts
		elif cut.cuttype=="CL":
			plt.subplot(212)
			plt.plot(f, pxx, color=color.rgb)



def plot_conventional_psd(tooldata):
	nfft = 256
	cuttype = "CO"
	smoother = 3
	cuts = [c for c in td.iter_cuts() if c.cuttype==cuttype]
	ncuts = len(cuts)
	colors = Color("green").range_to(Color("red"),ncuts)
	handles = []

	plt.figure(figsize=SIZE)
	for cut in cuts:
		f,pxx = cut.get_audio_power_spectrum(nfft)
		pxx = smooth(np.squeeze(pxx),smoother)
		color = colors.next()
		handle = plt.semilogy(f, pxx, color=color.rgb)
		handles.append(handle[0])
	plt.xlabel('Frequency [Hz]')
	plt.ylabel('Audio Power')
	plt.legend([handles[0],handles[-1]],["New Tool","Worn Tool"])


def plot_max_distance_for_all_cuts(tooldata):
	"""Plot the distance from the second cut for all cuts"""
	cuts = list(td.iter_cuts())
	climb = [cut for cut in cuts if cut.cuttype=="CL"]
	conv = [cut for cut in cuts if cut.cuttype=="CO"]
	climb_dist = get_max_distance_for_vibration_cuts(climb)
	conv_dist = get_max_distance_for_vibration_cuts(conv)
	plt.figure()
	plt.plot(range(len(climb_dist)), climb_dist)
	plt.plot(range(len(conv_dist)), conv_dist)
	# Plotting wear
	climb_wear = max(climb_dist)*get_wear_for_cuts(climb)/100
	conv_wear = max(conv_dist)*get_wear_for_cuts(conv)/103
	plt.plot(range(len(climb_wear)), climb_wear, color='r')
	plt.plot(range(len(conv_wear)), conv_wear, color='r')



def get_max_distance_for_audio_cuts(cuts):
	nfft = 512
	f,reference = cuts[2].get_audio_power_spectrum(nfft=nfft)
	distances = []
	for i,cut in enumerate(cuts[2:]):
		try:
			f,spectra = cut.get_audio_power_spectrum(nfft=nfft)
			distance = sum(spectra-reference)
			distances.append(distance)
		except:
			print("Skipping {0}".format(i))
	return distances



def get_max_distance_for_vibration_cuts(cuts):
	axis = 0
	nfft = 512
	f,reference = cuts[2].get_vibration_power_spectrum(nfft=nfft)
	reference = reference[:,axis]
	distances = []
	for i,cut in enumerate(cuts[2:]):
		try:
			f,spectra = cut.get_vibration_power_spectrum(nfft=nfft)
			spectra = spectra[:,axis]
			distance = sum(spectra-reference)
			distances.append(distance)
		except:
			print("Skipping {0}".format(i))
	return distances



def get_wear_for_cuts(cuts):
	"""Return the tool wear for a set of cuts"""
	return np.array([cut.toolwear for cut in cuts[2:]])



if __name__=="__main__":
	tool = int(sys.argv[1])
	td = ToolData(tool)
	plot_conventional_psd(td)
	plot_psd_for_all_cuts(td)
	plot_max_distance_for_all_cuts(td)
	plt.show()


