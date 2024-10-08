# Generated by Django 5.1 on 2024-09-01 17:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RealEstate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('city', models.CharField(choices=[('Kabul', 'Kabul'), ('Kandahar', 'Kandahar'), ('Herat', 'Herat'), ('Mazar-i-Sharif', 'Mazar-i-Sharif'), ('Kunduz', 'Kunduz'), ('Jalalabad', 'Jalalabad'), ('Ghazni', 'Ghazni'), ('Balkh', 'Balkh'), ('Faryab', 'Faryab'), ('Samangan', 'Samangan'), ('Sar-e Pol', 'Sar-e Pol'), ('Takhar', 'Takhar'), ('Baghlan', 'Baghlan'), ('Parwan', 'Parwan'), ('Kapisa', 'Kapisa'), ('Panjshir', 'Panjshir'), ('Wardak', 'Wardak'), ('Logar', 'Logar'), ('Paktia', 'Paktia'), ('Paktika', 'Paktika'), ('Khost', 'Khost'), ('Nangarhar', 'Nangarhar'), ('Laghman', 'Laghman'), ('Nuristan', 'Nuristan'), ('Badakhshan', 'Badakhshan'), ('Takhār', 'Takhār'), ('Badghis', 'Badghis'), ('Fāryāb', 'Fāryāb'), ('Ghōr', 'Ghōr'), ('Daykundi', 'Daykundi'), ('Uruzgan', 'Uruzgan'), ('Zabul', 'Zabul'), ('Helmand', 'Helmand'), ('Nimroz', 'Nimroz')], max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('area', models.IntegerField()),
                ('price_per_area', models.IntegerField()),
                ('contract_type', models.CharField(choices=[('mortgage', 'Mortgage'), ('on_sale', 'On Sale'), ('rental', 'Rental')], max_length=40)),
                ('type', models.CharField(choices=[('Apartment', 'Apartment'), ('House', 'House'), ('Building', 'Building'), ('Land', 'Land'), ('Condominium', 'Condominium'), ('Townhouse', 'Townhouse'), ('Villa', 'Villa'), ('Bungalow', 'Bungalow'), ('Duplex', 'Duplex'), ('Triplex', 'Triplex'), ('Commercial Building', 'Commercial Building'), ('Office Space', 'Office Space'), ('Retail Space', 'Retail Space'), ('Warehouse', 'Warehouse'), ('Factory', 'Factory'), ('Farm', 'Farm'), ('Ranch', 'Ranch'), ('Plot', 'Plot'), ('Vacant Land', 'Vacant Land'), ('Agricultural Land', 'Agricultural Land'), ('Industrial Land', 'Industrial Land'), ('Commercial Land', 'Commercial Land'), ('Residential Land', 'Residential Land')], max_length=100)),
                ('swap', models.BooleanField(default=False)),
                ('water', models.BooleanField(default=False)),
                ('sewage', models.BooleanField(default=False)),
                ('drilling_and_well', models.BooleanField(default=False)),
                ('road_opened', models.BooleanField(default=False)),
                ('heater', models.BooleanField(default=False)),
                ('loan_compliance', models.BooleanField(default=False)),
                ('price', models.IntegerField()),
                ('payment_plan_activation_date', models.DateTimeField(blank=True, null=True)),
                ('discount', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RealEstateImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='real_estate')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
