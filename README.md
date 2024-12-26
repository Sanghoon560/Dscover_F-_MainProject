# Dscover_F_MainProject
LLM을 활용하여 기존 기술의 한계를 해결하고, 데이터를 체계적으로 수집·분석하여 보다 정확한 스팸 탐지 방식을 제안

## 영상 선정 기준
영상 선정을 위한 기준을 세우기 위한 상관관계 분석
- 스팸 댓글 판단 기준 임의로 선정:
   - 작성자 닉네임에 특정 키워드(예: I9, 19)가 포함된 경우
   - 동일한 내용의 댓글이 반복적으로 달린 경우
   - 텍스트 내 광고성 링크나 키워드 포함

### 주제별
<img width="685" alt="스크린샷 2024-12-26 오전 9 57 26" src="https://github.com/user-attachments/assets/82ec4410-e335-410c-bd74-1ab72dbe2707" />

### 인급동
- 인기 급상승 동영상일수록 스팸 댓글이 많이 달릴 것이다: 유의미한 상관관계 없음
  <img width="662" alt="스크린샷 2024-12-26 오전 9 49 33" src="https://github.com/user-attachments/assets/a8a2aeba-f61e-486c-a22c-10b7ad595139" />
    - Correlation between rank and spam count: -0.059206064661581265
    - P-value: PearsonRResult(statistic=-0.05920606466158123, pvalue=0.755969157241787)
 - 최근 영상일수록 스팸 댓글이 잘 발견되며, 수일이 경과하면 삭제될 것이다: 유의미한 상관관계 없음
   <img width="646" alt="스크린샷 2024-12-26 오전 9 49 20" src="https://github.com/user-attachments/assets/481fa493-7cf7-444f-9742-e036da4bc646" />
    - Pearson Correlation: 0.07674152918834265
    - P-value: 0.686900062588453
   

### 썸네일 자극도
- 썸네일의 자극도 측정
- Method: llama3.2-vision model을 이용하여, 기존의 CNN 모델과 달리, 텍스트와 이미지 모두를 분석하여, 자극도 점수를 0-9로 평가하도록 함. 

- 인기동영상의 댓글과 썸네일 간의 독립 여부 판별: 독립적
가설: "인기동영상의 댓글의 스팸 댓글의 개수와 썸네일의 자극도 점수는 독립이다"
Chi-Square Test 결과 p-value가 0.4로 accept.

- One-Way ANOVA 
가설:  "썸네일 자극도 effect는 존재하지 않는다."

### 연령대별
<img width="694" alt="스크린샷 2024-12-26 오전 9 55 59" src="https://github.com/user-attachments/assets/18beb71f-8426-4f46-842c-7cf9a4896b13" />

→ 유의미한 상관관계가 발견되지 않음.

### (2차 분석)
### 카테고리별
<img width="310" alt="스크린샷 2024-12-26 오전 10 00 39" src="https://github.com/user-attachments/assets/b96fbe8e-266b-4d35-bfcf-de8534591bfe" />

Shorts(43), Gaming(20), Entertainment(24), News & Politics(25), Film & Entertainment(1)에서 댓글 데이터 수집 및 분석

→ 카테고리별 댓글 수와 스팸 비율 간 유의미한 차이 없음

### 인물별
올해의 브랜드 대상 리스트를 기반으로 특정 인물 관련 채널에서 댓글 분석

→ 특정 인물과 스팸 비율 간 뚜렷한 관계 확인되지 않음

### 구글 트렌드
구글 트렌드에서 추출한 인기 검색어로 검색한 영상의 댓글 분석

→ 트렌드 키워드와 스팸 댓글 발생률 간의 명확한 상관관계 확인 불가

### 유료 광고 포함 여부
유료 광고 포함 여부와 스팸 비율 비교

→ 스팸 비율에 유의미한 차이 없음


결과:
- 특정 주제나 조건(인기 급상승, 최근 업로드, 자극적 썸네일 등)과 스팸 댓글 비율 간의 유의미한 상관관계 발견되지 않음.
- 데이터가 특정 가설을 뒷받침하지 않음에도 불구하고, 다양한 조건에서 스팸 댓글 탐지 기준을 검토할 기회 제공.

한계점:
- 크롤링 기준 설정의 한계로 인해 데이터의 다양성이 부족.
- 경험적 기준(닉네임 패턴, 반복 대댓글)으로 스팸 탐지를 라벨링했지만, 일부 오류 가능성 존재.

## 댓글 수집
크롤링 형식 통일:
<img width="961" alt="스크린샷 2024-12-26 오전 10 15 16" src="https://github.com/user-attachments/assets/ed1ab1ff-b116-4637-813d-75b51a8d6f30" />

## 스팸 댓글 기준


## LLM 
- Model: Gemini-1.5-Flash
- 이유: 다국어 지원, 빠른 무료 API 제공
  
- Self evaluation prompt optimization
- 
<img width="826" alt="framework" src="https://github.com/user-attachments/assets/1d524ee6-dd1e-422b-aed1-9ae880243ac9" />
![프롬프트_최적화결과](https://github.com/user-attachments/assets/4f947727-aabd-4b93-a3ae-0139b97c9b83)

- Binary Classification

<img width="741" alt="classification" src="https://github.com/user-attachments/assets/442a75d5-6fe5-4ab4-87c0-17de9d8754d4" />




## 기능 구현


