#!/usr/bin/env python3.7
import dialogflow_v2 as dialogflow
from dialogflow_v2  import enums
from google.api_core.exceptions import InvalidArgument , GoogleAPIError
import time
import logging

from ctypes import *
import pyaudio
#from multiprocessing import JoinableQueue , Process , Queue , TimeoutError

def py_error_handler(filename, line, function, err, fmt):
    pass

class PinoDialogFlow():

    """
    A. Initializing DialogFlow Connection Module
    """
    def __init__(self, DFLOW_PROJECT_ID, 
                       DFLOW_LANGUAGE_CODE , 
                       GOOGLE_APPLICATION_CREDENTIALS):

        # 1. store Cloud Connection Settings as Private
        self._GOOGLE_APPLICATION_CREDENTIALS = GOOGLE_APPLICATION_CREDENTIALS 
        self._project_id = DFLOW_PROJECT_ID
        self._session_id = None         
        self.lang_code = DFLOW_LANGUAGE_CODE
        
        # 2. set private variables
        self._SAMPLE_RATE = 16000 
        self._CHUNK_SIZE = 2048
        self._MAX_RECORD_SECONDS = 5       

        # 3. set Logger, use Python Logging Module
        self.set_logger()

        # 4. set nomal variables
        self.gcloud_dict = {1: 'nomal',
                             0: 'fail prediction',
                            -1: 'Internet Error',
                            -2: 'google server error', 
                            -3: 'over use Error',
                            -4: 'authorization Error',
                            -5: 'code bug',
                            -6: 'critical'
        }
        self.gcloud_state = 1

        self.recording_state = False
        self.stt_response = None
        self.dflow_response = None
        self.audio = None

        # 5. init settings
        self.find_soundcard()
        self.init_pyaudio()

    def __del__(self):
        if self.audio is not None:
            self.audio.terminate()
            self.asound.snd_lib_error_set_handler(None) # set back handler as Default


    def find_soundcard(self):
        # 1. Remove alsa messages
        ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
        c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        
        audio = pyaudio.PyAudio()
        info = audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        # 2. find self.sound_cardsound card from index
        card_name = "2mic" # "ac108" for 4-mic hat module
        self.sound_card = 2 # usually, 2mic module index is 2
        for i in range(0, numdevices):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                if(card_name in audio.get_device_info_by_host_api_device_index(0, i).get('name')):
                    self.sound_card = i
        self.log.info("sound card index is : %d"%(self.sound_card))
        audio.terminate()

    """
    A.1 Initializing Logger
    """
    def set_logger(self):
        # 2.1 set logger and formatter
        self.log = logging.getLogger("DialogFlow")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s')

        # 2.2 set file logger 
        self.log_file = logging.FileHandler(filename = '/home/pi/PinoBot/log/DialogFlowlog.log', 
                                            mode='w',
                                            encoding='utf-8')
        self.log_file.setFormatter(formatter)
        self.log.addHandler(self.log_file)

        # 2.3 set consol logger
        self.log_consol = logging.StreamHandler()
        self.log_consol.setFormatter(formatter)
        self.log.addHandler(self.log_consol)

        # 2.4 logger Done.
        self.log.info("Start DialogFlow Module")


    """
    A.1 Initializing pyuadion
    """
    def init_pyaudio(self):
        if self.audio is not None:
            self.audio.terminate()
            self.asound.snd_lib_error_set_handler(None) # set back handler as Default
            
        # 1. Remove alsa messages
        ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
        c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
        self.asound = cdll.LoadLibrary('libasound.so')
        self.asound.snd_lib_error_set_handler(c_error_handler)
        
        # 2. init pyaudio
        self.audio = pyaudio.PyAudio()


    """
    B. Open DialogFlow Session

    Reference
    Dflow Docs: https://dialogflow-python-client-v2.readthedocs.io/en/latest/gapic/v2/api.html
    logger : https://docs.python.org/ko/3/howto/logging.html

    """
    def open_session(self):
        if self._session_id is not None:
            self.log.warning( "old_session %s exsists, Ignore and open New Session"%self._session_id)
        
        # set session id as [timestamp + project id]
        self._session_id = self._project_id

        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(self._GOOGLE_APPLICATION_CREDENTIALS)
        self.session_client = dialogflow.SessionsClient(credentials = credentials)
        self._session = self.session_client.session_path(self._project_id, self._session_id)
        self.log.info("Open New Session, SID [%s]" % self._session_id)

    """
    C. Send [TEXT] and return answer [Text]
    
    """
    def send_text(self, text_msg):
        """
        Args: text_msg (str): Text message to Send
        """
        # 1. check Session Exsist
        if self._session_id is None: # if not, exit fuction
            self.log.error("Session is not opened ignore command")
            return None
        
        # 2. make Quary
        text_input = dialogflow.types.TextInput(text=text_msg, language_code=self.lang_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        
        # 3. send Quary
        try:
            response = self.session_client.detect_intent(session=self._session, query_input=query_input)
        
        except InvalidArgument:  # quary error
            self.log.error("Invalid Argument Send")
            return None
        except Exception as GCLOUD_ERROR:  # Gcloud Error
            self.find_error(GCLOUD_ERROR)
            return None
            
        # 4. log Response , [to be deleted]
        #self.log.info(response.query_result.query_text)
        #self.log.info(response.query_result.intent_detection_confidence)
        #self.log.info(response.query_result.fulfillment_text)
        self.dflow_response = response
        return response.query_result.fulfillment_text

    # [WIP] , VOLUME setting fuctionm, using amixer command 
    def setVolume(self):
        pass
        # amixer -c 1 cset iface=MIXER,name="ADC1 PGA gain" 20

    """
    Reference Source : 
        https://github.com/GoogleCloudPlatform/python-docs-samples/blob/3444bf44054965a523aafbf256dd597e265d0480/dialogflow/cloud-client/mic_stream_audio_response.py
        https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/dialogflow/cloud-client/detect_intent_stream.py
        https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2

    D. Send [AUDIO STREAM] and return answer [Text]

    D.1 Request Generator.
    """
    def request_generator_stream(self,audio,audio_q=None):
        """
        Args: audio(Pyaudio object) : base pyaudio class for recording
              audio_q(Queue) : [NOT USED], only used Debuging, to save stream file as .wav 
        """
        # 1. Config request parametoers
        session_path = self.session_client.session_path(
            project=self._project_id, session=self._session_id
        )
        input_audio_config = dialogflow.types.InputAudioConfig(
            audio_encoding=enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
            language_code=self.lang_code,
            sample_rate_hertz=self._SAMPLE_RATE,
            single_utterance=False
        )
        query_input = dialogflow.types.QueryInput(
            audio_config=input_audio_config
        ) # https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2#google.cloud.dialogflow.v2.QueryInput
        
        # 2. Make Initial Request
        initial_request =  dialogflow.types.StreamingDetectIntentRequest(
            session=session_path,
            query_input=query_input
        ) # https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2#google.cloud.dialogflow.v2.StreamingDetectIntentRequest
        yield initial_request

        # 3. init recording
        # [NOTE] AUDIO CHANNEL should be=1. google STT can't recognize over 1
        stream = audio.open(format=pyaudio.paInt16, channels=1,
                    rate=self._SAMPLE_RATE , input=True,
                    frames_per_buffer=self._CHUNK_SIZE,input_device_index=self.sound_card)
        
        # 4. start streaming,
        # if over self._MAX_RECORD_SECONDS or self.recording_state is False(OFF), stop streaming,

        for loop in range(0, int(self._SAMPLE_RATE / self._CHUNK_SIZE * self._MAX_RECORD_SECONDS)): 
            try:           
                audio_chunk = stream.read(self._CHUNK_SIZE,  exception_on_overflow = False)
                # audio_q.put(chunk) # For debug Recording as ./recording2.wave
            except IOError as e:
                self.log.error(e)
                break
            except Exception as GCLOUD_ERROR:  # Gcloud Error
                self.find_error(GCLOUD_ERROR)
                break

            else :
                #self.log.info("send request!")
                yield dialogflow.types.StreamingDetectIntentRequest(
                     session=session_path,
                     query_input=query_input,
                     input_audio=audio_chunk)
            if self.recording_state is False :
                break

        # 5. stop streaming,
        stream.stop_stream()
        stream.close()
        
    """
    D. Send [AUDIO STREAM] and return answer [Text]

    D.2 Main S2T Process
    """

    def start_audio_stream(self): 
        # EXPERIMENTAL: This method interface might change in the future.
        # https://github.com/GoogleCloudPlatform/python-docs-samples/blob/3444bf44054965a523aafbf256dd597e265d0480/dialogflow/cloud-client/mic_stream_audio_response.py
        
        # 1. check Session Exsist
        if self._session_id is None: # if not, exit fuction
            self.log.error("Session is not opened ignore command")
            return -1

        # 2. init generator and start Recording
        requests = self.request_generator_stream(self.audio)
        self.responses = self.session_client.streaming_detect_intent(requests)
        return self.responses
    
    def get_audio_response(self):
        # 5. Wait for response
        while True: 
            try:
                #self.raise_error(2)
                item = next(self.responses) # receive Response
                self.log.info("get Response...")

                if item.recognition_result.is_final : # If STT is done
                    self.recording_state = False # stop request generator
                    self.stt_response = item # save stt response
                    
                elif len(item.query_result.fulfillment_text) > 0: # If dialog Flow send answer
                    self.log.info("done! ") 
                    self.dflow_response = item # save dflow response
                    break

            except StopIteration: # Close loop, before Final call, Warning
                self.stt_response = None
                self.dflow_response = None
                self.log.error("i can't get result by some reason")
                break

            except Exception as GCLOUD_ERROR:  # Gcloud Error
                self.find_error(GCLOUD_ERROR)
                self.asound.snd_lib_error_set_handler(None) # set back handler as Default
                break
            
        # 6. return Result        
        time.sleep(0.05) # wait for turn off Stream
        stt_result = ''
        if self.stt_response is not None:
            stt_result = self.stt_response.recognition_result.transcript

        chatbot_result = ''
        if self.dflow_response is not None:
            chatbot_result = self.dflow_response.query_result.fulfillment_text

        #self.log.info("exit program")
        return stt_result, chatbot_result

    """
    E. Google Error message handler
    """
    def find_error(self,GCLOUD_ERROR):
        import google.api_core.exceptions as E
        
        #  0: 'fail prediction',
        if isinstance(GCLOUD_ERROR, E.FailedPrecondition):
            self.log.error(GCLOUD_ERROR)
            self.gcloud_state = 0 

        # -1: 'Internet Error', 
        elif (isinstance(GCLOUD_ERROR, E.Forbidden) or isinstance(GCLOUD_ERROR, E.GatewayTimeout)):
            self.log.error(GCLOUD_ERROR)
            self.gcloud_state = -1 

        # -3: 'over use Error',
        elif isinstance(GCLOUD_ERROR, E.TooManyRequests):
            self.log.error(GCLOUD_ERROR)
            self.gcloud_state = -3 

        # -4: 'authorization Error',
        elif isinstance(GCLOUD_ERROR, E.Unauthorized):
            self.log.error(GCLOUD_ERROR)
            self.gcloud_state = -4 

        # -5: 'code bug',
        elif isinstance(GCLOUD_ERROR, E.BadRequest) :
            self.log.error(GCLOUD_ERROR)
            self.gcloud_state = -5

        # -2: 'ETC Network client and Server Error',
        elif (isinstance(GCLOUD_ERROR, E.ServerError) or isinstance(GCLOUD_ERROR, E.ClientError)):
            self.log.error(GCLOUD_ERROR)
            self.gcloud_state = -2 

        else:
            self.log.critical(GCLOUD_ERROR)
            self.gcloud_state = -6                        
        return 

    """ [DEBUG error raise CODE]
    def raise_error(self,i):
        import google.api_core.exceptions as E

        if i == 0:
            raise E.NotFound('asd')
        if i == 1:
            raise E.Unauthenticated('asd')
        if i == 2:
            raise E.PermissionDenied('asd')
        if i == 3:
            raise E.InvalidArgument('asdf')
        if i == 4:
            raise E.ResourceExhausted('as')
    """


 
""" 
def TTD_code_1():
    DIALOGFLOW_PROJECT_ID = 'a2-bwogyf'
    DIALOGFLOW_LANGUAGE_CODE = 'ko'
    GOOGLE_APPLICATION_CREDENTIALS = '/home/pi/Squarebot/Keys/a2-bwogyf-c40e46d0dc2b.json'

    Gbot = SqbDialogFlow(DIALOGFLOW_PROJECT_ID,
                         DIALOGFLOW_LANGUAGE_CODE,
                         GOOGLE_APPLICATION_CREDENTIALS)

    Gbot.open_session()
    Gbot.send_audio_stream()



if __name__ == "__main__":
    TTD_code_1()


[OLD TEST CODE]
def example_T2T():
    DIALOGFLOW_PROJECT_ID = 'a2-bwogyf'
    DIALOGFLOW_LANGUAGE_CODE = 'ko'
    GOOGLE_APPLICATION_CREDENTIALS = '/home/pi/Squarebot/Keys/a2-bwogyf-c40e46d0dc2b.json'

    Gbot = SqbDialogFlow(DIALOGFLOW_PROJECT_ID,
                         DIALOGFLOW_LANGUAGE_CODE,
                         GOOGLE_APPLICATION_CREDENTIALS)

    Gbot.open_session()
    answer = Gbot.send_text('이름')
    print(answer)

def example_A2T():
    DIALOGFLOW_PROJECT_ID = 'a2-bwogyf'
    DIALOGFLOW_LANGUAGE_CODE = 'ko'
    GOOGLE_APPLICATION_CREDENTIALS = '/home/pi/Squarebot/Keys/a2-bwogyf-c40e46d0dc2b.json'

    Gbot = SqbDialogFlow(DIALOGFLOW_PROJECT_ID,
                         DIALOGFLOW_LANGUAGE_CODE,
                         GOOGLE_APPLICATION_CREDENTIALS)

    Gbot.open_session()
    answer = Gbot.send_audio_file('~/Squarebot/hello.wav')
    print(answer)
"""

"""
    def send_audio_stream(self): 
        # EXPERIMENTAL: This method interface might change in the future.
        # https://github.com/GoogleCloudPlatform/python-docs-samples/blob/3444bf44054965a523aafbf256dd597e265d0480/dialogflow/cloud-client/mic_stream_audio_response.py
        
        # 1. check Session Exsist
        if self._session_id is None: # if not, exit fuction
            self.log.error("Session is not opened ignore command")
            return -1

        self.log.info("init pyaudio")
        # 2. Remove alsa messages
        ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
        c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        
        # 3. init pyaudio
        audio = pyaudio.PyAudio()

        # 4. init generator and start Recording
        #audio_q =None #Queue()
        requests = self.request_generator_stream(audio)
        responses = self.session_client.streaming_detect_intent(requests)
        self.log.info("Start Streaming...")

        # 5. Wait for response
        while True: 
            try:
                #self.raise_error(2)
                item = next(responses) # receive Response
                self.log.info("get Response...")

                if item.recognition_result.is_final : # If STT is done
                    self.recording_state = False # stop request generator
                    self.stt_response = item # save stt response
                    
                elif len(item.query_result.fulfillment_text) > 0: # If dialog Flow send answer
                    self.log.info("done! ") 
                    self.dflow_response = item # save dflow response
                    break

            except StopIteration: # Close loop, before Final call, Warning
                self.stt_response = None
                self.dflow_response = None
                self.log.error("i can't get result by some reason")
                return None
            except Exception as GCLOUD_ERROR:  # Gcloud Error
                self.find_error(GCLOUD_ERROR)
                asound.snd_lib_error_set_handler(None) # set back handler as Default
                return None
            
        # 6. return Result
        try :
            self.log.info('STT Result: "{}"'.format(self.stt_response.recognition_result.transcript) )
            self.log.info('Dflow Answer: {}'.format(self.dflow_response.query_result.fulfillment_text))
        except AttributeError :
            self.log.warning("STT return value is None")
        except Exception as e: # Critical Unknown Error
            self.log.critical(e)
            asound.snd_lib_error_set_handler(None) # set back handler as Default
            return -1
        
        time.sleep(0.05) # wait for turn off Stream
        audio.terminate()
        asound.snd_lib_error_set_handler(None) # set back handler as Default

        self.log.info("exit program")
        return self.dflow_response

        
        [ DEBUG Recording ]
        import wave
        waveFile = wave.open("./recording2.wav", 'wb')
        waveFile.setnchannels(1)
        waveFile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        waveFile.setframerate(16000)

        frames = []
        while audio_q.qsize():
            frames.append(audio_q.get())
        
        waveFile.writeframes(b''.join(frames))
        waveFile.close()
        """
        
