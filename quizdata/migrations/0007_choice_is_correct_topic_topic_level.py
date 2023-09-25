# Generated by Django 4.2.5 on 2023-09-25 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizdata', '0006_alter_question_force_ordered_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='is_correct',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_level',
            field=models.IntegerField(choices=[(1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced')], default=1),
        ),
    ]
