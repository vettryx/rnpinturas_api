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
        var cepValue = inputCep.val().replace(/\D/g, '');
        
        // Acha o container pai (a linha do endereço ou o grupo principal)
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

        // CHAMA O CÁLCULO PARA ATUALIZAR OS TOTAIS COM A NOVA LINHA VAZIA
        if (typeof calculateLiveTotals === "function") {
            calculateLiveTotals();
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

    // ======================================================
    // 6. MOTOR DE TOTAIS EM TEMPO REAL (SERVIÇOS E MATERIAIS)
    // ======================================================
    
    // Função para converter o texto do input (ex: "1.500,00" ou "1500") para Float matemático
    function parseBRLValue(val) {
        if (!val) return 0;
        var strVal = val.toString().trim();
        
        if (strVal.indexOf(',') === -1) {
            return parseFloat(strVal) || 0;
        }
        strVal = strVal.replace(/\./g, '').replace(',', '.');
        return parseFloat(strVal) || 0;
    }

    // Função para devolver o Float no formato visual bonito (R$ 1.500,00)
    function formatBRL(value) {
        return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function calculateLiveTotals() {
        var totalServices = 0;
        var totalMaterials = 0;
        var totalDiscounts = 0;

        // 1. Soma todos os Serviços
        $('input[name^="services-"][name$="-price"]').each(function() {
            var name = $(this).attr('name');
            if (name.includes('__prefix__')) return; // Ignora a linha fantasma do formset
            
            var index = name.match(/services-(\d+)-price/)[1];
            
            // Se o usuário marcou a linha para apagar, a gente ignora ela na soma
            if ($('input[name="services-' + index + '-DELETE"]').is(':checked')) return;

            var qty = parseBRLValue($('input[name="services-' + index + '-quantity"]').val()) || 1;
            var price = parseBRLValue($(this).val());
            var discount = parseBRLValue($('input[name="services-' + index + '-discount"]').val());

            totalServices += (qty * price);
            totalDiscounts += discount;
        });

        // 2. Soma todos os Materiais (se existirem na tela)
        $('input[name^="materials-"][name$="-price"]').each(function() {
            var name = $(this).attr('name');
            if (name.includes('__prefix__')) return;
            
            var index = name.match(/materials-(\d+)-price/)[1];
            
            if ($('input[name="materials-' + index + '-DELETE"]').is(':checked')) return;

            var qty = parseBRLValue($('input[name="materials-' + index + '-quantity"]').val()) || 1;
            var price = parseBRLValue($(this).val());
            var discount = parseBRLValue($('input[name="materials-' + index + '-discount"]').val());

            totalMaterials += (qty * price);
            totalDiscounts += discount;
        });

        // 3. Aplica no HTML
        var grandTotal = (totalServices + totalMaterials) - totalDiscounts;

        $('#live-val-services').text(formatBRL(totalServices));
        $('#live-val-materials').text(formatBRL(totalMaterials));
        $('#live-val-discounts').text('- ' + formatBRL(totalDiscounts));
        $('#live-val-grandtotal').text(formatBRL(grandTotal));
    }

    // Só inicializa o painel se a tela tiver campos de preço (Tela de Pedidos/Orçamentos)
    if ($('input[name$="-price"]').length > 0) {
        
        // Constrói o painel e injeta logo antes dos botões de salvar
        var panelHTML = `
            <div class="live-totals-wrapper">
                <div class="live-total-item">
                    <span class="label">Serviços</span>
                    <span class="value" id="live-val-services">R$ 0,00</span>
                </div>
                <div class="live-total-item">
                    <span class="label">Materiais</span>
                    <span class="value" id="live-val-materials">R$ 0,00</span>
                </div>
                <div class="live-total-item discount">
                    <span class="label">Descontos</span>
                    <span class="value" id="live-val-discounts">- R$ 0,00</span>
                </div>
                <div class="live-total-item grand-total">
                    <span class="label">Total Líquido</span>
                    <span class="value" id="live-val-grandtotal">R$ 0,00</span>
                </div>
            </div>
        `;
        $('.apps-form-btn-group').before(panelHTML);

        // Calcula ao carregar a página (para edições)
        calculateLiveTotals();

        // Recalcula sempre que alguém digitar nos campos de valor, qtd ou desconto
        $(document).on('input', 'input[name$="-price"], input[name$="-quantity"], input[name$="-discount"]', function() {
            calculateLiveTotals();
        });

        // Recalcula se o usuário marcar a checkbox de deletar uma linha
        $(document).on('change', 'input[name$="-DELETE"]', function() {
            calculateLiveTotals();
        });
    }
});