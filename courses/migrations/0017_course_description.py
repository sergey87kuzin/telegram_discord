# Generated by Django 4.2.5 on 2023-12-24 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_alter_lessontextblock_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='description',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Описание'),
        ),
    ]
