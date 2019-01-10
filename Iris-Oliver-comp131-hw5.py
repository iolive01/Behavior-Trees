#
#	Iris Oliver
#	comp131-hw5
#	Behavior Trees
#	Implemented using the Node method. 
#	Collaborated with: Cathy Cowell, Leah Stern, Ki Ki Chan
#
#	To run this program:
#		 python Iris-Oliver-comp131-hw5.py 
#
#

from __future__ import print_function
import json

# Used to color text output for readability. 
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# Base class for the nodes. 
# Each individual node contains a custom evaluate function, and any other
# helpers and private variables it needs. 
class TreeNode:
	def __init__(self, name, priority):
		self.name = name
		self.priority = priority
		self.status = "Not Yet Evaluated"

	def printNode(self):
		print(self.name)

# Class for the three types of decorator nodes. 
class Decorator(TreeNode):
	def __init__(self, name, priority, decType, timeStart, child):
		TreeNode.__init__(self, name, priority)
		self.category = decType
		self.timeStart = 0
		self.child = child

	def evaluate(self):
		if (self.category is 'timer'):
			self.evalTimer()
		elif(self.category is 'failLoop'):
			self.evalFailLoop()
		elif(self.category is 'logical'):
			self.evalLogic()
		print(self.name, ' --> ', self.status)
		return self.status
		
	def evalLogic(self):
		if (self.child.evaluate() is 'SUCCESS'):
			self.status = 'FAILURE'
		elif(self.child.evaluate() is 'FAILURE'):
			self.status = 'SUCCESS'
		elif (self.child.evaluate() is 'RUNNING'):
			self.status = 'RUNNING'

	def evalFailLoop(self):
		if (self.child.evaluate() is 'SUCCESS'):
			self.status = 'RUNNING'
		elif(self.child.evaluate() is 'FAILURE'):
			self.status = 'SUCCESS'
		elif (self.child.evaluate() is 'RUNNING'):
			self.status = 'RUNNING'

	def evalTimer(self):
		if (self.child.evaluate() is 'SUCCESS'):
			self.status = 'RUNNING'
		elif(self.child.evaluate() is 'FAILURE'):
			self.status = 'SUCCESS'
		elif (self.child.evaluate() is 'RUNNING'):
			self.status = 'RUNNING'

# Class for conditional nodes. Each node takes in a 'condition' which is a
# 	boolean function that represents the condition it is associated with. 
class Conditional(TreeNode):
	def __init__(self, name, priority, condition):
		TreeNode.__init__(self, name, priority)
		self.condition = condition

	def evaluate(self):
		if (self.condition()):
			self.status = 'SUCCESS'
		else:
			self.status = 'FAILURE'
		print(self.name, ' --> ', self.status)
		return self.status

# Class for the three types of composite nodes: sequence, selection, 
# 	and priority.
class Composite(TreeNode):
	def __init__(self, name, priority, comType, children):
		TreeNode.__init__(self, name, priority)
		self.category = comType
		self.children = children

	def evaluate(self):
		if (self.category is 'sequence'):
			for child in self.children:
				if (child.evaluate() is 'FAILURE'):
					self.status = 'FAILURE'
					print(self.name, ' --> ', self.status)
					return self.status	
				if (child.evaluate() is 'RUNNING'):
					self.status = 'RUNNING'
			self.status = 'SUCCESS'

		elif(self.category is 'selection'):
			for child in self.children:
				if (child.evaluate() is 'SUCCESS'):
					self.status = 'SUCCESS'
					print(self.name, ' --> ', self.status)
					return self.status	
				if (child.evaluate() is 'RUNNING'):
					self.status = 'RUNNING'
			self.status = 'FAILURE'

		elif(self.category is 'priority'):
			for child in self.children:
				if (child.evaluate() is 'SUCCESS'):
					self.status = 'SUCCESS'
					print(self.name, ' --> ', self.status)
					return self.status	
				if (child.evaluate() is 'RUNNING'):
					self.status = 'RUNNING'
			self.status = 'FAILURE'	

		print(self.name, ' --> ', self.status)
		return self.status			

# Class for task nodes. Passed in the taskFun, which is the function
# 	to simulate actually running the task, and is customary to each task.
class Task(TreeNode):
	def __init__(self, name, priority, taskFun):
		TreeNode.__init__(self, name, priority)
		self.task = taskFun

	def evaluate(self):
		self.task()					# execute the given task function
		self.status = 'SUCCESS' 	# tasks always succeed
		print(self.name, ' --> ', self.status)
		return self.status 

# Custom task functions to simulate executing each task. These functions 
# 	are passed into the Task objects which are created in the tree. Each 
# 	function corresponds to one Task in the original behavior tree.  
def findHomeTask():
	print(color.RED, 'Executing task: Finding Home', color.END, sep='')
	blackboard['homePath'] = 'updated home path'

def goHomeTask():
	print(color.RED, 'Executing task: Going Home', color.END, sep='')

def dockTask():
	blackboard['batteryLevel'] = 100
	print(color.RED, 'Executing task: Docking', color.END, sep='')

def cleanSpot20Task():
	print(color.RED, 'Executing task: Cleaning 20s Spot', color.END, sep='')
	print(blackboard['homePath'])

def doneSpotTask():
	print(color.RED, 'Executing task: Done Spot Cleaning', color.END, sep='')
	blackboard['spot'] = False

def cleanSpot35Task():
	print(color.RED, 'Executing task: Cleaning 35s Spot', color.END, sep='')

def cleanTask():
	print(color.RED, 'Executing task: Cleaned', color.END, sep='')

def doneGeneralTask():
	print(color.RED, 'Executing task: Done General', color.END, sep='')
	blackboard['general'] = False

def doNothingTask():
	print(color.RED, 'Executing task: Do Nothing', color.END, sep='')


# Functions to pass into the Conditionals, to specify which condition each
# 	Conditional is related to. Each function below corresponds to a conditional
# 	in the behavior tree. 
def batteryCheckFun():
	return blackboard['batteryLevel'] < 30

def spotCalledFun():
	return blackboard['spot']

def spotDustyFun():
	return blackboard['dustySpot']

def generalCalledFun():
	return blackboard['general']


# Function to build the tree and run it for the specified amount of time.
def runTree(seconds):
	
	# LEFT SUBTREE # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	batteryCheck = Conditional('Battery Low', 0, batteryCheckFun)
	findHome = Task('Find Home', 0, findHomeTask)
	goHome = Task('Go Home', 0, goHomeTask)
	dock = Task('Dock', 0, dockTask)
	batterySequence = Composite('Battery Sequence', 1, 'sequence', 
						[batteryCheck, findHome, goHome, dock])

	# MIDDLE SUBTREE # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
	# Spot sequence - right subtree of middle tree
	spotCalled = Conditional('Spot Command Called', 0, spotCalledFun)
	cleanSpot20 = Task('Clean Spot 20s', 0, cleanSpot20Task)
	spotTimer20 = Decorator('20s Spot Clean Timer', 0, 'timer', 
							0, cleanSpot20)
	doneSpot = Task('Done Spot Cleaning', 0, doneSpotTask)
	spotCleanSequence = Composite('Spot Clean Sequence', 0, 'sequence',
							[spotCalled, spotTimer20, doneSpot])

	# General sequence - left subtree of middle tree
	spotDusty = Conditional('Dusty Spot', 0, spotDustyFun)
	cleanSpot35 = Task('Clean Spot 35s', 0, cleanSpot35Task)
	spotTimer35 = Decorator('35s Spot Clean Timer', 0, 'timer',
								0, cleanSpot35)
	dustySpotSequence = Composite('Dusty Spot Clean Sequence', 0, 'sequence',
									[spotDusty, spotTimer35])

	clean = Task('Clean', 0, cleanTask)
	dustyCleanSelector = Composite('Dusty and Clean Selector', 0, 'selection',
									[dustySpotSequence, clean])

	batteryCheck1 = Conditional('Battery Low Until Fail', 0, batteryCheckFun)
	batteryNegate = Decorator('Negating Battery Low', 0, 'logical', 0, 
								batteryCheck1)
	
	findSpotSequence = Composite('Finding Spots until Battery is Low', 0, 
								 'sequence', [batteryNegate, dustyCleanSelector])
	untilFail = Decorator('Looping until Fail', 0, 'failLoop', 0, findSpotSequence)

	doneGeneral = Task('Done with General', 0, doneGeneralTask)
	generalCleaningSequence = Composite('Executing General Command', 0, 
										'sequence', [untilFail, doneGeneral])

	generalCalled = Conditional('General Command Called', 0, generalCalledFun)

	generalCommandSequence = Composite('Checking General Command', 0, 'sequence',
										[generalCalled, generalCleaningSequence])

	cleaningSelection = Composite('Battery is charged, starting cleaning', 2, 
									'selection',
									[spotCleanSequence, generalCommandSequence])


	# RIGHT SUBTREE # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
	doNothing = Task('Do Nothing', 3, doNothingTask)

	# FULL TREE BUILT # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
	priorityRoot = Composite('Priority Root', 0, 'priority',
								[batterySequence, cleaningSelection, doNothing])

	# evaluate tree for n seconds. Decrement battery by 1 each second.
	for i in range(seconds):
		priorityRoot.evaluate()
		blackboard['batteryLevel'] -= 1

# Initial blackboard to be used by the tree.
blackboard = {
	'batteryLevel' : 0,
	'spot' : False,
	'general' : False,
	'dustySpot': False,
	'homePath': 'path to home'
}

# Parse user input, fill blackboard, build and run tree. 
def getInput():
	print(color.BOLD, color.BLUE, 'Welcome to the Behavior Tree. ',
			'With each second, the Roomba battery decreases 1%.', color.END, 
			sep='')

	# Get user input
	seconds = input('How many seconds would you like to run the simulation for? ')
	batteryLevel = input('What is the starting battery level? ')
	spotClean = raw_input('Do you want to run a spot clean? (yes/no) ')
	generalClean = raw_input('Do you want to run a general clean? (yes/no) ')

	# Fill blackboard
	if (spotClean == 'yes'):
		blackboard['spot'] = True

	if (generalClean == 'yes'):
		blackboard['general'] = True

	blackboard['batteryLevel'] = batteryLevel

	# Display blackboard
	print(color.BOLD, color.BLUE, 'Here is the blackboard!', color.END, sep='')
	print(json.dumps(blackboard, indent=4))	

	# Begin running tree
	print(color.BLUE, color.BOLD, sep='', end='')
	raw_input('Press enter to build the tree and start the simulation. ')
	print(color.END)
	print(color.BOLD, color.BLUE, 'Building the tree now.', color.END, sep='')
	
	runTree(seconds)

	# Print outputs. 
	print(color.BOLD, color.BLUE, 'Here is the blackboard after running for ', 
			seconds, ' seconds.', color.END, sep='')
	print(json.dumps(blackboard, indent=4))	


getInput()

















