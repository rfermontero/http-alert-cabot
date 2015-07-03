from cabot.cabotapp.alert import AlertPlugin, AlertPluginUserData

from django.db import models
from django.conf import settings
from django.template import Context, Template
from os import environ as env

import requests

post_template = "test"


class HttpAlert(AlertPlugin):

	name = "AlertHttp"
	author = "rfernandez"

	def send_alert(self, service, users, duty_officers):

		if service.overall_status == service.WARNING_STATUS:
			alert = False
		if service.overall_status == service.ERROR_STATUS:
			if service.old_overall_status in (service.ERROR_STATUS, service.ERROR_STATUS):
				alert = False 
		if service.overall_status == service.PASSING_STATUS:
			color = 'green'
			if service.old_overall_status == service.WARNING_STATUS:
				alert = False
		else:
			color = 'red'

		c = Context({
			'service': service,
			'host': settings.WWW_HTTP_HOST,
			'scheme': settings.WWW_SCHEME,
			'alert': alert,
		})

		message = Template(post_template).render(c)
		self.post_http(message, color=color, sender='Cabot/%s' % service.name)

	def post_http(self, message, color='green', sender='Cabot'):

		url = env.get('http://10.0.35.44:3000')

		resp = requests.post(url, 
			data={
			'from': sender[:15],
			'message': message,
			'notify': 1,
			'color': color,
			'message_format': 'text',
		})

class HttpAlertUserData(AlertPluginUserData):
	name = "HttpAlert Plugin"
	key = models.CharField(max_length=32, blank=False, verbose_name="User/Group Key")
	alert_on_warn = models.BooleanField(default=False)



