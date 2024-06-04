import os
import dill as pickle  # Use dill instead of pickle
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from lib.file_util import is_binary_file, is_ignored
from config import API_KEY
from lib.checksum_util import calculate_directory_checksum
from lib.shell_util import (
    RESET_COLOR, BLACK_ON_WHITE, WHITE_ON_BLACK,
    LIGHT_PINK
)

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pydantic')

EMBEDDING_MODEL = "text-embedding-3-small"
CACHE_FILENAME = ".codey.cache.pkl"
CHECKSUM_FILENAME = ".codey.checksum.txt"

def get_top_relevant_files(startpath, ignore_patterns, query, num_files=42):
    current_checksum = calculate_directory_checksum(startpath, ignore_patterns)

    if os.path.exists(CHECKSUM_FILENAME):
        with open(CHECKSUM_FILENAME, 'r') as f:
            cached_checksum = f.read().strip()
    else:
        cached_checksum = ""

    if os.path.exists(CACHE_FILENAME) and cached_checksum == current_checksum:
        print(f"{WHITE_ON_BLACK} 📖 {LIGHT_PINK} Reading from cache... {RESET_COLOR}")
        with open(CACHE_FILENAME, 'rb') as f:
            cache_data = pickle.load(f)
            documents = [Document(**doc) for doc in cache_data['documents']]
            embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)
            db = DocArrayInMemorySearch.from_documents(documents, embeddings)
    else:
        file_contents = []
        files = []

        for root, _, file_list in os.walk(startpath):
            for file in file_list:
                file_path = os.path.join(root, file)
                if (
                    not is_ignored(file, ignore_patterns)
                    and not is_ignored(file_path, ignore_patterns)
                    and not is_binary_file(file)
                ):
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

        embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)
        db = DocArrayInMemorySearch.from_documents(docs, embeddings)

        cache_data = {
            'documents': [doc.dict() for doc in docs]
        }

        print(f"{WHITE_ON_BLACK} 📖 {BLACK_ON_WHITE} Writing cache... {RESET_COLOR}")
        with open(CACHE_FILENAME, 'wb') as f:
            pickle.dump(cache_data, f)
        with open(CHECKSUM_FILENAME, 'w') as f:
            f.write(current_checksum)

    # Performing similarity search
    similarities = db.similarity_search_with_score(query, k=num_files)
    print(f"{WHITE_ON_BLACK} 🔎 {LIGHT_PINK} Sorting and filtering... {RESET_COLOR}")
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
