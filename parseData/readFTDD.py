import csv #read ftdd
import requests#rest api
import os,pickle #saving stuff
import json
from helpers import *
from model import *
import sys

#########################################
## BUGREPORT
#########################################
class BugReportFTDD(Bugreport):
	severityLevels = {"enhancement":1, "trivial": 2, "minor":3, "normal":4, "major":5, "critical":6, "blocker":7}
	def __init__(self, mainrow):
		super().__init__()
		log("init FTDD bugreport", 2)
		self.bug_id = mainrow[0]
		self.succes = True
		#nr of days
		self.nr_of_days = None
		# get json from mozilla api for bug
		self.rest = self.get_bug_json()
		rest = self.rest
		log(rest,3)
		self.history = self.get_hist_json()
		history = self.history
		log(history,3)
		if "error" in rest:
			self.succes = False
			return
		# get opener	
		opener_email = rest["bugs"][0]["creator"]
		log(opener_email,2)
		self.opener = Developer.getDeveloper("FTDD",opener_email)
		self.opener.open("FTDD::"+self.bug_id)
		# get fixer if it is fixed
		self.fixed  = mainrow[5] == "FIXED"
		if(mainrow[5] == "FIXED"):
			closer_email = history["bugs"][0]["history"][-1]["who"]
			log(closer_email,2)
			closer = Developer.getDeveloper("FTDD",closer_email)
			closer.fix("FTDD::"+self.bug_id)
		# get severity
		self.severity = rest["bugs"][0]["severity"].lower()
		self.severity = BugReportFTDD.severityLevels[self.severity]
		# get nr of developers (begin with starter)
		developers_included = set()
		for change in history["bugs"][0]["history"]:
			developers_included.add(change["who"])
		self._nr_of_developers = len(developers_included)
		#nr of attachments
		self.nr_of_attachments = 0
		#nr of dependenices
		self.nr_of_dependencies = len(rest["bugs"][0]["depends_on"])


	def addTemporalActivity(self, row):
		log("adding temporal activity", 2)
		#activity
		a = row[2]
		if a == "Z":
			self.nr_of_days = int(row[3])
		elif a == "V" or a == "S":
			self.nr_of_attachments += 1
		#if a == ""
		#self.activities.append(row)
	
	def get_bug_json(self):
		log("get bug json", 2)
		url = "https://bugzilla.mozilla.org/rest/bug/"+str(self.bug_id)+"?token=561465-XfcyWXZVGTKlpYOy1ltr3k&include_fields=id,creator,depends_on,severity"
		log(url,2)		
		filename = ".cachefiles/ftdd___"+str(self.bug_id)+".p"
		if not os.path.isfile(filename):
			to_return = requests.get(url).json()
			with open(filename, 'wb') as pfile:
				pickle.dump(to_return, pfile, protocol=pickle.HIGHEST_PROTOCOL)
			return to_return
		else:
			with open(filename, 'rb') as pfile:
				return pickle.load(pfile)
	
	def get_hist_json(self):
		log("get history json", 2)
		url = "https://bugzilla.mozilla.org/rest/bug/"+str(self.bug_id)+"/history?token=561465-XfcyWXZVGTKlpYOy1ltr3k&include_fields=id,creator,depends_on,severity"
		log(url,2)	
		filename = ".cachefiles/ftddH___"+str(self.bug_id)+".p"	
		if not os.path.isfile(filename):
			to_return = requests.get(url).json()
			with open(filename, 'wb') as pfile:
				pickle.dump(to_return, pfile, protocol=pickle.HIGHEST_PROTOCOL)
			return to_return
		else:
			with open(filename, 'rb') as pfile:
				return pickle.load(pfile)

	def bugfix_time(self):
		return self.nr_of_days
	def developer_reputation(self):
		return self.opener.reputation()
	def bug_severity(self):
		return self.severity
	def nr_of_developers(self):
		return self._nr_of_developers
	def attachments(self):
		return self.nr_of_attachments
	def dependencies(self):
		return self.nr_of_dependencies
	def __str__(self):
		return str(self.__dict__)


#########################################
## READFROMFILE
#########################################
class readFTDD(readFile):
	def __init__(self):
		super().__init__()

	def readMain(self, name):
		log("reading main csv", 2)
		self.status = [0,0]
		with open(name, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			next(reader) #first line is header
			i = 0
			for row in reader:
				if i%10 ==0:
					log(i,1)
				i+=1
				bugreport = BugReportFTDD(row)
				if not bugreport.succes:
					log("ADDED TO FAILURE"+str(row[0]), 1)
					self.failed.add(row[0])
				else:
					self.Bugreports[row[0]] = bugreport



	def readTemporalActivity(self, name):
		log("reading temporal activity", 2)
		self.status = [1,0]
		with open(name, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			for row in reader:
				if row[0] not in self.failed:
					self.Bugreports[row[0]].addTemporalActivity(row)

	def printall(self):
		for bug in self.Bugreports:
			if self.Bugreports[bug].fixed:
				print( self.Bugreports[bug].opener)
				print( self.Bugreports[bug].getRow())


	def __str__(self):
		stringy = ""
		for br in self.Bugreports:
			stringy += str(self.Bugreports[br])
			stringy += "\n"
		return stringy




if __name__ == "__main__":
	log("start program", 2)
	#initialise parameters
	DATASET_FTDD_MAIN = sys.argv[1]
	DATASET_FTDD_TEMPORAL = sys.argv[2]
	#read in ftdd data
	log("read ftdd data", 2)
	ftdd_data = readFTDD()
	ftdd_data.readMain(DATASET_FTDD_MAIN)
	ftdd_data.readTemporalActivity(DATASET_FTDD_TEMPORAL)
	#ftdd_data.printall()
	log(ftdd_data,3)

	toFile("./FTDD_features.json",ftdd_data.Bugreports )