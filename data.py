# CSV reading file that interprets csv files into various data structures
# takes in an optional filename
# Written by Mathias Dyssegaard Kallick
# 2/16/16

import csv;
import numpy as np;
import analysis
import time

class Data:
	
	def __init__(self, filename = None):
		
		self.rawHeaders = [];
		self.dataHeaders = [];
		self.rawTypes = [];
		self.rawData = [];
		self.headerToRaw = {};
		self.matrixData = ([]);
		self.headerToMatrix = {};
		self.enumToNumberByCol = {}
		
		if (filename != None):
			self.read(filename);
	
	# opens a file specified by filename (as a string, with file extension)
	# reads that file into rawData, and also takes the numeric columns and
	# puts them into matrixData
	def read(self, filename):
		with open(filename, 'rU') as csvfile: # from csv python docs
			reader = csv.reader(csvfile)
			i = 0;
			for row in reader:
				if(i == 0):
					temprow = row[:]
					for j in range(len(temprow)):
						temprow[j] = (str)(temprow[j]).strip()
					self.rawHeaders = temprow;
				elif(i == 1):
					self.rawTypes = row;
				else:
					self.rawData.append(row);
				i+=1;
			
			for i in range(len(self.rawData)):
				if(self.rawData[i][0] == "#"): #checks for commented out lines, removes them
					self.rawData.pop(i)
			self.makeMatrix()
		
#		print self.matrixData
#		print "headerToMatrix: ", self.headerToMatrix
#		print "headers: ", self.rawHeaders
#		print "types: ", self.rawTypes
#		print "data: ", self.rawData
	
	# makes the matrix
	def makeMatrix(self):
		# make a matrix out of all of the numeric types here:
		tempNumArray = []
		k = 0
		for i in range(len(self.rawTypes)):
			if((str)(self.rawTypes[i]).strip() == "numeric" or self.rawTypes[i].strip() == "id"): # gets all columns with numeric data or cluster data
				tempCol = []
				for j in self.rawData:
					tempCol.append(j[i])
				tempNumArray.append(tempCol)
				self.dataHeaders.append(self.rawHeaders[i])
				self.headerToMatrix[self.rawHeaders[i]] = k
				k+=1
		for i in range(len(tempNumArray)):
			for j in range(len(tempNumArray[i])):
				if (tempNumArray[i][j] == ""): #checks for empty data, assigns value -9999
					tempNumArray[i][j] = -9999
				if ((str)(tempNumArray[i][j]).strip() == "M"): # specifically for my weather data set
					print i, j, "M"
				if ((str)(tempNumArray[i][j]).strip() == "T"):
					print i, j, "T"
				else:
					tempNumArray[i][j] = (float)(tempNumArray[i][j])
		self.matrixData = np.matrix(tempNumArray).T;
	
	def getMatrix(self, cols = None):
		if cols == None:
			return self.matrixData
		else:
			return self.matrixData[:,cols]
			
	def setMatrix(self, matrix):
		self.matrixData = matrix
	
	# returns the headers of all of the columns from the input file, in order
	def getRawHeaders(self):
		return self.rawHeaders;
	
	# returns all of the types of the columns from the input file, in order
	def getRawTypes(self):
		return self.rawTypes;
	
	# returns the number of columns in the input file
	def getRawNumCols(self):
		return len(self.rawHeaders);
	
	# returns the number of rows in the input file
	def getRawNumRows(self):
		return len(self.rawData);
	
	# given an integer index, returns the row specified by 
	# that index from the input file.
	def getRawRow(self,index):
		return self.rawData[index];
		
	# given an integer index and a string header,
	# returns the value specified by those from the input file
	def getRawValue(self,index,header):
		return self.rawData[(index)][self.rawHeaders.index(header)];
	
	# returns all of the headers that correspond to numeric columns (i.e., all
	# of the headers of the Matrix)
	def getHeaders(self):
		return self.dataHeaders;
		
	# returns the number of numeric columns in the input file (i.e., the number 
	# of columns in the Matrix
	def getNumColumns(self):
		return len(self.getHeaders());
		
	# returns the number of rows in the matrix
	def getNumRows(self):
		return (self.matrixData.shape[0])
	
	# given an integer index, returns that row from the Matrix
	def getRow(self, index):
		return self.matrixData[index];
	
	# given an integer index, returns that column from the Matrix
	def getCol(self, index):
		return self.matrixData[:,index];
		
	# given an integer index and a string header,
	# returns the value specified by those from the Matrix
	def getValue(self, index, header):
		return (self.matrixData[index][self.headerToMatrix[header]].tolist())[0][0]
	
	# headers is a list of strings, rows is a list of row numbers
	# takes a list of headers and rows and returns the data associated with those
	# in a numpy matrix
	def getData(self, headers, rows = None):
		if(rows == None):
			rows = range(self.getNumRows())
# 		print "getData matrixData: ", self.matrixData
# 		print "getData rows: ", rows
# 		print "getData headerToMatrix: ", self.headerToMatrix
# 		print "getData headers: ", headers
		tempMatrix = np.matrix(self.matrixData[rows[0],self.headerToMatrix[headers[0]]])
		for i in range(len(rows)-1):
			tempMatrix = np.vstack([tempMatrix,
								(self.matrixData[rows[i+1],self.headerToMatrix[headers[0]]])])
		for i in range(len(headers)-1):
			tempCol = np.matrix([self.matrixData[rows[0],self.headerToMatrix[headers[i+1]]]])
			for j in range(len(rows)-1):
				tempCol = np.vstack([tempCol,
									self.matrixData[rows[j+1],self.headerToMatrix[headers[i+1]]]])	
			tempMatrix = np.hstack([tempMatrix, tempCol])
		return tempMatrix
	
	# converts specified string columns (specified with the list headers) in the input
	# data to numeric. string columns must be ENUM types, and that is checked for 
	def convertEnumToNumeric(self,headers):
		tempDic = {}
		count = 0
		for i in range(len(self.rawHeaders)):
			for j in headers:
				if(self.rawHeaders[i] == j) and (self.rawTypes[i] == "enum"):
					for k in range(self.getRawNumRows()):
						if (tempDic.keys().count(self.rawData[k][i]) == 0):
							tempDic[self.rawData[k][i]] = count
							count+=1
					for k in range(self.getRawNumRows()):
						self.rawData[k][i] = (str)(tempDic[self.rawData[k][i]])
					self.enumToNumberByCol[j] = tempDic
					tempDic = {}
					
	# converts a column of dates to seconds from the epoch
	# only (currently) works with NOAA standard date data
	def convertDateToStandard(self,headers):
		for i in range(len(self.rawHeaders)):
			for j in headers:
				if(self.rawHeaders[i] == j) and (self.rawTypes[i] == "date"):
					for k in range(self.getRawNumRows()):
						t = [(int)(self.rawData[k][i][0:4])] #add year
						t.append((int)(self.rawData[k][i][5:6])) #add month
						t.append((int)(self.rawData[k][i][7:8])) # add day
						t.extend([0,0,0,0,1,0]) #adding all the stuff we don't have as 0s
						self.rawData[k][i] = (str)(time.mktime(t))
	
	# allows the user to add a column of data to the raw data and the matrix
	# column MUST be properly formatted with a header, type, and the right # of points
	def addColumn(self, column):
		self.rawHeaders.append(column[0])
		self.rawTypes.append(column[1])
		row = 2
		for i in self.rawData:
			i.append(column[row])
			row+=1
		self.makeMatrix()
		
	def addColToMatrix(self, columns, headers):
		self.matrixData = np.hstack([self.matrixData, columns])
		self.dataHeaders+=headers
		i=0
		for header in headers:
			self.headerToMatrix[header] = self.getNumColumns() + i - 1
			i+=1
		return self.matrixData
	
	# returns a string that represents the raw data from the input file
	def toString(self):
		maxColSizes = []
		printString = "|"
		for i in range(0,self.getRawNumCols()):
			tempMax = 0
			tempMax = len(self.rawHeaders[i])
			if (len(self.rawTypes[i]) > tempMax):
				tempMax = len(self.rawTypes[i])
			for j in range(0,self.getRawNumRows()):
				if(len(self.rawData[j][i]) > tempMax):
					tempMax = len(self.rawData[j][i])
			maxColSizes.append(tempMax)
		for i in range(0,self.getRawNumRows()+2):
			for j in range(0,self.getRawNumCols()):
				if(i==0):
					tempHeader = self.rawHeaders[j]
					while(len(tempHeader) < maxColSizes[j]):
						tempHeader+=" ";
					printString+=tempHeader
				elif(i==1):
					tempType = self.rawTypes[j]
					while(len(tempType) < maxColSizes[j]):
						tempType+=" ";
					printString+=tempType
				else:
					tempData = self.rawData[i-2][j]
					while(len(tempData) < maxColSizes[j]):
						tempData+=" ";
					printString+=tempData
				printString+="|";
			printString+="\n+"
			for k in range(0, len(maxColSizes)):
				for l in range(0, maxColSizes[k]):
					printString+="-"
				printString+="+"
			printString+="\n|"
		printString = printString[:-1]
		return printString;
	
	def matrixToString(self, headers=None):
		if headers == None:
			headers = self.getHeaders()
		printString = ""
		data = self.getData(headers)
		for i in range(0,data.shape[0]+2):
			for j in range(data.shape[1]):
				if(i==0):
					printString+=headers[j]
				elif(i==1):
					tempType = "numeric"
					if headers[j] == "cluster ids":
						tempType = "id"
					printString+=tempType
				else:
					if headers[j] == "cluster ids":
						printString+=str(int(data[i-2,j]))
					else:
						printString+=str(data[i-2,j])
				printString+=","
			printString+="\n"
# 		printString = printString[:-1]
		return printString;
	
	# like toString, but in a much simpler format, so that it takes up less space.
	def toStringSimple(self):
		maxColSizes = []
		printString = ""
		for i in range(0,self.getRawNumCols()):
			tempMax = 0
			tempMax = len(self.rawHeaders[i])
			if (len(self.rawTypes[i]) > tempMax):
				tempMax = len(self.rawTypes[i])
			for j in range(0,self.getRawNumRows()):
				if(len(self.rawData[j][i]) > tempMax):
					tempMax = len(self.rawData[j][i])
			maxColSizes.append(tempMax)
		for i in range(0,self.getRawNumRows()+2):
			for j in range(0,self.getRawNumCols()):
				if(i==0):
					tempHeader = self.rawHeaders[j]
					while(len(tempHeader) < maxColSizes[j]):
						tempHeader+=" ";
					printString+=tempHeader
				elif(i==1):
					tempType = self.rawTypes[j]
					while(len(tempType) < maxColSizes[j]):
						tempType+=" ";
					printString+=tempType
				else:
					tempData = self.rawData[i-2][j]
					while(len(tempData) < maxColSizes[j]):
						tempData+=" ";
					printString+=tempData
				printString+="|";
			printString+="\n"
		return printString;
	
	
	def write(self, filename, headers=None):
		file = open(filename, "w")
		file.write(self.matrixToString(headers))
		

class PCAData(Data):
	
	def __init__(self, dataHeaders, projData, eigenValues, eigenVectors, dataMeans):
		Data.__init__(self, None)
		# make headerToMatrix dictionary
		self.makeHeaderToMatrix(dataHeaders)
		self.rawData = projData.tolist()
		for i in range(len(dataHeaders)):
			self.rawHeaders.append("PCA%02d"%(i))
			self.rawTypes.append("numeric")
		self.dataHeaders = dataHeaders
		self.dataHeads = dataHeaders
		self.matrixData = projData.T
		self.eigVals = eigenValues
		self.eigVecs = eigenVectors
		self.meanVals = dataMeans
	
	def makeHeaderToMatrix(self,headers):
		colNum = 0
		for header in headers:
			self.headerToMatrix[header] = colNum
			colNum+=1
	def getEigenvalues(self):
		return self.eigVals
	def getEigenvectors(self):
		return self.eigVecs
	def getDataMeans(self):
		return self.meanVals
	def getDataHeaders(self):
		return self.dataHeads
		
# class CData(Data):
# 	
# 	def __init__(self,filename):
# 		Data.__init__(self,filename)

	
if __name__ == "__main__":
	data = Data("clusterdata.csv")
	data.addColToMatrix(data.getData(["thing1"]),["thing3"])
	data.write("test.txt")
