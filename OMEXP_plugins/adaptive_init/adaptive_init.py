#-*- coding:utf-8 -*-
from libopensesame.py3compat import *
from libopensesame import debug
from libopensesame.exceptions import osexception
from libopensesame import item
from qtpy import QtWidgets, QtGui, QtCore
from libopensesame.oslogging import oslogger
from libqtopensesame.items.qtautoplugin import qtautoplugin
from libqtopensesame.misc.translate import translation_context
from numpy import argsort
_ = translation_context(u'adaptive_init', category=u'item')

class adaptive_init(item.item):
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
        # Adaptive method
        self.var.up_value = 1
        self.var.down_value = 1
        self.var.target_up_down = u'50 %'

        # Step size parameters
        self.var.step_value_start = 4
        self.var.step_value_end = '2'
        self.var.step_value_change = True
        self.var.step_change_trial = '5'
        self.var.change_modality = u'Trials'

        # Tracked variable
        self.var.target_variable = ''
        self.var.start_track = ''

    def run(self):
        """
        desc:
            Run the item.
        """

        # Adapt target
        target = [self.var.up_value, self.var.down_value]
        
        # Create step size
        step = [self.var.step_value_start]
        if self.var.step_value_change in [True, 'yes']: # OS notation
            steps = str(self.var.step_value_end).split(";")
            steps = [float(v) for v in steps if v] # Remove empty values
            change = str(self.var.step_change_trial).split(";")
            change = [int(v) for v in change if v] # Remove empty values
            
            if len(change) != len(steps):
                raise osexception('Different number of steps and values')
            
            temp = [None] * (len(change) + len(steps))
            temp[::2] = steps
            temp[1::2] = change 
            step.extend(temp)


        # Create the object
        self.experiment.adaptive = Adaptive_object(
            self.experiment,
            target,
            step,
            self.var.target_variable,
            self.var.change_modality,
            )

        # Create the tracked variable
        self.experiment.var.set(
            self.var.target_variable, 
            self.var.start_track)

class qtadaptive_init(adaptive_init, qtautoplugin):
    """GUI controls"""
    description = _(u'Starts the adaptive method procedure.')
    help_url = u''
    lazy_init = True

    def __init__(self, name, experiment, string=None):
        """
        Constructor

        Arguments:
        name        --    The name of the item.
        experiment    --    The experiment instance.

        Keyword arguments:
        string        --    A definition string. (default=None)
        """

        adaptive_init.__init__(self, name, experiment, string)
        qtautoplugin.__init__(self, plugin_file = __file__)

    def add_control_line(self, label, widgets, tooltip=None, min_width=200,
        info=None):
        """
        desc:
            Adds a multiple generic control QWidget on the same line.

        arguments:
            label:    A text label that will be on the left of the first widget.
            widgets:    QWidgets to be put in line.

        keywords:
            tooltip:    A tooltip text.
            min_width:    A minimum width for the widget.
            info:        Additional info, to be presented to the right of the
                        control.
        """
        row = self.edit_grid.rowCount()
        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        hbox.setSpacing(12)
        label = QtWidgets.QLabel(label)
        #label.setAlignment(self.edit_grid.labelAlignment())
        for wid in widgets:
            #if tooltip is not None:
            #    try:
            #        wid.setToolTip(tooltip)
            #    except:
            #        pass
            if isinstance(min_width, int):
                wid.setMinimumWidth(min_width)
            hbox.addWidget(wid)
            self.set_focus_widget(wid)
        container = QtWidgets.QWidget()
        container.setLayout(hbox)
        self.edit_grid.insertRow(row, label, container)

    def init_edit_widget(self):

        super().init_edit_widget()
        # Link does not work, force
        # self.var.target_HINTPro = u'50 %'
        # self.update_script()

        # Create the different spinbox for stepsizes.
        self.spinbox_step_start = qtautoplugin.add_doublespinbox_control(
            self,
            u'step_value_start',
            u'Initial step size\n(tracked variable is decreased by this amount)',
            -100000,
            100000,
            tooltip = u'The step to apply to the tracked variable.'
            )

        self.edit_step_end = qtautoplugin.add_line_edit_control(
            self,
            u'step_value_end',
            u'',
            tooltip = u'The step to apply to the tracked variable.'
            )
        
        
        # Reorganize layout for many widgets on the same line
        self.add_control_line(
            u'Adaptive Method:\nTransformed up-down, Levitt (1971)', 
            [
                QtWidgets.QLabel(
                    u'Number of incorrect Trial/Reversal(s)\nbefore step up'
                    ),
                self.spinbox_trials_up, 
                QtWidgets.QLabel(u'Number of correct Trial/Reversal(s)\nbefore step down'),
                self.spinbox_trials_down
                ],
            min_width= 50
            )
        
        self.add_control_line(
            u'Resulting target on the psychometric curve',
            [
                self.edit_target_up_down,
                ],
            min_width = 50 
            )
        self.edit_target_up_down.setDisabled(True)
              
        
        self.add_control_line(
            u'Apply a stepsize change',
            [
                self.checkbox_step_change,
                QtWidgets.QLabel(
                    u'Number of Trials/Reversals for which\nchange occurs separated by ";"'),
                self.edit_step_change,
                QtWidgets.QLabel(u'New step size\nseparated by ";"'),
                self.edit_step_end
                ],
            min_width = 50 
            )
        
           
        # Make it prettier
        self.edit_grid.removeItem(self.edit_grid.takeAt(0)) # spinbox_trials_down
        self.edit_grid.removeItem(self.edit_grid.takeAt(0))
        self.edit_grid.removeItem(self.edit_grid.takeAt(0))
        self.edit_grid.removeItem(self.edit_grid.takeAt(0))
        self.edit_grid.removeItem(self.edit_grid.takeAt(0))
        
        
        
        # Add spacers
        self.edit_grid.insertRow(
            3, ' ',QtWidgets.QSpacerItem(0, 100).widget())
        self.edit_grid.insertRow(
            6, ' ',QtWidgets.QSpacerItem(0, 100).widget())
        self.edit_grid.insertRow(
            9, ' ',QtWidgets.QSpacerItem(0, 100).widget())

        super().auto_edit_widget()
        self.calc_target_up_down()

    def edit_widget(self):
        super().auto_edit_widget()
        self.calc_target_up_down()

    def apply_edit_changes(self):
        """
        Apply changes from the script to the UI
        """
        super(qtautoplugin, self).apply_edit_changes()
        self.calc_target_up_down()

    def calc_target_up_down(self):
        """
        desc:
            Run the item.
        """
        if self.var.up_value >= self.var.down_value:
            val = 1 - 0.5**(self.var.down_value / self.var.up_value)
            self.var.target_up_down = str(round(val * 100, 1)) + ' %'
        else:
            val = 0.5**(self.var.up_value / self.var.down_value)
            self.var.target_up_down = str(round(val * 100, 1)) + ' %'
        
        self.edit_target_up_down.setText(self.var.target_up_down)

class Adaptive_object(object):
    def __init__(self, experiment, target, stepsizes, tracked_variable,
        modality):
        """"Adaptive object to do the computation of the adaptive method.
        
        Arguments:
            method {string} -- Either 'Adaptive' or 'HINTPro', the two different methods implemented.
            target {list} -- In the case of the the adaptive it is a list of up and down vlues, for the HINTPro it is the target score in a list.
            stepsizes {list} -- The different step sizes, if it does not change then it is a list of 1 float, otherwise it is a list with 3 numbers: [initial step size, end step size, trial for it changes].
            tracked_variable: {str} -- The string representing the tracked variable
            modality: {str} -- Either 'Trials' or 'Reversals'
            stop_condition: {dic} -- Dictionnary containing the condition to stop the tracking or not.
        """
        self.experiment = experiment
        self.target = target
        self.stepsizes = stepsizes
        self.current_step = self.stepsizes[0] 

        self.modality = modality
        if modality == 'Trials':
            self.trial = 0
        else:
            # The first trial will be a reversal by design, we need to
            # not consider it
            self.trial = -1
            self.direction = 0

        self.tracked_variable = tracked_variable
        
        self.memory = []

        #self.stop_condition = stop_condition
        self.counter_wrong = 0
        self.counter_correct = 0
        self.stop = False

    def next_value(self, result):
        # Compute the next value based on score
        if result not in [True, False]:
            raise osexception('The result is not 0 or 1. ' + 
            'Check the adaptive_next plugin.')
        self.memory.append(result)
        correct_answer = self.memory.count(True)
        wrong_answer = len(self.memory) - correct_answer

        # Check if one of the condition of the up-down has been reached
        if wrong_answer == self.target[0]:
            self.memory = []
            sign = 1         

        elif correct_answer == self.target[1]:
            self.memory = []
            sign = -1
        else:
            # We didn't reach the change yet
            # We do not increase the trial change because we consider value changes.
            return
        
        # Update the trial and stepsize, change the stepsize variable to stop loop
        if self.modality == 'Reversals':
            # Compute direction
            if sign > 0:
                new_direction = 1
            else:
                new_direction = -1
            # Update if necessary
            if self.direction != new_direction:
                self.trial += 1
                self.direction = new_direction 
        else: 
            self.trial += 1

        # Check if step size should vary
        if len(self.stepsizes) > 1:
            print(self.trial, self.stepsizes[2])
            if self.trial >= self.stepsizes[2]:
                self.current_step = self.stepsizes[1]
                
                # Changing stepsize, removing previous steps
                self.stepsizes.pop(1)
                self.stepsizes.pop(1)
                
        # Get tracked variable        
        tracked = self.experiment.var.get(self.tracked_variable)
        
        self.experiment.var.set(
            self.tracked_variable, 
            tracked + sign * self.current_step
            )
                    
    def get_tracked_variable(self):
        return self.tracked_variable
