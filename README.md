# AWS 서버리스 서비스로 게임용 번역 API 구현하기
## 준비

* 다음 워크샵을 완료하고, 번역에 사용할 RAG model 생성을 준비합니다.

  [Easy Vector & Graph RAG 구현하기](https://catalog.us-east-1.prod.workshops.aws/workshops/9d4a1859-434f-4f79-902b-dd1ad020adef/ko-KR/20-start/00-setup)

* 다음 워크샵에서 Lambda, API-Gateway 생성 실습을 완료합니다.

  [AWS 서버리스 애플리케이션의 진화 : 대용량 트래픽도 서버리스로 처리할 수 있습니다!](https://github.com/aws-samples/the-evolution-of-aws-serverless-applications)

  1. [나의 첫 AWS Lambda](https://github.com/aws-samples/the-evolution-of-aws-serverless-applications/blob/main/module1/README.md) : AWS Lambda 를 사용해본 적 없는 분들을 위한 기초 과정입니다. 이미 Lambda 에 익숙하다면 진행하지 않아도 괜찮습니다. 다음 아키텍처와 같이 Lambda 를 활용해 단순한 자동화 프로세스를 구축해봅니다.
  
  2. [본격 REST API 기반 서버리스 애플리케이션 개발](https://github.com/aws-samples/the-evolution-of-aws-serverless-applications/blob/main/module2/README.md) : 본격적으로 AWS Lambda 를 활용해 서버리스 애플리케이션을 만들어 봅니다. 가장 많이 활용되는 형태인 Amazon API Gateway 의 REST API 구축에 AWS Lambda 를 활용하는 방법을 알아봅니다.
  
  3. [서버리스 애플리케이션의 DB 사용 경험 개선](https://github.com/aws-samples/the-evolution-of-aws-serverless-applications/blob/main/module3/README.md) : 앞서 Module 2 에서 개발한 REST API 기반 서버리스 애플리케이션의 DB 사용 경험을 개선합니다. Amazon RDS Proxy 를 통해 DB 커넥션을 효과적으로 관리하고 AWS Secrets Manager 를 통해 보안을 강화해봅니다.
  
  4. [서버리스 애플리케이션 코드 최적화 및 부하 테스트](https://github.com/aws-samples/the-evolution-of-aws-serverless-applications/blob/main/module4/README.md) : Moduel 2, 3 에서 개발한 서버리스 애플리케이션을 최적화하고 테스트합니다. 우선 AWS Lambda 의 코드 최적화를 통해 실행 시간을 단축하여 성능을 개선합니다. 또한 Locust 오픈 소스  부하 테스트 도구를 통해 부하를 줌으로써 Lambda 의 Scaling 동작을 확인하고, Provisioned Concurrency 설정으로 Cold Start 를 줄여 실행 시간을 최적화 해봅니다
  5. [서버리스 애플리케이션 추적 및 성능 모니터링](https://github.com/aws-samples/the-evolution-of-aws-serverless-applications/blob/main/module5/README.md) : 서버리스 애플리케이션에 AWS X-Ray를 연동하여 애플리케이션의 구성 요소를 시각화 하고 성능 및 오류 디버깅에 필요한 정보를 확인해봅니다. 클라이언트에서 보낸 요청이 Amazon API Gateway, AWS Lambda 그리고 SQL 쿼리문에서 소요된 레이턴시 정보 및 각 구간별 요청에 대한 상태 정보를 확인 해봅니다.
   

## 구현

1. Lambda 생성

    [lambda_handler_draft.py](https://github.com/iampizon/rag_translate_sample/blob/main/lambda_handler_draft.py) 파일로 새 Lambda 함수를 생성

2. KnowledgeBase ID 변경
  ```python
    model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    kb_id = "YUKIWF6M8T"
  ```
   
3. Text event 구현 및 테스트
4. Lambda 실행시간 늘리기 및 Role 추가
5. API-Gateway 생성 및 배포
6. Lamba 함수에 Parameter 추가
   
    ```python
    def lambda_handler(event, context):

      print(event)

      query_params = event.get('queryStringParameters', {})
      query_text = query_params.get('query_text', '')
   ```

   
8. 브라우져에서 테스트 해보기
9. 시스템 프롬프트 분리하기
   [lambda_handler_last.py](https://github.com/iampizon/rag_translate_sample/blob/main/lambda_handler_last.py) 파일 참고

   ```python
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
   ```

   ```python
   # Claude에 질의 구성
    prompt = read_file("./system_prompt.txt")
    prompt = prompt.replace("{context}", context).replace("{query}", query_text)
   ```
    
11. 시스템 프롬프트 다듬기
    [system_prompt_last.py](https://github.com/iampizon/rag_translate_sample/blob/main/system_prompt_last.py) 파일 참고


## 추가 자료

* [서버리스 웹 애플리케이션 워크샵](https://github.com/aws-samples/aws-serverless-workshops-kr/tree/master/WebApplication)
* [Best practices for working with AWS Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
