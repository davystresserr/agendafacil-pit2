/**
 * Cria no Google Forms o formulário de teste do AgendaFácil para os colegas
 * (mesmo roteiro de docs/situacao-3/formulario-colegas.md).
 *
 * Como usar: abra https://script.google.com, crie um projeto, cole este
 * arquivo, ajuste LINK_DO_SITE e execute a função criarFormulario.
 * Os links do formulário aparecem no "Registro de execução".
 */
const LINK_DO_SITE = 'https://agendafacil-l7je.onrender.com';

function criarFormulario() {
  const form = FormApp.create('Teste do AgendaFácil');
  form.setDescription(
    'Obrigado por testar! Você não precisa conhecer o sistema: siga o roteiro e marque o que aconteceu. ' +
    'Seja sincero, os erros que você encontrar vão ajudar a melhorar o sistema.\n\n' +
    'Endereço do sistema: ' + LINK_DO_SITE + '\n\n' +
    'Se a primeira página demorar até 1 minuto para abrir, é normal: o servidor gratuito "acorda" no primeiro acesso.\n' +
    'Se algo der erro, tire um print (Windows: Win+Shift+S · Mac: Cmd+Shift+4 · celular: botões de print).'
  );
  form.setCollectEmail(false);
  form.setProgressBar(true);

  const colunas = ['OK', 'Falhou', 'Não testei'];

  // Identificação
  form.addTextItem().setTitle('Seu nome').setRequired(true);
  form.addDateItem().setTitle('Data do teste').setRequired(true);
  form.addTextItem()
    .setTitle('Dispositivo e navegador')
    .setHelpText('Ex.: notebook Windows + Chrome, iPhone + Safari')
    .setRequired(true);

  // Parte A
  form.addPageBreakItem()
    .setTitle('Parte A: como cliente')
    .setHelpText(
      'A1. Abra o endereço do sistema → deve aparecer a lista de serviços com preço e duração.\n' +
      'A2. Clique em Criar conta, preencha (pode usar e-mail fictício, ex.: seunome@teste.com) com senha de 8+ caracteres e escreva a confirmação DIFERENTE de propósito → aviso "As senhas não conferem".\n' +
      'A3. Corrija a confirmação e clique em Criar conta → "Conta criada com sucesso!" e seu nome no topo.\n' +
      'A4. Clique em Sair e entre com senha ERRADA → "E-mail ou senha incorretos."\n' +
      'A5. Entre com a senha certa → "Olá, {seu nome}!"\n' +
      'A6. Clique em Agendar em um serviço, escolha profissional e data de segunda a sábado → botões com horários livres.\n' +
      'A7. Escolha um horário, escreva uma observação e confirme → "Agendamento confirmado" e o item em Meus agendamentos como "Agendado".\n' +
      'A8. Tente agendar de novo o mesmo horário com o mesmo profissional → o horário não aparece mais.\n' +
      'A9. Escolha um domingo → "Nenhum horário livre nesta data."\n' +
      'A10. Em Meus agendamentos, clique em Cancelar e depois em Voltar → nada muda.\n' +
      'A11. Clique em Cancelar e depois em Sim, confirmar → "Agendamento cancelado" e status "Cancelado".\n' +
      'A12. Agende para hoje, daqui a menos de 2 horas (se houver horário) → "Cancelamento indisponível (menos de 2h)".\n' +
      'A13. Digite o endereço seguido de /admin/ → "Acesso negado".\n' +
      'A14. Digite o endereço seguido de /pagina-que-nao-existe → "Página não encontrada" com botão para voltar.\n' +
      'A15. Repita A1, A6 e A7 no celular → tela ajustada e menu ☰ funcionando.'
    );
  form.addGridItem()
    .setTitle('Resultado da Parte A')
    .setRows([
      'A1 Lista de serviços', 'A2 Senhas diferentes', 'A3 Criar conta', 'A4 Senha errada',
      'A5 Login', 'A6 Horários livres', 'A7 Confirmar agendamento', 'A8 Mesmo horário',
      'A9 Domingo', 'A10 Cancelar → Voltar', 'A11 Cancelar → Confirmar', 'A12 Menos de 2h',
      'A13 /admin/', 'A14 Página inexistente', 'A15 Celular'
    ])
    .setColumns(colunas)
    .setRequired(true);

  // Parte B
  form.addPageBreakItem()
    .setTitle('Parte B: profissional e administrador (opcional)')
    .setHelpText(
      'Peça os acessos ao Davy. Se não fizer esta parte, marque "Não testei".\n\n' +
      'B1. Entre como profissional → a agenda com os atendimentos.\n' +
      'B2. Em Meus horários disponíveis, adicione um domingo das 10:00 às 12:00 → "Horário adicionado."\n' +
      'B3. Entre como administrador e crie um serviço com preço 0 → mensagem de erro sobre o preço.\n' +
      'B4. Crie um serviço válido → ele aparece na página inicial.'
    );
  form.addGridItem()
    .setTitle('Resultado da Parte B')
    .setRows(['B1 Agenda do profissional', 'B2 Adicionar horário', 'B3 Serviço com preço 0', 'B4 Serviço válido'])
    .setColumns(colunas)
    .setRequired(true);

  // Resultado
  form.addPageBreakItem().setTitle('Resultado do teste');
  form.addParagraphTextItem()
    .setTitle('1. O que você testou e funcionou?')
    .setHelpText('Ex.: cadastro, login, agendamento (A6–A7)')
    .setRequired(true);
  form.addParagraphTextItem()
    .setTitle('2. O que você testou e NÃO funcionou, e o que deve ser corrigido?')
    .setHelpText('Para cada problema: número do passo, o que você fez, o que aconteceu, o que esperava e o nome do print. Se nada falhou, escreva "nada".')
    .setRequired(true);
  form.addParagraphTextItem()
    .setTitle('3. Alguma funcionalidade você não testou? Por quê?')
    .setHelpText('Ex.: "Parte B, não recebi acesso" ou "A12, não havia horário hoje"')
    .setRequired(true);
  form.addParagraphTextItem().setTitle('4. Sugestões de melhoria (opcional)');
  form.addParagraphTextItem()
    .setTitle('5. Prints')
    .setHelpText('Cole aqui o link dos prints (Google Drive, por exemplo) ou liste os nomes dos arquivos que você mandou para o Davy.');

  Logger.log('Link para os colegas responderem: ' + form.getPublishedUrl());
  Logger.log('Link para você editar: ' + form.getEditUrl());
}
