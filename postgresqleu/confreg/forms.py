from django import forms
from django.forms import RadioSelect
from django.forms.fields import *
from django.forms import ValidationError

from postgresqleu.confreg.models import *

class ConferenceRegistrationForm(forms.ModelForm):
	additionaloptions = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
		required=False,
		queryset=ConferenceAdditionalOption.objects.all())

	def __init__(self, *args, **kwargs):
		super(ConferenceRegistrationForm, self).__init__(*args, **kwargs)
		self.fields['regtype'].queryset = RegistrationType.objects.filter(conference=self.instance.conference).order_by('sortkey')
		if not self.instance.conference.asktshirt:
			del self.fields['shirtsize']
		self.fields['additionaloptions'].queryset =	ConferenceAdditionalOption.objects.filter(
			conference=self.instance.conference)

	def clean_regtype(self):
		newval = self.cleaned_data.get('regtype')
		if self.instance and newval == self.instance.regtype:
			# Registration type not changed, so it's ok to save
			# (we don't want to prohibit other edits for somebody who has
			#  an already-made registration with an expired registration type)
			return newval

		if newval and not newval.active:
			raise forms.ValidationError('Registration type "%s" is currently not available.' % newval)

		if self.instance and self.instance.payconfirmedat and not self.instance.conference.autoapprove:
			raise forms.ValidationError('You cannot change type of registration once your payment has been confirmed!')

		return newval

	def compare_options(self, a, b):
		# First check if the sizes are the same
		if len(a) != len(b):
			return False

		# Then do a very expensive one-by-one check
		for x in a:
			found = False
			for y in b:
				if x.pk == y.pk:
					found = True
					break
			if not found:
				# Entry in a not found in b, give up
				return False

		# All entires in a were in b, and the sizes were the same..
		return True

	def clean_additionaloptions(self):
		newval = self.cleaned_data.get('additionaloptions')

		if self.instance and self.instance.pk:
			oldval = list(self.instance.additionaloptions.all())
		else:
			oldval = ()

		if self.instance and self.compare_options(newval, oldval):
			# Additional options not changed, so keep allowing them
			return newval

		# Check that the new selection is available by doing a count
		# We only look at the things that have been *added*
		for option in set(newval).difference(oldval):
			if option.maxcount > 0:
				# This option has a limit on the number of people
				# Count how many others have it. The difference we took on
				# the sets above means we only check this when *this*
				# registration doesn't have the option, and thus the count
				# will always increase by one if we save this.
				current_count = option.conferenceregistration_set.count()
				if current_count + 1 > option.maxcount:
					raise forms.ValidationError("The option \"%s\" is no longer available due to too many signups." % option.name)

		# Check if the registration has been confirmed
		if self.instance and self.instance.payconfirmedat and not self.instance.conference.autoapprove:
			raise forms.ValidationError('You cannot change your additional options once your payment has been confirmed! If you need to make changes, please contact the conference organizers via email')

		# Yeah, it's ok
		return newval

	class Meta:
		model = ConferenceRegistration
		exclude = ('conference','attendee','payconfirmedat','payconfirmedby','created',)

rating_choices = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (0, 'N/A'),
)

class ConferenceSessionFeedbackForm(forms.ModelForm):
	topic_importance = forms.ChoiceField(widget=RadioSelect,choices=rating_choices, label='Importance of the topic')
	content_quality = forms.ChoiceField(widget=RadioSelect,choices=rating_choices, label='Quality of the content')
	speaker_knowledge = forms.ChoiceField(widget=RadioSelect,choices=rating_choices, label='Speakers knowledge of the subject')
	speaker_quality = forms.ChoiceField(widget=RadioSelect,choices=rating_choices, label='Speakers presentation skills')

	class Meta:
		model = ConferenceSessionFeedback
		exclude = ('conference','attendee','session')


class ConferenceFeedbackForm(forms.Form):
	# Very special dynamic form. It's ugly, but hey, it works
	def __init__(self, *args, **kwargs):
		questions = kwargs.pop('questions')
		responses = kwargs.pop('responses')

		super(ConferenceFeedbackForm, self).__init__(*args, **kwargs)

		# Now add our custom fields
		for q in questions:
			if q.isfreetext:
				self.fields['question_%s' % q.id] = forms.CharField(widget=forms.widgets.Textarea,
																	label=q.question,
																	required=False,
																	initial=self.get_answer_text(responses, q.id))
			else:
				self.fields['question_%s' % q.id] = forms.ChoiceField(widget=RadioSelect,
																	  choices=rating_choices,
																	  label=q.question,
																	  initial=self.get_answer_num(responses, q.id))

	def get_answer_text(self, responses, id):
		for r in responses:
			if r.question_id == id:
				return r.textanswer
		return ""

	def get_answer_num(self, responses, id):
		for r in responses:
			if r.question_id == id:
				print "Match"
				print "Returning %s" % r.rateanswer
				return r.rateanswer
		return -1

class SpeakerProfileForm(forms.ModelForm):
	class Meta:
		model = Speaker
		exclude = ('user', 'fullname', )

	def clean_photofile(self):
		if not self.cleaned_data['photofile']:
			return self.cleaned_data['photofile'] # If it's None...
		img = None
		try:
			from PIL import ImageFile
			p = ImageFile.Parser()
			p.feed(self.cleaned_data['photofile'].read())
			p.close()
			img = p.image
		except Exception, e:
			raise ValidationError("Could not parse image: %s" % e)
		if img.format != 'JPEG':
			raise ValidationError("Only JPEG format images are accepted, not '%s'" % img.format)
		if img.size[0] > 128 or img.size[1] > 128:
			raise ValidationError("Maximum image size is 128x128")
		return self.cleaned_data['photofile']
