/* static/js/apps-scripts.js */

$(document).ready(function() {
    
    // ======================================================
    // 1. CONFIGURAÇÃO DO SELECT2 COM AJAX
    // ======================================================
    function initSelect2(element) {
        // Se for um campo de busca AJAX (Cidade)
        if ($(element).hasClass('select2-ajax')) {
            var ajaxUrl = $(element).attr('data-ajax-url');
            
            $(element).select2({
                width: '100%',
                placeholder: $(element).attr('data-placeholder') || 'Pesquise...',
                allowClear: true,
                ajax: {
                    url: ajaxUrl,
                    dataType: 'json',
                    delay: 250, // Delay para não bombardear o servidor enquanto digita
                    data: function (params) {
                        return {
                            term: params.term // envia o termo digitado
                        };
                    },
                    processResults: function (data) {
                        return {
                            results: data.results // mapeia o retorno do Django
                        };
                    },
                    cache: true
                },
                minimumInputLength: 3, // Só busca após 3 letras
                language: {
                    inputTooShort: function() { return "Digite 3 caracteres para buscar..."; },
                    noResults: function() { return "Nenhum resultado encontrado"; },
                    searching: function() { return "Buscando..."; }
                }
            });
        } 
        // Se for um Select normal (Static)
        else if ($(element).hasClass('select2')) {
            $(element).select2({
                width: '100%',
                placeholder: 'Selecione uma opção',
                allowClear: true
            });
        }
    }

    // Inicializa Select2 em todos os campos ao carregar a página
    $('select').each(function() {
        initSelect2(this);
    });


    // ======================================================
    // 2. GERENCIAMENTO DE FORMSETS (Adicionar/Remover)
    // ======================================================
    
    // Botão Adicionar (Agora genérico para qualquer aba que tenha formset)
    // Você precisará adicionar um botão no seu HTML com a classe .add-formset-row
    // e data-prefix="address_formset" (exemplo)
    
    // Mas para facilitar, vamos automatizar baseado no template que criei:
    // O template ainda precisa do "Empty Form" oculto. 
    // O Django envia isso no context['address_formset'].empty_form
    
    // **NOTA:** Como seu template apps_form.html não renderizou o empty_form explicitamente,
    // o Django geralmente não o exibe a menos que peçamos. 
    // Vou assumir que vamos clonar a ÚLTIMA linha visível e limpar os dados,
    // que é uma técnica robusta quando não se tem o empty_form renderizado.

    $('.apps-form-group-edit-sub').on('click', '.btn-add-row', function(e) {
        e.preventDefault();
        
        var container = $(this).closest('.apps-form-group-edit-sub').find('.apps-formset-container');
        var totalFormsInput = container.parent().find('input[name$="-TOTAL_FORMS"]'); // Acha o input hidden de gerenciamento
        var totalForms = parseInt(totalFormsInput.val());
        
        // Clona a última linha (item do formset)
        var newRow = container.find('.apps-formset-item:first').clone(true);
        
        // Se não tiver linha nenhuma (caso raro de deletar tudo), precisaria do empty_form.
        // Assumindo que sempre tem 1 extra=1.

        // Limpa os valores dos inputs da nova linha
        newRow.find('input, textarea, select').val('');
        newRow.find('input[type="checkbox"]').prop('checked', false);
        
        // Remove a instância do Select2 clonada (bug visual comum) para recriar depois
        newRow.find('.select2-container').remove();
        newRow.find('select').removeClass('select2-hidden-accessible').removeAttr('data-select2-id');

        // Atualiza os IDs e Names (Regex para trocar o índice -0- pelo novo índice)
        newRow.find('input, select, textarea, label').each(function() {
            var name = $(this).attr('name');
            var id = $(this).attr('id');
            var forAttr = $(this).attr('for');

            if (name) {
                var newName = name.replace(/-\d+-/, '-' + totalForms + '-');
                $(this).attr('name', newName);
            }
            if (id) {
                var newId = id.replace(/-\d+-/, '-' + totalForms + '-');
                $(this).attr('id', newId);
            }
            if (forAttr) {
                var newFor = forAttr.replace(/-\d+-/, '-' + totalForms + '-');
                $(this).attr('for', newFor);
            }
        });

        // Insere a nova linha
        container.append(newRow);
        
        // Atualiza o contador total do Django
        totalFormsInput.val(totalForms + 1);

        // Reinicializa o Select2 (Ajax ou Normal) na nova linha
        newRow.find('select').each(function() {
            initSelect2(this);
        });
        
        // Opcional: Adiciona botão de remover visualmente se não estiver usando o checkbox DELETE padrão
    });

});
