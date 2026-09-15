-- View para relacionar materiais_didaticos com escopo_sequencia via id_aula
CREATE OR REPLACE VIEW v_materiais_escopo_sequencia AS
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
    e.id AS escopo_id,
    e.etapa,
    e.componente AS escopo_componente,
    e.ano AS escopo_ano,
    e.id_ae,
    e.prefixo_ae,
    e.aula,
    e.conteudo,
    e.objetivos_aprendizagem,
    e.habilidades,
    e.aprendizagem_essencial,
    e.pagina_pdf
FROM devprovas.materiais_didaticos m
LEFT JOIN devprovas.escopo_sequencia e 
    ON m.id_aula = e.id_aula
    AND m.ano_referencia = e.ano_referencia
WHERE m.id_aula IS NOT NULL;