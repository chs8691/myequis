# Generated by Django 2.2.5 on 2019-09-28 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myequis', '0016_auto_20190917_1725'),
    ]

    operations = [
        migrations.RenameField(
            model_name='record',
            old_name='KM',
            new_name='km',
        ),
    ]
