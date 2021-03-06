# Generated by Django 2.2.5 on 2019-09-17 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myequis', '0015_auto_20190913_0540'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='Weight [g]',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='size',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
