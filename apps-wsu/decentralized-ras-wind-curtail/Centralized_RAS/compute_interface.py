from xlrd import open_workbook
import numpy
import scipy.optimize
import socket

class ComputeInterface():

	def get_sheet_array(self, sheetname):
		sheet = self.book.sheet_by_name(sheetname)
		sheet_array = list()
		for row in sheet.get_rows():
			row_list = list()
			for x in row:
				if x.ctype == 2:
					row_list.append(x.value)
				else:
					row_list.append(None)
			sheet_array.append(row_list)

		return sheet_array

	def __init__(self):
		self.book = open_workbook("/home/riaps/Sample/SampleProject/riaps_apps/RASApplication/Demo.xlsx")
		self.C = numpy.asarray(self.get_sheet_array("C"))
		self.X = numpy.asarray(self.get_sheet_array("X"))
		self.b = numpy.asarray(self.get_sheet_array("b"))
		lb = self.get_sheet_array("lb")
		ub = self.get_sheet_array("ub")
		bounds_list = [x for x in zip(lb, ub)]
		self.bounds = numpy.asarray(bounds_list)
		self.H = numpy.asarray(self.get_sheet_array("H"))
		

	
	def compute_result(self, tempPG):
		self.H[1][0] = tempPG[1]/100.0
		self.H[8][1] = tempPG[2]/100.0
		self.H[10][2] = tempPG[3]/100.0
		self.H[0][3] = (tempPG[0]-100.0)/100.0

		A = numpy.dot(self.C, self.X)
		A = numpy.dot(A, self.H)
		f = numpy.asarray([-1 * tempPG[1], -1 * tempPG[2], -1 * tempPG[3], 0])

		x = scipy.optimize.linprog(f, A, self.b, bounds = self.bounds)

		print(x)
		if x.success:
			return x.x
		else:
			return [1,1,1,1]


