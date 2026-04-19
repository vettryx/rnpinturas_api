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
    $(document).on('blur', '.cep-input', function() {
        var inputCep = $(this);
        var cepValue = inputCep.val().replace(/\D/g, ''); // Remove traços e pontos
        
        // Acha o container pai (a linha do endereço ou o grupo principal)
        // ATENÇÃO: Ajustado para pegar .apps-formset-item ou o novo .apps-form-group
        var container = inputCep.closest('.apps-formset-item, .apps-form-group');

        if (cepValue.length === 8) {
            inputCep.css('opacity', '0.5');

            $.ajax({
                url: '/common/api/cep/' + cepValue + '/',
                method: 'GET',
                success: function(data) {
                    if (!data.erro) {
                        container.find('.logradouro-input').val(data.logradouro);
                        container.find('.bairro-input').val(data.bairro);
                        
                        var compInput = container.find('.complemento-input');
                        if(data.complemento && compInput.val() === '') {
                            compInput.val(data.complemento);
                        }

                        container.find('input[name$="number"]').focus();

                        // --- MÁGICA DO SELECT2 AJAX ---
                        if (data.cidade_id && data.cidade_nome) {
                            var citySelect = container.find('.city-input');
                            
                            if (citySelect.find("option[value='" + data.cidade_id + "']").length) {
                                citySelect.val(data.cidade_id).trigger('change');
                            } else {
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
                    inputCep.css('opacity', '1');
                }
            });
        }
    });

    // ======================================================
    // 3. GERENCIAMENTO DE FORMSETS (ADICIONAR LINHA) - CORRIGIDO
    // ======================================================
    // Agora usamos delegação no document ou no wrapper principal, 
    // e buscamos a classe .apps-form-group (a nova classe do container)
    $(document).on('click', '.btn-add-row', function(e) {
        e.preventDefault();
        
        // 1. Encontra o container pai da seção (Card Principal)
        var parentSection = $(this).closest('.apps-form-group');
        
        // 2. Encontra o container onde ficam as linhas do formset
        var container = parentSection.find('.apps-formset-container');
        
        // 3. Encontra o input hidden de gerenciamento (TOTAL_FORMS)
        // Ele geralmente está logo antes do container, dentro do parentSection
        var totalFormsInput = parentSection.find('input[name$="-TOTAL_FORMS"]');
        
        if (totalFormsInput.length === 0) {
            console.error("Erro: Não foi possível encontrar o input TOTAL_FORMS. Verifique se {{ section.formset.management_form }} está no template.");
            return;
        }

        var totalForms = parseInt(totalFormsInput.val());
        
        // 4. Clona a primeira linha para usar de modelo
        var newRow = container.find('.apps-formset-item:first').clone();
        
        // Limpeza dos valores
        newRow.find('input, textarea, select').val(''); 
        newRow.find('input[type="checkbox"]').prop('checked', false);
        
        // Destrói o container visual do Select2 clonado
        newRow.find('.select2-container').remove();
        
        // A MÁGICA: Remove atributos fantasmas de TODOS os elementos da linha (incluindo as tags <option>)
        newRow.find('*')
            .removeClass('select2-hidden-accessible')
            .removeAttr('data-select2-id')
            .removeAttr('aria-hidden')
            .removeAttr('tabindex');
        
        // Limpa options do select AJAX para não copiar a cidade da linha anterior
        newRow.find('.select2-ajax').empty(); 

        // 5. Atualiza IDs e Names (Regex busca por -0- ou -1- e troca pelo novo índice)
        newRow.find('input, select, textarea, label').each(function() {
            var name = $(this).attr('name');
            var id = $(this).attr('id');
            var forAttr = $(this).attr('for');

            if (name) $(this).attr('name', name.replace(/-\d+-/, '-' + totalForms + '-'));
            if (id) $(this).attr('id', id.replace(/-\d+-/, '-' + totalForms + '-'));
            if (forAttr) $(this).attr('for', forAttr.replace(/-\d+-/, '-' + totalForms + '-'));
        });

        // 6. Adiciona ao DOM e atualiza contador
        container.append(newRow);
        totalFormsInput.val(totalForms + 1);

        // 7. Reinicia Select2 na nova linha
        newRow.find('select').each(function() {
            initSelect2(this);
        });

        // 8. Scroll Suave e Foco Inteligente na Nova Linha
        // A. Rola a tabela (wrapper) inteira de volta para a esquerda
        var tableWrapper = parentSection.find('.apps-table-wrapper');
        if (tableWrapper.length) {
            tableWrapper.animate({ scrollLeft: 0 }, 300); // 300ms de animação suave
        }

        // B. Encontra o primeiro campo visível da linha recém-criada
        var firstField = newRow.find('input:not([type="hidden"]), select, textarea').first();

        if (firstField.length) {
            // Se for um campo transformado em Select2, o foco tem que ir pro container dele
            if (firstField.hasClass('select2-hidden-accessible')) {
                // Foca na caixa de seleção gerada pelo Select2
                firstField.next('.select2-container').find('.select2-selection').focus();
            } else {
                // Se for um campo HTML normal (input texto, number, etc)
                firstField.focus();
            }
        }
    });

    // ======================================================
    // 4. INICIALIZAÇÃO GERAL AO CARREGAR
    // ======================================================
    $('select').each(function() {
        initSelect2(this);
    });

    // ======================================================
    // 5. CÁLCULO AUTOMÁTICO DE DATA DE VENCIMENTO
    // ======================================================
    // Mapeia os inputs gerados pelo Django
    var $issueDate = $('#id_issue_date');
    var $dueDate = $('#id_due_date');
    var $validityDays = $('#order-validity-days'); 

    function updateDueDate() {
        var issueVal = $issueDate.val();
        var daysVal = $validityDays.val();

        if (issueVal && daysVal) {
            var baseDate = new Date(issueVal + 'T00:00:00');
            var daysToAdd = parseInt(daysVal, 10);

            if (!isNaN(daysToAdd)) {
                var newDate = new Date(baseDate);
                newDate.setDate(newDate.getDate() + daysToAdd);

                var year = newDate.getFullYear();
                var month = String(newDate.getMonth() + 1).padStart(2, '0');
                var day = String(newDate.getDate()).padStart(2, '0');

                $dueDate.val(year + '-' + month + '-' + day);
            }
        }
    }

    if ($issueDate.length > 0 && $validityDays.length > 0 && $dueDate.length > 0) {
        $issueDate.on('change', updateDueDate);
        $validityDays.on('input change', updateDueDate); 
    }

});