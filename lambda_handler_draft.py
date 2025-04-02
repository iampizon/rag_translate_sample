import json
import boto3

bedrock_runtime = boto3.client('bedrock-runtime')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

def lambda_handler(event, context):
    model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    kb_id = "I7LVTCMYM3"
    max_tokens = 1000
    query_text = "활잽이 그로아 뭐 있음?"
    try:
        # 검색 요청 구성
        retrieve_response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={
                'text': query_text
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 3,
                    'overrideSearchType': 'SEMANTIC'                    
                }
            }
        )
        
        # 검색 결과 확인
        retrieved_results = retrieve_response.get('retrievalResults', [])
        
        if not retrieved_results:
            print("검색 결과가 없습니다.")
            return None
        
        # 검색 결과를 컨텍스트로 사용
        context = ""
        for i, result in enumerate(retrieved_results):
            content = result['content']['text']
            source = result.get('location', {}).get('s3Location', {}).get('uri', '알 수 없는 소스')
            score = result.get('score', 0)
            
            context += f"\n\n참고 문서 {i+1} (관련성 점수: {score}):\n{content}\n"
            print(f"검색 결과 {i+1}: 관련성 점수 {score}")
        
        # Claude에 질의 구성
        prompt = f"""
당신은 전문적인 게임 콘텐츠 번역가로서 MMORPG, FPS, MOBA 등 다양한 게임 장르의 번역에 특화되어 있습니다. 사용자가 제공하는 게임 채팅이나 콘텐츠를 자연스러운 인터넷 채팅 스타일로 번역하는 작업을 담당합니다.

## 번역 가이드라인
- 게임 용어 처리: 
게임 특화 용어(스킬, 아이템, 던전명 등)는 공식 로컬라이징 용어를 최우선적으로 사용
서버, 클래스, 직업명 등 게임 시스템 요소는 정확한 게임 용어로 번역
공식 번역어가 어색하더라도 게이머들이 실제 사용하는 통용어를 참고하여 적용

- 채팅 스타일 반영:
'gg', 'wp', 'ez', 'afk' 같은 게임 약어 혹은 'ㅋㅋㅋ', 'ㅠㅠ' 같은 특정 언어에서의 채팅 표현은 'lol', 'lmao', 'T_T' 등 상응하는 표현으로 변환
'탱커 구함', '힐러 2명 픽업' 같은 파티 모집 용어는 게임별 관례에 맞게 번역

- 인터넷 채팅 특성 반영:
문법적으로 완벽하지 않은 채팅체를 자연스럽게 유지
단어 축약(gonna, wanna, u, r 등), 속어, 신조어 적극 활용
대소문자 강조(NICE, GG)와 이모티콘(:D, xD, <3) 문화 차이 반영
과도한 문장부호(!!!, ???)나 이모티콘 사용 패턴 유지

-용어 미확인 시 처리:
게임 전용 은어는 대상 언어권 게이머들이 쓰는 상응 표현으로 대체
번역이 확실하지 않은 신조어는 의미 설명 후 괄호 안에 원문 표기
서버/게임 특화 밈이나 문화 요소는 간략한 설명 추가 가능

## 번역 정보
목표 언어: 영어 콘텐츠 유형: 게임 채팅/콘텐츠

## 여기 검색 결과를 참조하여 번역을 진행하세요: {context}

결과
입력된 게임 채팅을 위의 가이드라인에 따라 영어로 번역해주세요. 게이머들이 실제로 사용할 법한 자연스러운 표현과 생동감 있는 채팅체로 번역하되, 게임 용어의 정확성은 유지해주세요.
입력된 게임 채팅: {query_text}

답변:
"""
        
        # Claude에 질의 요청 (수정된 부분)
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            inferenceConfig={
                "maxTokens": max_tokens,
                "temperature": 0.7,
                "topP": 0.9
            }
        )
        
        # 응답 추출 및 반환
        print(response)
        answer = response['output']['message']['content'][0]['text'] 
    except Exception as e:
        print(f"쿼리 실행 중 오류 발생: {e}")
        return None
    return {
        'statusCode': 200,
        'body': answer
    }
