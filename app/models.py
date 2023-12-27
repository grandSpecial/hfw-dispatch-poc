from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid
from datetime import datetime 
from django.contrib.auth.models import AbstractUser

def generate_short_uuid():
	return str(uuid.uuid4())[:5]

class User(AbstractUser):
	verify_key = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
	is_verified = models.BooleanField(default=False)
	consent = models.BooleanField(default=False)

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

	def add_log_entry(self, name, contact_number, message, coordinates, status):
		log_entry = {
			'name': name,
			'contact_number': contact_number,
			'message': message,
			'coordinates': coordinates,
			'status': status,
			'updated_on': datetime.now().isoformat()
		}
		self.log.append(log_entry)
		self.save()

	@staticmethod
	def short_uuid():
		while True:
			short_uuid = str(uuid.uuid4())[:5]
			if not Case.objects.filter(id=short_uuid).exists():
				return short_uuid

