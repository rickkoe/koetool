# Generated by Django 4.2.2 on 2023-07-21 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Fabric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('zoneset_name', models.CharField(max_length=200)),
                ('vsan', models.IntegerField(blank=True, null=True)),
                ('exists', models.CharField(choices=[('True', 'True'), ('False', 'False')], max_length=5)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fabric_customer', to='san_app.customer')),
            ],
            options={
                'unique_together': {('customer', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('san_vendor', models.CharField(choices=[('BR', 'Brocade'), ('CI', 'Cisco')], max_length=7)),
                ('cisco_alias', models.CharField(choices=[('device-alias', 'device-alias'), ('fcalias', 'fcalias')], max_length=15)),
                ('cisco_zoning_mode', models.CharField(choices=[('basic', 'basic'), ('enhanced', 'enhanced')], max_length=15)),
                ('zone_ratio', models.CharField(choices=[('one-to-one', 'one-to-one'), ('one-to-many', 'one-to-many'), ('all-to-all', 'all-to-all')], max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='active_customer', to='san_app.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('wwpn', models.CharField(max_length=23, unique=True)),
                ('use', models.CharField(blank=True, choices=[('init', 'Initiator'), ('target', 'Target'), ('both', 'Both')], max_length=6, null=True)),
                ('create', models.CharField(choices=[('True', 'True'), ('False', 'False')], default='False', max_length=5)),
                ('include_in_zoning', models.CharField(choices=[('True', 'True'), ('False', 'False')], default='False', max_length=5)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alias_customer', to='san_app.customer')),
                ('fabric', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='san_app.fabric')),
            ],
        ),
    ]
