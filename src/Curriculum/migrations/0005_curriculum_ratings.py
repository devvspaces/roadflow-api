# Generated by Django 4.0 on 2023-04-29 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Curriculum', '0004_curriculumsyllabi_slug_syllabitopic_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='ratings',
            field=models.IntegerField(default=0),
        ),
    ]
