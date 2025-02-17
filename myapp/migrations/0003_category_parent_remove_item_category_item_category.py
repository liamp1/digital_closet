# Generated by Django 5.1.5 on 2025-01-18 20:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_brand_category_color_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='myapp.category'),
        ),
        migrations.RemoveField(
            model_name='item',
            name='category',
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.category'),
        ),
    ]
