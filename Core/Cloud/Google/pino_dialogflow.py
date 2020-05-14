#!/usr/bin/env python3.7
import dialogflow_v2 as dialogflow
from dialogflow_v2  import enums
from google.api_core.exceptions import InvalidArgument
import time
import logging

from ctypes import *
import pyaudio
import wave

def py_error_handler(filename, line, function, err, fmt):
    pass

class PinoDialogFlow():
    """
    Summary of Class

    A. Initializing parts.

        A.1. Variables used in class
            self._GOOGLE_APPLICATION_CREDENTIALS  --  path of GoogleCloud key json file
            self._project_id                      --  DialogFlow Project ID
            self._session_id                      --  session id of this class
            self._session_path                    --  session object
            self.lang_code                        --  language cod of DialogFlow Project, Default, ko

            self._SAMPLE_RATE = 16000             --  Sampleing Rate in Hz
            self._CHUNK_SIZE = 2048               --  Chuck size in byte
            self._MAX_RECORD_SECONDS              --  STT timeout, in Seconds
            self.gcloud_dict =                    --  GoogleCloud Error Code
            {        1: 'nomal',
                     0: 'fail prediction',
                    -1: 'Internet Error',
                    -2: 'google server error',
                    -3: 'over use Error',
                    -4: 'authorization Error',
                    -5: 'code bug',
                    -6: 'critical'
            }

            self.gcloud_state = 1                 --  Current GoogleCloud state
            self.recording_state = False          --  used for interrupt and stop Recording
            self.stt_response                     --  Final STT result
            self.dflow_response                   --  Chatbot result [ not include audio file! ]
            self.tts_response                     --  TTS result
            self.audio                            --  Pyaudio Object

        A.2 Delete, free fuction
            def __del__(self):

        A.3 Initializing Logger
            def _set_logger(self,path):

        A.4 Initializing pyuadio
            def _init_pyaudio(self):


    B. Open DialogFlow Session
        def open_session(self):

    C. Send [TEXT] and return answer [Text]
        def send_text(self, text_msg):

    D. Send [AUDIO STREAM] and return answer [AUDIO_BINARY]

        D.1 Request Generator
            def _request_generator(self):

        D.2 Start STREAM
            def start_stream(self):

        D.3 KEEP stream AND wait For Response,
            def get_response(self):


    E. play audio file stored in self.tts_response.output_audio

        E.1 play audio                                                          --[WIP]
            def play_audio(self):
        E.2 set volume                                                          --[WIP]
            def set_volume(self):


    F. Send [EVENT] and return answer [AUDIO]
        def send_event(self,event_name,parameters):

    G. Google Error message handler
        def _find_error(self,GCLOUD_ERROR):

    """

    """
    A.1 Initializing DialogFlow Connection Module
    """
    def __init__(self, DFLOW_PROJECT_ID, 
                       DFLOW_LANGUAGE_CODE , 
                       GOOGLE_APPLICATION_CREDENTIALS,
                       TIME_OUT = 5):

        # 1. store Cloud Connection Settings as Private
        self._GOOGLE_APPLICATION_CREDENTIALS = GOOGLE_APPLICATION_CREDENTIALS 
        self._project_id = DFLOW_PROJECT_ID
        self._session_id = None
        self._session_path = None
        self.lang_code = DFLOW_LANGUAGE_CODE
        
        # 2. set private variables
        self._SAMPLE_RATE = 16000 
        self._CHUNK_SIZE = 2048
        self._MAX_RECORD_SECONDS = TIME_OUT       

        # 3. set nomal variables
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
        self.tts_response = None
        self.audio = None

        # 4. set Logger, use Python Logging Module
        self._set_logger(path = "/home/pi/Desktop/PinoBot/log/DialogFlow.log")

        # 5. init settings
        self._find_soundcard()
        self._init_pyaudio()

    """
    A.2 Delete and Free Object
    
    """
    def __del__(self):
        if self.audio is not None:
            self.audio.terminate()
            self.asound.snd_lib_error_set_handler(None) # set back handler as Default

    """
    A.2 find Sound card index by name
    """
    def _find_soundcard(self):
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
    A.3 Initializing Logger
    """
    def _set_logger(self,path):
        # 2.1 set logger and formatter
        self.log = logging.getLogger("DialogFlow")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] (%(asctime)s : %(filename)s:%(lineno)d) > %(message)s')

        # 2.2 set file logger 
        self.log_file = logging.FileHandler(filename = path, 
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
    A.4 Initializing pyuadio
    """
    def _init_pyaudio(self):
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
        self.log.info("Start Open Session")
        if self._session_path is not None:
            self.log.warning( "old_session %s exsists, Ignore and open New Session"%self._session_id)
        
        # set session id as [timestamp + project id]
        self._session_id = self._project_id +time.asctime()
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(self._GOOGLE_APPLICATION_CREDENTIALS)
        try:
            self.session_client = dialogflow.SessionsClient(credentials = credentials)
            self._session_path = self.session_client.session_path(self._project_id, self._session_id)
            self.gcloud_state = 1
        except Exception as GCLOUD_ERROR:
            self._find_error(GCLOUD_ERROR)

        self.log.info("Open New Session, SID [%s]" % self._session_id)
        return self.gcloud_state

    """
    C. Send [TEXT] and return answer [Text]
    
    """
    def send_text(self, text_msg):
        """
        Args: text_msg (str): Text message to Send
        """
        # 1. check Session Exsist
        if self._session_path is None: # if not, exit fuction
            self.log.error("Session is not opened ignore command")
            return None


        # 2. make Quary
        text_input = dialogflow.types.TextInput(text=text_msg, language_code=self.lang_code)
        output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=dialogflow.enums.OutputAudioEncoding
                .OUTPUT_AUDIO_ENCODING_LINEAR_16,
            sample_rate_hertz=self._SAMPLE_RATE
        )
        query_input = dialogflow.types.QueryInput(text=text_input)

        # 3. send Quary
        try:
            response = self.session_client.detect_intent(session=self._session_path, query_input=query_input,
                                                         output_audio_config=output_audio_config)
        
        except InvalidArgument:  # quary error
            self.log.error("Invalid Argument Send")
            return None
        except Exception as GCLOUD_ERROR:  # Gcloud Error
            self._find_error(GCLOUD_ERROR)
            return None

        self.dflow_response = response
        self.tts_response = response
        return response

    """
    Reference Source : 
        https://github.com/GoogleCloudPlatform/python-docs-samples/blob/3444bf44054965a523aafbf256dd597e265d0480/dialogflow/cloud-client/mic_stream_audio_response.py
        https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/dialogflow/cloud-client/detect_intent_stream.py
        https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2


    D. Send [AUDIO STREAM] and return answer [AUDIO_BINARY]

    Main feature Fuctions, 

    1. Start timeout-audio-stream with generator
    2. Generator keep sending audio stream to Google Server.
    3. If talking is end or, timeout happen, stop generator and wait for response.
    4. Get respose and check is it valid
    5. return two response
        "stt_response" is [STT] result of talking,
        "chatbot_response" is [DialogFlow chatbot] result.

    D.1 Request Generator.
    """
    def _request_generator(self):
        """
        Args: None
            [deleted] # audio(Pyaudio object) : base pyaudio class for recording
        """

        # 1.1 Config request parametoers
        input_audio_config = dialogflow.types.InputAudioConfig(
            audio_encoding=enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
            language_code=self.lang_code,
            sample_rate_hertz=self._SAMPLE_RATE,
            single_utterance=False
        )

        # 1.2 [NEW], request voice synthesis 
        # Reference: https://cloud.google.com/dialogflow/docs/detect-intent-tts?hl=ko
        output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=dialogflow.enums.OutputAudioEncoding
            .OUTPUT_AUDIO_ENCODING_LINEAR_16,
            sample_rate_hertz=self._SAMPLE_RATE
        )
        # 1.3 Make Quary
        # Reference: https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2#google.cloud.dialogflow.v2.QueryInput
        query_input = dialogflow.types.QueryInput(
            audio_config=input_audio_config
        ) 

        # 1.4 Make Initial Request
        # https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2#google.cloud.dialogflow.v2.StreamingDetectIntentRequest
        initial_request = dialogflow.types.StreamingDetectIntentRequest(
            session=self._session_path,
            query_input=query_input,
            output_audio_config=output_audio_config # [NEW], add for voice synthesis
        ) 
        yield initial_request # Return Initial Request.

        # 2.1 init recording
        # [NOTE] AUDIO CHANNEL should be=1. google STT can't recognize over 1
        stream = self.audio.open(format=pyaudio.paInt16, channels=1,
                    rate=self._SAMPLE_RATE , input=True,
                    frames_per_buffer=self._CHUNK_SIZE, input_device_index=self.sound_card)
        
        # 2.2 start streaming,
        # if over self._MAX_RECORD_SECONDS or self.recording_state is False(OFF), stop streaming,
        self.recording_state = True
        for loop in range(0, int(self._SAMPLE_RATE / self._CHUNK_SIZE * self._MAX_RECORD_SECONDS)): 
            try:           
                audio_chunk = stream.read(self._CHUNK_SIZE,  exception_on_overflow = False)    
            except IOError as e:
                self.log.error(e)
                break
            except Exception as GCLOUD_ERROR:  # Gcloud Error
                self._find_error(GCLOUD_ERROR)
                break

            else :
                yield dialogflow.types.StreamingDetectIntentRequest(
                    session=self._session_path,
                    query_input=query_input,
                    input_audio=audio_chunk,
                    output_audio_config=output_audio_config)
            if self.recording_state is False :
                break

        #  5. if Generator End stop streaming,
        stream.stop_stream()
        stream.close()
        
    """
    D.2 Start STREAM, 
    [NOTE] This fuction ends, when Stream started!
    """
    def start_stream(self): 
        # GOOGLE EXPERIMENTAL: This method interface might change in the future.
        # https://github.com/GoogleCloudPlatform/python-docs-samples/blob/3444bf44054965a523aafbf256dd597e265d0480/dialogflow/cloud-client/mic_stream_audio_response.py
        
        # check Session Exsist
        if self._session_path is None: # if not, exit fuction
            self.log.error("Session is not opened ignore command")
            return None

        # 2.4 init generator and start Recording
        requests = self._request_generator()
        self.responses = self.session_client.streaming_detect_intent(requests)
        return self.responses # return iteratable response object, 
    
    """
    D.3 KEEP stream AND wait For Response, 
    This fuction should called after start stream to get response. 
    or you can write your owen response fuction 
    """    
    def get_response(self):
        if self._session_path is None: # if not, exit fuction
            self.log.error("Session is not opened ignore command")
            return None, None

        # 3. Wait for response
        while True: 
            try:
                item = next(self.responses) # receive Response
                self.log.info("get Response...")

                # 4.1 If STT Process is done
                # this response not include chatbot result, just STT result(talkers question)
                if item.recognition_result.is_final :
                    self.recording_state = False # stop request generator
                    self.stt_response = item # save at "stt_response"

                # 4.2 If dialogflow send answer
                # after stt is done, dialogflow send chatbot_result(robot's answer) to response
                elif len(item.query_result.fulfillment_text) > 0: # if answer valid
                    self.log.info("done! ")
                    self.dflow_response = item # save dialogflow response

                    # [NEW] , TO get TTS response, we need to get 1 More response.
                    try:
                        self.tts_response = next(self.responses)
                    except:
                        self.log.error("no tts response,")
                        self.tts_response = None
                    break

            # Close loop, before Final call
            # Error hander, usually called when user don't talk anything 
            except StopIteration: 
                self.stt_response = None
                self.dflow_response = None
                self.log.error("i can't get result by some reason")
                break

            except Exception as GCLOUD_ERROR:  # Gcloud Error
                self._find_error(GCLOUD_ERROR)
                self.asound.snd_lib_error_set_handler(None) # set back handler as Default
                break


        # 5. return Result        
        time.sleep(0.05) # wait for turn off Stream
        if self.stt_response is not None and self.dflow_response is not None:
            return self.stt_response, self.dflow_response
        
        return None, None

    """
       E. play audio file stored in self.tts_response.output_audio
    """

    """
        E.1 play audio
    """
    def play_audio(self):
        if self.tts_response.output_audio is not None:

            # [WIP] find alternative solution without using file system
            with open("./1.wav","wb") as f:
                f.write(self.tts_response.output_audio)
            time.sleep(0.01)
            wav_data = wave.open("./1.wav","rb")

            # Open play stream. Formats are fixed,
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self._SAMPLE_RATE,
                output=True
            )

            # Play wav file.
            data = wav_data.readframes(self._CHUNK_SIZE)
            while len(data) > 1:
                stream.write(data)
                data = wav_data.readframes(self._CHUNK_SIZE)
            stream.stop_stream()
            stream.close()
    """
        E.2 set volume
        [WIP] , VOLUME setting fuctionm, using amixer command
    """
    def set_volume(self):
        pass
        # amixer -c 1 cset iface=MIXER,name="ADC1 PGA gain" 20


    """
    F. Send [EVENT] and return answer [AUDIO]
    
    [WIP] Send Specific Custom Event to Dialogflow server
    and get response and save it.

    """
    def send_event(self,event_name, parameters = None):
        """
        Args: event_name (str): event name to call
              parameters (dict): dialogflow parameter in dictionary
        """
        # 1. check Session Exsist
        if self._session_path is None:  # if not, exit fuction
            self.log.error("Session is not opened ignore command")
            return None

        # 2. make Quary

        if parameters is None :
            event_input = dialogflow.types.EventInput(name=event_name,
                                                      language_code=self.lang_code)
        else :
            from google.protobuf import struct_pb2
            for key in parameters.keys():
                p = struct_pb2.Struct()
                p[key] = parameters[key]
            event_input = dialogflow.types.EventInput(name=event_name,
                                                      language_code=self.lang_code,
                                                      parameters=p)


        output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=dialogflow.enums.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16,
            sample_rate_hertz=self._SAMPLE_RATE
        )
        query_input = dialogflow.types.QueryInput(event=event_input)

        # 3. send Quary
        try:
            response = self.session_client.detect_intent(session=self._session_path, query_input=query_input,
                                                         output_audio_config=output_audio_config)

        except InvalidArgument:  # quary error
            self.log.error("Invalid Argument Send")
            return None
        except Exception as GCLOUD_ERROR:  # Gcloud Error
            self._find_error(GCLOUD_ERROR)
            return None

        self.dflow_response = response
        self.tts_response = response
        return response

    """

    G. Google Error message handler
    """
    def _find_error(self, GCLOUD_ERROR):
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
example code for test

"""
def example():

    # 1. Set google dialogflow project config
    DIALOGFLOW_PROJECT_ID = 'a2-bwogyf'
    DIALOGFLOW_LANGUAGE_CODE = 'ko'
    GOOGLE_APPLICATION_CREDENTIALS = '/home/pi/Desktop/PinoBot/Keys/a2-bwogyf-c40e46d0dc2b.json'
    TIME_OUT = 7

    # 2. init and connect dialogflow project
    Gbot = PinoDialogFlow(DIALOGFLOW_PROJECT_ID,
                         DIALOGFLOW_LANGUAGE_CODE,
                         GOOGLE_APPLICATION_CREDENTIALS,
                         TIME_OUT)
    Gbot.open_session()


    # 3. sent text and get Response
    print("\n\n Start!")
    text_response = Gbot.send_text("안녕하세요")
    print("[Q] : %s "%text_response.query_result.query_text)
    print("[A] : accuracy:%0.3f | %s "%(text_response.query_result.intent_detection_confidence,
                                        text_response.query_result.fulfillment_text))
    #Gbot.play_audio()

    # 4. send voice and get voice response
    Gbot.start_stream()
    print("Streaming started, say something timeout, %d seconds"%TIME_OUT)
    stt_response, chatbot_response = Gbot.get_response()
    if stt_response is not None and chatbot_response is not None:
        print("[Q] : %s "%stt_response.recognition_result.transcript)
        print("[A] : accuracy:%0.3f | %s "%(chatbot_response.query_result.intent_detection_confidence,
                                            chatbot_response.query_result.fulfillment_text))
    else :
        print("rec error")
    # [WIP]
    # play audio_binary file..
    #Gbot.play_audio()

    # 5. send Event with parameters
    print("\n\n Start!")
    event_response = Gbot.send_event("Wall_Event",{'Wall_time':50})
    print("[Q] : %s " % event_response.query_result.query_text)
    print("[A] : accuracy:%0.3f | %s " % (event_response.query_result.intent_detection_confidence,
                                          event_response.query_result.fulfillment_text))

   # 6. session Tester,
    cnt = 0
    while True:
        time.sleep(5)
        cnt += 5
        print('%d seconds went. '%cnt)
        if cnt % 2400 == 0:
            try :
                text_response = Gbot.send_text("안녕하세요")
                print("[Q] : %s " % text_response.query_result.query_text)
                print("[A] : accuracy:%0.3f | %s " % (text_response.query_result.intent_detection_confidence,
                                                      text_response.query_result.fulfillment_text))
            except :
                print("session Error")


if __name__ == "__main__":
    example()