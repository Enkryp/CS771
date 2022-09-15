from asyncio import base_tasks
from functools import WRAPPER_UPDATES
import numpy as np
# This is the only scipy method you are allowed to use
# Use of scipy is not allowed otherwise
from scipy.linalg import khatri_rao
import random as rnd
import time as tm
import random
import math
# SUBMIT YOUR CODE AS A SINGLE PYTHON (.PY) FILE INSIDE A ZIP ARCHIVE
# THE NAME OF THE PYTHON FILE MUST BE submit.py
# DO NOT INCLUDE PACKAGES LIKE SKLEARN, SCIPY, KERAS ETC IN YOUR CODE
# THE USE OF ANY MACHINE LEARNING LIBRARIES FOR WHATEVER REASON WILL RESULT IN A STRAIGHT ZERO
# THIS IS BECAUSE THESE PACKAGES CONTAIN SOLVERS WHICH MAKE THIS ASSIGNMENT TRIVIAL
# THE ONLY EXCEPTION TO THIS IS THE USE OF THE KHATRI-RAO PRODUCT METHOD FROM THE SCIPY LIBRARY
# HOWEVER, NOTE THAT NO OTHER SCIPY METHOD MAY BE USED IN YOUR CODE

# DO NOT CHANGE THE NAME OF THE METHODS solver, get_features, get_renamed_labels BELOW
# THESE WILL BE INVOKED BY THE EVALUATION SCRIPT. CHANGING THESE NAMES WILL CAUSE EVALUATION FAILURE

# You may define any new functions, variables, classes here
# For example, functions to calculate next coordinate or step length
def compute_grads(w,b,n,x,y,C,batch_size):
    # Shapes
	# x : (batch_size,d)
	# b : scalar
	# y : (batch_size, )
	# w : (d,1)
	y = np.reshape(y,(batch_size,1))
	# y : (batch_size,1)
	hinge_disc = (np.dot( x,w ) + b) * y
	# hinge_disc : (batch_size,1)
	sub_grads = np.zeros((batch_size,1))
	# sub_grads : (batch_size, 1)
	sub_grads[hinge_disc < 1] = -1
	# No grads if hinge_disc is greater than or equal to one, otherwise a multiplier of -1

	delb = C*1.0*n/batch_size *np.dot(sub_grads.T,y) 

	delw =w + C *1.0* n/batch_size * np.dot((x.T * sub_grads.T), y )
	
	return delw, delb 

featuresPrecomputed={}

def features_for_one(X):
	if (tuple(X) in featuresPrecomputed.keys()): return featuresPrecomputed[tuple(X)]

	X[X==0]=-1
	features_length = X.shape[0]
	for i in range(features_length):
		if(i==0):
			continue
		else:
			X[features_length-i-1] = X[features_length-i-1]*X[features_length-i]
	features = []

	for i in range(features_length + 1):
		for j in range(i,features_length + 1):
			for k in range(j,features_length + 1):
				q1,q2,q3 = 0,0,0
				if(i == features_length):
					q1 = 1
				else:
					q1 = X[i]
				if(j == features_length):
					q2 = 1
				else:
					q2 = X[j]
				if(k == features_length):
					q3 = 1
				else:
					q3 = X[k]
				features.append(q1*q2*q3)
	featuresPrecomputed[tuple(X)]=features
	return featuresPrecomputed[tuple(X)] #np.array(features)	
################################
# Non Editable Region Starting #
################################
def get_renamed_labels( y ):
################################
#  Non Editable Region Ending  #
################################

	# Since the dataset contain 0/1 labels and SVMs prefer -1/+1 labels,
	# Decide here how you want to rename the labels
	# For example, you may map 1 -> 1 and 0 -> -1 or else you may want to go with 1 -> -1 and 0 -> 1
	# Use whatever convention you seem fit but use the same mapping throughout your code
	# If you use one mapping for train and another for test, you will get poor accuracy
	y_new = np.copy( y )
	y_new[y_new==1]=-1
	y_new[y_new==0]= 1
	return y_new.reshape( ( y_new.size, ) )					# Reshape y_new as a vector


################################
# Non Editable Region Starting #
################################
def get_features( X ):
################################
#  Non Editable Region Ending  #
################################

	# Use this function to transform your input features (that are 0/1 valued)
	# into new features that can be fed into a linear model to solve the problem
	# Your new features may have a different dimensionality than the input features
	# For example, in this application, X will be 8 dimensional but your new
	# features can be 2 dimensional, 10 dimensional, 1000 dimensional, 123456 dimensional etc
	# Keep in mind that the more dimensions you use, the slower will be your solver too
	# so use only as many dimensions as are absolutely required to solve the problem
	# MY COMMENT : X shape is (D cross 1)
	
	features = []
	for i in range(0,X.shape[0]):
		features.append(features_for_one(X[i]))
	# print(X[0].shape)
	return np.array(features)


################################
# Non Editable Region Starting #
################################
def solver( X, y, timeout, spacing ):
	(n, d) = X.shape
	t = 0
	totTime = 0
	
	# W is the model vector and will get returned once timeout happens
	# B is the bias term that will get returned once timeout happens
	# The bias term is optional. If you feel you do not need a bias term at all, just keep it set to 0
	# However, if you do end up using a bias term, you are allowed to internally use a model vector
	# that hides the bias inside the model vector e.g. by defining a new variable such as
	# W_extended = np.concatenate( ( W, [B] ) )
	# However, you must maintain W and B variables separately as well so that they can get
	# returned when timeout happens. Take care to update W, B whenever you update your W_extended
	# variable otherwise you will get wrong results.
	# Also note that the dimensionality of W may be larger or smaller than 9
	
	W = []
	B = 0
	tic = tm.perf_counter()
################################
#  Non Editable Region Ending  #
################################
	W = np.random.randn((int)(d*(d-1)*(d+1)/6 + d*(d+1) +d) + 1,1)
	B = 0.0
	C = 2
	batch_size = 128
	step_length_OG = 0.01

	# You may reinitialize W, B to your liking here e.g. set W to its correct dimensionality
	# You may also define new variables here e.g. step_length, mini-batch size etc

################################
# Non Editable Region Starting #
################################
	while True:
		t = t + 1
		if t % spacing == 0:
			toc = tm.perf_counter()
			totTime = totTime + (toc - tic)
			if totTime > timeout:
				return ( W.reshape( ( W.size, ) ), B, totTime )			# Reshape W as a vector
			else:
				tic = tm.perf_counter()

################################
#  Non Editable Region Ending  #
################################

		# Write all code to perform your method updates here within the infinite while loop
		# The infinite loop will terminate once timeout is reached
		# Do not try to bypass the timer check e.g. by using continue
		# It is very easy for us to detect such bypasses which will be strictly penalized
		
		# Note that most likely, you should be using get_features( X ) and get_renamed_labels( y )
		# in this part of the code instead of X and y -- please take care
		
		# Please note that once timeout is reached, the code will simply return W, B
		# Thus, if you wish to return the average model (as is sometimes done for GD),
		# you need to make sure that W, B store the averages at all times
		# One way to do so is to define a "running" variable w_run, b_run
		# Make all GD updates to W_run e.g. W_run = W_run - step * delW (similarly for B_run)
		# Then use a running average formula to update W (similarly for B)
		# W = (W * (t-1) + W_run)/t
		# This way, W, B will always store the averages and can be returned at any time
		# In this scheme, W, B play the role of the "cumulative" variables in the course module optLib (see the cs771 library)
		# W_run, B_run on the other hand, play the role of the "theta" variable in the course module optLib (see the cs771 library)
	
		i = random.randrange(n-batch_size-1)
		step_length = step_length_OG/math.sqrt(t)
		x = get_features(X[i:i+batch_size,:])
		out = get_renamed_labels(y[i:i+batch_size])
		delw,delb = compute_grads(W,B,n,x,out,C,batch_size)
	
		W = W -step_length*delw
		B = B - step_length*delb
		
	return ( W.reshape( ( W.size, ) ), B, totTime )			# This return statement will never be reached