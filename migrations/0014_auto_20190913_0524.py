# Generated by Django 2.2.5 on 2019-09-13 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myequis', '0013_auto_20190911_1652'),
    ]

    operations = [
        migrations.RenameField(
            model_name='record',
            old_name='meter',
            new_name='KM',
        ),
    ]
