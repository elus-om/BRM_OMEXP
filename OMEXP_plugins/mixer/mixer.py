#-*- coding:utf-8 -*-
from libopensesame.py3compat import *
from libopensesame import item
from qtpy import QtWidgets, QtGui, QtCore
import os
import sys
from libqtopensesame._input.pool_select import pool_select
from libqtopensesame.items.qtplugin import qtplugin
from libqtopensesame.misc.translate import translation_context
from libopensesame.exceptions import osexception
import share.opensesame_plugins.mixer.libmixer as mx
from share.opensesame_plugins.mixer.libqt import LimistDelegate
_ = translation_context(u'mixer', category=u'item')

class mixer(item.item):
    """
    desc:
        A plug-in to play different sounds in multiple channels as well as different timings.
    """

    description = u'Play sounds in different channels with different' \
        + 'levels and starting times'

    def reset(self):
        """
        desc:
            Initialize plug-in.
        """

        # HARDCODED RE MAX FOR CALIBRATION 
        self.dB_re_max = 105

        # Default values for the plugin
        self.var.dB_max_out = 80 # No sound can exceed this value

        # Table parameters
        self.var.sound          = u''
        self.var.channels       = u''
        self.var.level          = u'0'
        self.var.message_start  = u''
        self.var.message_end    = u''
        self.tabvar             = ['sound', 'channels', 'level']
        self.var.fast           = False

    def prepare(self):

        """
        desc:
            Prepare the item.
        """
        
        # item.item.prepare(self)
        # Unpack values for the player    
        sep = ','
        channels_list = mx.string_to_list(self.var.channels, '-', to_num = False)
        channels = []
        for l in channels_list:
            channels.append(mx.string_to_list(l, sep, to_num = 'int'))
        fname = mx.string_to_list(self.var.sound, sep, to_num = False)
        
        fname = [self.experiment.pool[file] for file in fname]

        # Check if existing stream
        if hasattr(self.experiment, u'mixer_stream'):
            stream = self.experiment.mixer_stream
            # device = self.experiment.complex_sound_stream.device
            try:
                stream.active
            except mx.rtmixer._sd.PortAudioError:
                stream = None
        else:
            stream = None

        # Convert the different parameters to lists from the script
        levels = mx.string_to_list(str(self.var.level), sep, to_num = False)

        # Level can be stored in a variable, so account for that
        for (ix, lv) in enumerate(levels):
            if '[' in levels[ix]:
                levels[ix] = levels[ix].strip('[]')
                levels[ix] = self.experiment.get(levels[ix])
            levels[ix] = round(float(levels[ix]), 1)

        details = {}
        val = {'channels': channels, 'level' : levels}
        
        # create dictionnary for the player
        for (ix, idn) in enumerate(fname):
            details[idn] = val.copy() # Otherwise same reference and bug.
            for (keys, _1) in val.items():
                if type(val[keys]) is int:
                    details[idn][keys] = val[keys]
                else:
                    details[idn][keys] = val[keys][ix]

        message = [self.var.message_start, self.var.message_end]
        # Init the player
        self.player = mx.player(self.dB_re_max, 
                                details, 
                                stream = stream,
                                message = message)

        self.player.prepare()   
        smallblock = 0 if self.var.fast == 'no' else 1
        if self.experiment.has('LSL'):
            self.player.setLSL(self.experiment.get('LSL'))

    def run(self):

        """
        desc:
            Run the item.
        """
        self.set_item_onset()

        try:
            self.player.calibration = self.experiment.var.calibration
        except:
            self.player.calibration = []
        
        smallblock = 0 if self.var.fast == 'no' else 1
        self.player.play(smallblock = smallblock)
        
        # Set the stream once created.
        self.experiment.mixer_stream = self.player.get_stream()

class qtmixer(mixer, qtplugin):

    """GUI controls"""
    description = _(u'Play sounds in different channels with different' \
        + ' levels and starting times')
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
        
        mixer.__init__(self, name, experiment, string)
        qtplugin.__init__(self, plugin_file = __file__)
        
        self.tabdefval = [u'', u'', u'0']
        
    def init_edit_widget(self):

        """See qtitem.
        Builds the UI.
        """
        super(qtplugin, self).init_edit_widget(False)
        
        # Maximum level + device selection
        validator = QtGui.QIntValidator(0, 105)
        self.edit_dB_max_out = self.add_line_edit_control(
            u'dB_max_out', _(u'Maximum level'), 
            validator = validator
            )
        
        self.edit_message_start = self.add_line_edit_control(
            u'message_start', _(u'Message to send before the signal')
        )
        
        self.edit_message_end = self.add_line_edit_control(
            u'message_end', _(u'Message to send after the signal')
        )
        
        self.checkbox_fast = self.add_checkbox_control(
            u'fast', _('Use a more precise timing for LSL')
        )

        #self.button_asio.size = QtCore.QSize(50, 50)
        self.create_source_table()
        self.table.cellChanged.connect(self.apply_table_changes) 
        # update script after a change

    def add_table_control(self, row, column, header = u'', vars = None):

        """
        desc:
            Adds a QTableWidget control that is linked to a variable.

        arguments:
            row:                  Number of rows.
            column:             Number of columns.
            column names:    Name to display for the columns
        """

        table = QtWidgets.QTableWidget(row, column)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.horizontalHeader().setStyleSheet("color:black;"
                                               "background-color: lightblue;"
                                               "border-bottom: 1px solid grey")
        table.setHorizontalHeaderLabels(header)
        self.edit_vbox.addWidget(table) # Enable completion of the bottom of the window
        self.vars = vars
        return table

    def create_source_table(self):
        # Section for file selections
        self.table = self.add_table_control(0, 3, 
                                            header= [_(u'Sound'), (u'Channels'),
                                                      _(u'Level [dB]')]
                                            )
        # create delegate
        self.delegate = LimistDelegate(self.table, self.var.dB_max_out) 
        self.table.setItemDelegate(self.delegate)  # set delegate

        # self.add_row()
        # self.table.removeRow(0)

        # Add sound button
        append = QtWidgets.QPushButton(self.table)
        append.setIcon(self.main_window.theme.qicon(u'list-add'))
        append.setFlat(True)
        append.adjustSize()
        
        append.clicked.connect(self.add_row)

        # Context menu to add or remove row
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.popup)

        # Cosmetics
        head = self.table.horizontalHeader()
        head.setStyleSheet("QHeaderView::section{"
                            "border-top:0px solid #D8D8D8;"
                            "border-left:0px solid #D8D8D8;"
                            "border-right:1px solid #D8D8D8;"
                            "border-bottom: 1px solid #D8D8D8;"
                            "background-color: #e1e1e1;"
                            "padding:0px;"
                        "}"
                        "QTableCornerButton::section{"
                            "border-top:0px solid #D8D8D8;"
                            "border-left:0px solid #D8D8D8;"
                            "border-right:1px solid #D8D8D8;"
                            "border-bottom: 1px solid #D8D8D8;"
                            "background-color:white;"
                        "}"
                        )
    # @QtCore.Slot()
    def add_row(self, emit = True):
        rc = self.table.rowCount()
        self.table.insertRow(rc)
        # Init
        _edit = pool_select(self.main_window)
        self.table.setCellWidget(rc, 0, _edit)
        _edit.editingFinished.connect(lambda: self.apply_table_changes(rc, 0))
        _edit.textEdited.connect(lambda: self.apply_table_changes(rc, 0))
        if emit:
            _edit.editingFinished.emit()
        self.table.setItem(rc, 0, QtWidgets.QTableWidgetItem(''))
        self.table.setItem(rc, 1, QtWidgets.QTableWidgetItem(''))
        self.table.setItem(rc, 2, QtWidgets.QTableWidgetItem(u'0'))

    # @QtCore.Slot()
    def popup(self, pos):
        row_click = self.table.indexAt(pos).row()
        menu = QtWidgets.QMenu()
        delAction = menu.addAction("Delete source")
        adAction = menu.addAction("Add source")
        action = menu.exec_(self.table.mapToGlobal(pos))
        if action == delAction:
            if self.table.rowCount() >1:
                self.table.removeRow(row_click)
                self.apply_table_changes(row_click, delete = True)
        if action == adAction:
            self.add_row()

    def edit_widget(self):
        self.table.blockSignals(True)
        # Signal blocked, now let's verify the script for the table
        flag = []
        # For each of the column of the table we need to update
        for ixt, var in enumerate(self.tabvar):
            script_var = self.var.get(var)
            sep = ','
            # DIfferent separator for the channels
            if var == 'channels': 
                sep = '-'
            script_var = mx.string_to_list(str(script_var), sep, to_num = False)

            rc = self.table.rowCount()
            for ix, el in enumerate(script_var):
                # A new row appeared, we need to change the other variable
                if ix >= rc:
                    self.add_row(emit = False)
                    flag.append(ixt)
                    rc = self.table.rowCount() # New value after adding a row
                elif ix == rc-1 and len(flag) > 0: 
                # We have added a row before but no need to add other rows
                    flag.append(ixt)
                if var == 'sound':
                    self.table.cellWidget(ix, ixt).setText(el)
                else:     
                    self.table.setItem(ix, ixt, QtWidgets.QTableWidgetItem(el))

        # We added a row, meed to vhange the variable
        if len(flag) > 0:
            for ixt in range(3):
                if ixt not in flag:
                    var = self.tabvar[ixt]
                    script_var = self.var.get(var)
                    sep = ','
                    if var == 'channels': 
                        sep = '-'
                    script_var= str(script_var) + sep + self.tabdefval[ixt]
                    self.var.set(var, script_var)
            self.update_script()
            self.set_clean()
        self.table.blockSignals(False)
        self.auto_edit_widget()

        self.header.refresh()
        if len(flag) > 0: # Just force it to be updated
            self.edit_widget()

    def apply_edit_changes(self):
        """
        Apply changes from the script to the UI
        """
        self.delegate.max_db = int(self.edit_dB_max_out.text())
        super(qtplugin, self).apply_edit_changes()

    def apply_table_changes(self, *args, **kwargs):
        '''Apply change from UI to script'''

        # Pass a key word if row deleted
        if len(kwargs) == 0:
            ro = args[0]
            col = args[1]
            var = self.tabvar[col] 
            current_var = self.var.get(var)
            sep = ','
            if col == 1: 
                sep = '-'
            # Got the var, to list, add to it or change
            current_list = mx.string_to_list(str(current_var), sep, to_num = False)
            if col == 0:
                if len(current_list) == ro:
                    current_list.append(self.table.cellWidget(ro, col).text())
                else:
                    current_list[ro] = self.table.cellWidget(ro, col).text()
            else:
                if len(current_list) == ro:
                    current_list.append(self.table.item(ro, col).text())
                else:
                    current_list[ro] = self.table.item(ro, col).text()
            # Back to str and store
            new_var =  mx.list_to_string(current_list, sep)
            self.var.set(var, new_var)

        # This case is if there a deletion in the row
        else:
            ro, = args
            for var in self.tabvar: # For each var, update the model from view
                current_var = self.var.get(var)
                sep = ','
                if var == 'channels': 
                    sep = '-'
                # Got the var, to list, add to it or change
                current_list = mx.string_to_list(str(current_var),
                                             sep, to_num = False)
                del current_list[ro]
                # Back to str and store
                new_var =  mx.list_to_string(current_list, sep)
                self.var.set(var, new_var)
            

            # reassign functions and change the value at the run time
            def makeCall(val):
                return lambda: self.apply_table_changes(val, 0)
            # https://stackoverflow.com/questions/19510860/qtcore-qobject-connect-in-a-loop-only-affects-the-last-instance

            for r in range(0, self.table.rowCount()):
                self.table.cellWidget(r, 0).disconnect()
                self.table.cellWidget(r, 0).editingFinished.connect(
                    makeCall(r))
                self.table.cellWidget(r, 0).textEdited.connect(
                    makeCall(r))

        
        # update script
        self.update_script()
        self.set_clean()
        return True   
