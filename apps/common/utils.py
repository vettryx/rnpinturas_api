# apps/common/utils.py
import logging
import requests
from cities.models import City

logger = logging.getLogger(__name__)

def buscar_dados_cep(cep):
    """
    Busca dados do CEP na BrasilAPI.
    Estratégia de Busca Local:
    1. Tenta pelo código IBGE (Mais preciso).
    2. Se falhar, tenta pelo Nome da Cidade + Sigla do Estado (Fallback).
    """
    cep_limpo = str(cep).replace("-", "").replace(".", "").strip()
    url = f"https://brasilapi.com.br/api/cep/v2/{cep_limpo}"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            ibge_code = data.get("ibge")
            cidade_nome_api = data.get("city")
            uf_api = data.get("state")
            
            city_obj = None

            # TENTATIVA 1: Busca pelo ID (IBGE)
            if ibge_code:
                city_obj = City.objects.filter(pk=ibge_code).first()
            
            # TENTATIVA 2: Busca por Nome + UF (Caso a API não retorne IBGE)
            if not city_obj and cidade_nome_api and uf_api:
                try:
                    # Tenta filtrar por nome exato e sigla do estado
                    # Assumindo que seu model City tem relacionamento com UF via 'uf__sigla'
                    city_obj = City.objects.filter(
                        name__iexact=cidade_nome_api,
                        uf__sigla__iexact=uf_api
                    ).first()
                except Exception:
                    # Se der erro no filtro do estado (ex: campo tem outro nome),
                    # tenta apenas pelo nome da cidade como último recurso
                    city_obj = City.objects.filter(name__iexact=cidade_nome_api).first()

            return {
                "cep": data.get("cep"),
                "logradouro": data.get("street"),
                "complemento": data.get("complement", ""),
                "bairro": data.get("neighborhood"),
                "cidade_id": city_obj.pk if city_obj else None,
                "cidade_nome": str(city_obj) if city_obj else cidade_nome_api,
                "uf": uf_api,
                "encontrou_cidade_local": city_obj is not None
            }
            
        elif response.status_code == 404:
            return {"erro": "CEP não encontrado."}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão na busca de CEP: {e}")
        return {"erro": "Serviço de CEP indisponível no momento."}
    
    return {"erro": "Erro desconhecido ao buscar CEP."}
