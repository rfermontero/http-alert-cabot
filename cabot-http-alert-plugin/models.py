from cabot.cabotapp.alert import AlertPlugin, AlertPluginUserData

from django.db import models
from django.conf import settings
from django.template import Context, Template
from os import environ as env

import requests

post_template = " {{ service }} Service {{ service.name }} {% if service.overall_status == service.PASSING_STATUS %}is back to normal{% else %}reporting {{ service.overall_status }} status{% endif %}: {{ scheme }}://{{ host }}{% url 'service' pk=service.id %}. {% if service.overall_status != service.PASSING_STATUS %}Checks failing: {% for check in service.all_failing_checks %}{% if check.check_category == 'Jenkins check' %}{% if check.last_result.error %} {{ check.name }} ({{ check.last_result.error|safe }}) {{jenkins_api}}job/{{ check.name }}/{{ check.last_result.job_number }}/console{% else %} {{ check.name }} {{jenkins_api}}/job/{{ check.name }}/{{check.last_result.job_number}}/console {% endif %}{% else %} {{ check.name }} {% if check.last_result.error %} ({{ check.last_result.error|safe }}){% endif %}{% endif %}{% endfor %}{% endif %}"

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
		})

		self.post_http(alert, color=color, sender='Cabot/%s' % service.name)

	def post_http(self, alert, color='green', sender='Cabot'):
		headers = {'content-type': 'application/json'}
		data = json.dumps(alert.__dict__)
		url = 'http://169.254.161.235:3000/alerts'
		resp = requests.post(url,data=data,headers=headers)

class HttpAlertUserData(AlertPluginUserData):
	name = "HttpAlert Plugin"
	key = models.CharField(max_length=32, blank=False, verbose_name="User/Group Key")
	alert_on_warn = models.BooleanField(default=True)



