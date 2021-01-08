"""

def poll_thread(self):
    sensor measurement thread
    which calls every 0.5 seconds

    # 1. initializing
    s_state = 0
    d = 0
    T_LIMIT = 10
    detect_time = 0

    with  self.lock:
        d = self.react_distance
        T_LIMIT = self.wall_threshold_time

        # 2. main loop
    cur_volume = 0

    while True:
        time.sleep(0.2)  # check sonic sensor every 0.5 seconds
        with self.lock:
            volume, distance, serial_msgs = self.HardWare.read()
            # print("d: %0.2f %d"%(distance, time.time() - detect_time))

            # 2.1. onject  z
            if distance < d and s_state == 0:
                print("object in")
                s_state = 1
                detect_time = time.time()

            # 2.2. object [in -> out]
            elif distance > d and s_state == 1:
                print("object out")
                s_state = 0

            # 2.3. object [Measure WALL] is still in and over threathold time:
            elif distance < d and detect_time != 0 and time.time() - detect_time > T_LIMIT:
                print("wall in")
                s_state = -1

            # 2.4. object [Escape WALL]
            elif distance > d and s_state == -1:
                print("wall out")
                s_state = 0
            self.sensor_state = s_state

            if volume != cur_volume:
                print("change volume")
                cur_volume = volume

            if serial_msgs != "":
                print("serial: ", serial_msgs)
                self.rcv_serial_msgs = serial_msgs


def stream_voice(self):
    print("Streaming started, say something timeout, %d seconds" % self.TIME_OUT)  # [TEMP CODE]

    self.HardWare.write(text="Call me?", led=[200, 200, 0], servo_angle=[120, 120, 70])
    self.cloud.start_stream()

    stt_response, chatbot_response = self.cloud.get_response()

    self.HardWare.write(text="I Heard !", led=[0, 0, 0], servo_angle=[60, 60, 90])
    if stt_response is None:
        return -1
    elif len(stt_response.recognition_result.transcript) == 0:
        return 0
    elif len(chatbot_response.query_result.fulfillment_text) > 0:
        return 1
    else:
        return -2


def send_event(self, Event):
    event_response = self.cloud.send_event(Event)
    if event_response is None:
        print("rec error")
        return False
    elif len(event_response.query_result.fulfillment_text) > 0:
        return True
    else:
        print("rec error")
        return False


def do_action(self):

    [WIP] do some actions..

    # TODO : Parse Action and paramater
    actions = self.cloud.parse_response()

    audio_t = Thread(target=self.cloud.play_audio())
    # audio_t.start()

    with self.lock:
    control hardware
        pass

        # if audio_t.is_alive():
    #    audio_t.join()


def main_loop(self):
    # 0. BOOT
    if self.state == STATE.BOOT:
        print("BOOT ON")
        self.state = STATE.IDLE
        self.HardWare.write(text="안녕?     \n 만나서 반가워")
    # 1. IDLE
    elif self.state == STATE.IDLE:
        print("IDLE")
        self.HardWare.write(text="노는중..", led=[0, 0, 0, 0, 0, 0])
        time.sleep(1)
        self.HardWare.write(text="노는중..", led=[40, 40, 40, 40, 40, 40])
        sensor_state = -2
        time.sleep(1)

        with self.lock:
            sensor_state = self.sensor_state  # 1.1 Get sensor state with thread Lock

            if sensor_state == 1:  # 1.2 change state and do action
                self.state = STATE.VOICE_REC
            elif sensor_state == 0:
                # TODO :Do idle action random
                # self.send_event("IDLE")
                # self.do_action()
                pass

            elif sensor_state == -1:
                self.state = STATE.WALL_FACE

    # 2. WALL_FACE
    elif self.state == STATE.WALL_FACE:
        print("WALL FACE")
        if self.send_event("WALL_FACE"):  # 2.1 do wall face action
            self.HardWare.write(text="something..\n make me blind", led=[0, 0, 0])
            self.do_action()
            pass

        time.sleep(2)
        sensor_state = -2
        with  self.lock:  # 2.2 Get sensor state with thread Lock
            sensor_state = self.sensor_state
            if sensor_state == 0:
                self.state = STATE.IDLE

    # 3. VOICE_REC
    elif self.state == STATE.VOICE_REC:
        with self.lock:

            state = self.stream_voice()  # 3.1 do stream voice

            if state == 0:  # 3.2 fail to recognize user voice
                print("NO HEAR")
                if self.send_event("NOT_HEAR"):
                    self.do_action()

            elif state == 1:  # 3.3 sucess and get chatbot response
                print(" DO SOTHING ")
                self.do_action()

            # 3.4 back to idle
            self.state = STATE.IDLE
"""
