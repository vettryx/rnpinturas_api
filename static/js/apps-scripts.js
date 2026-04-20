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
    // 3. GERENCIAMENTO DE FORMSETS (ADICIONAR LINHA)
    // ======================================================
    $(document).on('click', '.btn-add-row', function(e) {
        e.preventDefault();
        
        var parentSection = $(this).closest('.apps-form-group');
        var container = parentSection.find('.apps-formset-container');
        var totalFormsInput = parentSection.find('input[name$="-TOTAL_FORMS"]');
        
        if (totalFormsInput.length === 0) {
            console.error("Erro: Não foi possível encontrar o input TOTAL_FORMS.");
            return;
        }

        var totalForms = parseInt(totalFormsInput.val());
        var newRow = container.find('.apps-formset-item:first').clone();
        
        // LIMPEZA INTELIGENTE: Preserva zeros em campos financeiros
        newRow.find('input, textarea, select').each(function() {
            var $el = $(this);
            var name = $el.attr('name') || '';
            var type = $el.attr('type') || '';

            if (type === 'checkbox' || type === 'radio') {
                $el.prop('checked', false);
            } 
            else if (name.includes('discount') || name.includes('price')) {
                $el.val('0');
            }
            else if (name.includes('quantity')) {
                $el.val('1'); 
            }
            else if (type === 'hidden' && name.includes('-id')) {
                $el.val('');
            }
            else if (type !== 'hidden') {
                // Limpa todos os outros campos visíveis (Selects, Textos, Ambientes)
                $el.val('');
            }
        });
        // ==========================================================
        
        // Destrói o container visual do Select2 clonado
        newRow.find('.select2-container').remove();
        
        // Remove atributos fantasmas do Select2
        newRow.find('*')
            .removeClass('select2-hidden-accessible')
            .removeAttr('data-select2-id')
            .removeAttr('aria-hidden')
            .removeAttr('tabindex');
        
        // Limpa options do select AJAX
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

        // Adiciona ao DOM e atualiza contador
        container.append(newRow);
        totalFormsInput.val(totalForms + 1);

        // Reinicia Select2 na nova linha
        newRow.find('select').each(function() {
            initSelect2(this);
        });

        // Scroll Suave e Foco Inteligente
        var tableWrapper = parentSection.find('.apps-table-wrapper');
        if (tableWrapper.length) {
            tableWrapper.animate({ scrollLeft: 0 }, 300);
        }

        var firstField = newRow.find('input:not([type="hidden"]), select, textarea').first();
        if (firstField.length) {
            if (firstField.hasClass('select2-hidden-accessible')) {
                firstField.next('.select2-container').find('.select2-selection').focus();
            } else {
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