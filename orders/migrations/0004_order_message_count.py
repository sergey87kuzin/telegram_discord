# Generated by Django 4.2.5 on 2023-12-09 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_course_alter_order_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='message_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Число генераций'),
        ),
    ]
