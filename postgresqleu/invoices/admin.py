from django.contrib import admin
from django.forms import ValidationError

from postgresqleu.util.forms import ConcurrentProtectedModelForm

from .models import Invoice, InvoiceLog, InvoiceProcessor, InvoicePaymentMethod
from .models import InvoiceRefund, VatRate


class InvoiceAdminForm(ConcurrentProtectedModelForm):
    class Meta:
        model = Invoice
        exclude = []

    def __init__(self, *args, **kwargs):
        super(InvoiceAdminForm, self).__init__(*args, **kwargs)
        self.fields['allowedmethods'].label_from_instance = lambda o: o.internaldescription
        self.fields['paidusing'].label_from_instance = lambda o: o.internaldescription

    def clean_recipient_email(self):
        if 'finalized' in self.cleaned_data:
            raise ValidationError("Can't edit email field on a finalized invoice!")
        return self.cleaned_data['recipient_email'].lower()

    def clean_recipient_name(self):
        if 'finalized' in self.cleaned_data:
            raise ValidationError("Can't edit name field on a finalized invoice!")
        return self.cleaned_data['recipient_name']

    def clean_recipient_address(self):
        if 'finalized' in self.cleaned_data:
            raise ValidationError("Can't edit address field on a finalized invoice!")
        return self.cleaned_data['recipient_address']

    def clean_title(self):
        if 'finalized' in self.cleaned_data:
            raise ValidationError("Can't edit title field on a finalized invoice!")
        return self.cleaned_data['title']

    def clean_total_amount(self):
        if 'finalized' in self.cleaned_data:
            raise ValidationError("Can't edit total amount field on a finalized invoice!")
        return self.cleaned_data['total_amount']

    def clean_total_vat(self):
        if 'finalized' in self.cleaned_data:
            raise ValidationError("Can't edit total vat field on a finalized invoice!")
        return self.cleaned_data['total_vat']

    def clean_processor(self):
        if "processor" in self.changed_data:
            raise ValidationError("Sorry, we never allow editing of the processor!")
        return self.cleaned_data['processor']


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'recipient_name', 'total_amount', 'ispaid')
    form = InvoiceAdminForm
    exclude = ['pdf_invoice', 'pdf_receipt', ]
    filter_horizontal = ['allowedmethods', ]
    search_fields = ['title', 'id', ]


class InvoiceLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'message_trunc', 'sent',)


class InvoiceRefundAdmin(admin.ModelAdmin):
    list_display = ('registered', 'issued', 'completed', 'amount', 'vatamount', 'reason')
    exclude = ['refund_pdf', ]


class InvoicePaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'internaldescription', 'classname', )


admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceProcessor)
admin.site.register(InvoicePaymentMethod, InvoicePaymentMethodAdmin)
admin.site.register(InvoiceLog, InvoiceLogAdmin)
admin.site.register(InvoiceRefund, InvoiceRefundAdmin)
admin.site.register(VatRate)
