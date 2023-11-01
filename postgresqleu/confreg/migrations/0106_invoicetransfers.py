# Generated by Django 3.2.14 on 2023-10-30 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0020_regtransfer_processor'),
        ('confreg', '0105_conferenceregistration_favs'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='transfer_cost',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Cost of transferring a registration, excluding VAT.', max_digits=10),
        ),
        migrations.CreateModel(
            name='RegistrationTransferPending',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='confreg.conference')),
                ('fromreg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_from_reg', to='confreg.conferenceregistration')),
                ('invoice', models.OneToOneField(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='invoices.invoice')),
                ('toreg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_to_reg', to='confreg.conferenceregistration')),
            ],
            options={
                'ordering': ('conference', 'created'),
            },
        ),
    ]
