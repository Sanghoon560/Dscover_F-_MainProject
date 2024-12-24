# Dscover_F_MainProject

## 영상 선정 기준


## 댓글 수집



## 스팸 댓글 기준


## LLM 학습


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


