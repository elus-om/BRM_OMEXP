# OMEXP plugins

We introduce a set of plugins for OpenSesame that enable the implementation of behavioural and cognitive tasks involving advanced audio playback.
For clarity we refer to the OpenSesame platform enhanced with these plugins as the Oticon Medical Experiment Platform (OMEXP).

The list of plugins added to OpenSesame to constitute OMEXP are summarized below and described in details in the following section.
- Audio Mixer.
- Calibration.
- LSL start.
- LSL message.
- LSL stop.
- Adaptive init.
- Adaptive next.
- 
***
## General information

The additional plugins were developed by Eleonora Sulas and Pierre-Yves Hasan. 

It is published under the GNU General Public License (version 3).
However, two of the libraries implemented duringthe development of the new plugins are Oticon Medical Copyrighted.

If you use any of the additional plugins in your published research, we kindly ask that you cite it as follows:

_Streamlining Experiment Design in Cognitive Hearing Science using OpenSesame_

***
## Installation

The plugins are available on the Python Package Index. To install the release, please run the following commands in Opensesame's debug window:

```python
import pip
pip.main(['install','opensesame-plugin-mousetrap'])
```

***

## Validation

The work presented in _Streamlining Experiment Design in Cognitive Hearing Science using OpenSesame_ showed and validated the OMEXP playback capabilities.

***
## Example
We exemplify the use of this extended OpenSesame platform with an implementation of the 3-alternative forced choice amplitude modulation detection test.

***
## Acknowledgments