from helpers import *
import os
import pickle
import requests
#model

class Developer:
	#all developers
	Developers = {}
	def __init__(self, emailaddress):
		log("init developer", 2)
		self.id = str(emailaddress)
		self.opened = set()
		self.fixed  = set()
	def open(self,id):
		self.opened.add(id)
	def fix(self,id):
		self.fixed.add(id)
	def reputation(self):
		#calculated opened(D) intersect closed(D)
		op_int_clo = 0
		for i in self.opened:
			if i in self.fixed:
				op_int_clo+=1
		return float(op_int_clo) / (float(len(self.opened))+1)
	def __str__(self):
		stringy = self.id
		stringy += "; opened: "
		stringy += str(len(self.opened))
		stringy += "\nfixed: "
		stringy += str(len(self.fixed))
		return stringy
	@staticmethod
	def getDeveloper(env,emailaddress):
		log("get developer: "+str(emailaddress), 2)
		if env not in Developer.Developers:
			Developer.Developers[env] = {}
		if emailaddress not in Developer.Developers[env]:
			Developer.Developers[env][emailaddress]= Developer(emailaddress)
		return Developer.Developers[env][emailaddress]

class Bugreport:
	def __init__(self):
		pass
	def developer_reputation(self):
		raise "Bugreport::calculate is a virtual method"
	def bug_severity(self):
		raise "Bugreport::calculate is a virtual method"
	def nr_of_developers(self):
		raise "Bugreport::calculate is a virtual method"
	def attachments(self):
		raise "Bugreport::calculate is a virtual method"
	def dependencies(self):
		raise "Bugreport::calculate is a virtual method"
	def bugfix_time(self):
		raise "Bugreport::calculate is a virtual method"
	def getRow(self):
		return {"bugfix_time": self.bugfix_time(),
				"developer_reputation": self.developer_reputation(),
				"bug_severity": self.bug_severity(),
				"nr_of_developers": self.nr_of_developers(),
				"attachments": self.attachments(),
				"dependencies":self.dependencies()}













