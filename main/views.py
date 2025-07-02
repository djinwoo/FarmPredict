import environ
import os
import json
from django.shortcuts import render
from pathlib import Path
from .models import Weatherdata,Soildata,Region,Cabbage,Onion
from django.http import JsonResponse
# BASE_DIR 설정 (manage.py가 있는 Django 프로젝트 루트 경로)
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경 변수 로드
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))

def safe_val(value):
    if value is None or str(value).strip().lower() in ('', 'nan'):
        return None  # 숫자 연산 전용 처리 위해 None 반환
    return value

def safe_mul(val, factor):
    try:
        if val is None:
            return '-'
        val = float(val)
        if val > 1e10:  # 너무 큰 값은 이상치로 간주
            return '-'
        return int(val * factor)
    except (ValueError, TypeError):
        return '-'

    
def mainpage(request):
    sido_list = Region.objects.using('default').values_list('sido', flat=True).distinct().order_by('sido')

    kakao_api_key = env('KAKAO_API_KEY')

    context = {
        'sido_list': sido_list,
    }

    sido = request.GET.get('sido')
    sigungu = request.GET.get('sigungu')
    eupmyeondong = request.GET.get('eupmyeondong')

    SPECIAL_REGIONS = [
        ("대구광역시", "북구"),
        ("포항시", "북구"),
        ("서울특별시", "서초구"),
        ("부산광역시", "강서구"),
        ("경기도", "용인시 처인구"),
    ]

    weather = None
    if sido and sigungu:
        is_special = (sido, sigungu) in SPECIAL_REGIONS

        # ✅ 날씨 조회
        weather_qs = Weatherdata.objects.using('climate').filter(
            sido=sido,
            sigungu=sigungu,
            year=2025,
            month=5
        )
        if not is_special and eupmyeondong:
            weather_qs = weather_qs.filter(eupmyeondong=eupmyeondong)

        weather = weather_qs.first()

    soil = None
    if sido and sigungu and eupmyeondong:
        for y in [2024, 2023, 2022]:
            soil = Soildata.objects.using('soil').filter(
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
        'latitude': soil.latitude if soil else 37.5665,
        'longitude': soil.longitude if soil else 126.9780,
        'kakao_api_key': kakao_api_key,
    })

    return render(request, 'main/mainpage.html', context)

def weatherpage(request):
    context = get_region_context()

    sido = request.GET.get('sido')
    sigungu = request.GET.get('sigungu')
    eupmyeondong = request.GET.get('eupmyeondong')
    selected_years = request.GET.getlist('year')

    weather_data = []
    selected_years_int = []
    year_list = list(range(2015, 2026))  # 연도 고정

    if sido and sigungu and eupmyeondong:
        base_qs = Weatherdata.objects.using('climate') \
            .filter(sido=sido, sigungu=sigungu, eupmyeondong=eupmyeondong)

        if selected_years:
            selected_years_int = list(map(int, selected_years))
            base_qs = base_qs.filter(year__in=selected_years_int)  # ✅ 필드명 수정

        weather_data = base_qs.order_by('-year', 'month')

    context.update({
        'sido': sido,
        'sigungu': sigungu,
        'eupmyeondong': eupmyeondong,
        'weather_data': weather_data,
        'year_list': year_list,
        'selected_years': selected_years_int,
    })

    return render(request, 'main/weatherpage.html', context)



def soilpage(request):
    context = get_region_context()

    sido = request.GET.get('sido')
    sigungu = request.GET.get('sigungu')
    eupmyeondong = request.GET.get('eupmyeondong')

    if sido and sigungu and eupmyeondong:
        # 연도별 데이터 불러오기
        soil_2024 = Soildata.objects.using('soil').filter(
            sido=sido, sigungu=sigungu, eupmyeondong=eupmyeondong, year=2024
        ).first()
        soil_2023 = Soildata.objects.using('soil').filter(
            sido=sido, sigungu=sigungu, eupmyeondong=eupmyeondong, year=2023
        ).first()
        soil_2022 = Soildata.objects.using('soil').filter(
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

def cabbagepage(request):

    return render(request, 'main/cabbagepage.html')

def onionpage(request):

    return render(request, 'main/onionpage.html')

def cabbagepage(request):
    selected_years = request.GET.getlist('year')  # ?year=2018&year=2020 형태로 받기

    # 🔍 연도 필터링 조건 추가
    if selected_years:
        selected_years = list(map(int, selected_years))
        cabbage_qs = Cabbage.objects.using('cabbage').filter(year__in=selected_years).order_by('-year', 'region')
    else:
        cabbage_qs = Cabbage.objects.using('cabbage').all().order_by('-year', 'region')

    cabbage_data = [{
        'region': safe_val(obj.region),
        'year': safe_val(obj.year),
        'yield_per_10a': safe_val(obj.yield_per_10a),
        'total_production': safe_mul(obj.total_production, 1000),
    } for obj in cabbage_qs]

    # 🔢 연도 리스트 (2013~2024 하드코딩 or DB에서 추출 가능)
    year_list = list(range(2013, 2025))

    context = {
        'cabbage_data': cabbage_data,
        'year_list': year_list,
        'selected_years': selected_years,
    }
    return render(request, 'main/cabbagepage.html', context)

def onionpage(request):
    selected_years = request.GET.getlist('year')  # ?year=2018&year=2020 형태로 받기

    # 🔍 연도 필터링 조건 추가
    if selected_years:
        selected_years = list(map(int, selected_years))
        onion_qs = Onion.objects.using('onion').filter(year__in=selected_years).order_by('-year', 'region')
    else:
        onion_qs = Onion.objects.using('onion').all().order_by('-year', 'region')

    onion_data = [{
        'region': safe_val(obj.region) or '-',
        'year': safe_val(obj.year) or '-',
        'yield_per_10a': safe_val(obj.yield_per_10a) or '-',
        'total_production': safe_mul(safe_val(obj.total_production), 1000),
    } for obj in onion_qs]

    year_list = list(range(2015, 2025))  # 연도 리스트

    context = {
        'onion_data': onion_data,
        'year_list': year_list,
        'selected_years': selected_years,
    }
    return render(request, 'main/onionpage.html', context)




