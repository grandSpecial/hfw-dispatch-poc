from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid
from datetime import datetime 
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	mobile_phone = models.CharField(max_length=15, unique=True)
	home_address = models.TextField()
	home_coordinates = models.CharField(max_length=50, blank=True, null=True)
	travel_distance = models.IntegerField()

def generate_short_uuid():
	return str(uuid.uuid4())[:5]

class Case(models.Model):
	id = models.CharField(primary_key=True, max_length=5, editable=False)
	animal = models.CharField(max_length=255)
	created_on = models.DateTimeField(auto_now_add=True)
	log = ArrayField(
		models.JSONField(
			default=dict,
			blank=True,
			null=True,
			help_text="update details for the case"
		),
		default=list,
		blank=True,
		help_text="a list of updates for the case"
	)
	messages_sent = models.IntegerField(default=0, help_text="Number of messages sent")

	def add_log_entry(self, name, contact_number, message, coordinates, status, messages_sent):
		log_entry = {
			'name': name,
			'contact_number': contact_number,
			'message': message,
			'coordinates': coordinates,
			'status': status,
			'updated_on': datetime.now().isoformat()
		}
		self.log.append(log_entry)
		self.messages_sent = messages_sent
		self.save()

	@staticmethod
	def short_uuid():
		while True:
			short_uuid = str(uuid.uuid4())[:5]
			if not Case.objects.filter(id=short_uuid).exists():
				return short_uuid

