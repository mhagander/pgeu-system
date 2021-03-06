#!/usr/bin/env python
#
# Expire waitlist offers that have expired, so others can get the
# seats.
#
# Copyright (C) 2015, PostgreSQL Europe
#
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from datetime import timedelta

from postgresqleu.confreg.models import RegistrationWaitlistEntry, RegistrationWaitlistHistory
from postgresqleu.confreg.util import send_conference_mail, send_conference_notification


class Command(BaseCommand):
    help = 'Expire conference waitlist offers'

    class ScheduledJob:
        scheduled_interval = timedelta(minutes=30)
        internal = True
        trigger_next_jobs = 'postgresqleu.confreg.confreg_expire_additionaloptions'

        @classmethod
        def should_run(self):
            # Are there any active waitlist entries at all?
            return RegistrationWaitlistEntry.objects.filter(offeredon__isnull=False, registration__payconfirmedat__isnull=True, registration__invoice__isnull=True).exists()

    @transaction.atomic
    def handle(self, *args, **options):
        # Any entries that actually have an invoice will be canceled by the invoice
        # system, as the expiry time of the invoice is set synchronized. In this
        # run, we only care about offers that have not been picked up at all.
        wlentries = RegistrationWaitlistEntry.objects.filter(registration__payconfirmedat__isnull=True, registration__invoice__isnull=True, offerexpires__lt=timezone.now())

        for w in wlentries:
            reg = w.registration

            # Create a history entry so we know exactly when it happened
            RegistrationWaitlistHistory(waitlist=w,
                                        text="Offer expired at {0}".format(w.offerexpires)).save()

            # Notify conference organizers
            send_conference_notification(
                reg.conference,
                'Waitlist expired',
                'User {0} {1} <{2}> did not complete the registration before the waitlist offer expired.'.format(reg.firstname, reg.lastname, reg.email),
            )

            # Also send an email to the user
            send_conference_mail(reg.conference,
                                 reg.email,
                                 'Your waitlist offer has expired',
                                 'confreg/mail/waitlist_expired.txt',
                                 {
                                     'conference': reg.conference,
                                     'reg': reg,
                                     'offerexpires': w.offerexpires,
                                 },
                                 receivername=reg.fullname,
            )

            # Now actually expire the offer
            w.offeredon = None
            w.offerexpires = None
            # Move the user to the back of the waitlist (we have a history entry for the
            # initial registration date, so it's still around)
            w.enteredon = timezone.now()

            w.save()
