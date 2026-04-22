Odoo Vendor Portal
==================

Visao Geral
===========

O modulo ``vendor_portal_odoo`` cria um fluxo de cotacao com fornecedores via
portal do Odoo. A equipe de compras pode convidar fornecedores registrados,
receber as respostas no portal, aprovar a melhor oferta e gerar a cotacao de
compra a partir do fornecedor escolhido.

Recursos Principais
===================

* Cadastro de fornecedores aptos a acessar o portal.
* Envio de convite por e-mail para cada RFQ.
* Portal para o fornecedor consultar RFQs e enviar sua proposta.
* Historico de cotacoes por fornecedor.
* Definicao manual ou automatica do fornecedor aprovado.
* Geracao de ``purchase.order`` a partir da cotacao vencedora.

Dependencias
============

O modulo depende destes aplicativos do Odoo:

* ``website``
* ``purchase``
* ``portal``
* ``contacts``
* ``stock``

Como Instalar
=============

1. Copie a pasta ``vendor_portal_odoo`` para o diretorio de addons do seu Odoo.
2. Atualize a lista de aplicativos.
3. Procure por ``Odoo Vendor Portal``.
4. Instale o modulo.

Permissoes Recomendadas
=======================

* Usuarios internos devem pertencer ao grupo de Compras
  (``purchase.group_purchase_user``) para operar o modulo.
* Fornecedores acessam apenas o portal e nao precisam de acesso interno ao
  backend.

Configuracao Inicial
====================

1. Acesse ``Vendor Portal > Vendors > Vendors``.
2. Abra o contato do fornecedor.
3. Clique em ``Make Portal User``.
4. O sistema criara o usuario de portal e enviara o convite de acesso.
5. Se o fornecedor ja tiver conta, use o mesmo assistente para enviar a
   redefinicao de senha.

Configuracao das Mensagens
==========================

1. Acesse ``Vendor Portal > Configuration > Settings``.
2. Escolha como o sistema deve marcar uma RFQ como concluida:

   * menor preco cotado
   * menor prazo de entrega

3. Ajuste as mensagens exibidas no portal para:

   * envio da cotacao
   * aprovacao da cotacao
   * cotacao nao aprovada
   * RFQ cancelada
   * pedido de compra gerado

Como Usar
=========

1. Acesse ``Vendor Portal > Vendor Quotations > Vendor Quotations``.
2. Crie uma nova RFQ.
3. Preencha:

   * produto
   * quantidade
   * valor estimado
   * data da cotacao
   * data limite
   * data estimada de entrega
   * fornecedores convidados

4. Clique em ``Send Invitation Mail`` para enviar o convite aos fornecedores.
5. O status da RFQ mudara para ``In Progress``.
6. Os fornecedores acessarao o portal em ``/my/vendor_rfqs`` e informarao:

   * preco cotado
   * data estimada de entrega
   * observacoes

7. Acompanhe as respostas na aba ``Vendor Quote Details``.
8. Quando quiser encerrar a RFQ, voce pode:

   * usar ``Mark as Done`` e escolher manualmente o fornecedor vencedor
   * aguardar o cron diario marcar automaticamente a RFQ conforme a regra da
     configuracao

9. Com a RFQ em ``Done``, clique em ``Create RFQ`` para gerar a cotacao de
   compra no modulo de Compras.
10. Use o botao ``Purchase Order`` para abrir o documento gerado.

Fluxo do Fornecedor no Portal
=============================

1. O fornecedor recebe o convite por e-mail.
2. Faz login no portal.
3. Abre ``RFQs`` na area ``My Account``.
4. Consulta os detalhes da solicitacao.
5. Envia ou atualiza sua proposta enquanto a RFQ estiver em andamento.
6. Visualiza a mensagem final quando a cotacao for aceita, rejeitada,
   cancelada ou convertida em pedido.

Automacao
=========

O modulo instala um ``cron`` diario chamado ``Set RFQs as Done``. Ele procura
RFQs com data de encerramento no dia atual e, quando houver cotacoes
registradas, aprova automaticamente o fornecedor conforme a configuracao
definida em ``Settings``.

Boas Praticas
=============

* Convide apenas fornecedores com e-mail valido.
* Defina a data limite antes de enviar os convites.
* Revise se todos os fornecedores convidados estao com acesso ao portal.
* Ajuste as mensagens do portal para refletir o seu processo de compras.

Suporte Operacional
===================

Se alguma RFQ nao aparecer para o fornecedor:

* confirme que o contato foi registrado como fornecedor de portal
* confirme que o fornecedor esta selecionado no campo ``Vendors``
* confirme que a RFQ nao ficou em ``Draft``
* confirme que o usuario entrou com a conta correta no portal
