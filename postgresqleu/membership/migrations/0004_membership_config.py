# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-19 12:51
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models

from postgresqleu.util.fields import LowercaseEmailField


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0010_payment_refector'),
        ('membership', '0003_proxy_voting'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipConfiguration',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('sender_email', LowercaseEmailField(max_length=254, help_text="Email address to use as sender on outgoing email")),
                ('membership_years', models.IntegerField(default=1, help_text='Membership length in years', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Membership length')),
                ('membership_cost', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Membership cost')),
                ('country_validator', models.CharField(max_length=100, blank=True, choices=[('europe', 'Must be from European country')], help_text='Validate member countries against this rule', verbose_name='Country validator')),
                ('paymentmethods', models.ManyToManyField(to='invoices.InvoicePaymentMethod', verbose_name='Invoice payment methods')),
            ],
        ),
        migrations.RunSQL("ALTER TABLE membership_membershipconfiguration ADD CONSTRAINT highlander CHECK (id=1)"),
        migrations.RunSQL("INSERT INTO membership_membershipconfiguration_paymentmethods (membershipconfiguration_id, invoicepaymentmethod_id) SELECT 1, id FROM invoices_invoicepaymentmethod WHERE active AND auto"),
    ]
