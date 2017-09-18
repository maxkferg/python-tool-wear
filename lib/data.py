import os
import glob
import pandas
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from lib.errors import FFTException



def running_mean(x, N):
	"""Return the N-moving average of signal x"""
	cumsum = np.cumsum(np.insert(x, 0, 0))
	return (cumsum[N:] - cumsum[:-N]) / N


def threshold_intercept(x,v):
	"""Return the indices where signal x crosses line v"""
	intercepts = []
	for i in range(len(x)-1):
		if x[i]>=v and x[i+1]<=v:
			intercepts.append(i)
		if x[i]<v and x[i+1]>v:
			intercepts.append(i)
	return intercepts


def iterfile(filename):
	"""Iterate over the lines in a data file, returning those without a date"""
	with open(filename,'r') as fd:
		for line in fd:
			if not line.startswith('2016'):
				yield line



class ToolCut():
	"""Represents a single cutting action"""

	def __init__(self, audio, vibration, audio_time, vibration_time, audio_sample, vibration_sample, toolwear, cuttype):
		"""Create the cut object"""
		self.audio = audio
		self.vibration = vibration
		self.audio_time = audio_time
		self.vibration_time = vibration_time
		self.audio_sample = audio_sample
		self.vibration_sample = vibration_sample
		self.toolwear = toolwear
		self.cuttype = cuttype


	def get_audio_power_spectrum(self,nfft):
		"""Return the 256n point audio power specrtum"""
		f,pxx = welch(self.audio.T, self.audio_sample, window='hanning', nperseg=nfft)
		if len(f) <= nfft/2:
			raise FFTException('Only {0} points in the fft'.format(len(f)))
		# Scale the audio to approx 0-1
		return f, pxx.T/1e22

	def get_vibration_power_spectrum(self,nfft):
		"""Return the 256x4 point vibration power spectrum"""
		power = []
		for i in range(3):
			f,pxx = welch(self.vibration[:,i].T, self.vibration_sample, window='hanning', nperseg=nfft)
			power.append(pxx)
			if len(f) <= nfft/2:
				raise FFTException('Only {0} points in the fft'.format(len(f)))
		return f, np.stack(power).T


	def plot_audio(self):
		"""Plot the audio time series"""
		plt.figure()
		plt.plot(self.audio_time,self.audio)
		plt.title('Audio')

	def plot_vibration(self):
		"""Plot the vibration time series"""
		plt.figure()
		plt.plot(self.vibration_time,self.vibration)
		plt.title('Vibration')


class ToolData():
	"""Represents data from one tool"""
	audio_sample = 8000 #Hz
	vibration_sample = 1000 #Hz

	def __init__(self,tool):
		"""
		Load a tool data set (audio and video) from file.
		@tool is the tool number to load
		"""
		self.tool = tool
		self.audio = self.load_audio() # A single column matrix of audio samples
		self.vibration = self.load_vibration() # A 4 column matrix of vibration samples

		# Audio and vibration time series step
		self.audio_time =  self.get_timeseries(self.audio_sample, self.audio)
		self.vibration_time =  self.get_timeseries(self.vibration_sample, self.vibration)


	def iter_cuts(self):
		"""Return an iterator that yields each cut as a class object"""
		metadata = ToolMetadata(self.tool).read_metadata()
		for index, row in metadata.iterrows():
  			toolwear = row["tool_wear"]
  			cuttype = row["cut_type"]
  			# Get a boolean vector of rows to select
  			aindx = np.logical_and(self.audio_time>=row["start_time"], self.audio_time<row["end_time"])
  			vindx = np.logical_and(self.vibration_time>=row["start_time"], self.vibration_time<row["end_time"])
  			# Select the rows we want
  			audio = self.audio[aindx]
  			vibration = self.vibration[vindx,:]
  			audio_time = self.audio_time[aindx]
  			vibration_time = self.vibration_time[vindx]
  			yield ToolCut(audio, vibration, audio_time, vibration_time, self.audio_sample, self.vibration_sample, toolwear, cuttype)


	def get_timeseries(self,sample_rate,recordings):
		step = 1.0/sample_rate
		tmax = step*recordings.shape[0]
		return np.arange(0,tmax,step)


	def load_audio(self):
		"""Return all the audio as a column array"""
		cache = "data/Cache/audio_T{0:02n}.npy".format(self.tool)
		audio_path = "data/Audio Data/audio_T{0:02n}*".format(self.tool)
		filenames = glob.glob(audio_path)
		return self.load_data(filenames,cache,skiprows=1)


	def load_vibration(self):
		"""Return all the audio as a column array"""
		cache = "data/Cache/accel_T{0:02n}.npy".format(self.tool)
		vibration_path = "data/Vibration Data/accel_T{0:02n}*".format(self.tool)
		filenames = glob.glob(vibration_path)
		return self.load_data(filenames,cache,skiprows=1)


	def load_data(self,filenames,cache,skiprows):
		if os.path.exists(cache):
			print("Loading from {0}".format(cache))
			return np.load(cache)

		# Load all of the minifiles
		rows = []
		for filename in filenames:
			print("Reading {0}".format(filename))
			row = np.loadtxt(iterfile(filename))
			if row.ndim==1:
				# Audio should be a column array
				row = row[np.newaxis].T
			# Detrend before appending
			rows.append(detrend(row,axis=0))
		data = np.vstack(rows)
		np.save(cache,data)
		return data


	def plot(self):
		"""Plot some of the audio spectrum"""
		plt.plot(self.vibration_time, self.vibration[:,0])
		plt.show()



class ToolMetadata():
	"""Metadata holding information about the different tool cuts ect"""

	def __init__(self,tool):
		self.tool = tool
		self.index = "index"


	def get_filepath(self):
		"""Return the paths to the audio files"""
		return "data/Metadata/metadata{tool}.csv".format(tool=self.tool)


	def read_metadata(self):
		"""Return the metadata as a pandas dataframe"""
		filepath = self.get_filepath()
		return pandas.read_csv(filepath, index_col=self.index)


	def write_metadata(self,tooldata):
		"""Write the estimated metadata to the csv file"""
		print("Estimating metadata for tool {0}".format(self.tool))
		metadata = self.estimate_metadata(tooldata)
		filepath = self.get_filepath()
		print("Writing metadata to {0}".format(filepath))
		metadata.to_csv(filepath, index_label=self.index)


	def estimate_metadata(self,tooldata):
		"""Write a file with the best guess metadata"""
		data = []
		boundaries = self.estimate_boundaries(tooldata)
		defaults = ['A','CL','A','CO']
		for i in range(len(boundaries)-1):
			row = {}
			row["start_time"] = boundaries[i]
			row["end_time"] = boundaries[i+1]
			row["cut_type"] = defaults[i%4]
			row["tool_wear"] = 0
			data.append(row)
		return pandas.DataFrame(data)


	def estimate_boundaries(self,tooldata):
		"""
		Estimate bounderies on the different cuts.
		Return as intercepts as time values
		"""
		step = 400
		threshold = 0.5
		signal = abs(tooldata.vibration[:,0])
		envelope_signal = running_mean(signal,step)
		envelope_time = tooldata.vibration_time[step/2-1:-step/2]
		envelope_threshold = threshold*np.average(envelope_signal)
		# Calculate the intercept points
		intercepts = threshold_intercept(envelope_signal,envelope_threshold)
		intercept_y = envelope_signal[intercepts]
		intercept_t = envelope_time[intercepts]
		# Plot the envelope for testing purpose
		#plt.figure()
		#plt.plot(envelope_time, envelope_signal)
		#plt.axhline(y=envelope_threshold)
		#plt.scatter(intercept_t,intercept_y)
		#plt.show()
		return intercept_t




if __name__=="__main__":
	td = ToolData(14)



