-- View completa: materiais_didaticos + escopo_sequencia
CREATE OR REPLACE VIEW v_materiais_completo AS
SELECT 
    m.id AS material_id,
    m.id_aula,
    m.ano_referencia,
    m.bimestre,
    m.serie,
    m.componente,
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
    -- Escopo-Sequência
    e.id AS escopo_id,
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
    e.pagina_pdf AS escopo_pagina
FROM devprovas.materiais_didaticos m
LEFT JOIN devprovas.escopo_sequencia e 
    ON m.id_aula = e.id_aula
    AND m.ano_referencia = e.ano_referencia
WHERE m.id_aula IS NOT NULL;