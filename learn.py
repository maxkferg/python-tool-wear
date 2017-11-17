import numpy as np
import matplotlib.pyplot as plt
from lib.utils import rmse
from lib.data import ToolData
from lib.errors import FFTException
from lib.featurize import featurize_tools
from sklearn.gaussian_process.kernels import ConstantKernel, RBF
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.decomposition import PCA


# 20 has no been labelled
test = [22]#,22,29]
#train = [18,19,21,23,25,26,28]
#train = [18,21,23,25,26,28]
train = [18]

scale_mins = None
scale_maxs = None
def scale_linear_bycolumn(rawpoints, high=1.0, low=0.0):
	"""Scale the columns to sit between low and high"""
	return rawpoints
	global scale_mins
	global scale_maxs
	if scale_mins is None or scale_maxs is None:
		print("Calculating column scales")
		scale_mins = np.min(rawpoints, axis=0)
		scale_maxs = np.max(rawpoints, axis=0)
	rng = scale_maxs - scale_mins
	return high - (((high - low) * (scale_maxs - rawpoints)) / rng)


def recursive_predict(model,x):
	"""
	Recursively predict the tool wear.
	Predicted toolwear is added to the last column
	"""
	toolwear = 0
	yhat = [toolwear]
	for i in range(1,x.shape[0]):
		x[i,-1] = toolwear
		toolwear = model.predict(x[i,:])
		yhat.append(toolwear)
	return np.array(yhat)


print("Calculating features")
trainingX,trainingY = featurize_tools(train)
testingX,testingY = featurize_tools(test)

# Normalize the columns on a 0-1 scale
#print("Normalizing columns"
##trainingX = scale_linear_bycolumn(trainingX)
#testingX = scale_linear_bycolumn(testingX)

# Plot the features f
plt.figure()
for rownum in range(trainingX.shape[0]):
	row = trainingX[rownum,:]
	x = range(len(row))
	plt.plot(x,row)
	plt.show()


print("Examining correlation")
energy = np.sum(trainingX,axis=1)
toolwear = trainingY
plt.figure()
plt.xlabel("Tool wear")
plt.ylabel("Energy sum")
plt.plot(toolwear,energy,'o',color="red")
plt.show()


pca = PCA(n_components=3)
pca.fit(trainingX)
trainingX = pca.transform(trainingX)
testingX = pca.transform(testingX)


kernel = RBF(length_scale=0.5, length_scale_bounds=(0.0, 10.0))
model = GaussianProcessRegressor(kernel=None, alpha=1e-10, optimizer='fmin_l_bfgs_b', n_restarts_optimizer=10, normalize_y=False)
model.fit(trainingX, trainingY)

# Self test the SVR model
print("Predicting")
predict = model.predict(trainingX)
print("RMSE on training {0}".format(rmse(predict,trainingY)))

plt.figure()
plt.scatter(trainingY,predict)
plt.title('Training accuracy')
plt.xlabel('Actual Tool Wear')

# Test on testing set
predict = model.predict(testingX)
print("RMSE on testing {0}".format(rmse(predict,testingY)))

plt.figure()
plt.scatter(testingY,predict)
plt.title('Testing accuracy')
plt.xlabel('Actual Tool Wear')
plt.show()






