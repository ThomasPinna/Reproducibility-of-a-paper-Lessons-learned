import time #BugReportFTDD, time creation
import json
#helper functions
verbosity = 0
def log(stringy, lvl = 0):
	"""
	lvl 0 = output
	lvl 1 = debug
	lvl 2 = verbose
	lvl 3 = large blocks of data (debug)
	"""
	if lvl <= verbosity:
		spaces = 3*lvl*" "
		print(spaces + str(stringy).replace("\n", spaces + "\n"))

#absteact readfile
class readFile:
	def __init__(self):
		self.Bugreports = {}
		self.failed = set()

	def printall(self):
		for bug in self.Bugreports:
			if self.Bugreports[bug].fixed:
				print( self.Bugreports[bug].opener)
				print( self.Bugreports[bug].getRow())

def toFile(filename, bugs):
	a = []
	for bugid in bugs:
		if bugs[bugid].fixed:
			a.append(bugs[bugid].getRow())
	with open(filename, 'w') as filey:
		json.dump(a,filey, indent=1)