# Generated by Django 5.1.3 on 2024-11-22 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Curriculum', '0009_syllabiprogress_last_attempted_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='curriculumreview',
            name='sentiment',
            field=models.CharField(blank=True, choices=[('POS', 'Positive'), ('NEG', 'Negative'), ('NEU', 'Neutral')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='curriculumsyllabi',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='curriculumsyllabi',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='syllabitopic',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='syllabitopic',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]