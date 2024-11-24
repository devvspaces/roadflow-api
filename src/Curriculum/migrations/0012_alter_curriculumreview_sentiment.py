# Generated by Django 5.1.3 on 2024-11-24 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Curriculum', '0011_alter_curriculumreview_label_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculumreview',
            name='sentiment',
            field=models.CharField(blank=True, choices=[('P', 'Positive'), ('NEG', 'Negative'), ('N', 'Neutral')], max_length=3, null=True),
        ),
    ]