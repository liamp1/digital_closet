# Generated by Django 5.1.5 on 2025-01-20 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_item_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
