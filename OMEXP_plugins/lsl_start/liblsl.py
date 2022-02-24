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
* Oticon Medical A/S, hereby claims all copyright interest in the program “liblsl.py”.
*
* Copyright,2020, Oticon Medical A/S.
*
'''

import liesl
import pylsl

class LSL_session(object):
    """ class LSL Session that combine the use of the pylsl and the liesl tool"""

    def __init__(self):
        ''' Init the LSL Session object'''        
        self.create_logger()
        self.resolve_streams()

    def init_session(self,DesiredInputsName,DesiredInputsHostname,folder_name,recording_path):
        """ init Session object of liesl """
        self.folder_name = folder_name
        self.recording_path = recording_path

        for k in range(len(DesiredInputsName)):
            if k==0:
                self.streamargs_session= [{'name':DesiredInputsName[k], "hostname": DesiredInputsHostname[k]}]
            else:
                self.streamargs_session= self.streamargs_session+[{'name':DesiredInputsName[k], "hostname": DesiredInputsHostname[k]}] 

        self.recording_session = liesl.Session(prefix=self.folder_name, mainfolder=self.recording_path, recorder= None, streamargs = self.streamargs_session)
    

    def resolve_streams(self):
        """ Resolve the streams """
        # get all streams on the lab network
        self.ResolvedStreams = list(pylsl.resolve_streams(1.0))
        # sort them by UID to get a reproducible order
        self.ResolvedStreams.sort(key=lambda x: x.uid())
        

    def get_ResolvedStreams(self):
        """ get Outlet Streams """
        return self.ResolvedStreams

    def get_ResolvedNames(self):
        """ get Outlet Streams names """
        # get their names
        self.ResolvedNames = [];
        self.ResolvedHostname = [];
        for k in range(len(self.ResolvedStreams)):
            self.ResolvedNames.append(self.ResolvedStreams[k].name()) 
            self.ResolvedHostname.append(self.ResolvedStreams[k].hostname())
        return self.ResolvedNames,self.ResolvedHostname

    def create_logger(self):
        """ create the logger """
        #  logger
        info = pylsl.StreamInfo(name='MyMarkerStream', type='Markers', channel_count=1, nominal_srate=0, channel_format='string', source_id='myuidw43536')
        # create its outlet
        self.outlet = pylsl.StreamOutlet(info)
        self.outlet.push_sample(['Markers init'])

    def push_string(self, lsl_message, timestamp = 0.0):
        """ Push a string into the Logger Outlet Stream """
        self.outlet.push_sample([lsl_message], timestamp = timestamp) 

    def send_message(self, message, timestamp = 0.0): 
        """Create an alias for compatibility"""
        self.push_string(message, timestamp= timestamp)

    def start_session(self):  
        """ start the recording """
        self.recording_session.start_recording(task='recording')

    def stop_session(self):
        """ stop the recording """
        self.recording_session.stop_recording()




    