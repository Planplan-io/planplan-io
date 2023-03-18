
from django.urls import path
from page import views
from core.view import TemplateView

urlpatterns = [
    path('', views.IndexView.as_view(), name='i'),
    path('<str:lang>/', views.IndexView.as_view(), name='i'),
    path('r', views.RechercheView.as_view(), name='r'),
    path('<str:lang>/r', views.RechercheView.as_view(), name='r'),
    path('m', views.MentionsView.as_view(), name='m'),
    path('<str:lang>/m', views.MentionsView.as_view(), name='m'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('google2ba2836593033a86.html', TemplateView.as_view(template_name='gg.html', content_type='text/html; charset=utf-8')),
    path('ahrefs_1d3f252491273252773eb5772f7d4b9a8289d7a6d19cb5f923ac2be8a45cc8c9', TemplateView.as_view(template_name='aa.html', content_type='text/html; charset=utf-8'))
    ]


