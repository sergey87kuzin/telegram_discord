# Generated by Django 4.2.5 on 2024-04-05 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_user_is_test_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='customsettings',
            name='enhance_style',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Дополнительный стиль'),
        ),
    ]
