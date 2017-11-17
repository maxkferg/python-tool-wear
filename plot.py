import sys
import matplotlib
from lib.data import ToolData
from lib.constants import *
from lib.featurize import get_audio_vibration_vector
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size': FONTSIZE})


tool = int(sys.argv[1])
td = ToolData(tool)
air_cuts = [cut for cut in td.iter_cuts() if cut.cuttype==AIR_CUT]
conv_cuts = [cut for cut in td.iter_cuts() if cut.cuttype==CONV_CUT]
climb_cuts = [cut for cut in td.iter_cuts() if cut.cuttype==CLIMB_CUT]


# Define the action to color mapping
colormap = {
	AIR_CUT: RED,
	CLIMB_CUT: BLUE,
	CONV_CUT: GREEN
}

titlemap = {
	AIR_CUT: 'Air Cutting',
	CLIMB_CUT: 'Conventional Cutting',
	CONV_CUT: 'Climb Cutting'
}


# Plot the vibration without labels
# Designed for experiment 28
print("Plotting vibration time series")
shift = 10 # Seconds
plt.figure(figsize=SIZE)
plt.plot(td.vibration_time-shift, td.vibration[:,0], color=BLUE)
plt.xlabel("Time [s]")
plt.ylabel("Acceleration [g]")
plt.xlim((0, 304))
plt.ylim((-0.7, 0.7))
#plt.show()


# Plot the vibration with labels
# Designed for experiment 28

print("Plotting vibration time series")
tmax = 304
tstart = 0
shift = 10 # Seconds
iterator = td.iter_cuts()
handles = []
plt.figure(figsize=SIZE)
while tstart<tmax:
	cut = iterator.next()
	tstart = cut.vibration_time[0]
	color = colormap[cut.cuttype]
	title = titlemap[cut.cuttype]
	handle = plt.plot(cut.vibration_time-shift, cut.vibration[:,0], color=color, label=title)
	handles.append(handle[0])
plt.xlabel("Time [s]")
plt.ylabel("Acceleration [g]")
plt.xlim((0, 304))
plt.ylim((-0.7, 0.7))
plt.legend([handles[0],handles[3],handles[1]], titlemap.values())
#plt.show()




print("Plotting vibration time series 0")
plt.figure()
plt.plot(cut.vibration_time, cut.vibration[:,0])

print("Plotting vibration time series 1")
plt.figure()
plt.plot(cut.vibration_time, cut.vibration[:,1])


# Plot the vibration vectors over time
"""
count = 0
plt.figure()
for cut in td.iter_cuts():
	print "Plotting vibration time series {0}".format(count)
	color = colormap[cut.cuttype]
	plt.plot(cut.vibration_time, cut.vibration[:,0], color=color)
	count += 1
"""

# Plot the generalized vector for old tool and new tool
nfft = 128
plt.figure()
plt.rc('text', usetex=True)
first = get_audio_vibration_vector(climb_cuts[0],nfft)
last = get_audio_vibration_vector(climb_cuts[-1],nfft)
plt.semilogy(range(len(first)), first, color=BLUE,ls="solid")
plt.semilogy(range(len(last)), last, color=RED,ls="dashed")
plt.xlabel(r'Generic Feature Vector Component, $j$')
plt.ylabel(r'Generic Feature Vector Magnitude, $x^{i}_j$')
plt.legend(['New Tool','Worn Tool'])

# Plot the generalized vector for climb cut, conv cut and air cut
plt.figure()
plt.rc('text', usetex=True)
climb = get_audio_vibration_vector(climb_cuts[2],nfft)
conv = get_audio_vibration_vector(conv_cuts[2],nfft)
air = get_audio_vibration_vector(air_cuts[3],nfft)
plt.semilogy(range(len(air)), air, color=RED, ls="solid",linewidth=2.0)
plt.semilogy(range(len(climb)), climb, color=GREEN, ls="dashed")
plt.semilogy(range(len(conv)), conv, color=BLUE, ls="solid")
plt.xlabel(r'Generic Feature Vector Component, $j$')
plt.ylabel(r'Generic Feature Vector Magnitude, $x^{i}_j$')
plt.legend(titlemap.values())

print("Showing plots")
plt.show()
