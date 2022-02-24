#-*- coding:utf-8 -*-
import share.opensesame_plugins.lsl_start.liblsl as lblsl
import numpy as np
from libopensesame.py3compat import *
from libopensesame.item import item
from libqtopensesame.items.qtautoplugin import qtautoplugin
import os
class lsl_start(item):     

    def reset(self):
        # available also in the OS version of OMEXP
        self.var.keyboard_checkbox = 'no'  
        self.var.audiocapturewin_checkbox = 'no'  
        self.var.mouse_checkbox = 'no'  
        self.var.Logger_checkbox = 'no' 
        self.var.pupillo_checkbox = 'no'  
        self.var.recording_path = 'C:\\Users\\Public\\OMEXP\\LSL'
        self.var.folder_name = 'RecordingLSL_0'          
     
    def prepare(self):
        """
        desc:
            Create the Logger Stream Outlet 
            Resolve the availabel Stream Outlet
        """
        LSL= lblsl.LSL_session()        
        ResolvedNames,ResolvedHostname = LSL.get_ResolvedNames() 
                   
        
        # get only the streams the user wants
        DesiredInputsName = []
        DesiredInputsHostname = []
        # keyboard       
        if self.var.keyboard_checkbox=='yes':
            temp='Keyboard'            
            if temp in ResolvedNames:
                DesiredInputsName.append('Keyboard')
                DesiredInputsHostname.append(ResolvedHostname[ResolvedNames.index(temp)])
            else:
                print("ERROR: Keyboard software was not opened, it will not be recorded")
        
        # Audio           
        if self.var.audiocapturewin_checkbox=='yes':
            temp='AudioCaptureWin'
            if temp in ResolvedNames:
                DesiredInputsName.append('AudioCaptureWin')
                DesiredInputsHostname.append(ResolvedHostname[ResolvedNames.index(temp)])
            else:
                print("ERROR: AudioCaptureWin software was not opened, it will not be recorded") 

        # Mouse
        if self.var.mouse_checkbox=='yes':
            temp='MouseButtons'
            if temp in ResolvedNames:
                DesiredInputsName.append('MouseButtons')
                DesiredInputsHostname.append(ResolvedHostname[ResolvedNames.index(temp)])
                temp= 'MousePosition'
                if temp in ResolvedNames:
                    DesiredInputsName.append('MousePosition')
                    DesiredInputsHostname.append(ResolvedHostname[ResolvedNames.index(temp)])
            else:
                print("ERROR: Mouse software was not opened, it will not be recorded") 

        # Pupil Labs 
        if self.var.pupillo_checkbox=='yes':
            temp='Tobii'            
            if temp in ResolvedNames:
                DesiredInputsName.append('Tobii')
                DesiredInputsHostname.append(ResolvedHostname[ResolvedNames.index(temp)])
            else:
                print("ERROR: Pupil Labs software was not opened, it will not be recorded")

        # logger                
        if self.var.Logger_checkbox=='yes':
            temp='MyMarkerStream'
            if temp in ResolvedNames:
                DesiredInputsName.append('MyMarkerStream')
                DesiredInputsHostname.append(ResolvedHostname[ResolvedNames.index(temp)])
            else:
                print("ERROR: Logger stream was not opened, it will not be recorded") 

        # Adding to the notifiers for the mixer plugin
        if hasattr(self.experiment, u'notifiers'):
            self.experiment.var.notifiers.add(LSL)
        else:
            self.experiment.var.notifiers = [LSL]
                    
        """ Start recording """    
        LSL.init_session(DesiredInputsName,DesiredInputsHostname,self.var.folder_name,self.var.recording_path)
        LSL.start_session()
        self.experiment.set("LSL",LSL)


class qtlsl_start(lsl_start, qtautoplugin):

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
		lsl_start.__init__(self, name, experiment, script)		
		qtautoplugin.__init__(self, __file__)
