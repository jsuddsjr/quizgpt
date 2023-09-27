# Generated by Django 4.2.5 on 2023-09-27 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizdata', '0013_choiceanswer_choice_answers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='choice',
            options={},
        ),
        migrations.AlterModelOptions(
            name='choiceanswer',
            options={'get_latest_by': '-created'},
        ),
        migrations.RemoveField(
            model_name='question',
            name='force_ordered',
        ),
        migrations.AddField(
            model_name='choiceanswer',
            name='bucket',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterOrderWithRespectTo(
            name='choice',
            order_with_respect_to='question',
        ),
        migrations.RemoveField(
            model_name='choice',
            name='choice_order',
        ),
    ]
