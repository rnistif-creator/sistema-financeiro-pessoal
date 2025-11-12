/**
 * CONFIGURAÇÃO GLOBAL DO SISTEMA
 * Centraliza constantes e configurações usadas em todo o frontend
 */

// Base URL da API - Usar caminho relativo para funcionar em qualquer ambiente
const API_BASE = window.location.origin;

// Configurações de formatação
const LOCALE = 'pt-BR';
const CURRENCY = 'BRL';

// Formatadores reutilizáveis
const formatters = {
  currency: new Intl.NumberFormat(LOCALE, { 
    style: 'currency', 
    currency: CURRENCY 
  }),
  
  number: new Intl.NumberFormat(LOCALE, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }),
  
  date: (dateStr) => {
    if (!dateStr) return '';
    const [ano, mes, dia] = dateStr.split('-');
    return `${dia}/${mes}/${ano}`;
  },
  
  datetime: new Intl.DateTimeFormat(LOCALE, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
};

// Funções auxiliares
const helpers = {
  // Obtém data atual no formato ISO (YYYY-MM-DD)
  todayISO() {
    const d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().split('T')[0];
  },
  
  // Parse de número com suporte a vírgula ou ponto
  parseNumber(value) {
    if (typeof value === 'number') return value;
    if (!value) return 0;
    const n = Number(String(value).replace(',', '.'));
    return isNaN(n) ? 0 : n;
  },
  
  // Formata número para usar vírgula como separador decimal
  formatNumber(value) {
    return String(value).replace('.', ',');
  },
  
  // Debounce para limitar chamadas de funções
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
};

// Exportar para uso global
window.CONFIG = {
  API_BASE,
  LOCALE,
  CURRENCY,
  formatters,
  helpers
};

// Manter compatibilidade com código existente que usa essas variáveis diretamente
window.API_BASE = API_BASE;

// Função brl() que pode ser usada de duas formas:
// 1. Como função: brl(1234.56) -> "R$ 1.234,56"
// 2. Como objeto com .format(): brl.format(1234.56) -> "R$ 1.234,56"
window.brl = Object.assign(
  (value) => formatters.currency.format(value),
  { format: (value) => formatters.currency.format(value) }
);

window.formatarData = formatters.date;
window.todayISO = helpers.todayISO;
window.parseNumber = helpers.parseNumber;
window.formatNumber = helpers.formatNumber;
