import Tkinter as tk
import tkFont as tkf
import math, os, random, numpy, tkFileDialog
from tkColorChooser import askcolor
import analysis, data, sys

class Dialog(tk.Toplevel):

	def __init__(self, parent, title = None):

		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)

	#
	# construction hooks

	def body(self, master):
		# create dialog body.  return widget that should have
		# initial focus.  this method should be overridden

		pass

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = tk.Frame(self)

		w = tk.Button(box, text="ok", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	#
	# standard button semantics

	def ok(self, event=None):

		if not self.validate():
			self.initial_focus.focus_set() # put focus back
#			return
		
		
		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()

	def cancel(self, event=None):

		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

	#
	# command hooks

	def validate(self):

		return 1 # override

	def apply(self):

		pass # override

# create a dialog box to select which columns of data you want to use
class LinearRegressionDialog(Dialog):

	def __init__(self, parent, colNames, title = None):
		
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body,colNames)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)
	
	def body(self,master,colNames):
		self.cols = []
		self.color = "black"
		self.size = 5
		self.okHit = False
		self.buildLists(master, colNames)

	def buildLists(self,master,colNames):
		self.cols = colNames
		self.dependent = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
		self.independent = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
		for name in colNames:
			self.dependent.insert(tk.END, name.strip())
			self.independent.insert(tk.END, name.strip())
		tk.Label(master, text = "Select Independent Variable:").grid(row=0,column=0)
		tk.Label(master, text = "Select Dependent Variable:").grid(row=0,column=1)
		self.dependent.grid(row=1,column=0)
		self.independent.grid(row=1,column=1)
		
	def ok(self, event=None):
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
		self.dependent = self.cols[self.dependent.curselection()[0]]
		self.independent = self.cols[self.independent.curselection()[0]]
		self.okHit = True
		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()
		
		
# create a dialog box to select which columns of data you want to use
class colSelectBox(Dialog):

	def __init__(self, parent, colNames, title = None):
		
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body,colNames)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)
	
	def body(self,master,colNames):
		self.cols = []
		self.color = "black"
		self.size = 5
		self.buildLists(master, colNames)

	def buildLists(self,master,colNames):
		self.col1 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
		self.col2 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
		self.col3 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
		self.sizeCol = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
		self.colorCol = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
#		self.numCol = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
		self.col3.insert(tk.END, "All Ones")
		for name in colNames:
			self.col1.insert(tk.END, name.strip())
			self.col2.insert(tk.END, name.strip())
			self.col3.insert(tk.END, name.strip())
			self.sizeCol.insert(tk.END, name.strip())
			self.colorCol.insert(tk.END, name.strip())
#			self.numCol.insert(tk.END, name.strip())
		tk.Label(master, text = "Select Column for X values:").grid(row=0,column=0)
		tk.Label(master, text = "Select Column for Y values:").grid(row=0,column=1)
		tk.Label(master, text = "Select Column for Z values:").grid(row=0,column=2)
		tk.Label(master, text = "Select Column for Size values:").grid(row=0,column=3)
		tk.Label(master, text = "Select Column for Color values:").grid(row=0,column=4)
#		tk.Label(master, text = "Select Column for Num values:").grid(row=0,column=5)
		self.col1.grid(row=1,column=0)
		self.col2.grid(row=1,column=1)
		self.col3.grid(row=1,column=2)
		self.sizeCol.grid(row=1,column=3)
		self.colorCol.grid(row=1,column=4)
#		self.numCol.grid(row=1,column=5)
#		self.colorSelect = tk.Button(master,text='Select Base Color', command=self.pickColor)
#		self.colorSelect.grid(row = 3, column = 2)
		self.sizeSelect = tk.Entry(master)
		self.sizeSelect.insert(0,"")
		tk.Label(master, text = "enter a base size:").grid(row=3,column=3)
		self.sizeSelect.grid(row=3,column=4)
		self.colorBase = tk.StringVar( master )
		self.colorBase.set("Red")
		colorBaseSelect = tk.OptionMenu( master, self.colorBase, 
										"Red", "Green", "Blue", "Gray" )
		colorBaseSelect.grid(row = 3, column = 2)
#		
#	def pickColor(self,event=None):
#		self.selectedColor = askcolor()
	
	def ok(self, event=None):
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
		self.column1 = self.col1.curselection()
		self.column2 = self.col2.curselection()
		self.column3 = self.col3.curselection()
		self.sizeColumn = self.sizeCol.curselection()
		self.colorColumn = self.colorCol.curselection()
		self.selectedRad = self.sizeSelect.get()
#		self.numColumn = self.numCol.curselection()
		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()
	
# create a dialog box where you can enter random distribution types
class dataEnterBox(Dialog):
	
	def __init__(self, parent,randTypeX, randTypeY, shape, title = None):
		
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body,randTypeX,randTypeY,shape)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)
		
	def body(self,master,randTypeX,randTypeY,shape):
		self.randTypeX = []
		self.randTypeY = []
		self.randTypeX.append(0)
		self.randTypeY.append(0)
		if (randTypeX == "Gaussian"):
			self.randSelectionX = 0;
		elif (randTypeX == "Uniform"):
			self.randSelectionX = 1;
		if (randTypeY == "Gaussian"):
			self.randSelectionY = 0;
		elif (randTypeY == "Uniform"):
			self.randSelectionY = 1;
		self.shape = shape
		self.numRandPoints = 100;
		self.buildLists(master)
		self.buildEntryBoxes(master)
		
	def buildLists(self,master):
		self.randSelectX = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
		self.randSelectX.insert(tk.END,"Gaussian")
		self.randSelectX.insert(tk.END,"Uniform")
		self.randSelectX.selection_set(self.randSelectionX)
		self.randSelectY = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
		self.randSelectY.insert(tk.END,"Gaussian")
		self.randSelectY.insert(tk.END,"Uniform")
		self.randSelectY.selection_set(self.randSelectionY)
		tk.Label(master, text = "Random Distribution for X:").pack(pady=5)
		self.randSelectX.pack(pady=5)
		tk.Label(master, text = "Random Distribution for Y:").pack(pady=5)
		self.randSelectY.pack(pady=5)
		self.selectShape = tk.Listbox(master, selectmode = tk.SINGLE, exportselection=0)
		self.selectShape.insert(tk.END,"Circle")
		self.selectShape.insert(tk.END,"Square")
		self.selectShape.selection_set(self.shape)
		tk.Label(master, text = "Select Shape of Data Points:").pack(pady=5)
		self.selectShape.pack(pady=5)
		
	def buildEntryBoxes(self, master):
		self.enterNumRand = tk.Entry(master)
		self.enterNumRand.insert(0, "100")
		tk.Label(master, text = "Enter Number of Random Points to Generate:").pack(pady=5)
		self.enterNumRand.pack(pady=0)
		
	def ok(self,event = None):
		if not self.validate():
				self.initial_focus.focus_set() # put focus back
		
		self.randTypeX = self.randSelectX.curselection()
		self.randTypeY = self.randSelectY.curselection()
		self.dataShape = self.selectShape.curselection()
		self.numRandPoints = self.enterNumRand.get()
		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()
		
# create a dialog box where you can enter random distribution types
class pcaAnalysisBox(Dialog):
	
	def __init__(self, parent, title = None):
		
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)
		
	def body(self,master):
		self.analyses = []
		self.analysisLabels = []
		self.pickFile = tk.Button(master, text="Pick Input File", 
									command=lambda: self.openFile(master))
		self.pickFile.grid(row=0,column=1,columnspan=2)
		
		self.pickHeaders = tk.Listbox(master, selectmode = tk.MULTIPLE, exportselection=0)
		self.pickHeaders.grid(row=1,column=1,columnspan=2)
		self.performPCA = tk.Button(master, text="Perform PCA on Selected File",
									command=self.performPCA)
		self.performPCA.grid(row=2,column=1,columnspan=2)
		self.pcaListBox = tk.Listbox(master, selectmode = tk.SINGLE, exportselection=0)
		self.pcaListBox.grid(row=3,column=1,columnspan=2)
		self.deleteAnalysis = tk.Button(master, text="Delete Selected Analysis",
										command=self.deletePCA)
		self.deleteAnalysis.grid(row=4,column=1,columnspan=2)
		self.pcaName = tk.Entry(master)
		self.pcaName.grid(row=5,column=2)
		self.pcaNameButton = tk.Button(master, text="Rename selected PCA to: ",
										command=self.namePCA)
		self.pcaNameButton.grid(row=5,column=1)
		
	# allows the user to select a file to draw data from for PCA analysis
	def openFile(self, master, event = None):
		self.pickHeaders.delete(0,tk.END)
		fn = tkFileDialog.askopenfilename( parent=master,
					title='Choose a pca file', initialdir='.' )
		print "filename: ", fn
		self.dataFile = data.Data(fn)
		for header in self.dataFile.getHeaders():
			self.pickHeaders.insert(tk.END, header)
		return fn
	
	# performs PCA on the current data file with the selected headers,
	# and puts it into the PCA listbox.
	def performPCA(self, event = None):
		pcaAnalysis = analysis.Analysis()
		headers = []
		for i in self.pickHeaders.curselection():
			headers.append(self.dataFile.getHeaders()[i])
#		print "headers in performPCA: ", headers
		pcadata = pcaAnalysis.pca( self.dataFile, headers )
		self.pcaListBox.insert(tk.END, (headers))
		self.analyses.append(pcadata)
		self.analysisLabels.append(headers)
	
	def namePCA(self, event = None):
		currSelection = self.pcaListBox.curselection()[0]
		self.analysisLabels[currSelection] = self.pcaName.get()
		self.pcaListBox.delete(currSelection)
		self.pcaListBox.insert(currSelection, self.pcaName.get())
	
	# deletes an analysis from the Listbox that holds PCAs.
	def deletePCA(self, event = None):
		self.pcaListBox.delete(self.pcaListBox.curselection())
		self.analyses.pop(self.pcaListBox.curselection())
		self.analysisLabels.pop(self.pcaListBox.curselection())
				
	def ok(self,event = None):
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
		
		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()

# create a dialog box that shows the current pca's eigenvectors and eigenvalues
class eigenDisplayBox(Dialog):
	
	def __init__(self, parent, eigenVectors, eigenValues, headers, title = None):
		
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body,eigenVectors, eigenValues, headers)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)
		
	def body(self,master,Eigenvectors,Eigenvalues,headers):
		gridLabels = []
		eigvalLabels = []
		cumulativeLabels = []
		fullSum = 0
		eigvecNameLabels = []
		colLabels = ["E-vec","E-val","Cumulative"]
		eigvecs = Eigenvectors.tolist()
		eigvals = Eigenvalues.tolist()
		#calculate the sum of all of the eigenvalues so cumulative sum can be a percentage
		for i in eigvals[0]:
			fullSum+=i
#		print "eigvecs: ", eigvecs, " eigvals: ", eigvals
		
		# make labels for the eigenvalues in the second column of the grid
		for i in range(len(eigvals[0])):
			eigvalLabels.append(tk.Label(master, text = ('%.4f' % eigvals[0][i])))
		for i in range(len(eigvalLabels)):
			eigvalLabels[i].grid(row=i+1,column=1)
		
		# make labels for the eigenvector names in the first column of the grid
		for i in range(len(eigvecs[0])):
			eigvecNameLabels.append(tk.Label(master, text = "PCA%02d"%(i)))
		for i in range(len(eigvecNameLabels)):
			eigvecNameLabels[i].grid(row=i+1,column=0)
	
		# make labels for the cumulative sum of the eigenvalues in the 3rd column
		sum = 0
		for i in range(len(eigvals[0])):
			sum+=eigvals[0][i]
			cumulativeLabels.append(tk.Label(master, 
									text = ('%.4f' % ((sum/fullSum)))))
		for i in range(len(cumulativeLabels)):
			cumulativeLabels[i].grid(row=i+1,column=2)
		
		# make labels for the column names
		for i in range(len(headers)):
			colLabels.append(str(headers[i]))
		for i in range(len(colLabels)):
			colLabels[i] = tk.Label(master, text = colLabels[i])
		for i in range(len(colLabels)):
			colLabels[i].grid(row=0,column=i)
		
		for i in range(len(eigvecs)):
			gridLabels.append([])
			for j in range(len(eigvecs[0])):
				gridLabels[i].append(tk.Label(master, text = ('%.4f' % eigvecs[i][j])))
		for i in range(len(gridLabels)):
			for j in range(len(gridLabels[i])):
				gridLabels[i][j].grid(row=i+1,column=j+3)

	def ok(self,event = None):
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
		
		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()
		
class pickPCAColumnsBox(Dialog):
	
	def __init__(self, parent, headers, title = None):
		
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body, headers)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)
		
	def body(self,master,headers):
		self.colSelectListBox = tk.Listbox(master, selectmode = tk.MULTIPLE, exportselection=0)
		for i in range(len(headers)):
			self.colSelectListBox.insert(tk.END, "PCA%02d"%(i))
		self.colorOption = tk.StringVar(master)
		self.colorOption.set("black")
		colorMenu = tk.OptionMenu( master, self.colorOption, 
								"black", "yellow","orange","red","red-purple","purple", 
								"blue-purple", "blue", "teal", "green", "yellow-green" )
		self.colSelectListBox.grid(row=0,column=0)
		colorMenu.grid(row=0,column=1)
		
	def ok(self,event = None):
		
		self.cols = self.colSelectListBox.curselection()
		self.color = self.colorOption.get()
	
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
		
		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()
		
class executeClusteringBox(Dialog):
	
	def __init__(self, parent, headers, title = None):
		
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body, headers)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)
		
	def body(self,master, headers):
		self.colSelectListBox = tk.Listbox(master, selectmode = tk.MULTIPLE, exportselection=0)
		for i in range(len(headers)):
			self.colSelectListBox.insert(tk.END,headers[i])
		self.colSelectListBox.grid(row=0,column=0,columnspan=2)
		self.kSelect = tk.Entry(master)
		self.kSelect.grid(row=2,column=0)
		self.kSelect.delete(0, tk.END)
		self.kSelect.insert(0, "5")
		self.checkVar = tk.IntVar(master)
		self.colorCheck = tk.Checkbutton(master, text = "", variable=self.checkVar)
		self.colorCheck.grid(row=2,column=1)
		self.kLabel = tk.Label(master, text = "Enter Number of Clusters")
		self.checkLabel = tk.Label(master, text = "Do you want preselected colors?")
		self.kLabel.grid(row=1,column=0)
		self.checkLabel.grid(row=1,column=1)
		
	def ok(self,event = None):
		
		self.cols = self.colSelectListBox.curselection()
		self.K = self.kSelect.get()
		self.check = self.checkVar.get()
	
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
		
		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()

class pickClusterPlotColumns(Dialog):
	
	def __init__(self, parent, headers, title = None):
		
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body, headers)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)
		
	def body(self,master, headers):
		self.colSelectListBox = tk.Listbox(master, selectmode = tk.MULTIPLE, exportselection=0)
		for i in range(len(headers)):
			self.colSelectListBox.insert(tk.END,headers[i])
		self.colSelectListBox.grid(row=0,column=0)
		
	def ok(self,event = None):
		
		self.cols = self.colSelectListBox.curselection()
	
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
		
		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()


if __name__ == "__main__":
	data = data.Data( sys.argv[1] )
	analysis = analysis.Analysis()
	root = tk.Tk()
	pcadata = analysis.pca( data, data.getHeaders(), False )
	testDiag = eigenDisplayBox(root, pcadata.getEigenvectors(),
								pcadata.getEigenvalues(),
								pcadata.getDataHeaders())
		
	
		