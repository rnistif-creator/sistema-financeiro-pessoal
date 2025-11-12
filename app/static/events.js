// Delegação de eventos para remover dependência de atributos inline
// Suporta data-onclick, data-onchange, data-onsubmit, data-oninput, data-onmouseover, data-onmouseout
// Cada atributo deve conter uma chamada de função: exemplo: data-onclick="excluirLancamento(123)"
// Segurança: parsing limitado a números, strings, booleanos, null. Evita eval arbitrário.
(function(){
  // Eventos suportados para data-action e data-on*
  const ATTR_MAP = {
    click: 'onclick', // usado para data-onclick
    change: 'onchange',
    input: 'oninput',
    submit: 'onsubmit'
    // Importante: NÃO interceptamos mouseover/mouseout para não quebrar efeitos inline simples
  };

  // data-action padrão: executa window[valor] sem argumentos adicionais
  // data-args (JSON) opcional: array ou objeto; se for array -> spread como args; objeto -> passado como único arg
  // Ex: <button data-action="editarLancamento" data-args='[123]'>Editar</button>
  //     <button data-action="aplicarPeriodoRapido" data-args='"mes_atual"'>Mês Atual</button>
  //     <button data-action="salvarConfigWidgets">Salvar</button>

  function parseCall(str){
    // Match funcName(args)
    const m = /^([a-zA-Z_$][\w$]*)\s*\((.*)\)$/.exec(str.trim());
    if(!m){ return null; }
    const name = m[1];
    const argsRaw = m[2].trim();
    if(!argsRaw) return { name, args: [] };
    const args = [];
    // Tokenize quoted strings or numbers/booleans/null
    const rgx = /'(.*?)'|"(.*?)"|(true|false|null)|(-?\d+(?:\.\d+)?)|/g;
    let lastIndex = 0; let match; let parts=[];
    while((match = rgx.exec(argsRaw))){
      if(match.index === lastIndex){
        lastIndex = rgx.lastIndex;
        if(match[1] !== undefined) parts.push(match[1]);
        else if(match[2] !== undefined) parts.push(match[2]);
        else if(match[3] !== undefined){
          if(match[3] === 'true') parts.push(true); else if(match[3]==='false') parts.push(false); else parts.push(null);
        } else if(match[4] !== undefined){
          parts.push(parseFloat(match[4]));
        }
      } else {
        lastIndex = rgx.lastIndex;
      }
    }
    return { name, args: parts };
  }

  function invokeCallString(callStr, el, evt){
    try {
      const parsed = parseCall(callStr);
      if(!parsed) return false; // não é chamada de função -> não interferir
      const { name, args } = parsed;
      const fn = window[name];
      if(typeof fn === 'function') {
        fn.apply(el, args.concat(evt));
      } else {
        console.warn('Função não encontrada:', name);
      }
    } catch (e){
      console.error('Erro executando handler delegado', callStr, e);
    }
    return true;
  }

  function invokeDataAction(el, evt){
    const action = el.getAttribute('data-action');
    if(!action) return false;
    const fn = window[action];
    if(typeof fn !== 'function'){
      console.warn('Função data-action não encontrada:', action);
      return false;
    }
    let raw = el.getAttribute('data-args');
    let parsedArgs = [];
    if(raw){
      try {
        // Permitir formas simples: número, string, array, objeto
        // Se for string pura sem aspas, tratamos como string
        raw = raw.trim();
        if(raw !== '' && !raw.startsWith('{') && !raw.startsWith('[') && !(raw.startsWith('"') || raw.startsWith("'"))){
          // transforma em string JSON
          raw = JSON.stringify(raw);
        }
        const data = JSON.parse(raw);
        if(Array.isArray(data)) parsedArgs = data; else parsedArgs = [data];
      } catch(e){
        console.warn('Falha ao parsear data-args:', raw, e);
      }
    }
    try {
      fn.apply(el, parsedArgs.concat(evt));
    } catch(e){
      console.error('Erro executando data-action', action, e);
    }
    return true;
  }

  function handleEvent(evt){
    const type = evt.type;
    const baseAttr = ATTR_MAP[type];
    const dataAttr = 'data-' + baseAttr;
    let el = evt.target;
    while(el && el !== document){
      // 1. data-action genérico
      if(el.hasAttribute('data-action')){
        // execute sem bloquear navegação a menos que retorne false
        const result = invokeDataAction(el, evt);
        if(result === false) {
          // se função não encontrada, não faz nada
        } else {
          // Se a função explicitamente retornar false, impedir ação padrão
          // (usuário pode usar 'return false;' dentro da função se quiser bloquear)
        }
        break;
      }
      // 2. data-<legacy> somente se for chamada de função válida
      if(el.hasAttribute(dataAttr)){
        if(invokeCallString(el.getAttribute(dataAttr), el, evt)){
          if(type === 'submit') evt.preventDefault();
          break;
        }
      }
      // 3. NÃO interceptar atributos inline (onclick, onchange, etc.)
      //    Deixamos o navegador executar normalmente (CSP atualmente permite 'unsafe-inline').
      el = el.parentElement;
    }
  }

  Object.keys(ATTR_MAP).forEach(type => {
    document.addEventListener(type, handleEvent, true); // capture para pegar antes de side-effects
  });

  // Removemos migração automática para não interferir com inline existente.
})();
