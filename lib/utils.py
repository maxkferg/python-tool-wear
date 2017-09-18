import numpy as np


def rmse(predictions, targets):
	"""Return the RMSE difference between predictions and targets"""
	return np.sqrt(((predictions - targets) ** 2).mean())
