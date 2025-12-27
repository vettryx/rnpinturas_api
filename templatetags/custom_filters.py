# templatetags/custom_filters.py

"""
Este módulo contém filtros e tags personalizados para templates Django.
"""

from urllib.parse import parse_qs, urlencode

from django import template
from django.utils.html import format_html, format_html_join

register = template.Library()

@register.filter
def remove_page_param(query_params):
    """
    Remove o parâmetro 'page' dos query parameters.
    """
    params = parse_qs(query_params)
    params.pop('page', None)
    return urlencode(params, doseq=True)

@register.simple_tag
def render_search_fields(fields, request):
    """
    Gera dinamicamente os campos de pesquisa de forma segura contra XSS.
    """
    # Iniciamos o HTML base. format_html marca essa string como segura.
    html_content = format_html('<div class="apps-list-form-group-search">')

    for field in fields:
        field_name = field.get("name")
        field_label = field.get("label", field_name.capitalize())
        field_type = field.get("type", "text")
        field_options = field.get("options", [])
        value = request.GET.get(field_name, "")

        # Montamos a parte inicial do campo (Label e Checkbox)
        # format_html garante que field_name e field_label sejam escapados se tiverem caracteres perigosos
        html_content += format_html(
            '<div class="apps-list-form-group-search-sub">'
            '<input type="checkbox" id="check-{}" data-target="{}">'
            '<label for="search-{}">{}:</label>',
            field_name, field_name, field_name, field_label
        )

        if field_type == "select":
            html_content += format_html(
                '<select name="{}" id="{}" class="select-search select2">'
                '<option value="">-- Selecione --</option>',
                field_name, field_name
            )

            for option_value, option_label in field_options:
                is_selected = str(value) == str(option_value)
                if is_selected:
                    html_content += format_html(
                        '<option value="{}" selected>{}</option>',
                        option_value, option_label
                    )
                else:
                    html_content += format_html(
                        '<option value="{}">{}</option>',
                        option_value, option_label
                    )

            html_content += format_html('</select>')

        else:
            # Input de texto padrão
            html_content += format_html(
                '<input type="{}" id="{}" name="{}" value="{}" class="form-control">',
                field_type, field_name, field_name, value
            )

        html_content += format_html('</div>')

    html_content += format_html('</div>')

    return html_content

@register.filter
def get_item(dictionary, key):
    """Obtém um item de um dicionário."""
    # print removido para produção, ou mantenha se estiver debugando
    return dictionary.get(key)
