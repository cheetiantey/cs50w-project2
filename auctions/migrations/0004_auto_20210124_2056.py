# Generated by Django 3.1.5 on 2021-01-24 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20210124_2000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='time',
        ),
        migrations.AddField(
            model_name='listing',
            name='photo',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]