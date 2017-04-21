# Written by Mathias Dyssegaard Kallick - 2/22/16
# specifies a class, analysis, that can analyze numpy matrices (with only floats)
# works with the Data class, not with pure numpy matrices

import data
import numpy as np
import scipy as sp
import scipy.stats
import scipy.cluster.vq as vq
import random, math

class Analysis():
	
	def __init__(self):
		return
	
	# takes in a list of headers and returns the min and max of each of the corresponding cols
	def dataRange(self, headers, data):
		tempData = data.getData(headers)
		tempRanges = []
		for i in range(len(headers)):
			tempRanges.append((tempData[:,i].max(),
								 tempData[:,i].min()))
		return tempRanges
	
	# takes in a list of headers and returns the mean of each of the corresponding cols
	def mean(self, headers, data):
		tempData = data.getMatrix()
		tempMeans = []
#		print "headerToMatrix: ", data.headerToMatrix
		for i in headers:
			tempMeans.append((tempData[:,data.headerToMatrix[i]].mean()))
		return tempMeans
	
	# takes in a list of headers and returns the std of each of the corresponding cols
	def std(self, headers, data):
		tempData = data.getData(headers)
		tempStds = []
		for i in headers:
			tempStds.append((tempData[:,data.headerToMatrix[i]].std()))
		return tempStds
	
	# takes in a list of headers and normalizes each corresponding column
	# with respect to itself
	def normalizeColumnsSeparately(self, headers, data):
		
# 		print "headers: ", headers
		if (type(headers[0]) is int):
			tempNormMat = data.getMatrix()
			rows = range(data.getRawNumRows())
			tempMatrix = np.matrix(tempNormMat[rows[0],headers[0]])
			for i in range(len(rows)-1):
				tempMatrix = np.vstack([tempMatrix,
									(tempNormMat[rows[i+1],headers[0]])])
			tempNormMat = tempMatrix
			tempMin = tempNormMat[:,headers[0]].min()
			tempMax = tempNormMat[:,headers[0]].max()
			if(tempMin == tempMax == 0):
				print "column ", headers[0], " has the same min and max, and they are zero."
				print "column ", headers[0], " not normalized"
				pass
			tempNormMat[:,headers[0]] = tempNormMat[:,headers[0]] - tempMin
			tempNormMat[:,headers[0]] = tempNormMat[:,headers[0]] / (tempMax - tempMin)
			for i in range(len(headers)-1):
				tempCol = np.matrix([tempNormMat[rows[0],headers[i+1]]])
				for j in range(len(rows)-1):
					tempCol = np.vstack([tempCol,
										tempNormMat[rows[j+1],headers[i+1]]])	
			tempMatrix = np.hstack([tempMatrix, tempCol])
		else:
			tempNormMat = data.getMatrix()
			for i in headers:
#				print "i in ncs: ", i
#				print "test: ", data.headerToMatrix[i]
				tempMin = tempNormMat[:,data.headerToMatrix[i]].min()
				tempMax = tempNormMat[:,data.headerToMatrix[i]].max()
				if(tempMin == tempMax == 0):
					print "column ", data.headerToMatrix[i], " has the same min and max, and they are zero."
					print "column ", data.headerToMatrix[i], " not normalized"
					pass
				tempNormMat[:,data.headerToMatrix[i]] = tempNormMat[:,data.headerToMatrix[i]] - tempMin
				tempNormMat[:,data.headerToMatrix[i]] = tempNormMat[:,data.headerToMatrix[i]] / (tempMax - tempMin)
			cols = []
			for header in headers:
				cols.append(data.headerToMatrix[header])
			tempNormMat = tempNormMat[:,cols]
		return tempNormMat
		
	# takes in a list of headers and normalizes each corresponding column with
	# respect to all of the columns specified
	def normalizeColumnsTogether(self, headers, data):
		tempNormMat = data.getData(headers)
		tempMin = tempNormMat[:,0].min()
		tempMax = tempNormMat[:,0].max()
		for i in headers:
			if(tempNormMat[:,data.headerToMatrix[i]].min() < tempMin):
				tempMin = tempNormMat[:,data.headerToMatrix[i]].min()
			if(tempNormMat[:,data.headerToMatrix[i]].max() > tempMax):
				tempMax = tempNormMat[:,data.headerToMatrix[i]].max()
		if(tempMin == tempMax == 0):
			print "this matrix has the same min and max, and they are zero."
			return 0
		for i in headers:			
			tempNormMat[:,data.headerToMatrix[i]] = tempNormMat[:,data.headerToMatrix[i]] - tempMin
			tempNormMat[:,data.headerToMatrix[i]] = tempNormMat[:,data.headerToMatrix[i]] / (tempMax - tempMin)
		return tempNormMat
	
	# takes in data, independent variables, and a dependent variables (by their headers 
	# in the data matrix). Performs multiple linear regression and returns values of 
	# the fit (b), the sum-squared error, the R^2 fit quality, the t-statistic, and the
	# probability of a random relationship.
	def linear_regression(self, data, indepHeaders, depHeader):
		y = data.getCol(data.headerToMatrix[depHeader]) # assign dependent variable to y
		tempCols = []
		for i in range(data.getNumColumns()):
			tempCols.append(False)
			for header in indepHeaders:
				if (i == data.headerToMatrix[header]):
					tempCols[i] = True
#		print tempCols
		A = np.compress(tempCols,data.getMatrix(),axis = 1) # assign independent vars to A
		A = np.hstack((A, np.ones((A.shape[0],1))))
		AAinv = np.linalg.inv(np.dot(A.T, A)) # covariance matrix (A.T * A)

		x = np.linalg.lstsq(A, y) # assign solution of y = Ab to x

		b = x[0] # contains all of the slopes, and the last element is the intercept
		N = y.shape[0] # number of data points
		C = b.shape[0] # number of coefficients
		df_e = N-C # degrees of freedom in error
		df_r = C-1 # degrees of freedom in model fit

		error = y - np.dot(A, b) # assign error of model prediction to error

		sse = np.dot(error.T, error) / df_e # make sse the sum squared error

		stderr = np.sqrt( np.diagonal(sse[0, 0] * AAinv) ) # calculate standard error

		t = b.T / stderr # calculate the t-statistics for each independent variable

		p = 2 * (1 - sp.stats.t.cdf(abs(t), df_e)) # probability of a random relationship

		r2 = 1 - error.var() / y.var() # calculate r^2 and assign to r2

		return b, sse, r2, t, p
		  # Return the values of the fit (b), the sum-squared error, the
		  # R^2 fit quality, the t-statistic, and the probability of a
		  # random relationship.
	
	# takes in a data object, and a list of headers. Also has an optional input that
	# determines whether the data is normalized before it is used. Then performs 
	# principle component analysis on that data, and returns a PCAData object with
	# the source column headers, projected data, eigenvalues, eigenvectors, and source
	# data means in it
	def pca(self, dataIn, headers, preNorm = True):
		# get data, normalize if preNorm is True
		if (preNorm == True):
			A = self.normalizeColumnsSeparately(headers, dataIn)
		else:
			A = dataIn.getData(headers)
		
#		print "dataIn: ", dataIn.toStringSimple()
#		print "headers: ", headers
		# perform SVD to get eigenVectors and eigenValues
		m = np.matrix([self.mean(headers, dataIn)])
		D = A - m
		U, S, V = np.linalg.svd(D, full_matrices=False)
		
		eigVals = np.matrix([(S**2)/(dataIn.getNumRows()-1)])
		
		pData = V * D.T 
		eigVecs = V
		
		pcad = data.PCAData( headers, pData, eigVals, eigVecs, m )
		return pcad
	
	# takes in a Data object, a set of headers, and k (# of clusters).
	# returns the codebook, codes, and representation error.
	def numpyKMeans(self, data, headers, k):
		A = data.getMatrix()
		W = vq.whiten(A)
		codebook, bookerror = vq.kmeans(W,k)
		codes, error = vq.vq(W, codebook)
		
		return codebook, codes, error
		
	def kmeans_init(self, data, k, categories=None):
		means = []
		data = np.matrix(data)
		if categories is None:
			i=0
			while i < k:
				rand = random.randint(0, data.shape[1]-1)
				means.append(data[rand,:].tolist()[0])
				i+=1
		
		else:
			means = []
			for k in range(k):
				mean = np.zeros_like( data[0] )
				catSize = 0
				for i in range(categories.shape[0]):
					if categories[i,0] == k:
						for j in range(data.shape[1]):
							mean[0,j] += data[i,j]
						catSize+=1
				mean = mean/catSize
				means.append(mean.tolist()[0])
		means = np.matrix(means)
		return means
	
	def kmeans_classify(self, A, means):
		cats = []
		dists = []
		for i in range(A.shape[0]):
			dist = 0
			for k in range(A.shape[1]):
				dist+=((A[i,k]-means[0,k])**2)
			tempMin = dist
			closestMean = 0
			for j in range(means.shape[0]):
				dist = 0
# 				print "shape of A, shape of means: ", A.shape, means.shape
				for k in range(A.shape[1]):
					dist+=((A[i,k]-means[j,k])**2)
				if tempMin > dist:
					tempMin = dist
					closestMean = j
			cats.append(closestMean)
			dists.append(math.sqrt(tempMin))
		catMatrix = np.matrix(cats)
		distMatrix = np.matrix(dists)
		return (catMatrix,distMatrix)
		
	def kmeans_algorithm(self, A, means):
		# set up some useful constants
		MIN_CHANGE = 1e-7
		MAX_ITERATIONS = 100
		D = means.shape[1]
		K = means.shape[0]
		N = A.shape[0]

		# iterate no more than MAX_ITERATIONS
		for i in range(MAX_ITERATIONS):
			# calculate the codes
			codes, errors = self.kmeans_classify( A, means )

			# calculate the new means
			newmeans = np.zeros_like( means )
			counts = np.zeros( (K, 1) )
			for j in range(N):
				newmeans[codes[0,j],:] += A[j,:]
				counts[codes[0,j],0] += 1.0

			# finish calculating the means, taking into account possible zero counts
			for j in range(K):
				if counts[j,0] > 0.0:
					newmeans[j,:] /= counts[j, 0]
				else:
					newmeans[j,:] = A[random.randint(0,A.shape[0]-1),:]

			# test if the change is small enough
			diff = np.sum(np.square(means - newmeans))
			means = newmeans
			if diff < MIN_CHANGE:
				break

		# call classify with the final means
		codes, errors = self.kmeans_classify( A, means )

		# return the means, codes, and errors
		return (means, codes, errors)
	# takes in a data object, headers, # clusters.
	# returns the codebook, codes, and representation errors
	# If given an Nx1 matrix of categories, it uses the category labels 
	# to calculate the initial cluster means.
	def kmeans(self, d, headers, K, whiten=True, categories = None):
		A = d.getData(headers)
		if whiten == True:
			W = vq.whiten(A)
		else:
			W = A
		codebook = self.kmeans_init(W,K,categories)
		codebook, codes, error = self.kmeans_algorithm(W, codebook)
		return codebook, codes.T, error
	
	def test(self,filename, indepHeaders, depHeader):
		dataObj = data.Data(filename)
		b, sse, r2, t, p = self.linear_regression(dataObj, indepHeaders, depHeader)
		print "slopes: \n", b[:len(indepHeaders)], "\nintercept: ",
		print b[len(indepHeaders)][0,0], "\nSum Squared Error: ", sse[0,0]
		print "R squared: ",r2
		print "t-statistic: ",t,"\nP value: ",p
		return b,r2,t,p
		
if __name__ == "__main__":
	analysis = Analysis()
	print "\nFor data-clean.csv: "
	analysis.test("data-clean.csv",["X0","X1"], "Y")
	print "\nFor data-good.csv: "
	analysis.test("data-good.csv",["X0","X1"], "Y")
	print "\nFor data-noisy.csv: "
	analysis.test("data-noisy.csv",["X0","X1"], "Y")
	
	