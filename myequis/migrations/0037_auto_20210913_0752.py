# Generated by Django 3.2.3 on 2021-09-13 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myequis', '0036_auto_20210822_0834'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='type',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='part',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]