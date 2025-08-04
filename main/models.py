# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Region(models.Model):
    id = models.AutoField(primary_key=True)
    sido = models.TextField(db_column="시도")
    sigungu = models.TextField(db_column="시군구")
    eupmyeondong = models.TextField(db_column="읍면동")

    class Meta:
        db_table = 'Region'  # 실제 SQLite 테이블 이름과 동일하게 설정
        managed = False  # Django가 이 테이블을 생성하거나 수정하지 않음

    
    def __str__(self):
        return f"{self.sido} {self.sigungu} {self.eupmyeondong}"

class Weatherdata(models.Model):
    year = models.IntegerField(db_column="년", primary_key=True)  # 기본키 설정 (연도를 기본키로 사용)
    month = models.IntegerField(db_column="월")
    sido = models.CharField(max_length=100, db_column="시도")
    sigungu = models.CharField(max_length=100, db_column="시군구")
    eupmyeondong = models.CharField(max_length=100, db_column="읍면동")
    avg_temp = models.FloatField(db_column="평균기온")
    min_temp = models.FloatField(db_column="최고기온")
    max_temp = models.FloatField(db_column="최저기온")
    humidity = models.FloatField(db_column="습도")
    wind_speed = models.FloatField(db_column="풍속")
    avg_precipitation = models.FloatField(db_column="강수량")
    solar_radiation = models.CharField(max_length=100, db_column="일사량")

    class Meta:
        db_table = "climatedata"  # SQLite의 'climate' 테이블과 매칭
        managed = False  # Django가 테이블을 관리하지 않도록 설정

    def __str__(self):
        return f"{self.year}-{self.month} {self.sido} {self.sigungu} {self.eupmyeondong} {self.avg_temp} {self.min_temp} {self.max_temp} {self.humidity} {self.wind_speed} {self.solar_radiation} {self.avg_precipitation}"

class Soildata(models.Model):
    year = models.IntegerField(db_column="년",primary_key=True)
    sido = models.CharField(max_length=100, db_column="시도")
    sigungu = models.CharField(max_length=100, db_column="시군구")
    eupmyeondong = models.CharField(max_length=100, db_column="읍면동")
    ph = models.FloatField(db_column='산도')
    organic_matter = models.FloatField(db_column='유기물')
    available_phosphorus = models.FloatField(db_column='유효인산')
    potassium = models.FloatField(db_column='칼륨')
    calcium = models.FloatField(db_column='칼슘')
    magnesium = models.FloatField(db_column='마그네슘')
    nitrogen = models.FloatField(db_column='질소')
    latitude = models.FloatField(db_column='위도')
    longitude = models.FloatField(db_column='경도')

    class Meta:
        db_table = "soildata"
        managed = False

    def __str__(self):
        return f"{self.year} {self.sido} {self.sigungu} {self.eupmyeondong} {self.ph} {self.organic_matter} {self.available_phosphorus} {self.potassium} {self.calcium} {self.magnesium} {self.nitrogen} {self.latitude} {self.longitude}"
    
class Cabbage(models.Model):
    region = models.CharField(max_length=50, db_column='시도',primary_key=True)  # 시도
    year = models.IntegerField(db_column='년')                  # 연도
    yield_per_10a = models.FloatField(db_column='10a당 생산량(kg)')  # 10a당 생산량(kg)
    total_production = models.FloatField(db_column='생산량(kg)')  # 총 생산량(톤)

    class Meta:
        db_table = "cabbagedata"  # 테이블 이름
        managed = False

    def __str__(self):
        return f"[{self.year}] {self.region} - 10a당: {self.yield_per_10a}kg / 총: {self.total_production}톤"


    
class Onion(models.Model):
    region = models.CharField(max_length=50, db_column='시도',primary_key=True)  # 시도
    year = models.IntegerField(db_column='년')                  # 연도
    yield_per_10a = models.FloatField(db_column='10a당 생산량(kg)')  # 10a당 생산량(kg)
    total_production = models.FloatField(db_column='생산량(kg)')  # 총 생산량(톤)

    class Meta:
        db_table = "oniondata"
        managed = False

    def __str__(self):
        return f"[{self.year}] {self.region} - 10a당: {self.yield_per_10a}kg / 총: {self.total_production}톤"

# main/models.py 파일에 추가

# main/models.py 파일

class FutureClimate(models.Model):
    # 시나리오 정보
    main_scenario = models.CharField(max_length=100, db_column='main_scenario',primary_key=True)
    sub_scenario = models.CharField(max_length=50, db_column='sub_scenario')

    # 날짜 및 지역 정보
    year = models.IntegerField(db_column='년')
    month = models.IntegerField(db_column='월')
    sido = models.CharField(max_length=50, db_column='시도')
    sigungu = models.CharField(max_length=50, db_column='시군구')
    eupmyeondong = models.CharField(max_length=50, db_column='읍면동', null=True, blank=True)

    # 기후 데이터
    avg_temp = models.FloatField(db_column='평균기온',null=True,blank=True)
    max_temp = models.FloatField(db_column='최고기온')
    min_temp = models.FloatField(db_column='최저기온')
    humidity = models.FloatField(db_column='습도')
    wind_speed = models.FloatField(db_column='풍속')
    avg_precipitation = models.FloatField(db_column='강수량')
    solar_radiation = models.FloatField(db_column='일사량')

    class Meta:
        db_table = "climate_scenarios"  # DB에 있는 실제 테이블 이름
        managed = False                 # Django가 이 테이블을 생성하거나 수정하지 않음

    def __str__(self):
        return f"{self.main_scenario} {self.sub_scenario} {self.year}-{self.month} {self.sido} {self.sigungu} {self.eupmyeondong} {self.avg_temp} {self.min_temp} {self.max_temp} {self.humidity} {self.wind_speed} {self.solar_radiation} {self.avg_precipitation}"