# apps/cities/views.py
from django.http import JsonResponse
from cities.models import City

def city_autocomplete_view(request):
    query = request.GET.get('term', '')
    cities = City.objects.none()
    
    if len(query) > 2:
        # Busca por nome que contenha o texto (case insensitive)
        cities = City.objects.filter(name__icontains=query)[:20]
        
    results = []
    for city in cities:
        # Tenta pegar a representação padrão (ex: "Belo Horizonte - MG")
        # Se não tiver __str__ configurado, usa só o nome para garantir que não quebre
        text_label = str(city) 
        
        results.append({
            'id': city.id,
            'text': text_label
        })

    return JsonResponse({'results': results})
