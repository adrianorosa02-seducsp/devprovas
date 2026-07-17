#!/usr/bin/env python
"""Importa fixtures SED para tabela materiais_didaticos no PostgreSQL."""

import json
import uuid
from pathlib import Path
from sqlalchemy import insert, select

from app.core.database import SessionLocal, engine
from sqlalchemy import Table, MetaData


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
        
        record = {
            'id': uuid.uuid4(),
            'ano_referencia': ano,
            'bimestre': bimestre,
            'serie': serie,
            'componente': componente,
            'cod_cronograma': item['codCronogramaAula'],
            'id_cronograma': item['idCronogramaAula'],
            'titulo': item['titulo'],
            'referencia_id': item['referenciaId'],
            'tipo': item['tipo'],
            'ordenacao': item['ordenacao'],
            'semana': item['semana'],
            'aulas_com_tarefa': item['aulasComTarefa'],
            'link_url_youtube': item['linkUrlYoutube'],
            'exibir_municipio': item['exibirMunicipio'],
            'arquivos': arquivos,
            'array_links_youtube': item['arrayLinksYoutube']
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