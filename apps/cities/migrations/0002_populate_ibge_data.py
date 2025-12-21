# apps/cities/migrations/0002_populate_ibge_data.py

from django.db import migrations
import json
import gzip
from urllib.request import urlopen, Request
from urllib.error import HTTPError

def load_ibge_data(apps, schema_editor):
    UF = apps.get_model('cities', 'UF')
    City = apps.get_model('cities', 'City')

    print("\n--- Iniciando Importação do IBGE (Versão Blindada) ---")

    # Função auxiliar para baixar e lidar com GZIP
    def get_json_from_url(url):
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Django Migration)')
        
        try:
            with urlopen(req) as response:
                content = response.read()
                if response.info().get('Content-Encoding') == 'gzip' or content[:2] == b'\x1f\x8b':
                    content = gzip.decompress(content)
                return json.loads(content.decode('utf-8'))
        except HTTPError as e:
            print(f"Erro ao baixar {url}: {e}")
            return []

    # 1. IMPORTAR ESTADOS (UFs)
    url_ufs = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    print(f"Baixando UFs de: {url_ufs}")
    
    ufs_data = get_json_from_url(url_ufs)

    if not ufs_data:
        return

    uf_objects = []
    for item in ufs_data:
        uf = UF(
            id=item['id'],
            abbreviation=item['sigla'],
            name=item['nome'],
            idle=False
        )
        uf_objects.append(uf)
    
    UF.objects.bulk_create(uf_objects, ignore_conflicts=True)
    print("✅ Estados importados com sucesso!")

    # 2. IMPORTAR CIDADES (Municípios)
    # TRUQUE: ?view=nivelado evita o erro de hierarquia deep nesting
    url_cities = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado"
    print(f"Baixando Cidades de: {url_cities}")
    
    cities_data = get_json_from_url(url_cities)

    if not cities_data:
        return

    print(f"Encontradas {len(cities_data)} cidades. Processando...")

    city_objects = []
    for item in cities_data:
        # Com a view nivelada, as chaves mudam, mas são seguras
        # item['municipio-id'] -> ID da Cidade
        # item['UF-id'] -> ID do Estado
        
        city = City(
            id=item['municipio-id'],
            name=item['municipio-nome'],
            uf_id=item['UF-id'],
            idle=False
        )
        city_objects.append(city)

    # Salvando em lotes
    City.objects.bulk_create(city_objects, batch_size=2000, ignore_conflicts=True)
    print(f"✅ {len(cities_data)} Cidades importadas com sucesso!")

def reverse_func(apps, schema_editor):
    UF = apps.get_model('cities', 'UF')
    City = apps.get_model('cities', 'City')
    City.objects.all().delete()
    UF.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_ibge_data, reverse_func),
    ]
