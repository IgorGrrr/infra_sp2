# Generated by Django 2.2.16 on 2022-10-27 14:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_genretitle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(10, 'Оценка не может быть меньше 10'), django.core.validators.MinValueValidator(1, 'Оценка не может быть меньше 1')], verbose_name='оценка'),
        ),
    ]
