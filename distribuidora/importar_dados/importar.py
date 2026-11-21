import os
import sys
import django
import pandas as pd

# 1. Aponta para a raiz do projeto (projeto_integrador/) e carrega as configurações do Django
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 2. Importa os Models Vendedor e Cliente
from distribuidora.models import Cliente, Vendedor

def importar_csv():
    caminho_csv = os.path.join(
        BASE_DIR, 
        'distribuidora', 
        'data', 
        'clientes_distribuidora_normalizado.csv'
    )

    # Lê o CSV mantendo zeros à esquerda em CNPJ, CEP e telefone
    df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig', dtype=str)

    criados = 0
    atualizados = 0

    for _, row in df.iterrows():
        # Trata a data de cadastro
        data_val = pd.to_datetime(row['data_cadastro'], errors='coerce')
        data_cad = data_val.date() if pd.notnull(data_val) else None

        # Trata o CEP: se for 'Não informado' ou diferente de 8 dígitos, salva como None (NULL)
        # para não ultrapassar o max_length=8 definido no models.py
        cep_val = str(row['cep']).strip()
        if cep_val == 'Não informado' or len(cep_val) != 8:
            cep_val = None

        # Trata o telefone (converte 'Não informado' ou vazio para None)
        tel_val = str(row['telefone']).strip()
        if not tel_val or tel_val in ['Não informado', 'nan']:
            tel_val = None

        # Busca ou cria o Vendedor na tabela Vendedor para obter a ForeignKey
        nome_vend = str(row['vendedor_responsavel']).strip()
        vendedor_obj, _ = Vendedor.objects.get_or_create(
            nome_vendedor=nome_vend
        )

        # Salva ou atualiza o Cliente mapeando exatamente para os campos do models.py
        _, created = Cliente.objects.update_or_create(
            id_cliente=row['id_cliente'].strip(),
            defaults={
                'razao_social': row['razao_social'].strip(),
                'cnpj_normalizado': row['cnpj'].strip(),
                'telefone_normalizado': tel_val,
                'email': row['email'].strip() if pd.notnull(row['email']) else None,
                'bairro_normalizado': row['bairro_informado'].strip(),
                'cep_normalizado': cep_val,
                'data_cadastro_normalizado': data_cad,
                'vendedor': vendedor_obj,
            }
        )

        if created:
            criados += 1
        else:
            atualizados += 1

    print(f"Importação concluída com sucesso!")
    print(f"Clientes criados: {criados} | Atualizados: {atualizados}")
    print(f"Total de vendedores cadastrados: {Vendedor.objects.count()}")

if __name__ == '__main__':
    importar_csv()