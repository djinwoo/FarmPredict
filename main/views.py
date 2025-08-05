import environ
import os
import json
from django.shortcuts import render
from pathlib import Path
from . import models
from .models import Region, Weatherdata, Soildata, Cabbage, Onion
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

MODEL_MAP = {
    'access_cm2': models.AccessCm2,
    'access_esm1_5': models.AccessEsm1_5,
    'canesm5': models.CanEsm5,
    'cnrm_cm6_1': models.CnrmCm6_1,
    'cnrm_esm2_1': models.CnrmEsm2_1,
    'ec_earth3': models.EcEarth3,
    'gfdl_esm4': models.GfdlEsm4,
    'inm_cm4_8': models.InmCm4_8,
    'inm_cm5_0': models.InmCm5_0,
    'ipsl_cm6a_lr': models.IpslCm6aLr,
    'kace_1_0_g': models.Kace1_0G,
    'miroc6': models.Miroc6,
    'miroc_es2l': models.MirocEs2l,
    'mpi_esm1_2_hr': models.MpiEsm1_2Hr,
    'mpi_esm1_2_lr': models.MpiEsm1_2Lr,
    'mri_esm2_0': models.MriEsm2_0,
    'noresm2_lm': models.NorEsm2Lm,
    'ukesm1_0_ll': models.UkEsm1_0Ll,
}
# main/views.py

from django.shortcuts import render
from . import models
import json

# settings.py의 DB 별칭과 실제 모델 클래스를 매핑하는 딕셔너리
MODEL_MAP = {
    'access_cm2': models.AccessCm2,
    'access_esm1_5': models.AccessEsm1_5,
    'canesm5': models.CanEsm5,
    'cnrm_cm6_1': models.CnrmCm6_1,
    'cnrm_esm2_1': models.CnrmEsm2_1,
    'ec_earth3': models.EcEarth3,
    'gfdl_esm4': models.GfdlEsm4,
    'inm_cm4_8': models.InmCm4_8,
    'inm_cm5_0': models.InmCm5_0,
    'ipsl_cm6a_lr': models.IpslCm6aLr,
    'kace_1_0_g': models.Kace1_0G,
    'miroc6': models.Miroc6,
    'miroc_es2l': models.MirocEs2l,
    'mpi_esm1_2_hr': models.MpiEsm1_2Hr,
    'mpi_esm1_2_lr': models.MpiEsm1_2Lr,
    'mri_esm2_0': models.MriEsm2_0,
    'noresm2_lm': models.NorEsm2Lm,
    'ukesm1_0_ll': models.UkEsm1_0Ll,
}

def futuredatapage(request):
    # --- 1. 사용자가 선택한 필터 값 가져오기 ---
    selected_model_db = request.GET.get('main_scenario', '')
    selected_sub_scenario = request.GET.get('sub_scenario', '')
    start_year = request.GET.get('start_year', '')
    end_year = request.GET.get('end_year', '')
    selected_sido = request.GET.get('sido', '')
    selected_sigungu = request.GET.get('sigungu', '')

    # --- 2. 템플릿에 전달할 변수들 초기화 ---
    context = {
        'results': [],
        'sub_scenario_list': [],
        'year_list': [],
        'sido_list': [],
        'location_data_json': '{}',
    }

    # --- 3. 동적 모델 선택 및 데이터 처리 ---
    TargetModel = MODEL_MAP.get(selected_model_db)
    if TargetModel:
        # --- 3-1. 드롭다운 옵션은 모델이 선택되면 항상 생성 ---
        base_queryset = TargetModel.objects.all()
        context['sub_scenario_list'] = base_queryset.values_list('sub_scenario', flat=True).distinct()
        context['year_list'] = base_queryset.values_list('year', flat=True).distinct().order_by('year')
        
        location_data = {}
        locations = base_queryset.values('sido', 'sigungu').distinct()
        for loc in locations:
            if loc['sido'] not in location_data:
                location_data[loc['sido']] = []
            if loc['sigungu'] not in location_data[loc['sido']]:
                location_data[loc['sido']].append(loc['sigungu'])
        
        context['sido_list'] = sorted(location_data.keys())
        context['location_data_json'] = json.dumps(location_data, ensure_ascii=False)

        # --- 3-2. '검색' 버튼을 눌렀을 때만 최종 결과 조회 ---
        # HTML의 <button name="search" value="true"> 에서 'search' 파라미터가 넘어왔는지 확인
        if 'search' in request.GET:
            results_queryset = TargetModel.objects.all()

            # 필터링 로직 적용
            if selected_sub_scenario:
                results_queryset = results_queryset.filter(sub_scenario=selected_sub_scenario)
            if start_year:
                results_queryset = results_queryset.filter(year__gte=start_year)
            if end_year:
                results_queryset = results_queryset.filter(year__lte=end_year)
            if selected_sido:
                results_queryset = results_queryset.filter(sido=selected_sido)
            if selected_sigungu:
                results_queryset = results_queryset.filter(sigungu=selected_sigungu)

            # 필요한 컬럼만 선택하여 조회
            fields_to_select = [
                'main_scenario', 'sub_scenario', 'year', 'month', 'sido', 'sigungu',
                'avg_temp', 'max_temp', 'min_temp', 'humidity', 'wind_speed', 
                'precipitation', 'solar_radiation'
            ]
            context['results'] = results_queryset.order_by('year', 'month').values(*fields_to_select)[:200]

    # --- 4. 템플릿에 전달할 전체 컨텍스트 구성 ---
    context['main_scenario_list'] = [(key, key.upper()) for key in MODEL_MAP.keys()]
    
    # 사용자가 선택했던 값들을 다시 전달하여 폼에 유지
    context.update({
        'selected_main_scenario': selected_model_db,
        'selected_sub_scenario': selected_sub_scenario,
        'selected_start_year': start_year,
        'selected_end_year': end_year,
        'selected_sido': selected_sido,
        'selected_sigungu': selected_sigungu,
    })
    
    return render(request, 'main/futuredatapage.html', context)


def parse_float_safe(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

def f_list(qs, attr):
    """qs에서 attr을 float 변환해 유효값만 리스트로 리턴"""
    return [
        v for v in
        (parse_float_safe(getattr(o, attr)) for o in qs)
        if v is not None
    ]

SIDO_REMAP = {
    '강원특별자치도': '강원',
    '경기도': '경기',
    '경상남도': '경남',
    '경상북도': '경북',
    '대구광역시': '대구',
    '부산광역시': '부산',
    '서울특별시': '서울',
    '울산광역시': '울산',
    '인천광역시': '인천',
    '전라남도': '전남',
    '전북특별자치도': '전북',
    '충청남도': '충남',
    '충청북도': '충북',
}

def cabbageforecast(request):
    # ① GET 파라미터
    selected_sido   = request.GET.get('sido')
    selected_year   = request.GET.get('year')
    selected_months = request.GET.getlist('month')    # now multi-select
    nitrogen        = request.GET.get('nitrogen')

    # month_list: 1~12월
    month_list = list(range(1,13))

    # ② Onion 데이터 필터링 (region/year)
    qs = Cabbage.objects.using('cabbage').all()
    if selected_sido:
        qs = qs.filter(region=selected_sido)
    if selected_year:
        qs = qs.filter(year=int(selected_year))
    qs = qs.order_by('-year','region')

    onion_data = [{
        'region': safe_val(o.region),
        'year':   safe_val(o.year),
        'yield_per_10a': safe_val(o.yield_per_10a),
        'total_production': safe_mul(o.total_production,1000),
    } for o in qs]

    # ③ 기상 평균 계산 (month__in)
    weather_stats = {
        'avg_temp':'-','humidity':'-','wind_speed':'-',
        'solar_radiation':'-','avg_precipitation':'-',
        'nitrogen': nitrogen or ''
    }

    # 정수 리스트로 바꿔서 필터
    months_int = [int(m) for m in selected_months if m.isdigit()]
    if selected_sido and selected_year and months_int:
        wqs = Weatherdata.objects.using('climate').filter(
            year=int(selected_year),
            sido=selected_sido,
            month__in=months_int
        )
        if wqs.exists():
            temps  = f_list(wqs,'avg_temp')
            hums   = f_list(wqs,'humidity')
            winds  = f_list(wqs,'wind_speed')
            solars = f_list(wqs,'solar_radiation')
            precs  = f_list(wqs,'avg_precipitation')
            weather_stats = {
                'avg_temp':          round(sum(temps)/len(temps),2) if temps else "-",
                'humidity':          round(sum(hums)/len(hums),2) if hums else "-",
                'wind_speed':        round((sum(winds)/len(winds))*3.6,2) if winds else "-",
                'solar_radiation':   round(sum(solars)/(30*(len(solars))),2) if solars else "-",
                'avg_precipitation': round(sum(precs)/(30*(len(precs))),2) if precs else "-",
                'nitrogen': nitrogen or ""
            }

    # ④ 예측·실제·오차율 계산
    prediction = actual = error_rate = None
    try:
        if all([
            weather_stats['avg_temp'] not in ['-',''],
            weather_stats['humidity'] not in ['-',''],
            weather_stats['wind_speed'] not in ['-',''],
            weather_stats['solar_radiation'] not in ['-',''],
            weather_stats['avg_precipitation'] not in ['-',''],
            nitrogen not in [None,'','-']
        ]):
            N = float(nitrogen); T=float(weather_stats['avg_temp'])
            H = float(weather_stats['humidity'])
            W = float(weather_stats['wind_speed'])
            S = float(weather_stats['solar_radiation'])
            P = float(weather_stats['avg_precipitation'])
            prediction = round(
                0.1930*N +2.6281*T +2.2951*H
                -4.9108*W +5.4245*S -2.5028*P
                -113.4609,2
            )
            # 실제값 조회
            remapped = SIDO_REMAP.get(selected_sido,selected_sido)
            if remapped and selected_year:
                actual_qs = Cabbage.objects.using('cabbage').filter(
                    region=remapped,
                    year=int(selected_year)
                )
                if actual_qs.exists():
                    val = actual_qs.values_list('yield_per_10a',flat=True).first()
                    actual = round(float(val)/100,2) if val is not None else None
                    if actual:
                        error_rate = round(abs(prediction-actual)/actual*100,2)
    except Exception as e:
        print(f"[예측 오류] {e}")

    # ⑤ 체크박스 옵션 (시도, 년)
    sido_list = Weatherdata.objects.using('climate')\
        .values_list('sido',flat=True).distinct().order_by('sido')
    year_list = Weatherdata.objects.using('climate')\
        .values_list('year',flat=True).distinct().order_by('year')

    # ⑥ context & render
    context = {
        'sido_list':      sido_list,
        'year_list':      year_list,
        'month_list':     month_list,
        'selected_sido':  selected_sido,
        'selected_year':  selected_year,
        'selected_months':selected_months,
        'onion_data':     onion_data,
        'weather_stats':  weather_stats,
        'nitrogen':       nitrogen or '',
        'prediction':     prediction,
        'actual':         actual,
        'error_rate':     error_rate,
    }
    return render(request,'main/cabbageforecast.html',context)

def onionforecast(request):
    # ① GET 파라미터
    selected_sido   = request.GET.get('sido')
    selected_year   = request.GET.get('year')
    selected_months = request.GET.getlist('month')    # now multi-select
    nitrogen        = request.GET.get('nitrogen')

    # month_list: 1~12월
    month_list = list(range(1,13))

    # ② Onion 데이터 필터링 (region/year)
    qs = Onion.objects.using('onion').all()
    if selected_sido:
        qs = qs.filter(region=selected_sido)
    if selected_year:
        qs = qs.filter(year=int(selected_year))
    qs = qs.order_by('-year','region')

    onion_data = [{
        'region': safe_val(o.region),
        'year':   safe_val(o.year),
        'yield_per_10a': safe_val(o.yield_per_10a),
        'total_production': safe_mul(o.total_production,1000),
    } for o in qs]

    # ③ 기상 평균 계산 (month__in)
    weather_stats = {
        'avg_temp':'-','humidity':'-','wind_speed':'-',
        'solar_radiation':'-','avg_precipitation':'-',
        'nitrogen': nitrogen or ''
    }

    # 정수 리스트로 바꿔서 필터
    months_int = [int(m) for m in selected_months if m.isdigit()]
    if selected_sido and selected_year and months_int:
        wqs = Weatherdata.objects.using('climate').filter(
            year=int(selected_year),
            sido=selected_sido,
            month__in=months_int
        )
        if wqs.exists():
            temps  = f_list(wqs,'avg_temp')
            hums   = f_list(wqs,'humidity')
            winds  = f_list(wqs,'wind_speed')
            solars = f_list(wqs,'solar_radiation')
            precs  = f_list(wqs,'avg_precipitation')
            weather_stats = {
                'avg_temp':          round(sum(temps)/len(temps),2) if temps else "-",
                'humidity':          round(sum(hums)/len(hums),2) if hums else "-",
                'wind_speed':        round((sum(winds)/len(winds))*3.6,2) if winds else "-",
                'solar_radiation':   round(sum(solars)/(30*(len(solars))),2) if solars else "-",
                'avg_precipitation': round(sum(precs)/(30*(len(precs))),2) if precs else "-",
                'nitrogen': nitrogen or ""
            }

    # ④ 예측·실제·오차율 계산
    prediction = actual = error_rate = None
    try:
        if all([
            weather_stats['avg_temp'] not in ['-',''],
            weather_stats['humidity'] not in ['-',''],
            weather_stats['wind_speed'] not in ['-',''],
            weather_stats['solar_radiation'] not in ['-',''],
            weather_stats['avg_precipitation'] not in ['-',''],
            nitrogen not in [None,'','-']
        ]):
            N = float(nitrogen); T=float(weather_stats['avg_temp'])
            H = float(weather_stats['humidity'])
            W = float(weather_stats['wind_speed'])
            S = float(weather_stats['solar_radiation'])
            P = float(weather_stats['avg_precipitation'])
            prediction = round(
                0.1016*N -0.1009*T -0.1267*H
                +0.0626*W +0.1437*S -0.0433*P
                +10.4367,2
            )
            # 실제값 조회
            remapped = SIDO_REMAP.get(selected_sido,selected_sido)
            if remapped and selected_year:
                actual_qs = Onion.objects.using('onion').filter(
                    region=remapped,
                    year=int(selected_year)
                )
                if actual_qs.exists():
                    val = actual_qs.values_list('yield_per_10a',flat=True).first()
                    actual = round(float(val)/100,2) if val is not None else None
                    if actual:
                        error_rate = round(abs(prediction-actual)/actual*100,2)
    except Exception as e:
        print(f"[예측 오류] {e}")

    # ⑤ 체크박스 옵션 (시도, 년)
    sido_list = Weatherdata.objects.using('climate')\
        .values_list('sido',flat=True).distinct().order_by('sido')
    year_list = Weatherdata.objects.using('climate')\
        .values_list('year',flat=True).distinct().order_by('year')

    # ⑥ context & render
    context = {
        'sido_list':      sido_list,
        'year_list':      year_list,
        'month_list':     month_list,
        'selected_sido':  selected_sido,
        'selected_year':  selected_year,
        'selected_months':selected_months,
        'onion_data':     onion_data,
        'weather_stats':  weather_stats,
        'nitrogen':       nitrogen or '',
        'prediction':     prediction,
        'actual':         actual,
        'error_rate':     error_rate,
    }
    return render(request,'main/onionforecast.html',context)

def scorepage(request):
    return render(request, 'main/scorepage.html')
