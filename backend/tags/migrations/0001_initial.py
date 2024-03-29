# Generated by Django 3.2 on 2023-06-29 19:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Краткое название')),
                ('color', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(code='invalid_color', message='Цвет должен быть представлен HEX кодом, например: #f54fa6', regex='^#\\w{6}$')], verbose_name='Цвет')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Бархатные Тяги',
            },
        ),
    ]
