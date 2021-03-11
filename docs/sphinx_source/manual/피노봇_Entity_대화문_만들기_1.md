# B. 개체(Entity)이용 챗봇 만들기 [1]

좀더 복잡하고 다양한 상황에서 작동하는 챗봇을 위해서 

개체 (Entity) 기능을 활용할수 있습니다. 


![](/_static/manual/2B_EntityIntent/목표.png)

이번에는 실제 커피종류와, 온도, 사이즈및 시럽여부등을 주문받고

해당 정보를 추출하는 대화문(Intent) 와 개채(Entity) 를 만들어 보겠습니다. 


## 1. 커피 메뉴판 

![](/_static/manual/2B_EntityIntent/01.png)

다음과 같은 커피 메뉴판을 예시로 들어보겠습니다. 

이 모든 경우에대해 챗봇을 개별로 제작하면 4X2X4X4 = 128가지의 대화의 경우가 나오게됩니다.

이를 모두 만들수는 없음으로 이를 개체(Entity) 를 통해서 처리할 수 있습니다.

개체(Entity) 는 문장에서 특정한 용도로 쓰이는 단어를 추출하기위해서 만드는 일종의 사전입니다. 

같은속성을 지닌 단어와 동의어들을 미리 정의를 해둠으로서 챗봇이 다양한 상황에서 단어를 이해할수 있게 해줍니다. 


## 2. 개체(Entity) 생성 및 작성

![](/_static/manual/2B_EntityIntent/02.png)


메인화면의 **"Entity"** 탭에 들어가서 **"Create Entity"** 버튼을 클릭, 새 개체(Entity)를 생성합니다 

![](/_static/manual/2B_EntityIntent/03.png)

개체(Entity) 작성은 다음과 같이 이루어집니다. 


### 2.a 개체(Entity) 작성 1

![](/_static/manual/2B_EntityIntent/04.png)


먼저 1번의 개체(Entity) 이름에는 이 단어들을 어떤 범주의 단어로 부를지 이름을 정합니다. 

간단하게  pino_drink로 작성을 했습니다. 


### 2.b 개체(Entity) 작성 2

![](/_static/manual/2B_EntityIntent/05.png)

그다음 2번에 이 **"pino_drink"** 라는 키워드로 처리하고싶은 단어들의 표준어 표현을 넣어줍니다. 

이 키워드로 우리는 음료를 구분하고 싶음으로 

**"카페아메리카노" , "카페라떼" , "카페모카" , "카라멜마끼아또"** 를 넣었습니다. 

그 다음에는 3번구역에 **동의어** 를 추가해줍니다, 

예를들면  **"카페아메리카노"를 "아메리카노" , "까페 아메리카노"** 라고도 많이 표현하고 
 
혹은 "그냥 커피" 라고 하시는 분이 있을수도 있음으로 이를 다이얼로그 플로우가 인식할 수 있게 동의어사전에 넣어줍니다. 

**동의어의 제일 첫 동의어는 표준어 표현이 자동으로 할당** 이 됩니다. 


### 2.c 개체(Entity) 작성 3

![](/_static/manual/2B_EntityIntent/06.png)

그리고 여기서 유연하게 **비슷한 단어도 인식하기 위해서** 3번 옵션을 체크하고 

4번의 **"세이브버튼"**을 누르면 개체(Entity)가 저장이 됩니다. 


<br>
<br>
<br>
<br>
<br>

## 3. 대화문(intent) 에서 개체(Entity) 사용 

![](/_static/manual/2B_EntityIntent/07.png)

자 그러면 이제 커피를 주문받는 인텐트를 만들어서 개체(Entity)를 실제 사용해 보겠습니다. 

Q : "아메리카노 주세요"  
 
A : "네 아메리카노 드리겠습니다" 

개체(Entity) 기능이 없다면 위의 메뉴판을 처리하려면 이런 인텐트를 수십개를 작성해야 하겠지만
 
개체(Entity)를 이용해서 이를 한가지로 통합할 수 있습니다. 


### 3.a 대화문(intent)  작성

![](/_static/manual/2B_EntityIntent/08.gif)

개체(Entity) 인식을 위해서는 Training Phases에서 어떤부분에 주문할 음료수(아메리카노)의 정보가 담겨있는지 설정해야합니다. 

"아메리카노 주세요" 에서는 **"아메리카노"** 에 정보가 담겨있음으로 이 부분을 드래그 해줍니다. 

그러면 자동으로 다음과 같이 검색창이 뜨는데 여기서 아까전 만든 **pino_drink** 를 검색해서 클릭합니다 


### 3.b 대화문(intent) 테스트 

![](/_static/manual/2B_EntityIntent/09.png)

그리고 저장버튼을 눌러서 테스트를 해보면 다음과 같이

**pino_drink**에 있던 모든 단어들을 "주세요" 하는 문장은 이 인텐트로 연결이 되게 됩니다. 

**주의**

> ![](/_static/manual/2B_EntityIntent/10.gif)

> entity 인식을 다이얼로그 플로우가 자동으로 진행하게 되면 종종 잘못된 entity로 인식이 됩니다
>
> 이경우에는 다음과 같이 삭제를 해주시면 됩니다. 


<br>
<br>
<br>
<br>
<br>

### 4. 답변에서 개체(Entity) 활용해보기  

다음은 인식된  개체(Entity)의 값을 대답에서 활용해 보겠습니다. 

![](/_static/manual/2B_EntityIntent/11.png)

인식된 개체(Entity) 는 인텐트에서 사용되는 변수로 인식되며

Action and parameters에 설정되어있고 $ 기호를 통해서 사용이 가능합니다.

![](/_static/manual/2B_EntityIntent/12.png)

다음과 같이 대화문을 작성하면 

$pino_drink 자리에는 다음과 같이 표준어 표현이 담겨서 처리되게 됩니다

![](/_static/manual/2B_EntityIntent/13.png)

표준어 표현이 아닌 입력단어 그대로 사용하려먼 $pino_drink.original 으로 사용하면 됩니다 

<br>
<br>
<br>
<br>
<br>

이제 다음장에서 여러개의 개체(Entity)를 이용한 대화문을 작성하는법을 알아보겠습니다.



