# Generated by Django 2.2.5 on 2019-09-11 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myequis', '0011_auto_20190911_0556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mounting',
            name='dismount_record',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, related_name='dismount_record', to='myequis.Record'),
        ),
    ]