# Sistema de Assinaturas (Billing)

Este projeto agora possui um módulo simples de assinaturas mensais para controlar o acesso e o uso do sistema.

## Conceitos
- Assinatura: vinculada a um usuário, com status (trial, ativa, inadimplente, cancelada), datas de início e próximo vencimento.
- Pagamento: registro de pagamento mensal (referência YYYY-MM), valor e método.
- Trial automática: ao primeiro uso autenticado que modifica dados, uma assinatura em `trial` de 14 dias é criada automaticamente.
- Bloqueio: requisições autenticadas que alteram o sistema (POST/PUT/PATCH/DELETE) são bloqueadas com HTTP 402 quando a assinatura está vencida.

## Tabelas criadas
- assinaturas
- pagamentos_assinatura

As tabelas são criadas automaticamente no SQLite ao iniciar o servidor (Base.metadata.create_all).

## Endpoints de Billing
- GET /api/billing/assinatura → retorna o status da sua assinatura
- POST /api/billing/assinatura/start → inicia/ativa a assinatura
  - body: { valor_mensal?: number, trial_dias?: number }
- POST /api/billing/pagamentos → registra um pagamento
  - body: { valor: number, referencia?: "YYYY-MM", metodo?: "manual|pix|boleto|cartao", transaction_id?: string }
- GET /api/billing/pagamentos → lista últimos pagamentos (padrão 12)

## Admin
- GET /api/admin/billing/stats → contadores de usuários e assinaturas
  - usuarios: cadastrados, utilizando_7d
  - assinaturas: em_dia, vencidos

## Como funciona o bloqueio
- Middleware HTTP verifica, para métodos de escrita (POST/PUT/PATCH/DELETE), se a requisição é autenticada e se a assinatura está em dia.
- Exceções liberadas: /auth, /api/billing, /api/health, /health, /api/debug, /static, /offline, /sw.js
- Se nenhum token é enviado (uso anônimo/legado), o bloqueio não é aplicado.

## Próximos passos sugeridos
- Tela/Admin UI para gestão de assinaturas e pagamentos.
- Integração com meio de pagamento (PIX, boleto, cartão) e webhooks.
- Políticas de limitação (ex.: leitura limitada) para inadimplentes em vez de bloqueio total de escrita.
- Jobs de notificação (aviso de vencimento, cobrança).
