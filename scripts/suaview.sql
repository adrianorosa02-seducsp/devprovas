-- View: escopo_sequencia (base) + materiais_didaticos + aprendizagens_essenciais
CREATE OR REPLACE VIEW v_escopo_materiais AS
SELECT 
    e.id AS escopo_id,
    e.id_aula,
    e.ano_referencia,
    e.bimestre,
    e.etapa AS escopo_etapa,
    e.componente AS escopo_componente,
    e.ano AS escopo_ano,
    e.id_ae AS escopo_id_ae,
    e.prefixo_ae AS escopo_prefixo_ae,
    e.aula AS escopo_aula,
    e.conteudo AS escopo_conteudo,
    e.objetivos_aprendizagem AS escopo_objetivos,
    e.habilidades AS escopo_habilidades,
    e.aprendizagem_essencial AS escopo_ae,
    e.pagina_pdf AS escopo_pagina,
    -- Materiais Didáticos
    m.id AS material_id,
    m.serie,
    m.cod_cronograma,
    m.id_cronograma,
    m.titulo AS material_titulo,
    m.tipo AS material_tipo,
    m.ordenacao,
    m.semana,
    m.aulas_com_tarefa,
    m.arquivos,
    m.link_url_youtube,
    m.array_links_youtube,
    -- Aprendizagens Essenciais
    ae.id AS ae_id,
    ae.etapa AS ae_etapa,
    ae.componente AS ae_componente,
    ae.ano AS ae_ano,
    ae.id_ae AS ae_id_ae,
    ae.prefixo AS ae_prefixo,
    ae.codigo_ae AS ae_codigo_ae,
    ae.descricao AS ae_descricao,
    ae.habilidade_priorizada AS ae_habilidade_priorizada,
    ae.habilidades_relacionadas AS ae_habilidades_relacionadas,
    ae.conhecimentos_previos AS ae_conhecimentos_previos,
    ae.prova_paulista AS ae_prova_paulista,
    ae.saresp AS ae_saresp,
    ae.desenvolvimento_aprendizagem AS ae_desenvolvimento
FROM escopo_sequencia e
LEFT JOIN materiais_didaticos m
    ON e.id_aula = m.id_aula
    AND e.ano_referencia = m.ano_referencia
    AND e.bimestre = m.bimestre
LEFT JOIN aprendizagens_essenciais ae
    ON e.aprendizagem_essencial #>> '{}' = ae.habilidade_priorizada
    AND e.ano_referencia = ae.ano_referencia;