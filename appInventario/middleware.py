from typing import Any
from django.shortcuts import render
from django.http import HttpResponseNotFound
from .views import error404


class NotFoundMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response
  
	def __call__(self, request):
		response = self.get_response(request)
		if response.status_code == 404:
			return error404(request, None)
		return response