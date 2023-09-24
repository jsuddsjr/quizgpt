# Generated by Django 4.2.5 on 2023-09-23 22:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(help_text='A topic or subtopic of study.', max_length=150)),
                ('superTopic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, parent_link=True, related_name='super_topic', to='quizdata.topic')),
                ('created', models.DateField()),
                ('subtopic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_topics', to='quizdata.topic')),
            ],
        ),
    ]