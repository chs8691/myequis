# Generated by Django 3.2.3 on 2021-09-17 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myequis', '0045_remove_material_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myequis.type'),
        ),
    ]