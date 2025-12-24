/* static/js/apps-scripts.js */

$(document).ready(function() {
    
    // ======================================================
    // 1. FUNÇÃO DE INICIALIZAÇÃO DO SELECT2
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
                    delay: 250,
                    data: function (params) { return { term: params.term }; },
                    processResults: function (data) { return { results: data.results }; },
                    cache: true
                },
                minimumInputLength: 3,
                language: {
                    inputTooShort: function() { return "Digite 3 caracteres..."; },
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

    // ======================================================
    // 2. BUSCA DE CEP INTELIGENTE (COM DELEGAÇÃO)
    // ======================================================
    // Usamos $(document).on para funcionar também nas linhas novas criadas dinamicamente
    $(document).on('blur', '.cep-input', function() {
        var inputCep = $(this);
        var cepValue = inputCep.val().replace(/\D/g, ''); // Remove traços e pontos
        
        // Acha o container pai (a linha do endereço)
        var container = inputCep.closest('.apps-formset-item, .apps-form-group-edit-sub');

        if (cepValue.length === 8) {
            // Feedback visual (opcional: mude a cor da borda ou ícone)
            inputCep.css('opacity', '0.5');

            // URL ajustada para o app 'common' que definimos
            $.ajax({
                url: '/common/api/cep/' + cepValue + '/',
                method: 'GET',
                success: function(data) {
                    if (!data.erro) {
                        // Preenche Logradouro e Bairro
                        container.find('.logradouro-input').val(data.logradouro);
                        container.find('.bairro-input').val(data.bairro);
                        
                        // Preenche Complemento se existir e o campo estiver vazio
                        var compInput = container.find('.complemento-input');
                        if(data.complemento && compInput.val() === '') {
                            compInput.val(data.complemento);
                        }

                        // Foca no Número
                        container.find('input[name$="number"]').focus();

                        // --- MÁGICA DO SELECT2 AJAX ---
                        // Se retornou cidade, criamos a option manualmente para o Select2 aceitar
                        if (data.cidade_id && data.cidade_nome) {
                            var citySelect = container.find('.city-input');
                            
                            // Verifica se a opção já existe, senão cria
                            if (citySelect.find("option[value='" + data.cidade_id + "']").length) {
                                citySelect.val(data.cidade_id).trigger('change');
                            } else {
                                // new Option(text, id, defaultSelected, selected)
                                var newOption = new Option(data.cidade_nome, data.cidade_id, true, true);
                                citySelect.append(newOption).trigger('change');
                            }
                        }
                    } else {
                        alert(data.erro || "CEP não encontrado.");
                    }
                },
                error: function() {
                    alert("Erro ao consultar CEP. Verifique sua conexão.");
                },
                complete: function() {
                    inputCep.css('opacity', '1'); // Remove feedback visual
                }
            });
        }
    });

    // ======================================================
    // 3. GERENCIAMENTO DE FORMSETS (ADICIONAR LINHA)
    // ======================================================
    $('.apps-form-group-edit-sub').on('click', '.btn-add-row', function(e) {
        e.preventDefault();
        
        var container = $(this).closest('.apps-form-group-edit-sub').find('.apps-formset-container');
        var totalFormsInput = container.parent().find('input[name$="-TOTAL_FORMS"]');
        var totalForms = parseInt(totalFormsInput.val());
        
        // Clona a primeira linha (que serve de modelo)
        var newRow = container.find('.apps-formset-item:first').clone(true);
        
        // Limpeza profunda da nova linha
        newRow.find('input, textarea, select').val(''); 
        newRow.find('input[type="checkbox"]').prop('checked', false);
        
        // Destrói o Select2 clonado (ele buga se copiar o HTML processado)
        newRow.find('.select2-container').remove();
        newRow.find('select')
            .removeClass('select2-hidden-accessible')
            .removeAttr('data-select2-id')
            .removeAttr('aria-hidden')
            .removeAttr('tabindex');
        
        // Limpa as options do Select de cidade (para não nascer com a cidade da linha anterior)
        newRow.find('.select2-ajax').empty(); 

        // Atualiza IDs e Names
        newRow.find('input, select, textarea, label').each(function() {
            var name = $(this).attr('name');
            var id = $(this).attr('id');
            var forAttr = $(this).attr('for');

            if (name) $(this).attr('name', name.replace(/-\d+-/, '-' + totalForms + '-'));
            if (id) $(this).attr('id', id.replace(/-\d+-/, '-' + totalForms + '-'));
            if (forAttr) $(this).attr('for', forAttr.replace(/-\d+-/, '-' + totalForms + '-'));
        });

        // Adiciona ao DOM
        container.append(newRow);
        
        // Atualiza TOTAL_FORMS
        totalFormsInput.val(totalForms + 1);

        // Reinicia o Select2 SOMENTE na nova linha
        newRow.find('select').each(function() {
            initSelect2(this);
        });
    });

    // ======================================================
    // 4. INICIALIZAÇÃO GERAL AO CARREGAR
    // ======================================================
    $('select').each(function() {
        initSelect2(this);
    });

});