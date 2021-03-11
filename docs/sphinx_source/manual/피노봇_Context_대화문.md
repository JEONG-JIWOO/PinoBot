# D. Context[문맥] 이용, 대화문 이어나가기

우리가 대화를 할때는 문맥도 중요합니다 

방금전까지 저녁메뉴에대해 이야기하고있다가

갑자기 어제본 유튜브 영상을 이야기하면 당황스럽겠죠.

다이얼로그 플로우는 이 문맥(Context)르 활용해서 한가지 주제에 대해서 대화를 이어나갈수 있는 기능을 지원합니다. 

그러면 이 문맥(Context)을 한번 방금전만든 커피주문 대화문(intent)에 적용을 해보겠습니다. 




## 1. 주문 성공, 주문 실패 대화문(intent) 


![](/_static/manual/2D_ContextIntent/01.png)


손님이 커피를 주문했을때 다음과같이 성공하는경우가 많겠지만



![](/_static/manual/2D_ContextIntent/02.png)

가끔은 다음과 같이 실패하는 경우에는 다시 주문을 받아야합니다. 



![](/_static/manual/2D_ContextIntent/03.png)

![](/_static/manual/2D_ContextIntent/04.png)

그래서 다음과같이 주문성공 & 주문실패 대화문(intent)을 만들어 봅시다.




## 2. 대화문(intent) 간의 혼동문제

그런데 주문실패 대화문(intent) 에는 한가지 문제가 있습니다. 

"아니" 가 들어간 대부분의 대화가 주문실패 대화문으로 연결되면서 



![](/_static/manual/2D_ContextIntent/05.png)

다음과 같이 엉뚱한 대답을 내놓는경우도 발생합니다. 




![](/_static/manual/2D_ContextIntent/06.png)

다이얼로그 플로우는 다음과같이 여러개의 대화문(intent) 중에서 가장 유사한 대화문(intent)을 실행할 뿐

그 이전의 상황이나 문맥이 어떗는지는 잘 모르기 때문입니다. 

다이얼로그 플로우는 그래서 수동으로 이 문맥을 지정하는 기능을 지원합니다. 


## 3. 문맥(Context) 만들기 

### 3.a 커피주문 인텐트 

![](/_static/manual/2D_ContextIntent/07.png)

먼저 커피주문인텐트로 들어가서 제일 상단의 context 메뉴를 누르고 

output context에 "coffee"를 추가해줍니다. 

이는 이 대화문이 발동된이후 

"coffee"에 대해서 대화를 나누고 있다고 다이얼로그 플로우를 설정하게 됩니다. 


### 3.b 주문성공 인텐트 

![](/_static/manual/2D_ContextIntent/08.png)

그리고 주문성공 인텐트에서 역시 상단의 context 메뉴를 누르고 

이번에는 input context에 "coffee"를 추가해줍니다. 

이는 "coffee"에 대해서 대화를 나누고 있을경우에만, (다이얼로그 플로우가 coffee 라는 context를 가지고 있을떄만)

이 대화문(intent) 를 발동시키겠다는 의미입니다. 

### 3.c 주문실패 인텐트 

![](/_static/manual/2D_ContextIntent/09.png)

주문실패 인텐트도 위의 주문성공 인텐트와 동일하게 추가해줍니다. 




## 4. 작동원리 


![](/_static/manual/2D_ContextIntent/11.png)

다이얼로그 플로우는 기본적으로 어떠한 단기기억없이 문맥을 이해하지못하고 

다음과같이 매번 새 대화를 반복합니다. 


### 4.a 문맥(context)를 추가했을 경우 

![](/_static/manual/2D_ContextIntent/12.png)

문맥(context)를 추가하면 처음 대화문에는 큰 차이가 없습니다. 

하지만 대화문을 종료할때 context "coffee"를 기억하게되고 

그 다음대화를 진행할때 input context로 "coffee"가 있는 대화문(intent)만 발동시키게 됩니다. 


### 4.b 문맥(context)이 있는 인텐트는 문맥없이는 실행이 불가능

![](/_static/manual/2D_ContextIntent/13.png)


이렇게 문맥(context)이 추가가되면 그 대화문(intent)은 해당 input context없이는 실행이 되지 않습니다. 

![](/_static/manual/2D_ContextIntent/10.png)

다음과 같은 대화를 테스트해보면 

![](/_static/manual/2D_ContextIntent/14.png)

"아니오"라는 질문으로 주문실패 인텐트를 실행해 보려하지만 "Default Fallback Intent"가 실행되면서 이해 못한 인텐트로 인식하는것을 알 수있습니다. 



## 5. 정리 


문맥(context)는 다이얼로그 플로우의 대화문을 일정조건에서만 발동되게해주는 일종의 메모리입니다. 

대화문이 늘어날수록 이 문맥(context)기능을 사용하면 편리하게 챗봇을 설계할 수 있습니다. 