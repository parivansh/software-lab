# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 19:53
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_remove_customer_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='pwd',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]