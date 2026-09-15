#!/usr/bin/env python
"""Importa fixtures SED para tabela materiais_didaticos no PostgreSQL."""

import json
import uuid
from pathlib import Path
from sqlalchemy import insert, select

from app.core.database import SessionLocal, engine
from sqlalchemy import Table, MetaData


# Mapeamento do código SED do componente para o prefixo de 2 letras usado no escopo_sequencia
# Formato do id_aula: EF01MA1 (EF=Ensino Fundamental, 01=1º ano, MA=Matemática, 1=Aula 1)
COMPONENTE_PREFIXO_MAP = {
    "13": "MA",   # Matemática
    "1": "LP",    # Língua Portuguesa
    "2": "CI",    # Ciências
    "3": "HI",    # História
    "4": "GE",    # Geografia
    "5": "IN",    # Inglês
    "6": "AR",    # Artes
    "7": "EF",    # Educação Física
}


TIPO_ENSINO_PREFIXO_MAP = {
    "1": "EF",   # Ensino Fundamental
    "2": "EM",   # Ensino Médio
}


def gerar_id_aula(tipo_ensino: str, serie: str, componente: str, aula_numero: int) -> str:
    """Gera o id_aula no formato EF01MA1."""
    prefixo_tipo = TIPO_ENSINO_PREFIXO_MAP.get(str(tipo_ensino), "EF")
    serie_formatada = str(serie).zfill(2)
    prefixo_componente = COMPONENTE_PREFIXO_MAP.get(str(componente), str(componente).upper()[:2])
    return f"{prefixo_tipo}{serie_formatada}{prefixo_componente}{aula_numero}"


def import_fixture(fixture_path: Path, db_session):
    """Importa um arquivo fixture para a tabela materiais_didaticos."""
    
    # Carrega a tabela existente via reflection
    metadata = MetaData()
    metadata.reflect(bind=engine, only=['materiais_didaticos'])
    materiais_table = metadata.tables['materiais_didaticos']
    
    # Lê o fixture
    with open(fixture_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    request = data['request']
    response = data['response']
    
    # Extrai parâmetros do request
    ano = int(request['Ano'])
    bimestre = int(request['Bimestre'])
    serie = request['Serie']
    componente = request['Componente']
    tipo_ensino = request.get('TipoEnsino', '1')
    
    # Prepara registros para insert
    records = []
    for item in response:
        arquivos = [
            {
                "idCronograma": arq['idCronograma'],
                "idArquivo": arq['idArquivo'],
                "nomeArquivo": arq['nomeArquivo'],
                "linkDownload": arq['linkDownload'],
                "baixou": arq['baixou'],
                "utilizou": arq['utilizou'],
                "avaliou": arq['avaliou'],
                "ativo": arq['ativo'],
                "dtArquivo": arq['dtArquivo'],
                "tipoArquivo": arq['tipoArquivo']
            }
            for arq in item['arquivos']
        ]
        
        # Usa ordenacao como número da aula para TODOS os itens (garante id_aula único)
        aula_numero = item.get('ordenacao', 0)
        if aula_numero <= 0:
            # Se não tem ordenacao válida, usa hash do cod_cronograma para garantir unicidade
            aula_numero = abs(hash(str(item['codCronogramaAula']))) % 10000 + 1
        
        id_aula = gerar_id_aula(tipo_ensino, serie, componente, aula_numero)
        
        record = {
            'id': uuid.uuid4(),
            'ano_referencia': ano,
            'bimestre': bimestre,
            'serie': serie,
            'componente': componente,
            'cod_cronograma': item['codCronogramaAula'],
            'id_cronograma': item['idCronogramaAula'],
            'titulo': item['titulo'],
            'tipo': item['tipo'],
            'ordenacao': item['ordenacao'],
            'semana': item['semana'],
            'aulas_com_tarefa': item['aulasComTarefa'],
            'link_url_youtube': item['linkUrlYoutube'],
            'exibir_municipio': item['exibirMunicipio'],
            'arquivos': arquivos,
            'array_links_youtube': item['arrayLinksYoutube'],
            'id_aula': id_aula
        }
        records.append(record)
    
    # Verifica se já existem registros para evitar duplicatas
    existing = db_session.execute(
        select(materiais_table.c.cod_cronograma)
        .where(
            materiais_table.c.ano_referencia == ano,
            materiais_table.c.bimestre == bimestre,
            materiais_table.c.serie == serie,
            materiais_table.c.componente == componente
        )
    ).scalars().all()
    
    existing_set = set(existing)
    new_records = [r for r in records if r['cod_cronograma'] not in existing_set]
    
    if new_records:
        db_session.execute(insert(materiais_table), new_records)
        db_session.commit()
        print(f"  Inseridos {len(new_records)} novos registros")
    else:
        print(f"  Todos os {len(records)} registros já existem")
    
    return len(new_records)


def main():
    fixture_dir = Path(__file__).parent.parent / "tests" / "fixtures" / "materiais-digitais"
    
    if not fixture_dir.exists():
        print(f"Diretório não encontrado: {fixture_dir}")
        return
    
    db = SessionLocal()
    try:
        total = 0
        for year_dir in sorted(fixture_dir.iterdir()):
            if year_dir.is_dir():
                for fixture_file in sorted(year_dir.glob("*.json")):
                    print(f"Importando {fixture_file.relative_to(fixture_dir)}...")
                    total += import_fixture(fixture_file, db)
        print(f"\nTotal de novos registros: {total}")
    finally:
        db.close()


if __name__ == "__main__":
    main()