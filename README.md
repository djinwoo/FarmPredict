# FarmPredict
농촌진흥청 작물 생산량 예측 서비스

원하는 지역의 토양 정보와 기상 데이터, 그리고 작물에 영향을 미치는 변수들을 활용하여 해당 지역의 작물 생산량을 예측

# Django 프로젝트 설정 및 실행 가이드

이 문서는 Django 프로젝트를 실행하는 방법을 단계별로 설명합니다.

## 🛠 가상환경 설정

1. **가상환경 생성**
    ```
    python -m venv venv
    ```
2. **가상환경 활성화**
    - **Windows**:
      ```
      source venv\Scripts\activate
      ```
    - **Mac/Linux**:
      ```
      source venv/bin/activate
      ```

## 📦 필수 패키지 설치

```
pip install -r requirements.txt
```

## 📂 데이터베이스 마이그레이션

```
python manage.py makemigrations
python manage.py migrate
```

## 🚀 서버 실행

```
python manage.py runserver
```