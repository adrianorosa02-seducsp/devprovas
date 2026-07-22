-- View para relacionar materiais_didaticos com aprendizagens_essenciais via prefixo da aula
CREATE OR REPLACE VIEW v_materiais_aprendizagens_essenciais AS
SELECT 
    m.id AS material_id,
    m.id_aula,
    m.ano_referencia,
    m.bimestre,
    m.serie,
    m.componente AS material_componente,
    m.cod_cronograma,
    m.id_cronograma,
    m.titulo AS material_titulo,
    m.tipo AS material_tipo,
    m.ordenacao,
    m.semana,
    m.arquivos,
    m.link_url_youtube,
    m.array_links_youtube,
    ae.id AS ae_id,
    ae.etapa,
    ae.componente AS ae_componente,
    ae.ano AS ae_ano,
    ae.id_ae,
    ae.prefixo,
    ae.codigo_ae,
    ae.descricao,
    ae.habilidade_priorizada,
    ae.habilidades_relacionadas,
    ae.conhecimentos_previos,
    ae.prova_paulista,
    ae.saresp,
    ae.desenvolvimento_aprendizagem AS ae_objetivos
FROM devprovas.materiais_didaticos m
LEFT JOIN devprovas.aprendizagens_essenciais ae 
    ON LEFT(m.id_aula, LENGTH(ae.prefixo)) = ae.prefixo
    AND m.ano_referencia = ae.ano_referencia
WHERE m.id_aula IS NOT NULL;