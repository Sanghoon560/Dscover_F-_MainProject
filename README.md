# Dscover_F_MainProject
LLM을 활용하여 기존 기술이 대댓글과 댓글의 구조적 차이를 충분히 반영하지 못했던 한계를 해결하고, 데이터를 체계적으로 수집·분석하여 보다 정확한 스팸 탐지 방식을 제안

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
- 인기동영상의 댓글과 썸네일 간의 독립 여부 판별: 독립적

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


## LLM 학습
모델 선정: Gemini-1.5
- 이유

데이터: 부모 댓글과 자식 댓글(대댓글)을 JSON 형식으로 저장

방법:


## 기능 구현


------
1. 작업환경 세팅
레포지토리 복제
```git 
git clone https://github.com/Sanghoon560/Dscover_F_MainProject
```

각자의 브렌치로 이동  (각자의 깃허브 내 이름으로 브렌치 생성했습니다)
```git
git checkout -b <your-branch-name>
```


2. 결과물 올리기 (simple version)
```
git add .
```

```
git commit -m "{전달내용}"
```

```
git push origin <your-branch-name>
```
**주의** main으로는 push 하지 않도록 주의!


3. 업데이트 가져오기 (작업 시작 전에 한번씩 하기)
   
(1) 자신이 작업 중인 브렌치에서
```
git pull origin <your-branch-name>
```

(2) main 브렌치 업데이트 사항 가져오기
main으로 이동

```git
git checkout -b main
```
main 변경사항 가져오기
```git
git pull origin main
```
자신의 브렌치로 돌아가서 작업하기

```git
git checkout -b <your-branch-name>
```


