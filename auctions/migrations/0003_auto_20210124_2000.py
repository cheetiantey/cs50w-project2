# Generated by Django 3.1.5 on 2021-01-24 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='time',
            field=models.TimeField(auto_now_add=True),
        ),
    ]
