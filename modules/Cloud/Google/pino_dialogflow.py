#!/usr/bin/env python3.7

"""
Description : PinoBot Dialogflow handling module
Author : Jiwoo Jeong
Email  : Jiwoo@gepetto.io  / jjw951215@gmail.com

V 1.0
    - make module and test done

V 1.0.1 [2021-02-16]
    - add comment

"""

import dialogflow_v2 as dialogflow
from dialogflow_v2 import enums
from google.protobuf.json_format import MessageToDict
from google.api_core.exceptions import InvalidArgument ,Unknown
from ctypes import *

import pyaudio
import time ,wave ,ast

# PortAudio Error Message Handler
def py_error_handler(filename, line, function, err, fmt):
    pass

class PinoResponse:
    def __init__(self):
        self.stt_result = ""
        self.tts_result = None
        self.intent_name = ""
        self.intent_response = ""
        self.intent_parameter = {}
        self.action_cmd = []
        self.raw_result = {}

class PinoDialogFlow:
    """
    Description:
    - dialogflow module for use in pinobot
    - play pyaudio

    Summary of Class

    A. Utility Functions
        A.1 _init_pyaudio(self):
            Remove alsa Warning message from console
            find sound card index from alsamixer
            init pyaudio object

        A.2 play_audio_response(self, response):
            Play wave file in responses object

        A.3 parsing_response(self,stt_response,dflow_response,tts_response):
                Parse dialogflow grpc responses and return PinoResponse object

        A.4 _find_error(self, GCLOUD_ERROR):
                identify Google cloud Exception and save

    B.  DialogFlow Functions
        B.1 open_session(self):
            Open DialogFlow session

        B.2 send_text(self, text_msg):
            Send text to DialogFlow server,and return Paresed response

        B.3 send_event(self, event_name, dialogflow_parameters=None):
            Call DialogFlow event by event name and parameters
            and return Parsed response

    C. DialogFlow Stream Functions
        C.1 _request_generator(self):
            make generator to request stream response

        C.2 start_stream(self):
            Start audio stream to DialogFlow server

        C.3 get_stream_response(self, fail_handler=False):
            get audio streaming responses from DialogFlow server
            and if failed, call fail event
            finally return parsed data
    """

    def __init__(
        self,
        DFLOW_PROJECT_ID,                 # google dialogflow project id
        DFLOW_LANGUAGE_CODE,              # language code  (ISO-639-1 Code)
        GOOGLE_APPLICATION_CREDENTIALS,   # credential json file pull (path)
        TIME_OUT=5,                       # stream recording timeout  (sec)
        log = None                        # logging object
    ):

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

        # 3. google cloud state variable
        self.gcloud_dict = {
            1: "nomal",
            0: "fail prediction",
            -1: "Internet Error",
            -2: "google server error",
            -3: "over use Error",
            -4: "authorization Error",
            -5: "code bug",
            -6: "critical",
        }
        self.gcloud_state = 1

        # 4. class objects
        self.stream_result = None               # iterable Raw dialogflow responses object
        self.session_client = None              # google session client
        self.p_response = PinoResponse()   # Response parsing result
        self.audio = None                       # pyaudio object
        self.log = log                          # logging

        # 5. class variable
        self.recording_state = False            # used to stop audio streaming
        self.sound_card = 2                     # sound card index
        self.flag_log_fail_case = True          # if True, log failed intent case

        # 5. init settings
        self._init_pyaudio()

    """
    A. Utility Functions
    """
    def _init_pyaudio(self):
        """
        Description
        -----------
            Remove alsa Warning message from console
            find sound card index from alsamixer
            init pyaudio object

        Notes
        -----

        """

        # 1. Remove alsa messages
        ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
        c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
        self.asound = cdll.LoadLibrary("libasound.so")
        self.asound.snd_lib_error_set_handler(c_error_handler)

        audio = pyaudio.PyAudio()
        info = audio.get_host_api_info_by_index(0)
        num_devices = info.get("deviceCount")

        # 2. find  sound card from index
        card_name = "2mic"   # "2mic" in sound card name
        for i in range(0, num_devices):
            #print(audio.get_device_info_by_host_api_device_index(0, i))
            if (audio.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")) > 0 and card_name in audio.get_device_info_by_host_api_device_index(0, i).get("name"):
                    self.sound_card = i
        self.log.info("pino_dialogflow.py: sound card index is : %d" % self.sound_card)
        audio.terminate()
        self.audio = pyaudio.PyAudio()


    def play_audio_response(self, response):
        """
        Description
        -----------
            Play wave file in responses object

        Parameters
        ----------
            response : { Parsed DialogFlow response  , PinoResponse object}
                PinoResponse.tts_result is audio binary file .wav format

        Examples
        --------
            response = Pdf.send_text("HI")
            Pdf.play_audio_response(response)

        """
        if response is None :
            return 0
        if response.tts_result is not None:
            # TODO [1.1] [WIP] find alternative solution without using file system
            with open("/home/pi/1.wav", "wb") as f:
                f.write(response.tts_result)
            time.sleep(0.01)
            wav_data = wave.open("/home/pi/1.wav", "rb")

            # Open play stream. Formats are fixed,
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self._SAMPLE_RATE,
                output=True,
                output_device_index=self.sound_card
            )

            # Play wav file.
            data = wav_data.readframes(self._CHUNK_SIZE)
            while len(data) > 1:
                stream.write(data)
                data = wav_data.readframes(self._CHUNK_SIZE)
            stream.stop_stream()
            stream.close()


    def parsing_response(self,stt_response,dflow_response,tts_response):
        """
        Description
        -----------
            Parse dialogflow grpc responses and return PinoResponse object

        Parameters
        ----------
            stt_response: ( dialogflow response, dialogflow library object)
                response from dialogflow server

            tts_response: ( dialogflow response, dialogflow library object)
                response from dialogflow server

            dflow_response: ( dialogflow response, dialogflow library object)
                response from dialogflow server

        Notes
        -----
            send_text() and send_event() :  stt_response  = tts_response   =  dflow_response
            get_stream_response()        :  stt_response =/= tts_response =/= dflow_response

            **dialogflow parameter has two types:**
            1. pinobot commands
                used to actuate pinobot hardware
            2. normal intent parameters
                used to intent

        Return
        ------
            self.parsed_response : { Parsed DialogFlow response  , PinoResponse object}

        """

        # 1. Reset PinoResponse
        self.p_response.stt_result = ""
        self.p_response.tts_result = None
        self.p_response.intent_name = ""
        self.p_response.intent_response = ""
        self.p_response.intent_parameter = {}
        self.p_response.action_cmd = []
        self.p_response.raw_result = {}

        # 2, if response in invalid, return Reset value
        if stt_response is None or dflow_response is None or tts_response is None:
            self.p_response.stt_result = "[Fail]"
            return self.p_response

        # 3. Extract simple values
        elif hasattr(stt_response,"recognition_result"):
            self.p_response.stt_result = stt_response.recognition_result.transcript

        if hasattr(dflow_response,"query_result"):
            self.p_response.intent_name =dflow_response.query_result.intent.display_name
            self.p_response.intent_response =dflow_response.query_result.fulfillment_text

        if tts_response .output_audio is not None:
            self.p_response.tts_result = tts_response .output_audio

        # 3. Extract parameters from query_result
        self.p_response.raw_result = MessageToDict(dflow_response.query_result)

        # 5. iter all dialogflow parameters and seperate
        for key in self.p_response.raw_result["parameters"].keys():
            # 5.1. if key -> dict, dict is not handled in this function
            if not isinstance(key, str):
                continue

            # 5.2. key is pinobot command
            elif 'pino'or 'Pino' or "PINO" or 'PiNo' in key:
                self.p_response.action_cmd.append([key, self.p_response.raw_result['parameters'][key]])

            # 5.3. key is Intent parameter
            else:
                self.p_response.intent_parameter[key] = self.p_response.raw_result["parameters"][key]

        return self.p_response

    def _find_error(self, gcloud_error):
        """
        Description
        -----------
            identify Google cloud Exception and save

        Parameters
        ----------
            gcloud_error : {google.api_core.exceptions}

        """
        import google.api_core.exceptions as E

        #  0: 'fail prediction',
        if isinstance(gcloud_error, E.FailedPrecondition):
            self.log.error("pino_dialogflow.py:"+ repr(gcloud_error))
            self.gcloud_state = 0

        # -1: 'Internet Error',
        elif isinstance(gcloud_error, E.Forbidden) or isinstance(
            gcloud_error, E.GatewayTimeout
        ):
            self.log.error("pino_dialogflow.py:"+ repr(gcloud_error))
            self.gcloud_state = -1

        # -3: 'over use Error',
        elif isinstance(gcloud_error, E.TooManyRequests):
            self.log.error("pino_dialogflow.py:"+ repr(gcloud_error))
            self.gcloud_state = -3

        # -4: 'authorization Error',
        elif isinstance(gcloud_error, E.Unauthorized):
            self.log.error("pino_dialogflow.py:"+ repr(gcloud_error))
            self.gcloud_state = -4

        # -5: 'code bug',
        elif isinstance(gcloud_error, E.BadRequest):
            self.log.error("pino_dialogflow.py:"+ repr(gcloud_error))
            self.gcloud_state = -5

        # -2: 'ETC Network client and Server Error',
        elif isinstance(gcloud_error, E.ServerError) or isinstance(
            gcloud_error, E.ClientError
        ):
            self.log.error("pino_dialogflow.py:"+ repr(gcloud_error))
            self.gcloud_state = -2

        else:
            self.log.critical("pino_dialogflow.py:"+ repr(gcloud_error))
            self.gcloud_state = -6

    """
    B.  DialogFlow Functions
    
    Reference
    Dflow Docs: https://dialogflow-python-client-v2.readthedocs.io/en/latest/gapic/v2/api.html

    """
    def open_session(self):
        """
        Description
        -----------
            Open DialogFlow session

        Notes
        -----
            1. load Google credential files from
                "self._GOOGLE_APPLICATION_CREDENTIALS"  =  json file path

            2. check Google cloud error

        """
        self.log.info("pino_dialogflow.py: Start Open Session")
        self._session_id = self._project_id + time.asctime()
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(
            self._GOOGLE_APPLICATION_CREDENTIALS
        )
        try:
            self.session_client = dialogflow.SessionsClient(credentials=credentials)
            self._session_path = self.session_client.session_path(
                self._project_id, self._session_id
            )
            self.gcloud_state = 1
        except Exception as GCLOUD_ERROR:
            self._find_error(GCLOUD_ERROR)

        self.log.info("pino_dialogflow.py: Open New Session, SID [%s]" % self._session_id)
        return self.gcloud_state


    def send_text(self, text_msg):
        """
        Description
        -----------
            Send text to DialogFlow server,
            and return Parsed response

        Parameters
        ----------
            text_msg : { str }
                texts to send DialogFlow

        Returns
        -------
            response : { Parsed DialogFlow response  , PinoResponse object}
                extract necessary data form dialogflow responses

        Example
        -------
            r = Pdf.send_text(hi)
            >> print(r.intent_response)
                "Hello"

        """
        # 1. check Session Exsist
        if self._session_path is None:
            self.open_session()
            return None

        # 2. make Quary
        text_input = dialogflow.types.TextInput(
            text=text_msg, language_code=self.lang_code
        )
        output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=dialogflow.enums.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16,
            sample_rate_hertz=self._SAMPLE_RATE,
        )
        query_input = dialogflow.types.QueryInput(text=text_input)

        # 3. send Query
        try:
            response = self.session_client.detect_intent(
                session=self._session_path,
                query_input=query_input,
                output_audio_config=output_audio_config,
            )
        # 4. check response
        except InvalidArgument:  # quary error
            self.log.error("pino_dialogflow.py: Invalid Argument Send")
            return None
        except Exception as GCLOUD_ERROR:  # Gcloud Error
            self._find_error(GCLOUD_ERROR)
            return None

        return self.parsing_response(response,response,response)

    def send_event(self, event_name, dialogflow_parameters=None):
        """
        Description
        -----------
            Call DialogFlow event by event name and parameters
            and return Parsed response


        Parameters
        ----------
            event_name   : { str }
                event name called in DialogFlow

            dialogflow_parameters   : { dict, optional }
                used in DialogFlow intent


        Returns
        -------
            response : { Parsed DialogFlow response  , PinoResponse object}
                extract necessary data form dialogflow responses


        Example
        -------
            r = Pdf.send_event("say_room_temp",{temp:20, humidity: 20})
            >> print(r.intent_response)
                "Room temperature is 20c and humidity is 20 persent!"


        """

        stt_response = None
        dflow_response = None
        tts_response = None

        # 1. check Session Exsist
        if self._session_path is None:
            self.open_session()
            return None

        # 2. make quary with parameter
        if isinstance(dialogflow_parameters, dict):
            from google.protobuf import struct_pb2

            p = struct_pb2.Struct()
            for key in dialogflow_parameters.keys():
                p[key] = dialogflow_parameters[key]
            event_input = dialogflow.types.EventInput(
                name=event_name, language_code=self.lang_code, parameters=p
            )
        # 3. make quary without parameter
        else:
            event_input = dialogflow.types.EventInput(
                name=event_name, language_code=self.lang_code
            )

        output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=dialogflow.enums.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16,
            sample_rate_hertz=self._SAMPLE_RATE,
        )
        query_input = dialogflow.types.QueryInput(event=event_input)

        # 4. send Quary
        try:
            response = self.session_client.detect_intent(
                session=self._session_path,
                query_input=query_input,
                output_audio_config=output_audio_config,
            )

        except InvalidArgument:  # quary error
            self.log.error("pino_dialogflow.py: Invalid Argument Send")
        except Exception as GCLOUD_ERROR:  # Gcloud Error
            self._find_error(GCLOUD_ERROR)
        else:
            self.gcloud_state = 1
            stt_response = response
            dflow_response = response
            tts_response = response

        # 5. return parsed responses
        return self.parsing_response(stt_response, dflow_response, tts_response)

    """
    C. DialogFlow Stream Functions 

    Reference Source : 
        https://github.com/GoogleCloudPlatform/python-docs-samples/blob/3444bf44054965a523aafbf256dd597e265d0480/dialogflow/cloud-client/mic_stream_audio_response.py
        https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/dialogflow/cloud-client/detect_intent_stream.py
        https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2

    """

    def _request_generator(self):
        """
        Description
        -----------
            make generator to request stream response

        Returns
        -------
            out : { generator }
                request generator contain stream chuck

        """

        # 1. Config request parameters
        input_audio_config = dialogflow.types.InputAudioConfig(
            audio_encoding=enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16,
            language_code=self.lang_code,
            sample_rate_hertz=self._SAMPLE_RATE,
            single_utterance=False,
        )

        # 2. [NEW], request voice synthesis
        # Reference: https://cloud.google.com/dialogflow/docs/detect-intent-tts?hl=ko
        output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=dialogflow.enums.OutputAudioEncoding.OUTPUT_AUDIO_ENCODING_LINEAR_16,
            sample_rate_hertz=self._SAMPLE_RATE,
        )
        # 3 Make Quary
        # Reference: https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2#google.cloud.dialogflow.v2.QueryInput
        query_input = dialogflow.types.QueryInput(audio_config=input_audio_config)

        # 4. Make Initial Request
        # https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2#google.cloud.dialogflow.v2.StreamingDetectIntentRequest
        initial_request = dialogflow.types.StreamingDetectIntentRequest(
            session=self._session_path,
            query_input=query_input,
            output_audio_config=output_audio_config,  # [NEW], add for voice synthesis
        )
        yield initial_request  # Return Initial Request.

        # 5. init recording
        # [NOTE] AUDIO CHANNEL should be=1. google STT can't recognize over 1

        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._SAMPLE_RATE,
            input=True,
            frames_per_buffer=self._CHUNK_SIZE
            #input_device_index=self.sound_card
        )

        # 6. start streaming,
        # if over self._MAX_RECORD_SECONDS or self.recording_state is False(OFF), stop streaming,
        self.recording_state = True
        for loop in range(
            0, int(self._SAMPLE_RATE / self._CHUNK_SIZE * self._MAX_RECORD_SECONDS)
        ):
            try:
                audio_chunk = stream.read(self._CHUNK_SIZE, exception_on_overflow=False)
                # print(audio_chunk) debug, check chunks.
            except IOError as e:
                self.log.error("pino_dialogflow.py:"+repr(e))
                break
            except Exception as GCLOUD_ERROR:  # Gcloud Error
                self._find_error(GCLOUD_ERROR)
                break

            else:
                yield dialogflow.types.StreamingDetectIntentRequest(
                    session=self._session_path,
                    query_input=query_input,
                    input_audio=audio_chunk,
                    output_audio_config=output_audio_config,
                )
            if self.recording_state is False:
                break

        #  7. if Generator End stop streaming,
        stream.stop_stream()
        stream.close()

    def start_stream(self):
        """
        Description
        -----------
            Start audio stream to DialogFlow server

        Returns
        -------
            out : {bool}
                stream result Fail or Success

        See Also
        --------
            self.get_response()

        Notes
        -----
            iterable responses object is stored in self.stream_result


        Example
        -------
            r = Pdf.start_stream()
            print("streaming started, talk something in next 7 seconds)
            Pdf.get_response()  # blocked in 7 sec

        """

        # 1. check Session Exsist
        if self._session_path is None:
            self.open_session()
            return None

        # 2. init generator and start Recording
        """
         Google Unknown error could accur by alsamixer error, 
         
         therefor , try max 50 times to connect
        """
        for attempt in range(3):
            try:
                requests = self._request_generator()
                self.stream_result = self.session_client.streaming_detect_intent(requests)
            except Unknown:
                self.stream_result = None
            except Exception as E:
                self.log.error("pino_dialogflow.py start_stream() : "+repr(E))
                return -1
            else :
                return 0
        return 0

    def get_stream_response(self, fail_handler=False):
        """
        Description
        -----------
            get audio streaming responses from DialogFlow server
            and if failed, call fail event
            finally return parsed data


        Parameters
        ----------
            fail_handler : { bool, optional }
                flag to call extra answer when fail to get answer from DialogFlow


        Returns
        -------
            out : { Parsed DialogFlow response  , PinoResponse object}
                extract necessary data form dialogflow responses


        Notes
        -----
            this function is blocked in self._MAX_RECORD_SECONDS


        Example
        -------
            r = Pdf.start_stream()
            print("streaming started, talk something in next 7 seconds)
            Pdf.get_response()  # blocked in 7 sec
            >> print(r.intent_response)
                "hi! i am pinobot!"

        """

        stt_response = None
        dflow_response = None
        tts_response = None


        # 1. check Session Exsist
        if self._session_path is None:
            self.open_session()
            return None

        # 2. Wait for response
        print("get Response", end="")
        for item in self.stream_result:
            try:
                print(".", end="")
                #print(item.query_result.fulfillment_text)
                #print(item.output_audio)
                # 4. If STT Process is done
                # this response not include chat bot intent result, just STT result(talkers question)
                if item.recognition_result.is_final:
                    self.recording_state = False  # stop request generator
                    stt_response = item  # save at "stt_response"

                # 5. If Dialogflow send answer
                # [TODO] fine more good ways to check responce
                # after stt is done, dialogflow send chat bot intent result to response
                elif len(item.query_result.fulfillment_text) > 0 or item.output_audio != b'':  # if answer valid
                    print("done! ")
                    dflow_response = item  # save dialogflow response

                    # 6. To get TTS response, we need to get 1 More response.
                    try:
                        tts_response = next(self.stream_result)
                    except:
                        print("no tts response,")
                    break

            # 7. check google cloud error.
            except Exception as GCLOUD_ERROR:  # Gcloud Error
                self._find_error(GCLOUD_ERROR)
                break

        time.sleep(0.05)  # wait for turn off Stream

        # 8. return Result
        if stt_response is not None and dflow_response is not None:
            self.gcloud_state = 1
            return self.parsing_response(stt_response,dflow_response,tts_response)


        # 9. Fail case
        elif self.flag_log_fail_case : # log fail case
            try:
                with open("./fail_case.txt", "a") as fail_file:
                    m = (
                            time.asctime()
                            + "    %s\n"
                            % stt_response.recognition_result.transcript
                    )
                    fail_file.write(m)
            except:
                pass

        # E1. streaming can't rec talking
        if stt_response is None :
            if fail_handler:
                return self.send_event("Cant_Rec_Talk_Intent")
            else :
                return self.parsing_response(stt_response, dflow_response, tts_response)

        # E2. do not talk anything
        elif len(stt_response.recognition_result.transcript) == 0:
            if fail_handler:
                return self.send_event("Dont_Talk_Intent")
            else :
                return self.parsing_response(stt_response, dflow_response, tts_response)

        # E3. no matched event
        elif dflow_response.query_result.intent.display_name == "Default Fallback Intent" and fail_handler:
            return self.send_event("Fail_No_Match_Intent")


        return self.parsing_response(stt_response,dflow_response,tts_response)


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