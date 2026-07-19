from app.core.database import SessionLocal
from app.models.models import AprendizagemEssencial


def main():

    db = SessionLocal()

    try:

        ae = AprendizagemEssencial(

            ano_referencia=2025,

            etapa="EFAI",

            componente="Matemática",

            ano=1,

            id_ae="EF01MAAE1",

            prefixo="EF01MA",

            codigo_ae="AE1",

            descricao="Identificar as figuras geométricas planas, reconhecendo-as nos objetos do cotidiano.",

            habilidade_priorizada="EF01MA14",

            habilidades_relacionadas=[
                {"codigo": "EF01MA01"},
                {"codigo": "EF01MA02"}
            ],

            conhecimentos_previos=[
                {"codigo": "EF01MA03"}
            ],

            prova_paulista=[
                "3º bim.: 5,8,9",
                "3º bim.: 10,11"
            ],

            saresp=[
                "Item 14",
                "Item 18"
            ],

            desenvolvimento_aprendizagem=[
                {
                    "ordem": 1,
                    "bloco_tematico": "Geometria",
                    "materiais_digitais": "3º bim.: 5,8",
                    "livro_estudante": "Volume 3 - p.22"
                }
            ]
        )

        db.add(ae)

        db.commit()

        db.refresh(ae)

        print("\n====================================")
        print("REGISTRO GRAVADO COM SUCESSO")
        print("====================================")

        print(f"UUID.............: {ae.id}")
        print(f"id_AE............: {ae.id_ae}")
        print(f"Descrição........: {ae.descricao}")
        print(f"Criado em........: {ae.created_at}")

    except Exception as e:

        db.rollback()

        print("\nERRO:")
        print(e)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()