# Generated by Django 3.2.3 on 2021-09-16 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myequis', '0038_auto_20210916_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='type',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]