# Generated by Django 3.2 on 2023-11-29 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_todosharing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todosharing',
            name='access_type',
            field=models.CharField(choices=[('read_only', 'Read Only'), ('read_write', 'Read/Write')], default='read_only', max_length=20),
        ),
    ]
