# Generated by Django 4.2.5 on 2023-11-26 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_remove_lesson_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='cover_blocked',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Обложка заблокированная'),
        ),
    ]
