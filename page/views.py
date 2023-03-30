from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from core.view import View
from django.template import loader
from django.shortcuts import get_object_or_404
from page.models import PageModel, ProduitModel, PModel
from asgiref.sync import sync_to_async
from django.db.models import Q
import datetime

class IndexView(View):
    async def get(self, request, lang=None):
        if lang is None:
            lang = 'fr'
        ui =  get_object_or_404(PageModel , lang=lang, url='i')
        if r := request.GET.get('r', None):
            return HttpResponseRedirect(f'/{ui.lang}/r?r={r}')

        return  HttpResponse(loader.get_template('i.html').render(cache.get('cF', {'ui':ui}), request), content_type='text/html; charset=utf-8')


class RechercheView(View):
    async def get(self, request, lang=None):
        if lang is None:
            lang = 'fr'

        ui = get_object_or_404(PageModel , lang=lang, url='r')

        r = request.GET.get('r', None)
        p =  request.GET.get('p', None)
        bb1 = PModel.objects.filter(Q(ia__search=r) | Q(ia__icontains=r), lang=lang, df__lte=int(round(datetime.datetime.now().timestamp())))
        
        if p is None :
            k,kk = 0,21
        elif p == '2':
             k,kk = 20,41
        elif p == '3':
             k,kk = 40,61
        elif p == '4':
             k,kk = 60,81
        elif p == '5':
             k,kk = 80,101
        elif p == '6':
             k,kk = 100,121
        elif p == '7':
             k,kk = 120,141
        elif p == '8':
             k,kk = 140,161
        elif p == '9':
             k,kk = 160,181
        elif p == '10': 
             k,kk = 180,200
        
        bb = bb1.values_list('url',flat=True)[k:kk]
        resultat = bb1.count()
        
        prn = None if p is None else int(p) -1
        if prn not in [None, 1]:
            prp = f'/{lang}/r?r={r}&p={prn}'
        elif prn == 1 :
            prp = f'/{lang}/r?r={r}'
        else: 
            prp = None
       
        nen = 2 if p is None else int(p) +1
        nep = None
        if resultat != 0:
            nep = f'/{lang}/r?r={r}&p={nen}' if nen != None and bb.count() == 21 else None
   
        up = ProduitModel.objects.filter(url__in=list(bb), valide='1').order_by('it')
        return  HttpResponse(loader.get_template('r.html').render(cache.get('cF', {'ui':ui,'up':up,'r':r, 'resultat':resultat,'nep':nep,'prp':prp,'nen':nen,'prn':prn}), request), content_type='text/html; charset=utf-8')


class MentionsView(View):
    
    async def get(self, request, lang=None):
        if lang is None:
            lang = 'fr'
        
        ui = get_object_or_404(PageModel , lang=lang, url='m')
        if r := request.GET.get('r', None):
            return HttpResponseRedirect(f'/{ui.lang}/r?r={r}')
        
        uc = await sync_to_async(list)(PageModel.objects.filter(url='m').exclude(lang='fr'))

        return  HttpResponse(loader.get_template('m.html').render(cache.get('cF', {'ui':ui,'uc':uc}), request), content_type='text/html; charset=utf-8')
