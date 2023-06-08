# Generated by Django 4.2.1 on 2023-06-08 14:44

from django.db import migrations, models
import necrotopia.models


class Migration(migrations.Migration):

    dependencies = [
        ('necrotopia', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skillitem',
            name='category',
            field=models.IntegerField(choices=[(4, 'Anomaly'), (2, 'Civilized'), (1, 'Combat'), (5, 'Lore'), (3, 'Wasteland')], default=necrotopia.models.SkillCategory['Anomaly']),
        ),
        migrations.AlterField(
            model_name='skillratings',
            name='description',
            field=models.CharField(max_length=3000),
        ),
    ]