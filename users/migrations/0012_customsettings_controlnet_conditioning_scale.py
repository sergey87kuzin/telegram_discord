# Generated by Django 4.2.5 on 2024-01-13 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_customsettings_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='customsettings',
            name='controlnet_conditioning_scale',
            field=models.FloatField(blank=True, null=True, verbose_name='Шкала контролнет'),
        ),
    ]
