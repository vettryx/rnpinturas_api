# rnpinturas/views.py

from django.shortcuts import render


# ----- View para a Página Inicial do Projeto -----
def home(request):
    """
    Renderiza a página inicial do projeto.

    Parâmetros:
    - request: Objeto HttpRequest representando a requisição HTTP recebida.

    Retorna:
    - HttpResponse: Resposta HTTP que renderiza o template da página inicial.
    """
    return render(request, "home.html")
