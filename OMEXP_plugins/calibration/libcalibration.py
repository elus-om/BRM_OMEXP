'''
* All Rights Reserved.
* 
* NOTICE: All information contained herein is, and remains
* the property of Oticon Medical A/S,if any.
* The intellectual and technical concepts contained
* herein are proprietary to Oticon Medical A/S
* and may be covered by U.S. and other Patents (e.g. EP, CN or AU patents),
* patents in process, and are protected by trade secret or copyright law.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Oticon Medical.
*
* Oticon Medical A/S, hereby claims all copyright interest in the program “libcalibration.py”.
*
* Copyright,2020, Oticon Medical A/S.
*
'''

from qtpy import QtWidgets, QtGui, QtCore 
import numpy as np
import os
import share.opensesame_plugins.mixer.libmixer as mx

class CalibrationApp():
    """
    CalibrationApp, a window to do the calibration.
    
    Returns
    -------
    ``list``
        The list of gains to apply to the output to ensure the correct 
        calibration.
    """    
    def __init__(self, filename = None):
        #self.app = QtWidgets.QApplication([])
        #self.app.setStyle('Fusion')
        self.container = QtWidgets.QWidget()
        self.container.setGeometry(500, 200, 800, 400)

        self.outputs = mx.get_max_output_channels()
        self.calibration = np.zeros([self.outputs])
        self.level = 70
        self.selected_channel = 1     
        
        self.dirname = os.path.dirname(__file__)
        if (filename is None):
            raise Exception("No filename to do the calibration.")
        else:
            self.filename = filename
        self.create_GUI()
        self.container.activateWindow() # To make window appear on top
    
    def create_GUI(self):
        """create_GUI:

        Create the whole graphical aspects and links the controls to callbacks.
        """
        # Layouts
        self.v_layout = QtWidgets.QVBoxLayout(self.container)

        # Start first row, level, Play/Stop, Done 
        # Then push button goup for sources
        # Then spin box for correction
        self.row1 = QtWidgets.QHBoxLayout()
        self.row2 = QtWidgets.QHBoxLayout()
        self.row3 = QtWidgets.QHBoxLayout()

        # Create the level control
        self.level_spin = QtWidgets.QSpinBox()
        self.level_spin.setValue(self.level)
        self.level_spin.setRange(0, 90)
        font = self.level_spin.font()
        font.setPointSize(32)
        self.level_spin.setFont(font)
        self.level_spin.valueChanged.connect(self.callback_level_changed)
        self.level_spin.setMinimumHeight(70)

        # Play/Stop button
        self.play_stop_button = QtWidgets.QPushButton()
        # Load the different icons
        path_play = os.path.join(self.dirname, 'play.png')
        pixmap_play = QtGui.QPixmap(path_play)

        path_pause = os.path.join(self.dirname, 'pause.png')
        pixmap_pause = QtGui.QPixmap(path_pause)

        self.play_stop_ico = [
            QtGui.QIcon(pixmap_play), 
            QtGui.QIcon(pixmap_pause)
            ]
        
        self.play_stop_button.setIcon(self.play_stop_ico[0])
        self.play_stop_button.setCheckable(True)
        font = self.play_stop_button.font()
        font.setPointSize(36)
        self.play_stop_button.setFont(font)
        self.play_stop_button.setMinimumSize(QtCore.QSize(100, 70))
        opt = self.play_stop_button.setIconSize(QtCore.QSize(62, 62))
        self.play_stop_button.clicked.connect(self.callback_play_stop)

        # Done button
        self.done_button = QtWidgets.QPushButton('Done')
        font = self.done_button.font()
        font.setPointSize(30)
        self.done_button.setFont(font)
        self.done_button.clicked.connect(self.quit)
        self.done_button.setMinimumHeight(70)

        # Text
        self.text = QtWidgets.QLabel('Calibration: Paused')
        font = self.text.font()
        font.setPointSize(36)
        self.text.setFont(font)
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        # Create the push buttons and corresponding spin boxes
        self.button_group = QtWidgets.QButtonGroup()
        self.buttons = []
        self.calibration_spin = []
        for num in range(self.outputs):
            # Create button for sources to play
            self.buttons.append(QtWidgets.QPushButton('Channel ' + str(num+1)))
            self.button_group.addButton(self.buttons[num], id = num+1) 
            self.buttons[num].setCheckable(True)
            font = self.buttons[num].font()
            font.setPointSize(20)
            self.buttons[num].setFont(font)
            self.row2.addWidget(self.buttons[num])
            self.buttons[0].setChecked(True)

            # Create corresponding edit to control volume
            self.calibration_spin.append(QtWidgets.QDoubleSpinBox())
            self.calibration_spin[num].setSingleStep(0.1)
            self.calibration_spin[num].setDecimals(1)
            self.calibration_spin[num].setRange(-50,15)
            font = self.calibration_spin[num].font()
            font.setPointSize(16)
            self.calibration_spin[num].setFont(font)
            self.calibration_spin[num].valueChanged.connect(
                self.callback_calibration_changed)
            self.row3.addWidget(self.calibration_spin[num])

        self.button_group.buttonClicked.connect(self.callback_button_group)

        # Organize position
        self.row1.addWidget(self.level_spin)
        self.row1.addWidget(self.play_stop_button)
        self.row1.addStretch(1)
        self.row1.addWidget(self.done_button)
        self.row1.addStrut(100)

        self.v_layout.addLayout(self.row1, stretch = 1)
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.text)
        self.v_layout.addStretch(1)
        self.v_layout.addLayout(self.row2)
        self.v_layout.addLayout(self.row3)

        self.get_player()

    def callback_level_changed(self):
        self.level = self.level_spin.value()
        self.changed_parameters(stop_playing = True)

    def callback_play_stop(self):
        if self.player is not None:
            self.player.start_pause()

        if self.play_stop_button.isChecked():
            self.text.setText('Calibration: Playing')
            self.play_stop_button.setIcon(self.play_stop_ico[1])
        else:
            self.text.setText('Calibration: Paused')
            self.play_stop_button.setIcon(self.play_stop_ico[0])

    def callback_button_group(self):
        # We changed the source, let's stop the stream and restart it
        self.selected_channel = self.button_group.checkedId()
        self.changed_parameters(stop_playing = False)

    def callback_calibration_changed(self):
        for num in range(self.outputs):
            self.calibration[num] = self.calibration_spin[num].value()
        self.changed_parameters()

    def changed_parameters(self, stop_playing = True):
        if self.play_stop_button.isChecked():
            self.play_stop_button.setChecked(False)
            self.callback_play_stop()
            
            self.get_player()
            if not stop_playing:
                self.play_stop_button.setChecked(True)
                self.callback_play_stop()
                
        else:
            self.get_player()

    def get_player(self):
        if 'player' in dir(self):
            self.player.loop = False
            self.player.cleanup()
            
        if isinstance(self.calibration, np.ndarray):
            self.calibration = self.calibration.tolist() 

        self.player_dict = {
            self.filename : {
                'channels': [self.selected_channel],
                'level': self.level
                }
                }
        try:
            stream = self.player.get_stream()
        except AttributeError:
            stream = None

        self.player = mx.player(
            105, 
            self.player_dict, 
            loop = True, 
            stream = stream, 
            calibration = self.calibration
            )
        self.player.prepare()

        # Start player but immediatly stop it
        self.player.play()
        self.player.start_pause()

    def run(self):
        self.container.show()
        #self.app.exec_()
        # Just create an event loop together with Qt event loop.
        timer = QtCore.QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)       

        return self.calibration

    def quit(self):
        if self.play_stop_button.isChecked():
            self.player.loop = False
            self.player.start_pause()
        
        if 'player' in dir(self):
            self.player.loop = False
            self.player.cleanup()
        self.container.close()
        #self.app.quit()

if __name__ == '__main__':

    a = CalibrationApp('white_noise.wav')
    ret = a.run()
    print(ret)