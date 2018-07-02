# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-07-01 08:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Areas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='名称')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subs', to='areas.Areas', verbose_name='父级')),
            ],
            options={
                'verbose_name': '地区表',
                'db_table': 'tb_areas',
                'verbose_name_plural': '地区表',
            },
        ),
    ]
