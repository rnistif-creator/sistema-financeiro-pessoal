/**
 * COMPONENTES REUTILIZÁVEIS - FEEDBACK VISUAL E ACESSIBILIDADE
 * Funções utilitárias para loading, toast, atalhos de teclado, etc.
 */

// ============================================
// LOADING OVERLAY
// ============================================

const LoadingOverlay = {
  element: null,
  
  init() {
    if (!this.element) {
      this.element = document.createElement('div');
      this.element.className = 'loading-overlay';
      this.element.setAttribute('role', 'status');
      this.element.setAttribute('aria-live', 'polite');
      this.element.innerHTML = `
        <div class="spinner"></div>
        <div class="loading-overlay-text">Carregando...</div>
      `;
      document.body.appendChild(this.element);
    }
  },
  
  show(text = 'Carregando...') {
    this.init();
    this.element.querySelector('.loading-overlay-text').textContent = text;
    this.element.style.display = 'flex';
  },
  
  hide() {
    if (this.element) {
      this.element.style.display = 'none';
    }
  }
};

// ============================================
// TOAST MELHORADO
// ============================================

const Toast = {
  container: null,
  queue: [],
  isShowing: false,
  
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.style.cssText = 'position: fixed; bottom: 24px; right: 24px; z-index: 10000;';
      document.body.appendChild(this.container);
    }
  },
  
  show(message, type = 'info', duration = 4000) {
    this.queue.push({ message, type, duration });
    if (!this.isShowing) {
      this.showNext();
    }
  },
  
  showNext() {
    if (this.queue.length === 0) {
      this.isShowing = false;
      return;
    }
    
    this.isShowing = true;
    this.init();
    
    const { message, type, duration } = this.queue.shift();
    
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    
    const titles = {
      success: 'Sucesso!',
      error: 'Erro!',
      warning: 'Atenção!',
      info: 'Informação'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.innerHTML = `
      <div class="toast-icon">${icons[type]}</div>
      <div class="toast-content">
        <div class="toast-title">${titles[type]}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close" aria-label="Fechar notificação">✕</button>
    `;
    
    this.container.appendChild(toast);
    
    const closeBtn = toast.querySelector('.toast-close');
    const close = () => {
      toast.classList.remove('show');
      setTimeout(() => {
        toast.remove();
        this.showNext();
      }, 300);
    };
    
    closeBtn.addEventListener('click', close);
    
    setTimeout(close, duration);
  },
  
  success(message, duration) {
    this.show(message, 'success', duration);
  },
  
  error(message, duration) {
    this.show(message, 'error', duration);
  },
  
  warning(message, duration) {
    this.show(message, 'warning', duration);
  },
  
  info(message, duration) {
    this.show(message, 'info', duration);
  }
};

// ============================================
// BUTTON LOADING STATE
// ============================================

const ButtonLoader = {
  setLoading(button, loading = true) {
    if (loading) {
      button.disabled = true;
      button.classList.add('loading');
      button.setAttribute('aria-busy', 'true');
      button._originalText = button.textContent;
    } else {
      button.disabled = false;
      button.classList.remove('loading');
      button.setAttribute('aria-busy', 'false');
      if (button._originalText) {
        button.textContent = button._originalText;
      }
    }
  }
};

// ============================================
// ATALHOS DE TECLADO
// ============================================

const KeyboardShortcuts = {
  shortcuts: {},
  
  register(key, callback, description = '') {
    this.shortcuts[key] = { callback, description };
  },
  
  init() {
    document.addEventListener('keydown', (e) => {
      // Ignorar se estiver digitando em input/textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) {
        return;
      }
      
      let shortcutKey = '';
      
      if (e.ctrlKey) shortcutKey += 'ctrl+';
      if (e.altKey) shortcutKey += 'alt+';
      if (e.shiftKey) shortcutKey += 'shift+';
      shortcutKey += e.key.toLowerCase();
      
      if (this.shortcuts[shortcutKey]) {
        e.preventDefault();
        this.shortcuts[shortcutKey].callback(e);
      }
    });
  },
  
  showHelp() {
    const shortcuts = Object.entries(this.shortcuts)
      .map(([key, data]) => `
        <div style="display:flex; justify-content:space-between; padding:8px; border-bottom:1px solid rgba(148,163,184,0.1)">
          <span>${data.description}</span>
          <kbd class="kbd">${key}</kbd>
        </div>
      `)
      .join('');
    
    Toast.info(`
      <div style="max-height:300px; overflow-y:auto;">
        <strong style="display:block; margin-bottom:12px;">Atalhos de Teclado:</strong>
        ${shortcuts}
      </div>
    `, 8000);
  }
};

// ============================================
// FETCH COM LOADING E TRATAMENTO DE ERROS
// ============================================

async function fetchWithLoading(url, options = {}, showOverlay = false) {
  // Suporte a timeout opcional via options.timeout (padrão 15s)
  const { timeout, signal, overlayText, ...fetchOptions } = options || {};
  const controller = !signal ? new AbortController() : null;
  const effectiveSignal = signal || (controller && controller.signal);
  const timeoutMs = typeof timeout === 'number' && timeout > 0 ? timeout : 15000;
  
  // Novo: permitir passar overlayText em options em vez do 3º parâmetro
  const shouldShowOverlay = showOverlay || !!overlayText;
  if (shouldShowOverlay) {
    const text = typeof showOverlay === 'string' ? showOverlay : (overlayText || 'Carregando...');
    LoadingOverlay.show(text);
  }
  
  let timeoutId;
  try {
    if (controller) {
      timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    }

    const response = await fetch(url, { ...fetchOptions, signal: effectiveSignal });
    // Tratamento central de limites do gratuito -> redireciona para contratar
    if (response.status === 402) {
      try {
        const errorData = await response.json();
        const reason = encodeURIComponent(errorData?.message || 'Limite do plano gratuito atingido');
        window.location.href = `/contratar?reason=${reason}`;
      } catch {
        window.location.href = '/contratar';
      }
      throw new Error('Limite do plano gratuito atingido');
    }
    
    if (!response.ok) {
      let errorMessage = `Erro ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        try {
          errorMessage = (await response.text()) || errorMessage;
        } catch {
          // ignore
        }
      }
      throw new Error(errorMessage);
    }
    
    // Tentar JSON; se falhar, retornar texto
    try {
      return await response.json();
    } catch {
      return await response.text();
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('Requisição expirada:', url);
      Toast.error('Tempo de resposta excedido. Tente novamente.');
    } else {
      console.error('Erro na requisição:', error);
      Toast.error(error.message || 'Erro ao processar requisição');
    }
    throw error;
  } finally {
    if (timeoutId) clearTimeout(timeoutId);
    if (shouldShowOverlay) {
      LoadingOverlay.hide();
    }
  }
}

// ============================================
// CONFIRMAÇÃO ACESSÍVEL
// ============================================

function confirmAction(message, callback) {
  if (confirm(message)) {
    callback();
  }
}

// Versão melhorada com modal customizado (opcional)
const ConfirmDialog = {
  show(titleOrOptions, message, onConfirm, onCancel = null) {
    // Retorna uma Promise que resolve com true (confirmado) ou false (cancelado)
    return new Promise((resolve) => {
    // Suporta tanto assinatura antiga (title, message, onConfirm, onCancel)
    // quanto nova com objeto de opções: { title, message, confirmText, cancelText, onConfirm, onCancel }
    let opts;
    if (typeof titleOrOptions === 'object' && titleOrOptions !== null && !Array.isArray(titleOrOptions)) {
      opts = {
        title: titleOrOptions.title || '',
        message: titleOrOptions.message || '',
        confirmText: titleOrOptions.confirmText || 'Confirmar',
        cancelText: titleOrOptions.cancelText || 'Cancelar',
        variant: titleOrOptions.variant || 'danger',
        onConfirm: titleOrOptions.onConfirm,
        onCancel: titleOrOptions.onCancel,
      };
    } else {
      opts = {
        title: titleOrOptions || '',
        message: message || '',
        confirmText: 'Confirmar',
        cancelText: 'Cancelar',
        variant: 'danger',
        onConfirm,
        onCancel,
      };
    }
    
    const modal = document.createElement('div');
    modal.className = 'confirm-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-labelledby', 'confirm-title');
    modal.setAttribute('aria-describedby', 'confirm-message');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10001;
      animation: fadeIn 0.2s;
    `;
    
    modal.innerHTML = `
      <div style="
        background: var(--card);
        padding: 24px;
        border-radius: 12px;
        max-width: 400px;
        width: 90%;
        animation: slideUp 0.3s;
      ">
        <h3 id="confirm-title" style="margin-bottom: 12px; font-size: 18px;">${opts.title}</h3>
        <p id="confirm-message" style="color: var(--muted); margin-bottom: 24px; white-space: pre-line;">${opts.message}</p>
        <div style="display: flex; gap: 12px; justify-content: flex-end;">
          <button class="btn btn-outline" id="confirm-cancel">${opts.cancelText}</button>
          <button class="btn ${opts.variant === 'danger' ? 'btn-danger' : 'btn-primary'}" id="confirm-ok">${opts.confirmText}</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    const okBtn = modal.querySelector('#confirm-ok');
    const cancelBtn = modal.querySelector('#confirm-cancel');
    
    okBtn.focus();
    
    const close = (confirmed) => {
      modal.remove();
      try {
        if (confirmed && typeof opts.onConfirm === 'function') {
          opts.onConfirm();
        } else if (!confirmed && typeof opts.onCancel === 'function') {
          opts.onCancel();
        }
      } finally {
        resolve(!!confirmed);
      }
    };
    
    okBtn.addEventListener('click', () => close(true));
    cancelBtn.addEventListener('click', () => close(false));
    modal.addEventListener('click', (e) => {
      if (e.target === modal) close(false);
    });
    
    // ESC para cancelar
    const escHandler = (e) => {
      if (e.key === 'Escape') {
        close(false);
        document.removeEventListener('keydown', escHandler);
      }
    };
    document.addEventListener('keydown', escHandler);
    });
  }
};

// ============================================
// PROMPT DIALOG ACESSÍVEL
// ============================================

const PromptDialog = {
  currentModal: null,
  show({ title, message, defaultValue = '', placeholder = '', type = 'text', required = true, onConfirm, onCancel = null }) {
    const modal = document.createElement('div');
    modal.className = 'prompt-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-labelledby', 'prompt-title');
    modal.setAttribute('aria-describedby', 'prompt-message');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10001;
      animation: fadeIn 0.2s;
    `;
    
    const inputType = type === 'date' ? 'date' : type === 'number' ? 'number' : 'text';
    const step = type === 'number' ? 'step="0.01"' : '';
    
    modal.innerHTML = `
      <div style="
        background: var(--card);
        padding: 24px;
        border-radius: 12px;
        max-width: 450px;
        width: 90%;
        animation: slideUp 0.3s;
      ">
        <h3 id="prompt-title" style="margin-bottom: 8px; font-size: 18px;">${title}</h3>
        <p id="prompt-message" style="color: var(--muted); margin-bottom: 16px; font-size: 14px;">${message}</p>
        <div style="margin-bottom: 20px;">
          <input 
            type="${inputType}" 
            id="prompt-input" 
            value="${defaultValue}"
            placeholder="${placeholder}"
            ${step}
            ${required ? 'required' : ''}
            style="
              width: 100%;
              padding: 10px 12px;
              border-radius: 8px;
              border: 1px solid rgba(148,163,184,0.3);
              background: var(--bg);
              color: var(--text);
              font-size: 14px;
            "
            aria-required="${required}"
          />
          <div id="prompt-error" role="alert" style="
            color: var(--danger);
            font-size: 12px;
            margin-top: 6px;
            display: none;
          "></div>
        </div>
        <div style="display: flex; gap: 12px; justify-content: flex-end;">
          <button class="btn btn-outline" id="prompt-cancel">Cancelar</button>
          <button class="btn btn-primary" id="prompt-ok">Confirmar</button>
        </div>
      </div>
    `;
    
  document.body.appendChild(modal);
  this.currentModal = modal;
    
    const input = modal.querySelector('#prompt-input');
    const okBtn = modal.querySelector('#prompt-ok');
    const cancelBtn = modal.querySelector('#prompt-cancel');
    const errorDiv = modal.querySelector('#prompt-error');
    
    // Focar no input
    setTimeout(() => input.focus(), 100);
    
    const showError = (msg) => {
      errorDiv.textContent = msg;
      errorDiv.style.display = 'block';
      input.style.borderColor = 'var(--danger)';
      input.setAttribute('aria-invalid', 'true');
    };
    
    const clearError = () => {
      errorDiv.style.display = 'none';
      input.style.borderColor = '';
      input.setAttribute('aria-invalid', 'false');
    };
    
    const validate = () => {
      clearError();
      const value = input.value.trim();
      
      if (required && !value) {
        showError('Este campo é obrigatório');
        return false;
      }
      
      if (type === 'number' && value && isNaN(parseFloat(value))) {
        showError('Digite um número válido');
        return false;
      }
      
      if (type === 'date' && value) {
        const date = new Date(value);
        if (isNaN(date.getTime())) {
          showError('Digite uma data válida');
          return false;
        }
      }
      
      return true;
    };
    
    const close = (confirmed) => {
      // limpar referência antes de callbacks
      if (this.currentModal === modal) {
        this.currentModal = null;
      }
      if (confirmed) {
        if (!validate()) {
          input.focus();
          return;
        }
        
        modal.remove();
        if (onConfirm) {
          onConfirm(input.value.trim());
        }
      } else {
        modal.remove();
        if (onCancel) {
          onCancel();
        }
      }
    };
    
    okBtn.addEventListener('click', () => close(true));
    cancelBtn.addEventListener('click', () => close(false));
    modal.addEventListener('click', (e) => {
      if (e.target === modal) close(false);
    });
    
    // Enter para confirmar
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        close(true);
      }
    });
    
    // ESC para cancelar
    const escHandler = (e) => {
      if (e.key === 'Escape') {
        close(false);
        document.removeEventListener('keydown', escHandler);
      }
    };
    document.addEventListener('keydown', escHandler);
  },
  close() {
    if (this.currentModal) {
      try { this.currentModal.remove(); } catch (_) {}
      this.currentModal = null;
    }
  }
};

// ============================================
// VALIDAÇÃO DE FORMULÁRIO COM FEEDBACK
// ============================================

const FormValidator = {
  showError(input, message) {
    // Remove erro anterior
    this.clearError(input);
    
    input.setAttribute('aria-invalid', 'true');
    input.style.borderColor = '#ef4444';
    
    const error = document.createElement('div');
    error.className = 'error-message';
    error.setAttribute('role', 'alert');
    error.innerHTML = `
      <span class="error-message-icon">⚠</span>
      <span>${message}</span>
    `;
    
    input.parentElement.appendChild(error);
  },
  
  clearError(input) {
    input.setAttribute('aria-invalid', 'false');
    input.style.borderColor = '';
    
    const error = input.parentElement.querySelector('.error-message');
    if (error) {
      error.remove();
    }
  },
  
  clearAllErrors(form) {
    form.querySelectorAll('input, select, textarea').forEach(input => {
      this.clearError(input);
    });
  }
};

// ============================================
// PAYMENT DIALOG (para pagamento de parcelas)
// ============================================

const PaymentDialog = {
  formasPagamento: null,
  
  async carregarFormasPagamento() {
    if (this.formasPagamento) return this.formasPagamento;
    
    try {
      const API_BASE = window.API_BASE || '';
      const response = await fetch(`${API_BASE}/api/formas-pagamento`);
      if (!response.ok) throw new Error('Erro ao carregar formas de pagamento');
      this.formasPagamento = await response.json();
      return this.formasPagamento;
    } catch (error) {
      console.error('Erro ao carregar formas de pagamento:', error);
      return [];
    }
  },
  
  async show({ parcelaId, valorOriginal, fornecedor, numeroParcela = null }) {
    return new Promise(async (resolve) => {
      const formas = await this.carregarFormasPagamento();
      const hoje = new Date().toISOString().split('T')[0];
      const valorFmt = (typeof window !== 'undefined' && window.brl) ? brl.format(valorOriginal) : valorOriginal.toFixed(2);
      
      const dialogHTML = `
        <div id="paymentDialogOverlay" role="dialog" aria-modal="true" aria-labelledby="paymentDialogTitle" style="
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.85);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10001;
          animation: fadeIn 0.2s;
        ">
          <div style="
            position: relative;
            max-width: 520px;
            width: 92vw;
            background: var(--card);
            border-radius: 16px;
            padding: 24px 20px;
            border: 1px solid rgba(148,163,184,0.15);
            box-shadow: 0 14px 40px rgba(0,0,0,0.45);
            animation: slideUp 0.25s;
          ">
            <button id="paymentCloseBtn" aria-label="Fechar" style="
              position:absolute; top:12px; right:12px;
              background:transparent; border:none; color:var(--text);
              font-size:20px; cursor:pointer; padding:6px; border-radius:8px;
            " onmouseover="this.style.background='rgba(239,68,68,0.2)'" onmouseout="this.style.background='transparent'">✕</button>
            <h3 id="paymentDialogTitle" style="margin:0 0 6px; font-size:20px;">💰 Registrar Pagamento</h3>
            <div style="margin:0 0 16px; color: var(--muted); display:flex; align-items:center; justify-content:space-between; gap:8px; flex-wrap:wrap;">
              <div><strong>${fornecedor}</strong>${numeroParcela ? ` - Parcela ${numeroParcela}` : ''}</div>
              <div class="readonly-chip" style="min-width:auto;">Valor original: ${valorFmt}</div>
            </div>
            
            <form id="paymentForm" style="display: flex; flex-direction: column; gap: 14px;">
              <div>
                <label for="dataPagamento" style="display:block; font-weight:600; color:var(--muted); margin-bottom:6px;">Data do Pagamento *</label>
                <input 
                  type="date" 
                  id="dataPagamento" 
                  value="${hoje}" 
                  required
                  style="width:100%; padding:10px; background: var(--surface); border: 1px solid rgba(148,163,184,0.2); border-radius: 10px; color: var(--text);"
                >
              </div>
              
              <div>
                <label for="valorPago" style="display:block; font-weight:600; color:var(--muted); margin-bottom:6px;">Valor Pago (R$) *</label>
                <input 
                  type="number" 
                  id="valorPago" 
                  value="${valorOriginal.toFixed(2)}" 
                  step="0.01" 
                  min="0" 
                  required
                  style="width:100%; padding:10px; background: var(--surface); border: 1px solid rgba(148,163,184,0.2); border-radius: 10px; color: var(--text);"
                >
              </div>
              
              <div>
                <div style="display:flex; align-items:flex-end; gap:8px;">
                  <div style="flex:1;">
                    <label for="formaPagamento" style="display:block; font-weight:600; color:var(--muted); margin-bottom:6px;">Forma de Pagamento</label>
                    <select 
                      id="formaPagamento"
                      style="width:100%; padding:10px; background: var(--surface); border: 1px solid rgba(148,163,184,0.2); border-radius: 10px; color: var(--text);"
                    >
                      <option value="">Selecione...</option>
                      ${formas.map(f => `<option value="${f.id}">${f.nome} ${f.banco ? `- ${f.banco}` : ''}</option>`).join('')}
                    </select>
                  </div>
                  <button type="button" id="btnAbrirNovaForma" class="btn btn-outline" style="white-space:nowrap;">+ Nova</button>
                </div>
                <div class="input-description">Cadastre rapidamente uma nova forma sem sair desta tela.</div>
                
                <div id="novaFormaContainer" style="display:none; margin-top:12px; padding:12px; border:1px solid rgba(148,163,184,0.25); border-radius:10px; background: rgba(148,163,184,0.05);">
                  <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                    <div>
                      <label style="display:block; font-weight:600; color:var(--muted); margin-bottom:6px;">Nome *</label>
                      <input id="nfNome" type="text" required placeholder="Ex: Nubank, Dinheiro" style="width:100%; padding:10px; background:var(--surface); border:1px solid rgba(148,163,184,0.2); border-radius:10px; color:var(--text);">
                    </div>
                    <div>
                      <label style="display:block; font-weight:600; color:var(--muted); margin-bottom:6px;">Tipo *</label>
                      <select id="nfTipo" required style="width:100%; padding:10px; background:var(--surface); border:1px solid rgba(148,163,184,0.2); border-radius:10px; color:var(--text);">
                        <option value="conta">Conta</option>
                        <option value="cartao_credito">Cartão de Crédito</option>
                        <option value="cartao_debito">Cartão de Débito</option>
                        <option value="dinheiro">Dinheiro</option>
                        <option value="pix">PIX</option>
                      </select>
                    </div>
                    <div>
                      <label style="display:block; font-weight:600; color:var(--muted); margin-bottom:6px;">Banco</label>
                      <input id="nfBanco" type="text" placeholder="Opcional" style="width:100%; padding:10px; background:var(--surface); border:1px solid rgba(148,163,184,0.2); border-radius:10px; color:var(--text);">
                    </div>
                    <div>
                      <label style="display:block; font-weight:600; color:var(--muted); margin-bottom:6px;">Limite de Crédito</label>
                      <input id="nfLimite" type="number" step="0.01" min="0" placeholder="Opcional" style="width:100%; padding:10px; background:var(--surface); border:1px solid rgba(148,163,184,0.2); border-radius:10px; color:var(--text);">
                    </div>
                    <div style="grid-column: 1 / -1;">
                      <label style="display:block; font-weight:600; color:var(--muted); margin-bottom:6px;">Observação</label>
                      <textarea id="nfObs" rows="2" maxlength="500" placeholder="Opcional" style="width:100%; padding:10px; background:var(--surface); border:1px solid rgba(148,163,184,0.2); border-radius:10px; color:var(--text); resize:vertical; font-family:inherit;"></textarea>
                    </div>
                  </div>
                  <div style="display:flex; gap:8px; justify-content:flex-end; margin-top:10px;">
                    <button type="button" class="btn btn-outline" id="btnCancelarNovaForma">Cancelar</button>
                    <button type="button" class="btn btn-primary" id="btnSalvarNovaForma">Salvar forma</button>
                  </div>
                </div>
              </div>
              
              <div>
                <label for="observacaoPagamento" style="display:block; font-weight:600; color:var(--muted); margin-bottom:6px;">Observação</label>
                <textarea 
                  id="observacaoPagamento"
                  rows="3"
                  maxlength="500"
                  placeholder="Informações adicionais sobre o pagamento..."
                  style="width:100%; padding:10px; background: var(--surface); border: 1px solid rgba(148,163,184,0.2); border-radius: 10px; color: var(--text); resize: vertical; font-family: inherit;"
                ></textarea>
              </div>
              
              <div style="display:flex; gap:10px; justify-content:flex-end; margin-top:6px;">
                <button type="button" class="btn btn-outline" id="paymentCancelBtn">Cancelar</button>
                <button type="submit" class="btn btn-primary" id="paymentConfirmBtn">✓ Confirmar Pagamento</button>
              </div>
            </form>
          </div>
        </div>
      `;
      
      // Inserir dialog no DOM
      const container = document.createElement('div');
      container.innerHTML = dialogHTML;
      document.body.appendChild(container);
      
  const overlay = document.getElementById('paymentDialogOverlay');
  const cancelBtn = document.getElementById('paymentCancelBtn');
  const confirmBtn = document.getElementById('paymentConfirmBtn');
  const closeBtn = document.getElementById('paymentCloseBtn');
  const form = document.getElementById('paymentForm');
  const btnAbrirNovaForma = document.getElementById('btnAbrirNovaForma');
  const btnCancelarNovaForma = document.getElementById('btnCancelarNovaForma');
  const btnSalvarNovaForma = document.getElementById('btnSalvarNovaForma');
  const novaFormaContainer = document.getElementById('novaFormaContainer');
  const selectForma = document.getElementById('formaPagamento');
      
      function close(result = null) {
        if (container && container.parentNode) container.parentNode.removeChild(container);
        resolve(result);
      }
      
      // Fechar ao clicar no overlay
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) close(null);
      });
      
      // Fechar ao pressionar ESC
      function handleEscape(e) {
        if (e.key === 'Escape') {
          close(null);
          document.removeEventListener('keydown', handleEscape);
        }
      }
      document.addEventListener('keydown', handleEscape);
      
  // Botões fechar/cancelar
  if (closeBtn) closeBtn.addEventListener('click', () => close(null));
      cancelBtn.addEventListener('click', () => close(null));

      // Alternar criação rápida de forma
      if (btnAbrirNovaForma && novaFormaContainer) {
        btnAbrirNovaForma.addEventListener('click', () => {
          novaFormaContainer.style.display = novaFormaContainer.style.display === 'none' ? 'block' : 'none';
        });
      }
      if (btnCancelarNovaForma && novaFormaContainer) {
        btnCancelarNovaForma.addEventListener('click', () => {
          novaFormaContainer.style.display = 'none';
        });
      }
      if (btnSalvarNovaForma) {
        btnSalvarNovaForma.addEventListener('click', async () => {
          try {
            const nome = document.getElementById('nfNome').value.trim();
            const tipo = document.getElementById('nfTipo').value;
            const banco = document.getElementById('nfBanco').value.trim() || null;
            const limiteStr = document.getElementById('nfLimite').value;
            const limite_credito = limiteStr ? parseFloat(limiteStr) : null;
            const observacao = document.getElementById('nfObs').value.trim() || null;
            if (!nome || !tipo) {
              Toast.warning('Preencha nome e tipo da forma.');
              return;
            }
            const API_BASE = window.API_BASE || '';
            const res = await fetch(`${API_BASE}/api/formas-pagamento`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ nome, tipo, banco, limite_credito, ativo: true, observacao })
            });
            if (!res.ok) {
              const err = await res.json().catch(() => ({}));
              throw new Error(err.detail || 'Erro ao salvar forma');
            }
            const nova = await res.json();
            // Atualizar dropdown
            if (selectForma) {
              const opt = document.createElement('option');
              opt.value = nova.id;
              opt.textContent = `${nova.nome}${nova.banco ? ' - ' + nova.banco : ''}`;
              selectForma.appendChild(opt);
              selectForma.value = String(nova.id);
            }
            Toast.success('Forma criada com sucesso!');
            if (novaFormaContainer) novaFormaContainer.style.display = 'none';
          } catch (e) {
            console.error(e);
            Toast.error(e.message || 'Erro ao criar forma');
          }
        });
      }
      
      // Botão confirmar
      confirmBtn.addEventListener('click', () => {
        if (!form.checkValidity()) {
          form.reportValidity();
          return;
        }
        
        const dataPagamento = document.getElementById('dataPagamento').value;
        const valorPago = parseFloat(document.getElementById('valorPago').value);
        const formaPagamentoId = document.getElementById('formaPagamento').value;
        const observacaoPagamento = document.getElementById('observacaoPagamento').value;
        
        close({
          paga: true,
          data_pagamento: dataPagamento,
          valor_pago: valorPago,
          forma_pagamento_id: formaPagamentoId || null,
          observacao_pagamento: observacaoPagamento || null
        });
      });
      
      // Permitir Enter no form para confirmar
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        confirmBtn.click();
      });
      
      // Focar no primeiro campo
      setTimeout(() => document.getElementById('dataPagamento').focus(), 100);
    });
  }
};

// ============================================
// INICIALIZAÇÃO
// ============================================

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    KeyboardShortcuts.init();
  });
} else {
  KeyboardShortcuts.init();
}

// Registrar atalhos globais
KeyboardShortcuts.register('?', () => KeyboardShortcuts.showHelp(), 'Mostrar ajuda de atalhos');
KeyboardShortcuts.register('escape', () => {
  // Fechar modais abertos
  document.querySelectorAll('[role="dialog"]').forEach(modal => {
    const closeBtn = modal.querySelector('[aria-label*="Fechar"]');
    if (closeBtn) closeBtn.click();
  });
}, 'Fechar modais');

// Exportar para uso global
window.LoadingOverlay = LoadingOverlay;
window.Toast = Toast;
window.ButtonLoader = ButtonLoader;
window.KeyboardShortcuts = KeyboardShortcuts;
window.fetchWithLoading = fetchWithLoading;
window.ConfirmDialog = ConfirmDialog;
window.PromptDialog = PromptDialog;
window.PaymentDialog = PaymentDialog;
window.FormValidator = FormValidator;

// Compatibilidade: algumas páginas usam showToast(msg, type) em vez de Toast.show()
window.showToast = function(message, type = 'info', duration) {
  if (typeof Toast !== 'undefined' && Toast.show) {
    Toast.show(message, type, duration);
  } else if (typeof alert === 'function') {
    alert(message);
  }
};

// ============================================
// FORMATAÇÃO DE DATAS - PADRÃO DO SISTEMA
// ============================================

/**
 * Formata data ISO (YYYY-MM-DD) para formato brasileiro (DD/MM/YYYY)
 * @param {string} dataISO - Data no formato YYYY-MM-DD ou YYYY-MM-DD HH:mm:ss
 * @returns {string} Data formatada em DD/MM/YYYY
 */
window.formatarDataBR = function(dataISO) {
  if (!dataISO) return '';
  
  // Se for data com hora, pegar apenas a parte da data
  const dataStr = dataISO.split(' ')[0];
  
  // Tentar criar data a partir do formato ISO
  const partes = dataStr.split('-');
  if (partes.length === 3) {
    const [ano, mes, dia] = partes;
    return `${dia.padStart(2, '0')}/${mes.padStart(2, '0')}/${ano}`;
  }
  
  return dataISO;
};

/**
 * Formata data ISO (YYYY-MM-DD HH:mm:ss) para formato brasileiro com hora (DD/MM/YYYY HH:mm)
 * @param {string} dataISO - Data no formato YYYY-MM-DD HH:mm:ss ou timestamp ISO
 * @returns {string} Data formatada em DD/MM/YYYY HH:mm
 */
window.formatarDataHoraBR = function(dataISO) {
  if (!dataISO) return '';
  
  try {
    const data = new Date(dataISO);
    if (isNaN(data.getTime())) return dataISO;
    
    const dia = String(data.getDate()).padStart(2, '0');
    const mes = String(data.getMonth() + 1).padStart(2, '0');
    const ano = data.getFullYear();
    const hora = String(data.getHours()).padStart(2, '0');
    const min = String(data.getMinutes()).padStart(2, '0');
    
    return `${dia}/${mes}/${ano} ${hora}:${min}`;
  } catch (e) {
    return dataISO;
  }
};

/**
 * Converte data brasileira (DD/MM/YYYY) para formato ISO (YYYY-MM-DD)
 * @param {string} dataBR - Data no formato DD/MM/YYYY
 * @returns {string} Data formatada em YYYY-MM-DD
 */
window.dataParaISO = function(dataBR) {
  if (!dataBR) return '';
  
  const partes = dataBR.split('/');
  if (partes.length === 3) {
    const [dia, mes, ano] = partes;
    return `${ano}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`;
  }
  
  return dataBR;
};
