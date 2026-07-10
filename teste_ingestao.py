# No seu arquivo teste_ingestao.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, MaterialDidatico  # Agora o app.models entende o que buscar
from scripts.carregar_dados_sed_teste import carregar_dados_sed_teste # Importando do seu script

# Configuração (Dica: use variáveis de ambiente para não expor o DB)
DATABASE_URL = "postgresql://appuser:appsenha@db.inetz.com.br:5432/appdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# No seu teste_ingestao.py, você pode adicionar isto antes de rodar a ingestão:
from app.models import Base
# ...
Base.metadata.create_all(engine)

def run_test():
    db = SessionLocal()
    # O seu token obtido no payload
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJMT0dJTiI6InJnMjAwOTU0MjM0c3AiLCJOSUNLTkFNRSI6IkFEUklBTk9KVVNUSU4yMDA5NTQyIiwiQ0RfVVNVQVJJTyI6IjEwMDAwMDA5Njk2ODAwIiwidW5pcXVlX25hbWUiOiJQRVJGSVMiLCJQRVJGSVMiOiJbe1wiQ0RfUEVSRklMXCI6XCI0XCIsXCJOTV9QRVJGSUxcIjpcIlByb2Zlc3NvclwiLFwiTlJfQ09NUE9SVEFNRU5UT1wiOlwiNFwiLFwiQ09NUE9SVEFNRU5UT1wiOlwiUHJvZmVzc29yXCJ9LHtcIkNEX1BFUkZJTFwiOlwiMTY1MVwiLFwiTk1fUEVSRklMXCI6XCJQcm9mZXNzb3IgLSAgQXVsYSBFdmVudHVhbFwiLFwiTlJfQ09NUE9SVEFNRU5UT1wiOlwiNFwiLFwiQ09NUE9SVEFNRU5UT1wiOlwiUHJvZmVzc29yXCJ9LHtcIkNEX1BFUkZJTFwiOlwiMTY3NFwiLFwiTk1fUEVSRklMXCI6XCJQQUVFVC0gUHJvZmVzc29yIGRlIEFwb2lvIGFvIEVuc2lubyBUw6ljbmljbyBcIixcIk5SX0NPTVBPUlRBTUVOVE9cIjpcIjNcIixcIkNPTVBPUlRBTUVOVE9cIjpcIkVzY29sYVwifV0iLCJOQU1FIjoiQURSSUFOTyBKVVNUSU5PIFJPU0EiLCJNRVRPRE9MT0dJTiI6IkdPVkJSIiwiQ1BGIjoiMTEwNTczODE4MzciLCJFTUFJTCI6ImFkcmlhbm9AaWRlYWwudHVyLmJyIiwibmJmIjoxNzgzNjM2ODUzLCJleHAiOjE3ODM3MjMyNTMsImlhdCI6MTc4MzYzNjg1M30.ByJFGdY8W0qRbHtwwJ88BWEwxQQk5OhkjWCDkCvP5T8"
    
    try:
        print("Executando ingestão direta da API SED...")
        carregar_dados_sed_teste(db, token)
        print("Sucesso! Verifique seu PostgreSQL.")
    except Exception as e:
        print(f"Erro na execução: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_test()

