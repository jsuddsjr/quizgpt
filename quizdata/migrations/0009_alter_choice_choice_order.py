# Generated by Django 4.2.5 on 2023-09-25 04:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizdata', '0008_alter_choice_choice_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='choice_order',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]