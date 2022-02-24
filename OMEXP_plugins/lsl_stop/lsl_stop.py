#-*- coding:utf-8 -*-`
import share.opensesame_plugins.lsl_start.liblsl as lblsl
from libopensesame.py3compat import *
from libopensesame.item import item
from libqtopensesame.items.qtautoplugin import qtautoplugin

class lsl_stop(item):   
     
	def run(self):        
		""" Stop Recording """        
		LSL= self.experiment.get("LSL")
		LSL.stop_session()
		LSL.outlet.__del__()
		self.experiment.set("LSL",LSL)


class qtlsl_stop(lsl_stop, qtautoplugin):

	"""
	This class handles the GUI aspect of the plug-in. By using qtautoplugin, we
	usually need to do hardly anything, because the GUI is defined in info.json.
	"""
	def __init__(self, name, experiment, script=None):

		"""
		Constructor.

		Arguments:
		name		--	The name of the plug-in.
		experiment	--	The experiment object.

		Keyword arguments:
		script		--	A definition script. (default=None)
		"""

		# We don't need to do anything here, except call the parent
		# constructors.
		lsl_stop.__init__(self, name, experiment, script)		
		qtautoplugin.__init__(self, __file__)

	
