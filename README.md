# OMEXP plugins

We introduce a set of plugins for OpenSesame that enable the implementation of behavioural and cognitive tasks involving advanced audio playback.
For clarity we refer to the OpenSesame platform enhanced with these plugins as the Oticon Medical Experiment Platform (OMEXP).

The list of plugins added to OpenSesame to constitute OMEXP are summarized below and described in details in the following section.
- LSL start: initializes the Lab Streaming Layer (LSL) protocol (see https://labstreaminglayer.readthedocs.io/index.html) and starts the recording. It allows to select the folder in which the recording will be saved and the filename under which the data should be saved. 
- LSL message: allows to timestamp an acquisition stream synchronized with the recording. It is useful, for example, to save the exact instant when a stimulus is shown to the user. The recordings are synchronized and saved in an XDF file format (Extensible Data Format), see https://labstreaminglayer.readthedocs.io/info/intro.html.  
- LSL stop: stops and saves the recordings.
- Adaptive init: implements an adaptive method for psychoacoustic experiments, specifically the ‘transformed up-down’ methodology implements the procedure introduce by Levitt in 1971. It can specify parameters of the up-down procedure, such as the
step size, the number of reversals or trials after which the step-size change may occur, the variable holding the tracked value and its starting
value.
- Adaptive next: changes the tracked variable according to the settings specified in the adaptive routine init plugin.
- Audio Mixer: allows to play sounds in different audio channels with different levels. for example, this plugin is particularly useful for multi-loudspeaker studies, with for example 5 loudspeakers (0°, 90°, 150°, 210°, 270°), where the front speaker is to be assigned with a target sound, and side speakers are speech maskers and back speakers are speech masker and noise, and you want to set different dB level for each channel. In addition, LSL markers are created within the Audio Mixer plugin, at the beginning and at the end of the audio sounds sequence.
- Calibration: enables to do the audio calibration of the setup and must be placed before the use of the Mixer plugin.

***
## General information

The code is published under the GNU General Public License (version 3).
However, the standalone libraries are Oticon Medical Copyrighted.



***
## Installation

We introduce a set of plugins for OpenSesame. For installing Opensesame: https://github.com/open-cogsci/OpenSesame/releases?page=2 .
The plugins are compatible with Opensesame 3.2.7 and 3.2.8 based on python 3.

The plugins are available on the Python Package Index. To install the release, please open Opensesame (run as administrator) and  run the following commands in Opensesame's debug window:

```python
import pip
pip.main(['install','opensesame-plugin-omexp'])
```

or from the command window (run as administrator) from the Opensesame folder:

```python
python.exe -m pip install opensesame-plugin-omexp
```

Opensesame needs to be restarted to see the plugins.

The code is available in github: (https://github.com/elus-om/BRM_OMEXP)

***

## Validation


***
## Example

We exemplify the use of this extended OpenSesame platform with an implementation of the 3-alternative forced choice amplitude modulation detection test. The test is shared in the example folder in GitHub.

To be able to record from Lab Streaming Layer library, your should run the related App. Regarding the 3 AFC amplitude modulation detection test, you need to download and run the App AudioCaptureWin (https://github.com/labstreaminglayer/App-AudioCapture). 

The data will be saved in a XDF file the in the specified path chosen in the LSL record plugin. 

***

## Acknowledgement

OMEXP plugins extends OpenSesame platform developed by the development team led by Sebastiaan Mathôt. 

