# Generated by Django 5.1 on 2024-08-19 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='room',
            constraint=models.UniqueConstraint(fields=('user1', 'user2'), name='unique_room_users'),
        ),
    ]
