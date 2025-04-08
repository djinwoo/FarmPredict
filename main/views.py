import environ
import os
import json
from django.shortcuts import render
from pathlib import Path
from .models import Weatherdata,Soildata,Region
from django.http import JsonResponse
# BASE_DIR 설정 (manage.py가 있는 Django 프로젝트 루트 경로)
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경 변수 로드
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))


def mainpage(request):
    sido_list = Region.objects.using('default').values_list('sido', flat=True).distinct().order_by('sido')

    kakao_api_key = env('KAKAO_API_KEY')

    context = {
        'sido_list': sido_list,
    }

    sido = request.GET.get('sido')
    sigungu = request.GET.get('sigungu')
    eupmyeondong = request.GET.get('eupmyeondong')

    weather = None
    if sido and sigungu and eupmyeondong:
        weather = Weatherdata.objects.using('test').filter(
            sido=sido,
            sigungu=sigungu,
            eupmyeondong=eupmyeondong,
            year=2024,
            month=12
        ).first()

    soil = None
    if sido and sigungu and eupmyeondong:
        for y in [2024, 2023, 2022]:
            soil = Soildata.objects.using('soildata').filter(
                sido=sido,
                sigungu=sigungu,
                eupmyeondong=eupmyeondong,
                year=y
            ).first()
            if soil:
                break

    context.update({
        'sido': sido,
        'sigungu': sigungu,
        'eupmyeondong': eupmyeondong,
        'weather': weather,
        'soil': soil,
        'latitude': weather.latitude if weather else 37.5665,
        'longitude': weather.longitude if weather else 126.9780,
        'kakao_api_key': kakao_api_key,
    })

    return render(request, 'main/mainpage.html', context)


def weatherpage(request):
    context = get_region_context()

    sido = request.GET.get('sido')
    sigungu = request.GET.get('sigungu')
    eupmyeondong = request.GET.get('eupmyeondong')

    weather_data = []

    if sido and sigungu and eupmyeondong:

        # 2024년 1월 ~ 12월 데이터 가져오기
        weather_data = Weatherdata.objects.using('test').filter(
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

def get_sigungu(request):
    sido = request.GET.get('sido')
    sigungu_list = Region.objects.using('default').filter(sido=sido).values_list('sigungu', flat=True).distinct().order_by('sigungu')
    return JsonResponse({'sigungu_list': list(sigungu_list)})


def get_eupmyeondong(request):
    sido = request.GET.get('sido')
    sigungu = request.GET.get('sigungu')
    emd_list = Region.objects.using('default').filter(sido=sido, sigungu=sigungu).values_list('eupmyeondong', flat=True).distinct().order_by('eupmyeondong')
    return JsonResponse({'eupmyeondong_list': list(emd_list)})

def get_region_context():
    from .models import Region
    sido_list = Region.objects.using('default').values_list('sido', flat=True).distinct().order_by('sido')

    # 시도-시군구 매핑
    region_data = {}
    emd_data = {}

    for sido in sido_list:
        sigungus = Region.objects.using('default').filter(sido=sido).values_list('sigungu', flat=True).distinct()
        region_data[sido] = list(sigungus)

        for sigungu in sigungus:
            eupmyeons = Region.objects.using('default').filter(sido=sido, sigungu=sigungu).values_list('eupmyeondong', flat=True).distinct()
            emd_data[sigungu] = list(eupmyeons)

    return {
        'region_json': json.dumps(region_data, ensure_ascii=False),
        'emd_json': json.dumps(emd_data, ensure_ascii=False),
    }
