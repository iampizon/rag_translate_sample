import json
import boto3

bedrock_runtime = boto3.client('bedrock-runtime')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

def read_file(file_path):
    """Load system prompt from a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Warning: System prompt file not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading system prompt file: {str(e)}")
        return None

def lambda_handler(event, context):

    print(event)

    query_params = event.get('queryStringParameters', {})
    query_text = query_params.get('query_text', '')

    model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    kb_id = "YUKIWF6M8T"
    max_tokens = 1000
    #query_text = "활잽이 그로아 뭐 있음?"
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
        prompt = read_file("./system_prompt.txt")
        prompt = prompt.replace("{context}", context).replace("{query}", query_text)
        
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
