import os
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from config import get_api_keys
from lib.shell_util import (
    RESET_COLOR, WHITE_ON_BLACK, LIGHT_PINK
)
from lib.litellm_client import create_litellm_client_embeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pydantic')

EMBEDDINGS_CACHE_DIR = ".arcode.embeddings"

def get_top_relevant_files(startpath, upload_filter, query, model_embedding, num_files=42):
    """
    Get the top N relevant files to a given query using embeddings.

    Args:
        startpath (str): The starting directory path to scan for files.
        upload_filter (UploadedFileFilter): Filter class to determine if a file should be considered.
        query (str): The query to compare file contents against.
        model_embedding (str): The embedding model to use for comparison.
        num_files (int): Number of most relevant file chunks to retrieve.

    Returns:
        list: A list of dictionaries containing file paths, data and relevance scores.
    """
    api_base = None
    api_version = None
    if model_embedding.startswith('azure/'):
        api_key, api_base, api_version = get_api_keys(model_embedding)
    else:
        api_key = get_api_keys(model_embedding)

    store = LocalFileStore(f"{startpath}/{EMBEDDINGS_CACHE_DIR}/")
    embeddings = create_litellm_client_embeddings(model=model_embedding, api_key=api_key, api_base=api_base, api_version=api_version)
    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        embeddings, store, namespace=embeddings.model
    )

    file_contents = []
    files = []

    for root, _, file_list in os.walk(startpath):
        for file in file_list:
            file_path = os.path.join(root, file)
            if (upload_filter.should_upload(os.path.relpath(os.path.join(root, file), startpath))):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        file_contents.append(Document(page_content=content, metadata={'source': file_path}))
                        files.append((file_path, content))
                except UnicodeDecodeError:
                    # Skip files that can't be read as UTF-8
                    continue

    if not file_contents:
        return []

    text_splitter = CharacterTextSplitter(chunk_size=2500, chunk_overlap=20)
    docs = text_splitter.split_documents(file_contents)

    db = DocArrayInMemorySearch.from_documents(docs, cached_embedder)

    # Performing similarity search
    similarities = db.similarity_search_with_score(query, k=num_files)
    print(f"\n{WHITE_ON_BLACK} 🔎 {LIGHT_PINK} Sorting and filtering... {RESET_COLOR}")
    sorted_files = sorted([(doc.metadata['source'], score) for doc, score in similarities], key=lambda x: x[1], reverse=True)
    top_files = []
    for file, score in sorted_files[:num_files]:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = f.read()
                top_files.append({'path': file, 'data': data, 'score': score})
        except UnicodeDecodeError:
            # Skip files that can't be read as UTF-8
            continue

    return top_files