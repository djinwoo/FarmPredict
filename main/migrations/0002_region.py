# Generated by Django 5.1.6 on 2025-04-08 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sido', models.TextField()),
                ('sigungu', models.TextField()),
                ('eupmyeondong', models.TextField()),
            ],
            options={
                'db_table': 'region',
                'managed': False,
            },
        ),
    ]
