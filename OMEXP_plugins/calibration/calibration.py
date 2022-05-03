#-*- coding:utf-8 -*-

from libopensesame.py3compat import *
from libopensesame import debug
from libopensesame import item, widgets
from qtpy import QtWidgets, QtGui, QtCore
import os
import share.opensesame_plugins.mixer.libmixer as mx
import share.opensesame_plugins.calibration.libcalibration as calib
from libqtopensesame.items.qtitem import requires_init
from libqtopensesame.items.qtplugin import qtplugin
from libqtopensesame.misc.translate import translation_context
from libopensesame.exceptions import osexception
_ = translation_context(u'calibration', category=u'item')

class calibration(item.item):
    def reset(self):
        """
        desc:
            Initialize plug-in.
        """
        self.var.calibration = []
        self.var.filename = u'white_noise.wav'

    def prepare(self):
        # Run the form        
        self.form = widgets.form(self.experiment, cols=[1,1], rows=[3,1],)

        label = widgets.label(self.form, text='Complete the Calibration first, then press Next')           
        self.form.set_widget(label, (0,0), colspan=2)  
        button = widgets.button(self.form, text='Next', frame=True, center=True)       
        self.form.set_widget(button, (0,1), colspan=2)

    def run(self):
        """
        desc:
            Run the item.
        """
        # Get file path
        file =  self.experiment.pool[self.var.filename]

        # Create app and run
        self.app = calib.CalibrationApp(filename=file)

        self.experiment.var.calibration = self.app.run()

        self.form._exec()

        
class qtcalibration(calibration, qtplugin):
    """GUI controls"""
    description = _(u'Setup the sound calibration.')
    help_url = u''
    lazy_init = False
    
    def __init__(self, name, experiment, string=None):
        """
        Constructor

        Arguments
        ---------
        name : ``string``        --    
            The name of the item.

        experiment : ``experiment``  --    The experiment instance.

        Keyword arguments
        -----------------
        ``string``        --    A definition string. (default=None)
        """
        
        dirname = os.path.dirname(__file__)
        calibration.__init__(self, name, experiment, string)
        qtplugin.__init__(self, __file__)

        noisefile = os.path.join(dirname, 'white_noise.wav')
        if u'white_noise.wav' not in self.experiment.pool:
            self.experiment.pool.add(noisefile, u'white_noise.wav')

    def init_edit_widget(self):
        super().init_edit_widget()
        # The calibration file is in the filepool, by default some white noise
        self.add_filepool_control(u'filename', _(u'Sound file'),
			info=_(u'In .ogg or .wav format'))
        

