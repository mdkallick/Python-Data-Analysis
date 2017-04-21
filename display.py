# Skeleton Tk interface example
# Written by Bruce Maxwell
# Modified by Stephanie Taylor
# Modified by Mathias Kallick to add functionality
#
# CS 251
# Spring 2015

import Tkinter as tk
import tkFont as tkf
import numpy as np
import math, os, random, copy, data, tkFileDialog
import view, analysis, dialog
import scipy.stats
		
# create a class to build and manage the display
class DisplayApp:

	def __init__(self, width, height):

		# create a tk object, which is the root window
		self.root = tk.Tk()
		
		# setup all of the variables not used for the actual root window
		self.setupVariables(width, height)

		# set up the geometry for the window
		self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

		# set the title of the window
		self.root.title("Random Points Plotter")

		# set the maximum size of the window for resizing
		self.root.maxsize( 1600, 900 )

		# setup the menus
		self.buildMenus()

		# build the controls
		self.buildControls()

		# build the Canvas
		self.buildCanvas()
		
		# build the actual axis information
		self.buildAxes()

		# bring the window to the front
		self.root.lift()

		# - do idle events here to get actual canvas size
		self.root.update_idletasks()

		# now we can ask the size of the canvas
		print self.canvas.winfo_geometry()

		# set up the key bindings
		self.setBindings()

		# set up the application state
		self.objects = [] # list of data objects that will be drawn in the canvas
		self.data = None # will hold the raw data someday.
		self.baseClick = None # used to keep track of mouse movement
	
	# sets up all of the none-root based variables.
	# mostly just cleans up my __init__ method.
	def setupVariables(self, width, height):
		# setup a new View object
		self.viewObj = view.View()
		self.viewObj.setVariables(np.matrix([0.,.5,1.]), np.matrix([0,0,-1]),
									np.matrix([0,1,0]), np.matrix([-1,0,0]),
									[1,1,1], [400,400], [20,20])
		
		# setup a matrix to hold the axis endpoints, and a list to hold the axes
		self.axes = np.matrix( [[0,0,0,1],[1,0,0,1],
								[0,0,0,1],[0,1,0,1],
								[0,0,0,1],[0,0,1,1]] ).T
		self.axisLines = [(self.axes[0,0],self.axes[1,0],self.axes[0,1],self.axes[1,1]),
						  (self.axes[0,2],self.axes[1,2],self.axes[0,3],self.axes[1,3]),
						  (self.axes[0,4],self.axes[1,4],self.axes[0,5],self.axes[1,5])]
	
	
		# setup variables to hold the type of random distribution for x and y
		self.randTypeX = "Gaussian"
		self.randTypeY = "Gaussian"
		
		# setup variable to hold the shape of the data points
		self.shape = 0
		
		# setup variable to hold axis labels
		self.axisHeaders = ["","",""]
		
		# setup variable to hold the current mouse position, and the text.
		self.mousePosition = (0,0)
		self.mousePosText = "(0,0)"
		
		# setup radius of data points and distance mouse moved for various methods
		# and for changing radius or points
		self.rad = 1
		self.clickPosition = 0;
		self.mouse2Distance = 0;
		self.canvasCoords = []
		self.mousePos = [0,0]
		self.mouse3Pos = 0
		
		# setup a global variable for the current x and y rotation
		self.curRotation = [0,0]
		
		# setup variables for the user-input parameters of rotation,translation,
		# and scale speeds
		self.rotSpeed = 1
		self.tranSpeed = 1
		self.scaleSpeed = 1
		
		# set a variable for linear regression objects and the 4th and 5th axes
		self.linReg = []
		self.linRegEndPoints = None
		self.linRegActive = False
		self.plotActive = False
		self.pointSizes = None
		self.colorValues = None
		
		# make a list for pca's
		self.pcaAnalyses = []
		
		# set a variable for the color of input points
 		self.color = "black"
				
		# width and height of the window
		self.initDx = width
		self.initDy = height
	
	def buildMenus(self):
		
		# create a new menu
		menu = tk.Menu(self.root)

		# set the root menu to our new menu
		self.root.config(menu = menu)

		# create a variable to hold the individual menus
		menulist = []

		# create a file menu
		filemenu = tk.Menu( menu )
		menu.add_cascade( label = "File", menu = filemenu )
		menulist.append(filemenu)

		# create another menu for kicks
		cmdmenu = tk.Menu( menu )
		menu.add_cascade( label = "Command", menu = cmdmenu )
		menulist.append(cmdmenu)

		# menu text for the elements
		# the first sublist is the set of items for the file menu
		# the second sublist is the set of items for the option menu
		menutext = [ [ 'Open Data \xE2\x8C\x98-O', 'Clear Data \xE2\x8C\x98-N', 'Quit	\xE2\x8C\x98-Q' ],
					 [ 'Perform Linear Regression', '-', '-' ] ]

		# menu callback functions (note that some are left blank,
		# so that you can add functions there if you want).
		# the first sublist is the set of callback functions for the file menu
		# the second sublist is the set of callback functions for the option menu
		menucmd = [ [self.handleOpen, self.clearData, self.handleQuit],
					[self.handleLinearRegression, None, None] ]
		
		# build the menu elements and callbacks
		for i in range( len( menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j] != '-':
					menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					menulist[i].add_separator()

	# create the canvas object
	def buildCanvas(self):
		self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
		self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
		return

	# build a frame and put controls in it
	def buildControls(self):

		### Control ###
		# make a control frame on the right
		rightcntlframe = tk.Frame(self.root)
		rightcntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

		# make a separator frame
		sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)

		# use a label to set the size of the right panel
		label = tk.Label( rightcntlframe, text="Control Panel", width=20 )
		label.pack( side=tk.TOP, pady=10 )
		
		# make a button in the right frame that resets the axes.
		resetAxisButton = tk.Button( rightcntlframe, text = "Reset Axes",
									command=self.resetAxes )
		resetAxisButton.pack(side=tk.TOP)
		
		# define two text input boxes where the user can input the desired xy rotation
		self.enterXAngle = tk.Entry(rightcntlframe)
		self.enterXAngle.insert(0, "0")
		self.enterYAngle = tk.Entry(rightcntlframe)
		self.enterYAngle.insert(0, "0")
		tk.Label(rightcntlframe, text = "Enter X and Y rotation:").pack(pady=5)
		self.enterXAngle.pack(pady=0)
		self.enterYAngle.pack(pady=0)
		
		# make a button in the right frame that rotates the axes to the angles specified
		# in the text boxes above.
		self.rotateAxesButton = tk.Button( rightcntlframe, text = "Rotate Axes",
									command=self.rotateAxes )
		self.rotateAxesButton.pack(side=tk.TOP)
		
		# make a button that plots the data from the input file
		self.plotDataButton = tk.Button( rightcntlframe, text = "Plot Data from Input File",
									command=self.plotData )
		self.plotDataButton.pack(side=tk.TOP)
		
		# create a set of controls that deal with PCA stuff
		self.PCAAnalysisButton = tk.Button( rightcntlframe, text = "Perform PCA",
									command=self.pickPCA )
		self.PCAAnalysisButton.pack(side=tk.TOP)
		self.PCALabel = tk.Label( rightcntlframe, 
								text = "Principal Component Analyses").pack(side=tk.TOP)
		self.PCAListBox = tk.Listbox(rightcntlframe, selectmode = tk.SINGLE, exportselection=0)
		self.PCAListBox.pack(side=tk.TOP)
		self.PCAGraphButton = tk.Button( rightcntlframe, text = "plot selected PCA",
												command=self.graphPCA )
		self.PCAGraphButton.pack(side=tk.TOP)
		self.PCAEigenButton = tk.Button( rightcntlframe, 
					text = "Show Eigenvalues and EigenVectors", command=self.showEigen)
		self.PCAEigenButton.pack(side=tk.TOP)
		self.PCASelectColumnsToPlot = tk.Button(rightcntlframe, 
								text = "choose columns to plot from the selected PCA",
								command=self.choosePCAPlottedCols)
		self.PCASelectColumnsToPlot.pack(side=tk.TOP)
		
		self.openClusteringButton = tk.Button( rightcntlframe,	
												text = "Choose Clustering Headers",
												command=self.openClustering )
		self.openClusteringButton.pack(side=tk.TOP)
		self.plotClustersButton = tk.Button( rightcntlframe, text="Plot Clusters",
												command=self.plotClusters )
		self.plotClustersButton.pack(side=tk.TOP)
					
		# define three text input boxes where the user can input the desired 
		# speeds for rotation, translation, and scaling
		self.enterRotSpeed = tk.Entry(rightcntlframe)
		self.enterRotSpeed.insert(0, "1")
		self.enterTranSpeed = tk.Entry(rightcntlframe)
		self.enterTranSpeed.insert(0, "1")
		self.enterScaleSpeed = tk.Entry(rightcntlframe)
		self.enterScaleSpeed.insert(0, "1")
		tk.Label(rightcntlframe, text = "Enter rotation speed multiplier:").pack(pady=5)
		self.enterRotSpeed.pack(pady=0)
		tk.Label(rightcntlframe, text = "Enter translation speed multiplier:").pack(pady=5)
		self.enterTranSpeed.pack(pady=0)
		tk.Label(rightcntlframe, text = "Enter scale speed multiplier:").pack(pady=5)
		self.enterScaleSpeed.pack(pady=0)
		setMultipliers = tk.Button( rightcntlframe, text = "Set specified multipliers",
									command=self.changeMultipliers )
		setMultipliers.pack(side=tk.TOP)
		
		return

	# combines all of my update functions for simplicity
	def updateAll(self):
		self.updateAxes()
		try:
			self.updatePoints()
		except:
			pass
 		try:
			self.updateFits()
		except:
			pass

	# builds a vtm from the current viewObj and creates axes based on it
	def buildAxes(self):
		vtm = self.viewObj.build()
		tempAxes = vtm * np.copy(self.axes)
		self.axisLineIDs = []
		self.axisLabels = []
		self.axisLines = [(tempAxes[0,0],tempAxes[1,0],tempAxes[0,1],tempAxes[1,1]),
						  (tempAxes[0,2],tempAxes[1,2],tempAxes[0,3],tempAxes[1,3]),
						  (tempAxes[0,4],tempAxes[1,4],tempAxes[0,5],tempAxes[1,5])]
		self.labelPoints = [(tempAxes[0,1],tempAxes[1,1]),
							(tempAxes[0,3],tempAxes[1,3]),
							(tempAxes[0,5],tempAxes[1,5]),
							'   X'+self.axisHeaders[0],
							'   Y'+self.axisHeaders[1],
							'   Z'+self.axisHeaders[2]]
# 		print "axisLines before: \n", self.axisLines
		for i in self.axisLines:
			pt = self.canvas.create_line(i)
			self.axisLineIDs.append(pt)
		for i in range(3):
			pt = self.canvas.create_text(self.labelPoints[i], text=self.labelPoints[i+3])
			self.axisLabels.append(pt)
		self.enterXAngle.delete(0, tk.END)
		self.enterYAngle.delete(0, tk.END)
		self.enterXAngle.insert(0, "%.3f" % (self.curRotation[0] * (180/math.pi)))
		self.enterYAngle.insert(0, "%.3f" % (self.curRotation[1] * (180/math.pi)))
	
	# updates the position of the axes based on new rotation, translation, and scaling
	def updateAxes(self):
		vtm = self.viewObj.build()
# 		print "vtm axes: ", vtm
		tempAxes = vtm * np.copy(self.axes)
		self.axisLines = [(tempAxes[0,0],tempAxes[1,0],tempAxes[0,1],tempAxes[1,1]),
						  (tempAxes[0,2],tempAxes[1,2],tempAxes[0,3],tempAxes[1,3]),
						  (tempAxes[0,4],tempAxes[1,4],tempAxes[0,5],tempAxes[1,5])]
		self.labelPoints = [(tempAxes[0,1],tempAxes[1,1]),
							(tempAxes[0,3],tempAxes[1,3]),
							(tempAxes[0,5],tempAxes[1,5]),
							'   X'+self.axisHeaders[0],
							'   Y'+self.axisHeaders[1],
							'   Z'+self.axisHeaders[2]]
# 		print "axisLines after: \n", self.axisLines
		for i in range(len(self.axisLineIDs)):
			self.canvas.coords(self.axisLineIDs[i], self.axisLines[i])
		for i in range(3):
			pt = self.canvas.create_text(self.labelPoints[i], text=self.labelPoints[i+3])
			self.canvas.delete(self.axisLabels[i])
			self.axisLabels[i] = pt
		self.enterXAngle.delete(0, tk.END)
		self.enterYAngle.delete(0, tk.END)
		self.enterXAngle.insert(0, "%.3f" % (self.curRotation[0] * (180/math.pi)))
		self.enterYAngle.insert(0, "%.3f" % (self.curRotation[1] * (180/math.pi)))

	def setBindings(self):
		# bind mouse motions to the canvas
		self.canvas.bind( '<Control-Button-1>', self.handleMouseButton2 )
		self.canvas.bind( '<Button-2>', self.handleMouseButton2 )
		self.canvas.bind( '<Button-3>', self.handleMouseButton3 )
		self.canvas.bind( '<B3-Motion>', self.handleMouseButton3Motion )
		self.canvas.bind( '<B2-Motion>', self.handleMouseButton2Motion )
		self.canvas.bind( '<Control-B1-Motion>', self.handleMouseButton2Motion )
		self.canvas.bind( '<Motion>', self.handleMouseMotion )
		self.canvas.bind( '<Button-1>', self.handleButton1 )
		self.canvas.bind( '<B1-Motion>', self.handleButton1Motion )
		

		# bind command sequences to the root window
		self.root.bind( '<Command-q>', self.handleQuit )
		self.root.bind( '<Command-n>', self.clearData )
		self.root.bind( '<Command-o>', self.handleOpen )
	
	
	def handleQuit(self, event=None):
		print 'Terminating'
		self.root.destroy()
	
	# calls when mouse button 1 are hit, and saves the position that happened in
	def handleButton1(self, event):
		self.mousePos = (event.x, event.y)
	
	# calls when mouse button 1 are clicked and dragged,
	# and moves the axes based on mouse motion
	def handleButton1Motion(self, event):
		diff = [self.mousePos[0] - event.x, self.mousePos[1] - event.y]
		delta0 = (float(diff[0])/self.root.winfo_width())*self.viewObj.extent[0]
		delta1 = (float(diff[1])/self.root.winfo_height())*self.viewObj.extent[1]
 		delta0,delta1 = (self.tranSpeed * delta0*-1), (self.tranSpeed * delta1*-1)
		updateVector = ((delta0*self.viewObj.u) + (delta1*self.viewObj.vup))
		self.viewObj.vrp = self.viewObj.vrp + updateVector
		self.updateAll()
 		self.mousePos = (event.x, event.y)

	# this method shows what position a point is at when the mouse hovers over it
	def handleMouseMotion(self, event):
		curMouseCoords = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
		for pt in self.objects:
			if (pt in curMouseCoords):
				self.mousePosition = ((int)(self.canvas.coords(pt)[0]),
											(int)(self.canvas.coords(pt)[1]))
		self.canvas.delete(self.mousePosText)
		mousePositionString = "Mouse is Hovering Over a Point With Coords: "
		mousePositionString += (str)(self.mousePosition)
		self.mousePosText = self.canvas.create_text(200,575,text=mousePositionString)
	
	def handleMouseButton2(self, event):
		self.mousePos2 = (event.x, event.y)
		self.mB2View = self.viewObj.clone()
		self.clickPosition = event.y
			
	# This is called if the second button of a real mouse has been pressed
	# and the mouse is moving. Or if the control key is held down while
	# a person moves their finger on the track pad.
	def handleMouseButton2Motion(self, event):
		delta0 = self.rotSpeed * (-((self.mousePos2[0] - event.x)/200.)*math.pi)
		delta1 = self.rotSpeed * (-((self.mousePos2[1] - event.y)/200.)*math.pi)
		svf = self.mB2View.clone()
		self.curRotation[0] += delta0
		self.curRotation[1] += delta1
		for i in range(2):
			if (self.curRotation[i] > 2 * math.pi):
				self.curRotation[i] -= (2*math.pi)
			elif (self.curRotation[i] < 0):
				self.curRotation[i] += (2*math.pi)
		svf.rotateVRC(delta0, delta1)
		self.viewObj = svf
		self.updateAll()
				
	# calls when the third mouse button is pressed, and stores a copy of the current
	# extent so that the axes can be scaled linearly
	def handleMouseButton3(self, event):
		print 'handling button 3:', (event.x, event.y)
		self.mouse3Pos = float(event.y)
		self.tempExtent = self.viewObj.extent[:]

	# calls when the third mouse button is held and dragged, and scales the axes based on
	# how far the mouse has been dragged from the start position
	def handleMouseButton3Motion(self, event):
		temp = self.tempExtent[:]
		diff = self.scaleSpeed *((float(self.mouse3Pos - event.y)/(self.root.winfo_height())))+1
		if (diff > 3.0):
			diff = 3.0
		elif (diff < .1):
			diff = .1
		for i in range(len(temp)):
			self.viewObj.extent[i] = temp[i]*diff
		self.updateAll()
	
	# opens a dialog box that allows the user to choose an independent and a 
	# dependent variable for linear regression
	def handleLinearRegression( self, event=None ):
		try:
			self.dataObj.makeMatrix()
		except:
			print "No file opened yet"
			return
		linRegBox = dialog.LinearRegressionDialog(self.root, 
									self.dataObj.getHeaders(), title="Linear Regression")
		if (linRegBox.okHit == False):
			return
		self.indepData = linRegBox.independent
		self.depData = linRegBox.dependent
# 		print "indepData: ", self.indepData, " depData: ", self.depData
		for pt in self.objects:
			self.canvas.delete(pt)
		self.objects = []
		for line in self.linReg:
			self.canvas.delete(line)
		self.linReg = []
		self.linRegEndPoints = []
		self.buildLinearRegression()
		self.resetAxes()
		self.updateAll()
	
	# creates a canvas line object and does linear regression on the columns selected
	# by the user
	def buildLinearRegression(self):
		self.linRegActive = True
		self.plotActive = False
		self.Xcol = self.dataObj.getCol(self.dataObj.headerToMatrix[self.indepData])
		self.Ycol = self.dataObj.getCol(self.dataObj.headerToMatrix[self.depData])
		tempShape = self.Xcol.shape
# 		print "Xcol: ", self.Xcol, " Ycol: ", self.Ycol
 		self.linRegMatrix = np.matrix( [self.Xcol.T.tolist()[0],
										self.Ycol.T.tolist()[0],
										np.zeros(tempShape).T.tolist()[0],
										np.ones(tempShape).T.tolist()[0]] )
# 		print "linRegMatrix: \n", self.linRegMatrix
		self.linRegMatrix = self.normalizeMatrix(self.linRegMatrix, 4)
		vtm = self.viewObj.build()
# 		print "vtm: \n", vtm
		tmpMat = vtm * self.linRegMatrix
		for i in self.objects:
			self.canvas.delete(i)
		self.objects = []
		self.pointMatrix = self.linRegMatrix
		self.pointSizes = None
		self.colorValues = None
		self.plotPoints(tmpMat.tolist())
# 		print "linRegMatrix: \n", self.linRegMatrix
# 		print "tmpMat: \n", tmpMat
		slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(np.hstack( (self.Xcol,self.Ycol) ) )
# 		print slope, intercept, r_value, p_value, std_err
		analysisObj = analysis.Analysis()
		print "indep: ", self.indepData, "dep: ", self.depData
		ranges = analysisObj.dataRange((self.indepData, self.depData), self.dataObj)
		print "ranges: ", ranges
		xmin, xmax, ymin, ymax = ranges[0][1], ranges[0][0], ranges[1][1], ranges[1][0]
		self.linRegEndPoints = []
		print "slope: ", slope, "intercept: ", intercept, "ymin, ymax: ", ymin, ymax
		self.linRegEndPoints.append([1.,((xmax * slope + intercept) - ymin)/(ymax - ymin),0.,1.])
		self.linRegEndPoints.append([0.,((xmin * slope + intercept) - ymin)/(ymax - ymin),0.,1.])
		print "linRegEndPoints: ", self.linRegEndPoints
		self.linRegEndPoints = np.matrix(self.linRegEndPoints).T
		tmpEndpoints = vtm * self.linRegEndPoints
		print "tmpEndpoints: ", tmpEndpoints
# 		print "linRegEndpoints: ", self.linRegEndPoints
# 		print "tmpEndpoints: ", tmpEndpoints
		line = self.canvas.create_line((tmpEndpoints[0,0],tmpEndpoints[1,0],
										tmpEndpoints[0,1],tmpEndpoints[1,1]),
										fill="red")
		self.linReg.append(line)
# 		print "linreg: ", self.linReg
		
		linRegCof=("slope: %2f intercept: %2f \nr: %2f r^2: %2f p: %2f, std_err: %2f" %
						(slope,intercept,r_value,(r_value**2),p_value,std_err))
		txt=self.canvas.create_text((tmpEndpoints[0,0],tmpEndpoints[1,0]),text=linRegCof,
										fill="red")
		self.linReg.append(txt)
		self.axisHeaders = [":"+self.indepData,":"+self.depData,""] #x,y,z
								
	
	# updates the position of the linear fit line on the screen so that 
	# it rotates with the data points and the axes
	def updateFits(self):
		vtm = self.viewObj.build()
		try:
			tmpEndpoints = vtm * self.linRegEndPoints
		except:
			return
		self.canvas.coords(self.linReg[0],tmpEndpoints[0,0],tmpEndpoints[1,0],
										  tmpEndpoints[0,1],tmpEndpoints[1,1])
		self.canvas.coords(self.linReg[1],tmpEndpoints[0,0],tmpEndpoints[1,0])
	
	# gets rid of all of the data points
	def clearData( self, event=None ):
		for pt in self.objects:
			self.canvas.delete(pt)
		self.objects = []
	
	# rotates the axes based on the numbers displayed in the two Entry boxes in the
	# right control frame
	def rotateAxes(self, event=None):
		self.inputXRotation = ((float(self.enterXAngle.get()))/180) * math.pi
		self.inputYRotation = ((float(self.enterYAngle.get()))/180) * math.pi
		delta0 = self.inputXRotation - self.curRotation[0]
		delta1 = self.inputYRotation - self.curRotation[1]
		self.curRotation = [self.inputXRotation, self.inputYRotation]
		svf = self.viewObj.clone()
		svf.rotateVRC(delta0, delta1)
		self.viewObj = svf
		self.updateAll()
	
	# resets the axes to rotation (0,0)
	def resetAxes(self, event=None):
		for line in self.axisLineIDs:
			self.canvas.delete(line)
		for label in self.axisLabels:
			self.canvas.delete(label)
		self.viewObj.reset()
		self.curRotation = [0.,0.]
		self.buildAxes()
		try:
			if(self.plotActive):
				self.buildPoints(self.plottedCols)
		except:
			print "no columns for plotting selected"
		try:
			if(self.linRegActive):
				for pt in self.objects:
					self.canvas.delete(pt)
				self.objects = []
				for line in self.linReg:
					self.canvas.delete(line)
				self.linReg = []
				self.linRegEndPoints = []
				self.buildLinearRegression()
		except:
			print "linear regression not currently in place"
		self.updateAll()
	
	# sets the multipliers for the speed of scaling, rotation and translation
	def changeMultipliers(self):
		self.rotSpeed = float(self.enterRotSpeed.get())
		self.tranSpeed = float(self.enterTranSpeed.get())
		self.scaleSpeed = float(self.enterScaleSpeed.get())
	
	# plots the data from handleOpen's file selection
	def plotData(self, event=None):
		try:
			self.dataObj.makeMatrix()
		except:
			print "No data file has been selected yet. Please enter a data file"
			return
		self.plottedCols = self.handleChooseAxes()
# 		print "plottedCols: ", self.plottedCols
		if (len(self.plottedCols) == 3):
			self.axisHeaders = [":"+self.plottedCols[0],":"+self.plottedCols[1],":"+self.plottedCols[2]]
		else:
			self.axisHeaders = [":"+self.plottedCols[0],":"+self.plottedCols[1],""]
		self.buildPoints(self.plottedCols)
		self.updateAll()
	
	# normalize axis data for plotting. Totally not almost the same as
	# normalizeColumnsSeparately in my analysis class
	def normalizeMatrix(self, data, numCols):
		for i in range(numCols):
			tempMin = data.T[:,i].min()
# 			print "currentCol: ", data.T[:,i]
# 			print "tempMin: ", tempMin
			tempMax = data.T[:,i].max()
# 			print "tempMax: ", tempMax
			if(tempMin == tempMax == 0):
				print "column ", i, " has the same min and max, and it is zero"
				print "column ", i, " not normalized"
				pass
			elif(tempMin == tempMax):
# 				print "column ", data.T[:,i], " has the same min and max"
				data.T[:,i] = data.T[:,i] / tempMax # brings everything to 1
			else:
				data.T[:,i] = data.T[:,i] - tempMin
				data.T[:,i] = data.T[:,i] / (tempMax - tempMin)
#  		print "normalized data: ", data.T
		return data
	
	# plots the data columns specified from handleChooseAxes through plotData
	def buildPoints(self, cols):
		self.plotActive = True
		self.linRegActive = False
		vtm = self.viewObj.build()
		try:
			i = np.array(self.order)
			self.pointMatrix = self.dataObj.getMatrix().T[i]
		except:
			# not plotting from handleChooseAxes
			self.pointMatrix = self.dataObj.getMatrix(cols).T
		while (len(cols) < 3):
			self.pointMatrix = np.vstack((self.pointMatrix,
												np.ones((1,self.pointMatrix.shape[1]))))
			cols.append(0)
		self.pointMatrix = (np.vstack((self.pointMatrix,
										np.ones((1,self.pointMatrix.shape[1])))))
		self.pointMatrix = self.normalizeMatrix(self.pointMatrix, 4)
# 		print "pointMatrix: ", self.pointMatrix
		tmpthing = vtm * self.pointMatrix
# 		print "tmpthing: ", tmpthing
		dataPoints = tmpthing.tolist()
		for i in self.objects:
			self.canvas.delete(i)
		self.objects = []
		for i in self.linReg:
			self.canvas.delete(i)
		self.linReg = []
		self.plotPoints(dataPoints)

	# actually plots the points after the pointMatrix has been built.
	# exists mostly for cleaner code integration with the regression functions
	def plotPoints(self, dataPoints):
		if self.pointSizes is not None:
			pass
		else:
			self.pointSizes = np.ones((len(dataPoints[0]),1))
			self.pointSizes = (self.normalizeMatrix(self.pointSizes.T, 1))*2
		if self.colorValues is not None:
			pass
		else:
			self.colorValues = []
			for i in range(len(dataPoints[0])):
				self.colorValues.append("#%02x%02x%02x" % (0.00,0.00,0.00))
		for i in range(len(dataPoints[0])):
				pt = self.canvas.create_oval(dataPoints[0][i]+((self.pointSizes[0,i]+2)*self.rad),
											 dataPoints[1][i]+((self.pointSizes[0,i]+2)*self.rad), 
											 dataPoints[0][i]-((self.pointSizes[0,i]+2)*self.rad),
											 dataPoints[1][i]-((self.pointSizes[0,i]+2)*self.rad), 
											 fill=self.colorValues[i], outline='' )
				self.objects.append(pt)
# 		print "example point: ", self.canvas.coords(self.objects[0])
	
	# updates the points with the new rotations and such
	def updatePoints(self):
		vtm = self.viewObj.build()
		tempPointMat = vtm * self.pointMatrix
		dataPoints = tempPointMat.tolist()
		i = 0
		for pt in self.objects:
			self.canvas.coords( pt,
								dataPoints[0][i]+((self.pointSizes[0,i]+2)*self.rad),
								dataPoints[1][i]+((self.pointSizes[0,i]+2)*self.rad), 
								dataPoints[0][i]-((self.pointSizes[0,i]+2)*self.rad),
								dataPoints[1][i]-((self.pointSizes[0,i]+2)*self.rad))
			i+=1
		return 0;
			
	# opens a dialog box to choose columns of data to plot
	def handleChooseAxes(self, event=None):
		axes = []
		colSelectBox = dialog.colSelectBox(self.root,
											self.dataObj.getHeaders(), title="colSelect")
		col1 = colSelectBox.column1
		col2 = colSelectBox.column2	
		axes.append(self.dataObj.getHeaders()[col1[0]])
		axes.append(self.dataObj.getHeaders()[col2[0]])
		
		R,G,B = 1.,1.,1.
		
		if (colSelectBox.colorBase.get() == "Red"):
			R,G,B = 1.,0.,0.
		elif (colSelectBox.colorBase.get() == "Green"):
			R,G,B = 0.,1.,0.
		elif (colSelectBox.colorBase.get() == "Blue"):
			R,G,B = 0.,0.,1.
		elif (colSelectBox.colorBase.get() == "Gray"):
			R,G,B = 1.,1.,1.
		col3exist = False
		if (colSelectBox.column3 != ()):
			col3 = colSelectBox.column3
			axes.append(self.dataObj.getHeaders()[(col3[0]-1)])
			col3exist = True
		if (colSelectBox.sizeColumn != ()):
			self.pointSizes = self.dataObj.matrixData[:,colSelectBox.sizeColumn[0]]
			self.pointSizes = (self.normalizeMatrix(self.pointSizes.T, 1))*5
		else:
			self.pointSizes = np.ones(self.dataObj.matrixData[:,0].shape)
			self.pointSizes = (self.normalizeMatrix(self.pointSizes.T, 1))*5
		if (colSelectBox.colorColumn != ()):
			self.colorValues = self.dataObj.matrixData[:,colSelectBox.colorColumn[0]]
			self.colorValues = (self.normalizeMatrix(self.colorValues.T, 1))*255
			self.colorValues = self.colorValues.tolist()[0]
# 			print self.colorValues
			for i in range(len(self.colorValues)):
				self.colorValues[i] = "#%02x%02x%02x" % (self.colorValues[i]*R,
										self.colorValues[i]*G,self.colorValues[i]*B)
		else:
			self.colorValues = np.ones(self.dataObj.matrixData[:,0].shape)
			self.colorValues = (self.normalizeMatrix(self.colorValues.T, 1))*255
			self.colorValues = self.colorValues.tolist()[0]
			for i in range(len(self.colorValues)):
				self.colorValues[i] = "#%02x%02x%02x" % (self.colorValues[i]*R,
										self.colorValues[i]*G,self.colorValues[i]*B)
# 		if (colSelectBox.numColumn != ()):
# 			self.numValues = self.dataObj.matrixData[:,colSelectBox.numColumn[0]]
# 			self.numValues = (self.normalizeMatrix(self.numValues.T, 1))
# 		
		self.order = [self.dataObj.headerToMatrix[self.dataObj.getHeaders()[col1[0]]],
					  self.dataObj.headerToMatrix[self.dataObj.getHeaders()[col2[0]]]]
		if (col3exist):
			self.order.append(self.dataObj.headerToMatrix[self.dataObj.getHeaders()[col3[0]]])
# 		print self.order
		
		try:
			self.color = colSelectBox.selectedColor[1]
		except:
			print "color not assigned"
		
		try:
			self.rad = (float)(colSelectBox.selectedRad)
		except:
			print "size not assigned, or invalid input"

		return axes
	
	# opens a dialog box for the user to choose a file to get data from and perform
	# pca analysis on.
	def pickPCA(self, event=None):
		pcaSelectBox = dialog.pcaAnalysisBox(self.root, "PCAPICKER")
		for pca in pcaSelectBox.analysisLabels:
			self.PCAListBox.insert(tk.END, pca)
		self.pcaAnalyses = self.pcaAnalyses + pcaSelectBox.analyses
		
	def graphPCA(self, cols=None, event=None):
		plottedPCA = self.PCAListBox.curselection()[0]
		self.dataObj = self.pcaAnalyses[plottedPCA]
		if cols == None:
			if (len(self.dataObj.getDataHeaders()) < 3):
				cols = range(len(self.dataObj.getDataHeaders()))
			else:
				cols = range(3)
		self.buildPoints(cols)
		self.updateAll()
	
	def choosePCAPlottedCols(self, event=None):
		currPCA = self.PCAListBox.curselection()[0]
		okay = False
		while okay == False:
			chooseColsDiag = dialog.pickPCAColumnsBox(self.root,
												self.pcaAnalyses[currPCA].getDataHeaders(),
												"pick columns from the PCA to plot")
			cols = list(chooseColsDiag.cols)
			if (len(cols) > len(self.pcaAnalyses[currPCA].getDataHeaders())):
				print "You Selected Too Many Columns. Reselect with 5 or less."
				okay = False
			else:
				okay = True
			# assign Color values for the 4th dimension
			if (len(cols) > 3):
				colorDic = {}
				colors = ["black", "yellow","orange","red","red-purple","purple", 
							"blue-purple", "blue", "teal", "green", "yellow-green"]
				colorRGBs = [[0.,0.,0.], [1.,1.,0.],[1.,.5,0.],[1.,0.,0.],[.8,0.,.4],
								[.6,0.,.6],[.4,0.,.8],[0.,0.,1.],[0.,.8,.8],[0.,1.,0.],[.6,1.,.2]]
				for i in range(len(colors)):
					colorDic[colors[i]] = colorRGBs[i]
				RGB = colorDic[chooseColsDiag.color]
				R,G,B = RGB[0],RGB[1],RGB[2]
				self.colorValues = self.pcaAnalyses[currPCA].getMatrix()[:,3]
				self.colorValues = (self.normalizeMatrix(self.colorValues.T, 1))*255
				self.colorValues = self.colorValues.tolist()[0]
				for i in range(len(self.colorValues)):
					self.colorValues[i] = "#%02x%02x%02x" % (self.colorValues[i]*R,
											self.colorValues[i]*G,self.colorValues[i]*B)
				cols.pop(3)
				
			# assign size values for the 5th dimension
			if (len(cols) > 3):
				self.pointSizes = self.pcaAnalyses[currPCA].getMatrix()[:,4]
				self.pointSizes = (self.normalizeMatrix(self.pointSizes.T, 1))*5
				cols.pop(3)
				
		self.graphPCA(cols)
			
			
	def showEigen(self, event=None):
		currPCA = self.PCAListBox.curselection()[0]
		eigenDisplayBox = dialog.eigenDisplayBox(self.root,
								self.pcaAnalyses[currPCA].getEigenvectors(),
								self.pcaAnalyses[currPCA].getEigenvalues(),
								self.pcaAnalyses[currPCA].getDataHeaders(),
												"Eigenvectors and EigenValues")
	
	# opens a dialog box to let the user select columns of the data to perform clustering
	# analysis on. Also lets the user select the number of clusters and if they want a
	# continous color spectrum or discrete colors. Runs the clustering analysis and prints
	# the results with the columns used to a file.
	def openClustering(self, event=None):
		self.dataObj=copy.copy(self.permData)
		clusterPick = dialog.executeClusteringBox(self.root, self.dataObj.getHeaders(), "clustering")
		headers = []
		K = int(clusterPick.K)
		self.colorCheck = clusterPick.check
		self.clusterFile = "Clusters.csv"
		for i in clusterPick.cols:
			headers.append(self.dataObj.getHeaders()[i])
		headers.append("cluster ids")
		tempData = copy.copy(self.dataObj)
				
		an = analysis.Analysis()
		codebook, codes, errors = an.kmeans(tempData, tempData.getHeaders(), K)
		
# 		print "codebook: ", codebook
# 		print "codes: ", codes
# 		print "errors: ", errors
		
		tempData.addColToMatrix(codes, ["cluster ids"])
		tempData.write(self.clusterFile, headers)

	# reads data from the clustering data file and plots the data from that
	def plotClusters(self, event=None):
		cData = data.Data(self.clusterFile)
		clusters = cData.getData(["cluster ids"]).tolist()
		for i in range(len(clusters)):
			clusters[i] = clusters[i][0]
		plotData = cData.getMatrix()[:,range(cData.getMatrix().shape[1]-1)]
		self.colorValues = []
		R,G,B = 0, 255, 255
		cMax, cMin = float(max(clusters)), float(min(clusters))
		for i in range(len(clusters)):
			clusters[i] = (clusters[i]-cMin)/(cMax-cMin)
			if self.colorCheck == 1:
				self.colorValues.append("#%02x%02x%02x" % (R+clusters[i]*255,G-clusters[i]*255,B-clusters[i]*255))
			else:
				temp = float(i)/len(clusters)
				self.colorValues.append("#%02x%02x%02x" % (R+temp*255,G-temp*255,B-temp*255))
		self.dataObj.setMatrix(plotData)
		headers = self.dataObj.getHeaders()
		headers.pop()
		colSelect = dialog.pickClusterPlotColumns(self.root, headers, "pick cols to plot")
		cols = colSelect.cols

		if (len(cols) > 3):
			print "Too many columns being selected! Select 3 only"
			return
		columns = []
		for i in cols:
			columns.append(i)
		self.buildPoints(columns)
		self.updateAll()
								
	# allows the user to choose a data file to get data from
	def handleOpen(self, event=None):
		fn = tkFileDialog.askopenfilename( parent=self.root,
					title='Choose a data file', initialdir='.' )
		self.dataObj = data.Data(fn)
		self.permData = copy.copy(self.dataObj)

	def main(self):
		print 'Entering main loop'
		self.root.mainloop()


if __name__ == "__main__":
	dapp = DisplayApp(1200, 675)
	dapp.main()


