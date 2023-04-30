# Generated by Django 4.0 on 2023-04-27 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Curriculum', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.CharField(max_length=255)),
                ('reason', models.TextField(blank=True, null=True)),
                ('is_correct', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Curriculum.syllabitopic')),
            ],
        ),
        migrations.CreateModel(
            name='QSelection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_correct', models.BooleanField(default=False)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Quiz.quiz')),
                ('selected', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Quiz.qoption')),
                ('topic_progress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Curriculum.syllabiprogress')),
            ],
        ),
        migrations.AddField(
            model_name='qoption',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Quiz.quiz'),
        ),
    ]