/**
 * SISTEMA DE GERAÇÃO DE PLANOS DE AULA COM QR CODE
 */

const PLANILHA_ID = '1NhYxV2b0nAM_YPhH3bYmI9y9eJJP4mbbQrD-cgGyH9s';
const ABA = 'planos';
const TEMPLATE_ID = '1MN-Il4moS_NTtKoADzKGfd87C071X8l1OdbcPGVqzuA';
//const TEMPLATE_ID = '1oJEtgKdHxx-AOylh3VXb0dJrQaIJwiMDb6EVhpUe1Ic';
const TEMPLATE_BIMESTRAL_ID = '11xBDRXDczxHP2ngs-aXuCDNDufm2nYCfJMT3vMRDCEA';
//const PASTA_DESTINO_ID = '1XH8-ilVO0rBeCS7yQStPhmVFhA76cI4n';
//const PASTA_DESTINO_ID = '10loAksVqF2igayTXNbvRJajGxl_L-U_6'    //Redes de computadores
//const PASTA_DESTINO_ID = '1vQsx8JaZed2WSVvD1lLsOLSXhXOyUQ_z'      //Carreiras 
//const PASTA_DESTINO_ID = '1GSPbLZuZVV9Px8-7TwHwWK4SU07DjdWZ'      // Inteligencia Artificial
const PASTA_DESTINO_ID = '1il1zZeCIxOQ0lPHimGmbxzpzh5dGNCyI'      // Programação Backend
// --- CONFIGURAÇÃO MESTRE (Altere aqui para testar) ---
const CONFIG = {
  professor: 'Adriano Justino Rosa',
  codigoComponente: 'C2',
  modulo: 'SIS',
  bimestre: 1
};
/**
 * Função principal: Percorre a planilha e processa as linhas marcadas.
 */
function gerarPlanosComDiaAulaPreenchido() {
  const planilha = SpreadsheetApp.openById(PLANILHA_ID);
  const aba = planilha.getSheetByName(ABA);
  const valores = aba.getDataRange().getValues();
  const cabecalho = valores[0];

  const indiceDiaAula = cabecalho.indexOf('DIA_AULA');
  const indiceImprimir = cabecalho.indexOf('IMPRIMIR');

  if (indiceDiaAula === -1 || indiceImprimir === -1) {
    throw new Error('Certifique-se de que as colunas DIA_AULA e IMPRIMIR existem na planilha.');
  }

  for (let i = 1; i < valores.length; i++) {
    const linha = valores[i];
    const diaAula = String(linha[indiceDiaAula] || '').trim();
    const imprimir = String(linha[indiceImprimir] || '').trim().toUpperCase();

    // Só processa se tiver data e se a coluna IMPRIMIR for "S"
    if (diaAula !== '' && imprimir === 'S') {
      const dados = {};
      cabecalho.forEach((campo, index) => {
        dados[campo] = linha[index];
      });

      // Validação crítica para evitar o erro "Cannot read properties of undefined"
      if (!dados.ID_AULA) {
        Logger.log('Aviso: Linha ' + (i + 1) + ' ignorada pois ID_AULA está vazio.');
        continue;
      }

      try {
        // Chama a função que gera o Doc, insere QR Code e converte para PDF
        const urlPdf = gerarPlanoDeAulaQrcode(dados);

        // Marca como "N" para não gerar novamente
        aba.getRange(i + 1, indiceImprimir + 1).setValue('N');
        Logger.log('Sucesso na linha ' + (i + 1) + ': ' + urlPdf);
      } catch (erro) {
        Logger.log('Erro ao processar linha ' + (i + 1) + ': ' + erro.message);
      }
    }
  }
}


/**
 * Gera o documento, insere o QR Code e salva como PDF.
 */
function gerarPlanoDeAulaQrcode(dados) {
  const nomeArquivo = 'PLANO_' + dados.ID_AULA;
  const arquivoTemplate = DriveApp.getFileById(TEMPLATE_ID);
  const pastaDestino = DriveApp.getFolderById(PASTA_DESTINO_ID);
  
  // 1. Cria cópia do Google Docs
  const copia = arquivoTemplate.makeCopy(nomeArquivo, pastaDestino);
  const doc = DocumentApp.openById(copia.getId());
  const body = doc.getBody();

  // --- NOVA LÓGICA: Extrair links antes das substituições ---
  const links = separarLinks(dados.MATERIAIS);

  // 2. Substituições Simples
  substituir(body, 'ID_AULA', dados.ID_AULA);
  substituir(body, 'DIA_AULA', formatarData(dados.DIA_AULA));
  substituir(body, 'NOME_COMPONENTE', dados.NOME_COMPONENTE);
  substituir(body, 'COMPETENCIA', dados.COMPETENCIA);
  
  const tituloFull = String(dados.TITULO_AULA || '');
  const tituloLimpo = tituloFull.includes(':') ? tituloFull.split(':').pop().trim() : tituloFull;
  substituir(body, 'TITULO_AULA', tituloLimpo);

  // Tratamento especial dos links
  if (links.pdf) {
    body.replaceText("\\[PDF\\]", dados.ID_AULA+".pdf");
    const el = body.findText(dados.ID_AULA+".pdf");
    if(el) el.getElement().asText().setLinkUrl(links.pdf);
  } else {
    body.replaceText("\\[PDF\\]", "PDF não disponível");
  }

  if (links.ap) {
    body.replaceText("\\[AP\\]", dados.ID_AULA+"AP.pdf");
    const el = body.findText(dados.ID_AULA+"AP.pdf");
    if(el) el.getElement().asText().setLinkUrl(links.ap);
  } else {
    body.replaceText("\\[AP\\]", "Atividade Prática não disponível para essa Aula");
  }

  substituir(body, 'MATERIAIS', dados.MATERIAIS);
  substituir(body, 'APRENDIZAGEM', dados.APRENDIZAGEM);
  substituir(body, 'CONTEUDOS', dados.CONTEUDOS);
  substituir(body, 'ATIVIDADES', dados.ATIVIDADES);
  substituir(body, 'RESUMO', dados.RESUMO);
  substituir(body, 'AVALIACAO', dados.AVALIACAO);
  substituir(body, 'RECURSOS', dados.RECURSOS);

  // 3. Substituições de Listas JSON
  substituir(body, 'OBJETIVO_AULA', formatarListaJson(dados.OBJETIVO_AULA));
  //substituir(body, 'ESTRATEGIAS', formatarEstrategias(dados.ESTRATEGIAS));
  const estrategiasFormatadas = formatarListaEmLinhas(dados.ESTRATEGIAS);
  substituir(body, 'ESTRATEGIAS', estrategiasFormatadas);
  substituir(body, 'BIBLIOGRAFIA', formatarBibliografia(dados.BIBLIOGRAFIA));

  // --- QR CODE ---
  const linkParaQrCode = "https://drive.google.com/uc?export=download&id=" + copia.getId();
  const qrCodeUrl = "https://quickchart.io/qr?text=" + encodeURIComponent(linkParaQrCode) + "&size=150";
  
  try {
    const imagemBlob = UrlFetchApp.fetch(qrCodeUrl).getBlob();
    const elemento = body.findText("\\[QR_CODE\\]");
    if (elemento) {
      const rangeElement = elemento.getElement();
      const pai = rangeElement.getParent();
      if (pai.getType() == DocumentApp.ElementType.PARAGRAPH) {
         pai.asParagraph().appendInlineImage(imagemBlob);
         rangeElement.asText().deleteText(elemento.getStartOffset(), elemento.getEndOffsetInclusive());
      }
    }
  } catch (e) {
    Logger.log("Erro no QR Code: " + e.message);
  }

  doc.saveAndClose();

  // 5. Exportação para PDF
  const arquivoPdf = DriveApp.getFileById(copia.getId()).getAs(MimeType.PDF);
  arquivoPdf.setName(nomeArquivo + '.pdf');
  const pdfCriado = pastaDestino.createFile(arquivoPdf);

  // --- Registra metadados do plano na aba 'db_planos' ---
  try {
    const ss = SpreadsheetApp.openById(PLANILHA_ID);
    let sheetDb = ss.getSheetByName('db_planos');
    if (!sheetDb) {
      sheetDb = ss.insertSheet('db_planos');
      sheetDb.appendRow(['id','modulo','componente','data_aula','titulo','link_plano']);
    }

    const idPlano = dados.ID_AULA || '';
    const moduloPlano = String(idPlano).substring(0, 3);
    const componentePlano = CONFIG.codigoComponente || '';
    const dataAulaFormatada = formatarData(dados.DIA_AULA);
    const tituloPlano = tituloLimpo || '';
    const urlPdfCriado = pdfCriado.getUrl();

    sheetDb.appendRow([idPlano, moduloPlano, componentePlano, dataAulaFormatada, tituloPlano, urlPdfCriado]);
  } catch (e) {
    Logger.log('Erro ao salvar em db_planos: ' + e.message);
  }

  //copia.setTrashed(true);
  return pdfCriado.getUrl();
}

/**
 * Auxiliar para separar os links do Google Drive
 */
function separarLinks(conteudoBruto) {
  const regex = /https:\/\/drive\.google\.com\/file\/d\/[a-zA-Z0-9_-]+\/view\?usp=drivesdk/g;
  const links = String(conteudoBruto).match(regex);
  return {
    pdf: links && links[0] ? links[0] : null,
    ap: links && links[1] ? links[1] : null
  };
}
//fim recupera

/**
 * FUNÇÕES AUXILIARES DE FORMATAÇÃO
 */

function formatarListaEmLinhas(texto) {
  if (!texto) return "";
  
  // Divide a string onde houver "; " e junta novamente com uma quebra de linha (\n)
  return texto.split('; ').join('\n');
}

function substituir(body, campo, valor) {
  const texto = valor !== null && valor !== undefined ? String(valor) : '';
  body.replaceText('\\[' + campo + '\\]', texto);
}

function formatarData(valor) {
  if (!valor) return '';
  if (Object.prototype.toString.call(valor) === '[object Date]' && !isNaN(valor)) {
    return Utilities.formatDate(valor, Session.getScriptTimeZone(), 'dd/MM/yyyy');
  }
  return String(valor).trim();
}

function formatarListaJson(jsonTexto) {
  if (!jsonTexto) return '';
  let itens;
  try { itens = typeof jsonTexto === 'string' ? JSON.parse(jsonTexto) : jsonTexto; } 
  catch (e) { return String(jsonTexto); }
  
  return itens.map(item => typeof item === 'string' ? '• ' + item : '• ' + Object.values(item).join(' - ')).join('\n');
}

function formatarEstrategias(jsonTexto) {
  if (!jsonTexto) return '';
  let itens;
  try { itens = typeof jsonTexto === 'string' ? JSON.parse(jsonTexto) : jsonTexto; } 
  catch (e) { return String(jsonTexto); }

  let resultado = '';
  itens.forEach((item, index) => {
    if (typeof item === 'string') {
      resultado += (index + 1) + '. ' + item + '\n\n';
    } else if (item && typeof item === 'object') {
      const etapa = item.ETAPA || '';
      const descricao = item.DESCRICAO || '';
      resultado += (index + 1) + '. ' + (etapa ? etapa + '\n' + descricao : Object.values(item).join(' - ')) + '\n\n';
    }
  });
  return resultado.trim();
}

function formatarBibliografia(jsonTexto) {
  return formatarListaJson(jsonTexto);
}

function teste() {
  gerarPlanoDeAulaQrcode();
}

//--- FUNÇÃO PARA EXECUTAR (CHAME ESTA!) ---
function rodarGeracaoTabela() {
  const ano = 'ANO2';
  const codComponente = 'C2';
  const bimestre = 1;
  
  // Obtenha esses valores de onde estiverem (ex: célula da planilha)
  const params = {
    professor: 'Adriano Justino Rosa',
    codigoComponente: codComponente,
    modulo: 'SIS',
    bimestre: bimestre
  };
  
  const dados = buscarDados(ano, codComponente, bimestre);
  
  if (dados.length > 0) {
    const url = gerarTabela(dados, params);
    Logger.log('Documento gerado: ' + url);
  } else {
    Logger.log('Nenhum dado encontrado para o filtro.');
  }
}

// --- BUSCA OS DADOS ---


// Você não precisa mais passar argumentos nas funções, 
// elas leem direto a constante CONFIG definida no topo.

function buscarDados() {
  const ss = SpreadsheetApp.openById(PLANILHA_ID);
  const sheet = ss.getSheetByName(ABA);
  const valores = sheet.getDataRange().getValues();
  const dados = [];

  for (let i = 1; i < valores.length; i++) {
    const linha = valores[i];
    const str = linha[0];

    if (!str) continue;

    const match = str.match(/B(\d+)/);
    if (!match) continue;

    const bimestreExtraido = parseInt(match[1], 10);
    const moduloExtraido = str.substring(0, 3);

    // Comparação usando a variável global CONFIG
    if (bimestreExtraido !== CONFIG.bimestre || moduloExtraido !== CONFIG.modulo) {
      if (dados.length > 0) break; // Para o processamento se já pegamos o bloco
      continue;
    }
    
    dados.push({
     
        ID_AULA: valores[i][0],          // Coluna A
        DIA_AULA: valores[i][1],
        TITULO_AULA: valores[i][4],
        OBJETIVO_AULA: valores[i][5],
        NOME_COMPONENTE: valores[i][2],  // Coluna C
        MATERIAIS: valores[i][6],        // Coluna G
        APRENDIZAGEM: valores[i][7], // Coluna H
        CONTEUDOS: valores[i][8],    // Coluna I
        AVALIACAO: valores[i][9],    // Coluna J
        RECURSOS: valores[i][10],    // Coluna K
        ESTRATEGIAS: valores[i][11]  // Coluna L
      
    });
  }
  return dados;
}
 

function gerarTabela(listaDados, params) {
  const template = DriveApp.getFileById(TEMPLATE_BIMESTRAL_ID);
  const pasta = DriveApp.getFolderById(PASTA_DESTINO_ID);
  
  // Nome do arquivo: Professor + Código Componente
  const nomeArquivo = params.professor + '_' + params.codigoComponente + '_B' + params.bimestre;
  const copia = template.makeCopy(nomeArquivo, pasta);
  const doc = DocumentApp.openById(copia.getId());
  const body = doc.getBody();
  
  // 1. Substituição de Placeholders no cabeçalho
  //const nomeComponente = (String(item.NOME_COMPONENTE));
  //console.log(listaDados[0].NOME_COMPONENTE)
  substituir(body, 'bimestre',  params.bimestre);
  substituir(body, 'professor',  params.professor);
  substituir(body, 'componente',  params.codigoComponente);
  substituir(body, 'nomecomponente',  listaDados[0].NOME_COMPONENTE);
  //body.replaceText('[bimestre]', params.bimestre);
  //body.replaceText('[professor]', params.professor);
  //body.replaceText('[componente]', params.codigoComponente);
  //body.replaceText('[nomecomponente]', nomeComponente);
  
  // 2. Processamento da Tabela
  const tabela = body.getTables()[0];
  const linhaModelo = tabela.getRow(1);

  listaDados.forEach(item => {
    const novaLinha = tabela.appendTableRow(linhaModelo.copy());
    //novaLinha.getCell(0).setText(String(item.ID_AULA)+'  '+String(item.DIA_AULA));
    novaLinha.getCell(0).setText(formatarCelulaIDeData(item.ID_AULA, item.DIA_AULA, item.TITULO_AULA));
    novaLinha.getCell(1).setText(String(item.OBJETIVO_AULA));
    novaLinha.getCell(2).setText(String(item.APRENDIZAGEM));
    novaLinha.getCell(3).setText(String(item.CONTEUDOS));
    novaLinha.getCell(4).setText(String(item.AVALIACAO));
    novaLinha.getCell(5).setText(String(item.RECURSOS) + '\n \n' + item.MATERIAIS);
    novaLinha.getCell(6).setText(String(item.ESTRATEGIAS));
  });

  tabela.removeRow(1);
  doc.saveAndClose();
  return copia.getUrl();
}

/**
 * Função para formatar o texto da primeira coluna
 */
function formatarCelulaIDeData(idAula, diaAula, titulo) {
  const id = String(idAula || '');
  const data = formatarData(diaAula); // Usa sua função existente
  return id + '\n' + data + '\n' + titulo;
}