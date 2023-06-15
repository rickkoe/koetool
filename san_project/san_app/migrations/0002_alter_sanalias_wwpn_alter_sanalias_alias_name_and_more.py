# Generated by Django 4.2.2 on 2023-06-15 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("san_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sanalias",
            name="WWPN",
            field=models.CharField(max_length=23, unique=True),
        ),
        migrations.AlterField(
            model_name="sanalias",
            name="alias_name",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="sanalias",
            name="use",
            field=models.CharField(
                choices=[("init", "Initiator"), ("target", "Target"), ("both", "Both")],
                default="init",
                max_length=6,
            ),
        ),
    ]
