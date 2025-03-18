# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TestData(models.Model):
    year = models.IntegerField(db_column="년", primary_key=True)  # 기본키 설정 (연도를 기본키로 사용)
    month = models.IntegerField(db_column="월")
    sido = models.CharField(max_length=100, db_column="시도")
    sigungu = models.CharField(max_length=100, db_column="시군구")
    eupmyeondong = models.CharField(max_length=100, db_column="읍면동")
    min_temp = models.FloatField(db_column="최저온도")
    max_temp = models.FloatField(db_column="최고온도")
    humidity = models.FloatField(db_column="습도")
    wind_speed = models.FloatField(db_column="풍속")
    solar_radiation = models.CharField(max_length=100, db_column="일사량")
    cumulative_precipitation = models.CharField(max_length=100, db_column="누적강수량")
    avg_precipitation = models.FloatField(db_column="평균강수량")
    latitude = models.FloatField(db_column="위도")
    longitude = models.FloatField(db_column="경도")

    class Meta:
        db_table = "test"  # SQLite의 'test' 테이블과 매칭
        managed = False  # Django가 테이블을 관리하지 않도록 설정

    def __str__(self):
        return f"{self.year}-{self.month} {self.sido} {self.sigungu}"
