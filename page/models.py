from django_cassandra_engine.models import DjangoCassandraModel
from cassandra.cqlengine import columns
from functools import cached_property
from django.urls import reverse
import uuid, datetime
from django.db import models

class PModel(models.Model):
    ia = models.TextField(db_index=True, max_length=2050)
    lang = models.CharField(max_length=2,null=True, blank=True)
    url = models.CharField(primary_key=True, max_length=1000, blank=True )
    df = models.IntegerField(null=True, blank=True )

    def __str__(self):
        return f'{self.ia} {self.lang}'

    class Meta:
        verbose_name = 'Recherche produit'

class ProduitModel(DjangoCassandraModel):
    __keyspace__ = 'Cluster1'
    __table_name__ = 'produit_model'
    __connection__ = 'cassandra'
    
    #produit_id = columns.Text(default=uuid.uuid4, primary_key=True)
    produit_id = columns.Text(default=0)
    domaine = columns.Text()

    di = columns.Text(default=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    df = columns.Integer(default=0)

    lang = columns.Text()
    url = columns.Text(primary_key=True)
    img = columns.Text()
    

    titre = columns.Text()
    prix = columns.Decimal()
    devise = columns.Text()
    detection = columns.Integer(default=0)
    valide = columns.Integer(default=0)
    
    categorie = columns.Text()
    url_avis = columns.Text()
    avis = columns.Decimal()

    ia = columns.Text()
    it = columns.Integer(default=0)
    
    
    def __str__(self):
        return f'{self.titre} {self.lang} {self.url} {self.img} {self.prix} {self.devise} {self.categorie} {self.avis} {self.url_avis} {self.valide}'
    
    class Meta:
        get_pk_field = 'url'
        verbose_name = 'Produit'
        
class PageModel(DjangoCassandraModel):
    __keyspace__ = 'Cluster1'
    __table_name__ = 'page_model'
    __connection__ = 'cassandra'
    
    page_id = columns.BigInt(primary_key=True)
    titre = columns.Text()
    description = columns.Text()
    date = columns.Text()
    lang = columns.Text()
    url = columns.Text()
    h1 = columns.Text()
    texte = columns.Text()
    mentions1 = columns.Text()
    recherche1 = columns.Text()
    recherche2 = columns.Text()
    footer2 = columns.Text()
    
    def __str__(self):
        return f'{self.page_id} {self.titre}'
    
    class Meta:
        get_pk_field = 'page_id'
        verbose_name = 'page'
    
    @cached_property
    def url_mentions(self):
        return reverse('m', args=[ self.lang]) if self.lang != 'fr' else reverse('m')

    
    @cached_property
    def url_index(self):
        return reverse('i', args=[ self.lang]) if self.lang != 'fr' else reverse('i')