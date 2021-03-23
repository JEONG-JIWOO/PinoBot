#include <SoftwareSerial.h>

SoftwareSerial mySerial(2, 3); // RX, TX


String example = "event_name:humidity_event|humidity:50|temp:12.3|cds:";
String rcv_msg = "";
char rcv_data[3];
int state =  0; 
/*  상태 종류 
 *  0 메세지 전송 가능  
 *  1 라즈베리파이 응답 대기 
 *  2 라즈베리파이 응답 수신완료
 */
int i = 0;
int timeout = 20000;  // 응답 대기 최대시간 (msec)
unsigned long wait_start = 0;

bool parse_string(String rcv_msg);

void setup()
{
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  mySerial.begin(115200);
  Serial.println("Serial Start!");
}

void loop() // run over and over
{
  serialCheck();         //  라즈베리파이 상태 확인 
  
  if (state == 0)        //  라즈베리파이에 전송가능, 
  {
    int cds =  analogRead(A0);
    if(cds > 450 and state == 0)
    {
      mySerial.print(example+String(cds));
      delay(1);
      Serial.println("dflow msg send : "+ example+String(cds));  // 메세지 전송
      state = 1;   // 메세지 중복전송 방지를 위해 상태 변경
      wait_start = millis();
      delay(1); 
    }
  }
  else if (state == 2)   // 라즈베리파이로부터 응답 수신 
  {
    Serial.println("[2] TODO : Do something .. " );  // 응답에 따른 액션
    if (rcv_msg = "measure_temp")
    {
      int cds =  analogRead(A0);
      mySerial.print(example+String(cds));
      delay(1);
      Serial.println("dflow msg send : "+ example+String(cds));  // 메세지 전송
      state = 1;   // 메세지 중복전송 방지를 위해 상태 변경
      wait_start = millis();
      delay(1); 
    }
    state = 0;     // 초기 상태로 복귀 
  }
}


void serialCheck()
{
  if (mySerial.available())          // Case 1. 라즈베리파이와 시리얼통신 연결됬을경우, 
  {
    rcv_msg = "";
    while(mySerial.available())
      rcv_msg += mySerial.readString();
    
    if (rcv_msg.equals("ready"))           // Case 1.1 시리얼 메세지가 준비완료 메세지일경우
    {
        state = 0;
        Serial.println("[0] raspi ready!  set to idle  " +rcv_msg);
    }
    else if (parse_string(rcv_msg))   // Case 1.2 시리얼 메세지 파싱에 성공한경우 
    {
        state = 2;  
        Serial.println("[2] Parse success!  msg: [" +rcv_msg+"]");
    }
    else                              // Case 1.4 메세지 파싱에 실패한경우
    {    
        state = 0;
        Serial.println("[0] Parse Fail!  return to idle " +rcv_msg);   
    }
  }
  else                                // Case 2. 라즈베리파이와 시리얼 연결되지 않음.         
  {
    i++;
    if (i % 20000 == 0){
      Serial.println("["+String(state)+ "] wait..");    
      i = 0;
    }
  }

  if ((state == 1) and ( millis() - wait_start  > timeout) )
  {
      Serial.println("[1] Timeout! return to idle ");   
      state = 0;
  }
}

bool parse_string(String rcv_msg)
{
  /*  데이터 형식
   *  $stt_result|$intent_name|$intent_response|$number_of_parameter|$parameter_strings.. 
   *  
   *  ex1 파라미터 0개일때: 
   *    안녕하세요|Welcome|반가워요|0
   *      stt결과 : 안녕하세요
   *      dialogflow 인텐트 이름  : Welcome
   *      dialogflow 응답 텍스트  : 반가워요
   *      dialogflow 파라미터 개수 : 0 
   *    
   *    
   *  ex2 파라미터 1개일때: 
   *    안녕하세요|Welcome|반가워요|1|play_sound:1.wav|
   *      dialogflow 파라미터 개수 : 1
   *      파라미터1 이름 : play_sound
   *      파라미터1 값   : 1.wav 
   *    
   *    
   *  ex2 파라미터 2개일때: 
   *    안녕하세요|Welcome|반가워요|2|play_sound:1.wav|temp:30
   *      dialogflow 파라미터 개수 : 2
   *      
   *      파라미터1 이름 : play_sound
   *      파라미터2 값   : 1.wav 
   *      파라미터2 이름 : temp
   *      파라미터2 값   : 30 
   *      
   *  TODO : 메세지 내용 파싱후 전역변수로 저장. 
   */
   
  return true;
}
