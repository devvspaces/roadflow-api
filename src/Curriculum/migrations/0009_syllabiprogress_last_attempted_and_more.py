# Generated by Django 4.0 on 2023-04-30 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Curriculum', '0008_alter_syllabitopic_order_alter_syllabitopic_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='syllabiprogress',
            name='last_attempted',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='syllabiprogress',
            name='quiz_mark',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
