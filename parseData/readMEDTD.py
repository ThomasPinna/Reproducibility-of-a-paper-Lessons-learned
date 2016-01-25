from helpers import *
from model import *
import json
import sys

#########################################
## BUGREPORT
#########################################
class BugReportMozillaEclipse(Bugreport):
	def __init__(self, id, initrow, env):
		log("init MEDTD bugreport", 2)
		self.bug_id = id

		self.fixed = initrow["current_resolution"] == "FIXED"
		self.succes = True
		self.env = env
		self.products = set()
		# nr of days
		self.current_time = initrow["opening"]
		self.nr_of_days = None
		# get opener
		opener_id = initrow["reporter"]
		self.opener = Developer.getDeveloper("MEDTD"+self.env,opener_id)
		self.opener.open("MEDTD::"+self.bug_id)
		# get fixer if it is fixed (in temporal bugstatus)
		# get severity 
		self.severity_table = {"enhancement":1,"trivial":2,"minor": 3,"normal": 4,"major":  5,"critical":  6, "blocker":7}
		self.severity = None
		# get nr of developers (begin with starter)
		self.developers = set()
		self.developers.add(opener_id)
		# get nr of attachments
		self._attachments = 0
		# get nr of dependencies
		self._dependencies = 0

	def temporalBugStatus(self,status):
		log("temporalBugStatus", 2)
		log(status,3)
		self.getDevs(status)
		if self.fixed:
			for j in status:
				if j["what"] == "RESOLVED":
					self._attachments+=1
			final_status_change = status[-1]
			#register fixing developer
			Developer.getDeveloper("MEDTD"+self.env,final_status_change["who"]).fix("MEDTD::"+self.bug_id)
			#rounded because to keep consistency with FTDD
			time_passed = final_status_change["when"]
			self.nr_of_days = (time_passed-self.current_time)//(60*60*24)

	def temporalSeverity(self, severity):
		self.getDevs(severity)
		log("temporalSeverity", 2)
		log(severity,3)
		if self.fixed:
			self.severity = self.severity_table[severity[-1]["what"]]

	def temporalComponent(self,components):
		self.getDevs(components)
		log("temporalComponent", 2)
		log(components,3)
		if self.fixed:
			self._dependencies=len(components)
	def temporalProduct(self,products):
		self.getDevs(products)
		log("temporalProduct", 2)
		log(products,3)
		for elem in products:
			self.products.add(elem["what"])
	def getDevs(self, row):
		for elem in row:
			if "who" in elem:
				self.developers.add(elem["who"])

	def bugfix_time(self):
		return self.nr_of_days
	def developer_reputation(self):
		return self.opener.reputation()
	def bug_severity(self):
		return self.severity
	def nr_of_developers(self):
		return len(self.developers)
	def attachments(self):
		return self._attachments
	def dependencies(self):
		return self._dependencies
	def __str__(self):
		return str(self.__dict__)



#########################################
## READFROMFILE
#########################################
class readMEDTD(readFile):
	def __init__(self):
		super().__init__()

	def readMain(self, name):
		env = "eclipse"
		if "mozilla" in name:
			env = "mozilla"
		log("reading main MEDTD", 2)
		with open(name,'r') as filey:
			main = json.load(filey)["reports"]
			for i in main:
				bugreport = BugReportMozillaEclipse(i, main[i], env)
				if not bugreport.succes:
					log("ADDED TO FAILURE"+str(i), 1)
					self.failed.add(i)
				else:
					self.Bugreports[i] = bugreport
	
	def readBugStatus(self,name):
		log("reading Bugstatus "+name, 2)
		with open(name,'r') as filey:
			dummy,main = json.load(filey).popitem()
			for i in main:
				if i not in self.failed:
					self.Bugreports[i].temporalBugStatus(main[i])
					self.Bugreports[i].getDevs(main[i])

	def readSeverity(self,name):
		log("reading Bugstatus "+name,2)
		with open(name,'r') as filey:
			dummy,main = json.load(filey).popitem()
			for i in main:
				if i not in self.failed:
					self.Bugreports[i].temporalSeverity(main[i])
					self.Bugreports[i].getDevs(main[i])

	def readComponent(self,name):
		log("reading component"+name, 2)
		with open(name,'r') as filey:
			dummy,main = json.load(filey).popitem()
			for i in main:
				if i not in self.failed:
					self.Bugreports[i].temporalComponent(main[i])

	def readDevs(self,name):
		log("reading "+name, 2)
		with open(name,'r') as filey:
			dummy,main = json.load(filey).popitem()
			for i in main:
				if i not in self.failed:
					self.Bugreports[i].getDevs(main[i])
	def readProd(self,name):
		log("reading "+name, 2)
		with open(name,'r') as filey:
			dummy,main = json.load(filey).popitem()
			for i in main:
				if i not in self.failed:
					self.Bugreports[i].temporalProduct(main[i])

	def __str__(self):
		stringy = ""
		for br in self.Bugreports:
			stringy += str(self.Bugreports[br])
			stringy += "\n"
		return stringy

	def getBugsGroupedByProduct(self):
		bugsgrouped = {}
		for bug_id in self.Bugreports:
			bug = self.Bugreports[bug_id]
			for product in bug.products:
				if product in bugsgrouped:
					bugsgrouped[product][bug_id] = bug
				else:
					bugsgrouped[product] = {bug_id:bug}
		return bugsgrouped

if __name__ == "__main__":
	log("start program", 2)
	#initialise parameters
	pre = "dataset_MozillaAndEclipseDefectTrackingDataset/msr2013-bug_dataset/data/v02/"+sys.argv[1]+"/"
	DATASET_MEDTD = []
	DATASET_MEDTD.append( pre + "reports.json" )
	DATASET_MEDTD.append( pre + "assigned_to.json" )
	DATASET_MEDTD.append( pre + "bug_status.json" )
	DATASET_MEDTD.append( pre + "cc.json" )
	DATASET_MEDTD.append( pre + "component.json" )
	DATASET_MEDTD.append( pre + "op_sys.json" )
	DATASET_MEDTD.append( pre + "priority.json" )
	DATASET_MEDTD.append( pre + "product.json" )
	DATASET_MEDTD.append( pre + "resolution.json" )
	DATASET_MEDTD.append( pre + "severity.json" )
	DATASET_MEDTD.append( pre + "short_desc.json" )
	DATASET_MEDTD.append( pre + "version.json" )



	#read in ftdd data
	log("read ftdd data", 2)
	medtd_data = readMEDTD()
	medtd_data.readMain(DATASET_MEDTD[0])
	medtd_data.readBugStatus(DATASET_MEDTD[2])
	medtd_data.readSeverity(DATASET_MEDTD[9])
	medtd_data.readComponent(DATASET_MEDTD[4])
	medtd_data.readProd(DATASET_MEDTD[7])
	medtd_data.readDevs(DATASET_MEDTD[1])
	medtd_data.readDevs(DATASET_MEDTD[3])
	medtd_data.readDevs(DATASET_MEDTD[5])
	medtd_data.readDevs(DATASET_MEDTD[6])	
	medtd_data.readDevs(DATASET_MEDTD[8])
	medtd_data.readDevs(DATASET_MEDTD[10])
	medtd_data.readDevs(DATASET_MEDTD[11])
	#medtd_data.printall()
	#print(json.dumps(medtd_data.getBugsGroupedByProduct(),indent=2, skipkeys=True))
	grouped_by = medtd_data.getBugsGroupedByProduct()
	for prod in grouped_by:
		toFile("MEDTD_"+prod+".json", grouped_by[prod])
	#toFile("MEDTD_"+sys.argv[1]+".json", medtd_data.Bugreports)
	#print(resolutions)
	log(medtd_data,3)