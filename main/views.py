import environ
import os
import json
from django.shortcuts import render
from pathlib import Path
from .models import Weatherdata,Soildata
# BASE_DIR 설정 (manage.py가 있는 Django 프로젝트 루트 경로)
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경 변수 로드
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))


def mainpage(request):
    base_context = get_region_context()

    sido = request.GET.get('sido')
    sigungu = request.GET.get('sigungu')
    eupmyeondong = request.GET.get('eupmyeondong')

    weather = None
    if sido and sigungu and eupmyeondong:
        weather = Weatherdata.objects.filter(
            sido=sido,
            sigungu=sigungu,
            eupmyeondong=eupmyeondong,
            year=2024,
            month=12
        ).first()  # 1개만 가져옴

    soil = None
    if sido and sigungu and eupmyeondong:
        for y in [2024,2023,2022]:
            soil = Soildata.objects.using('soildata').filter(
                sido=sido,
                sigungu=sigungu,
                eupmyeondong=eupmyeondong,
                year=y
            ).first()
            if soil:
                break

    base_context.update({
        'latitude': weather.latitude if weather else 37.5665,
        'longitude': weather.longitude if weather else 126.9780,
        'weather': weather,
        'soil' : soil
    })

    return render(request, 'main/mainpage.html', base_context)
    


def weatherpage(request):
    context = get_region_context()

    sido = request.GET.get('sido')
    sigungu = request.GET.get('sigungu')
    eupmyeondong = request.GET.get('eupmyeondong')

    weather_data = []

    if sido and sigungu and eupmyeondong:

        # 2024년 1월 ~ 12월 데이터 가져오기
        weather_data = Weatherdata.objects.filter(
            sido=sido,
            sigungu=sigungu,
            eupmyeondong=eupmyeondong,
            year=2024
        ).order_by('month')

        # ✅ 평균값 계산        
        if weather_data:
            fields = ['min_temp', 'max_temp', 'humidity', 'wind_speed', 'solar_radiation', 'avg_precipitation']
            averages = {}
            for field in fields:
                values = [
                    float(getattr(w, field))
                    for w in weather_data
                    if getattr(w, field) is not None and str(getattr(w, field)).replace('.', '', 1).replace('-', '', 1).isdigit()
                ]
                avg = round(sum(values) / len(values), 2) if values else None
                averages[field] = avg

            averages['year'] = 2024
            averages['month'] = '평균'
            context['weather_avg'] = averages

        context.update({
            'sido': sido,
            'sigungu': sigungu,
            'eupmyeondong': eupmyeondong,
            'weather_data': weather_data,
        })

    return render(request, 'main/weatherpage.html', context)

def soilpage(request):
    context = get_region_context()

    sido = request.GET.get('sido')
    sigungu = request.GET.get('sigungu')
    eupmyeondong = request.GET.get('eupmyeondong')

    if sido and sigungu and eupmyeondong:
        # 연도별 데이터 불러오기
        soil_2024 = Soildata.objects.using('soildata').filter(
            sido=sido, sigungu=sigungu, eupmyeondong=eupmyeondong, year=2024
        ).first()
        soil_2023 = Soildata.objects.using('soildata').filter(
            sido=sido, sigungu=sigungu, eupmyeondong=eupmyeondong, year=2023
        ).first()
        soil_2022 = Soildata.objects.using('soildata').filter(
            sido=sido, sigungu=sigungu, eupmyeondong=eupmyeondong, year=2022
        ).first()

        # 평균 계산
        soil_list = [soil_2024, soil_2023, soil_2022]
        fields = ['ph', 'organic_matter', 'available_phosphorus', 'potassium', 'calcium', 'magnesium', 'nitrogen']

        averages = {'year':'평균'}
        for field in fields:
            values = [
                getattr(s, field)
                for s in soil_list
                if s is not None and getattr(s, field) is not None
            ]
            averages[field] = round(sum(values) / len(values), 3) if values else None

        context.update({
            'soil_2024': soil_2024,
            'soil_2023': soil_2023,
            'soil_2022': soil_2022,
            'soil_avg': averages,  # ✅ 평균값 추가
            'soil_data': [s for s in soil_list if s],
            'sido': sido,
            'sigungu': sigungu,
            'eupmyeondong': eupmyeondong,
        })

    return render(request, 'main/soilpage.html', context)








def get_region_context():
    region_data = {
        '서울특별시': [
        '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구',
        '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구',
        '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구',
        '은평구', '종로구', '중구', '중랑구'
    ],
    '광주광역시': ['광산구', '남구', '동구', '북구', '서구'],
    '대구광역시': [
        '남구', '달서구', '동구', '북구', '서구', '수성구', '중구',
        '군위군', '달성군'
    ],
    '대전광역시': ['대덕구', '동구', '서구', '유성구', '중구'],
    '부산광역시': [
        '강서구', '금정구', '남구', '동구', '동래구', '부산진구', '북구', 
        '사상구', '사하구', '서구', '수영구', '연제구', '영도구', '중구', '해운대구', 
        '기장군'
    ],
    '세종특별자치시': [
        '고운동', '다정동', '대평동', '도담동', '반곡동', '보람동', '새롬동', '소담동', 
        '아름동', '종촌동', '한솔동', 
        '금남면', '부강면', '소정면', '연기면', '연동면', '연서면', '장군면', '전동면', '전의면', 
        '조치원읍'
    ],
    '울산광역시': ['남구', '동구', '북구', '중구', '울주군'],
    '인천광역시': [
        '계양구', '남동구', '동구', '미추홀구', '부평구', '서구', '연수구', '중구',
        '강화군', '옹진군'
    ],
    '강원도': ['강릉시', '동해시', '삼척시', '속초시', '원주시', '춘천시', '태백시',
    '고성군', '양구군', '양양군', '영월군', '인제군', '정선군', '철원군', '평창군', '홍천군', '화천군', '횡성군'],
    '경기도': ['가평군', '고양시', '과천시', '광명시', '광주시', '구리시', '군포시', '김포시', '남양주시', '동두천시', '부천시', '성남시', '수원시', '시흥시', '안산시', '안성시', '안양시',
            '양주시', '양평군', '여주시', '연천군', '오산시', '용인시', '의왕시', '의정부시', '이천시', '파주시', '평택시', '포천시', '하남시', '화성시'],
    '경상남도': ['거제시', '김해시', '마산시', '밀양시', '사천시', '양산시', '진주시', '창원시', '통영시',
            '거창군', '고성군', '남해군', '산청군', '의령군', '창녕군', '하동군', '함안군', '함양군', '합천군'],
    '경상북도': ['경산시', '경주시', '구미시', '김천시', '문경시', '상주시', '안동시', '영주시', '영천시', '포항시'
            '고령군', '군위군', '봉화군', '성주군', '영덕군', '영양군', '예천군', '울릉군', '울진군', '의성군', '청도군', '청송군', '칠곡군'],
    '전라남도': ['광양시', '나주시', '목포시', '순천시', '여수시',
            '강진군', '고흥군', '곡성군', '구례군', '담양군', '무안군', '보성군', '신안군', '영광군', '영암군', '완도군', '장성군', '장흥군', '진도군', '함평군', '해남군', '화순군'],
    '전라북도': ['군산시', '김제시', '남원시', '익산시', '전주시', '정읍시',
            '고창군', '무주군', '부안군', '순창군', '완주군', '임실군', '장수군', '진안군'],
    '충청남도': ['계룡시', '공주시', '논산시', '당진시', '보령시', '서산시', '아산시', '천안시',
            '금산군', '부여군', '서천군', '예산군', '청양군', '태안군', '홍성군'],
    '충청북도': ['제천시', '청주시', '충주시',
            '괴산군', '단양군', '보은군', '영동군', '옥천군', '음성군', '증평군', '진천군'],
    '제주특별자치도': ['서귀포시', '제주시'],
    }
    emd_data = {
        '춘천시' : ['신북읍', '동면','남산면','교동','효자동'],
        '김포시' : ['월곶면'],
        '남양주시' : ['진건읍'],
        '수원시' : ['서둔동'],
    }
    return {
        'region_json': json.dumps(region_data, ensure_ascii=False),
        'emd_json': json.dumps(emd_data, ensure_ascii=False),
        'kakao_api_key': env('KAKAO_API_KEY'),
    }
