import brotli, re, time
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils.http import http_date
from django.contrib.messages.storage import default_storage
from importlib import import_module
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.utils.cache import patch_vary_headers
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.text import compress_string
 

class SimpleMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.redirect = True


    
    def process_view(self, request, view_func, view_args, views_kwargs):
        request.lang = views_kwargs.get('lang', None)
     




    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        
        patch_vary_headers(response, ('Accept-Encoding',))

        if self._accepts_brotli_encoding(request):
            compressed_content = brotli.compress(response.content)
            if response.has_header('ETag'):
                response['ETag'] = re.sub(r"\"$", r";br\"", response['ETag'])
            aa = 'br'
        else:
            compressed_content = compress_string(response.content)
            etag = response.get("ETag")
            if etag and etag.startswith('"'):
                response.headers["ETag"] = f"W/{etag}"
            aa = "gzip"
        
        response.headers["Content-Encoding"] = aa

        response.content = compressed_content
        response['content-length'] = str(len(response.content))
        response['content-language'] = 'fr' if request.lang is None else request.lang

        if response.status_code != [404 , 500] and request.accepts('text/html') and response['content-language'] == 'fr' :
            response.headers['Link'] = f'<{request.build_absolute_uri(request.path)}>; rel="canonical"'

        #elif response['content-language'] in ['en','es','de','it'] and reverse('m'): 
          #  response.headers['Link'] = f'<https://planplan.io/m>; rel="canonical"'
        
        #response.headers['Cache-Control'] = 'max-age=3600' if request.user_agent.is_bot else 'no-cache'


        return response

    def _accepts_brotli_encoding(self, request: HttpRequest) -> bool:
        return bool(re.compile(r'\bbr\b').search(request.META.get('HTTP_ACCEPT_ENCODING', '')))