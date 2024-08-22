import yaml
import os
from pymed import PubMed
import requests
from xml.etree import ElementTree

# Inicializar o PubMed com a biblioteca pymed
pubmed = PubMed(tool="MyTool", email="my@email.address")

def get_pubmed_id_from_doi(doi):
    # Define a URL para a pesquisa no Entrez
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    # Define os parâmetros da requisição
    params = {
        'db': 'pubmed',
        'term': doi,
        'retmode': 'xml'
    }
    
    # Faz a requisição GET para a API Entrez
    response = requests.get(url, params=params)
    
    # Verifica se a requisição foi bem sucedida
    if response.status_code == 200:
        # Analisa a resposta XML
        root = ElementTree.fromstring(response.content)
        # Obtém o ID do PubMed a partir do XML
        id_list = root.find('IdList')
        if id_list is not None:
            ids = [id_elem.text for id_elem in id_list.findall('Id')]
            if ids:
                return ids[0]  # Retorna o primeiro ID encontrado
        return None
    else:
        raise Exception(f"Erro ao buscar dados do Entrez: {response.status_code}")

def get_article_details(pmid):
    # Recuperar artigos usando pymed
    articles = list(pubmed._getArticles(article_ids=[pmid]))
    if articles:
        article = articles[0]
        article_details = {
            'title': article.title,
            'journal': article.journal,
            'publication_date': article.publication_date,
            'authors': [f"{author['firstname']} {author['lastname']}" for author in article.authors],
            'abstract': article.abstract
        }
        return article_details
    else:
        return None

# Carregar o arquivo YAML
with open('citations.yaml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

# Criar uma pasta para salvar os arquivos de texto
os.makedirs('articles', exist_ok=True)

# Processar cada DOI
for entry in data:
    doi = entry.get('id', '').replace('doi:', '').strip()
    if doi:
        try:
            # Buscar o PubMed ID usando a API Entrez
            pmid = get_pubmed_id_from_doi(doi)
            if pmid:
                # Buscar detalhes do artigo usando pymed
                article_details = get_article_details(pmid)
                if article_details:
                    file_path = os.path.join('articles', f"{doi.replace('/', '_')}.txt")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Title: {article_details['title']}\n")
                        f.write(f"Journal: {article_details['journal']}\n")
                        f.write(f"Publication Date: {article_details['publication_date']}\n")
                        f.write("Authors:\n")
                        for author in article_details['authors']:
                            f.write(f"  - {author}\n")
                        f.write(f"Abstract: {article_details['abstract']}\n")
                    print(f"Detalhes do artigo para DOI {doi} salvos em {file_path}.")
                else:
                    print(f"Nenhum detalhe encontrado para o PubMed ID {pmid}.")
            else:
                print(f"Nenhum PubMed ID encontrado para o DOI {doi}.")
        except Exception as e:
            print(f"Erro ao processar o DOI {doi}: {e}")
