#-*- coding:utf-8 -*-
from libopensesame.py3compat import *
from libopensesame import debug
from libopensesame.exceptions import osexception
from libopensesame import item
from libopensesame.oslogging import oslogger
from libqtopensesame.items.qtautoplugin import qtautoplugin
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'adaptive_init', category=u'item')

class adaptive_next(item.item):
    """
    desc:
        Setup comunication and interface with pupil service and pupil capture.
    """
    description = u'Starts the adaptive method procedure.'

    def reset(self):
        """
        desc:
            Initialize plug-in.
        """
        self.var.target_result = u''


    def run(self):
        """
        desc:
            Run the item.
        """
        # Get the answer variable value and compute next value
        resp = self.var.get(self.var.target_result)
        adapt = self.experiment.adaptive
        # Weird behaviour, if boolean, it is replaced by yes or no
        if resp == 'yes':
            resp = True
        elif resp == 'no':
            resp = False

        adapt.next_value(resp)

        # Check if routine should be stopped
        if adapt.stop:
            self.experiment.var.set('stop', 1)
                  
class qtadaptive_next(adaptive_next, qtautoplugin):
    """GUI controls"""
    description = _(u'Starts the adaptive method procedure.')
    help_url = u''
    lazy_init = False
    def __init__(self, name, experiment, string=None):
        """
        Constructor

        Arguments:
        name        --    The name of the item.
        experiment    --    The experiment instance.

        Keyword arguments:
        string        --    A definition string. (default=None)
        """
        adaptive_next.__init__(self, name, experiment, string)
        qtautoplugin.__init__(self, plugin_file = __file__)

    def edit_widget(self):
        super().auto_edit_widget()

    def apply_edit_changes(self):
        """
        Apply changes from the script to the UI
        """
        super(qtautoplugin, self).apply_edit_changes()