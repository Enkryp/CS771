import numpy as np
from numpy import random as rand
from joblib import load
from params import *
import tensorflow as tf
# DO NOT CHANGE THE NAME OF THIS METHOD OR ITS INPUT OUTPUT BEHAVIOR

# PLEASE BE CAREFUL THAT ERROR CLASS NUMBERS START FROM 1 AND NOT 0. THUS, THE FIFTY ERROR CLASSES ARE
# NUMBERED AS 1 2 ... 50 AND NOT THE USUAL 0 1 ... 49. PLEASE ALSO NOTE THAT ERROR CLASSES 33, 36, 38
# NEVER APPEAR IN THE TRAINING SET NOR WILL THEY EVER APPEAR IN THE SECRET TEST SET (THEY ARE TOO RARE)

# Input Convention
# X: n x d matrix in csr_matrix format containing d-dim (sparse) bag-of-words features for n test data points
# k: the number of compiler error class guesses to be returned for each test data point in ranked order

# Output Convention
# The method must return an n x k numpy nd-array (not numpy matrix or scipy matrix) of classes with the i-th row 
# containing k error classes which it thinks are most likely to be the correct error class for the i-th test point.
# Class numbers must be returned in ranked order i.e. the label yPred[i][0] must be the best guess for the error class
# for the i-th data point followed by yPred[i][1] and so on.

# CAUTION: Make sure that you return (yPred below) an n x k numpy nd-array and not a numpy/scipy/sparse matrix
# Thus, the returned matrix will always be a dense matrix. The evaluation code may misbehave and give unexpected
# results if an nd-array is not returned. Please be careful that classes are numbered from 1 to 50 and not 0 to 49.

def get_top_k_preds(model_code,model,x,k):
	"""Directs the call to the appropriate predictor function using the model_code. 
	Add your predictor function in this file
	Then modify this function
	Add the model_code to params.py"""

	if(model_code == DT_TREE_CODE):
		return DT_preds(model,x,k)
	if(model_code ==  DL_CODE):
		return DL_preds(model,x,k)

def DL_preds(model,x,k):
	"""Takes a DL model (tf.keras.models.Sequential). Predicts the top k classes """
	# Divide x by its norm
	x = x.toarray()
	norm = np.linalg.norm(x)
	x = x/norm
	preds = model(x)
	top_k = tf.math.top_k(preds,k)[-1]
	return np.reshape(top_k,(top_k.shape[1]))	

def DT_preds(model,x,k):
	"""Takes a DT model (sklearn.tree.DecisionTreeClassfier). Predicts the top k classes """
	y_pred = model.predict_proba(x)
	probs = [-1]
	for i in range(1,CLASSES + 1):
		probs.append(1.0 - y_pred[i][0][0])
	res = (sorted(range(len(probs)), key = lambda sub: probs[sub])[-k:])
	res.reverse()
	return np.array(res)

def findErrorClass( X, k ):
	# Find out how many data points we have
	n = X.shape[0]
	# Load and unpack a dummy model to see an example of how to make predictions
	# The dummy model simply stores the error classes in decreasing order of their popularity
	model = tf.keras.models.load_model(MODEL_PATH)
	y_pred = []
	for j in range(n):
		y_pred.append(get_top_k_preds(DL_CODE,model, X[j],k))
	return np.array(y_pred)