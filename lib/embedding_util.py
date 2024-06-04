import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document  
from lib.file_util import is_binary_file, is_ignored
from config import API_KEY

EMBEDDING_MODEL = "text-embedding-3-small"

def get_top_relevant_files(startpath, ignore_patterns, query, num_files=42):
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
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    file_contents.append(Document(page_content=content, metadata={'source': file_path}))  
                    files.append((file_path, content))

    if not file_contents:
        return []

    text_splitter = CharacterTextSplitter(chunk_size=2500, chunk_overlap=20)
    docs = text_splitter.split_documents(file_contents)

    embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)
    db = DocArrayInMemorySearch.from_documents(docs, embeddings)
    
    similarities = db.similarity_search_with_score(query, k=max(num_files, len(docs)))

    sorted_files = sorted(zip(files, [score for _, score in similarities]), key=lambda x: x[1], reverse=True)
    top_files = [{'path': file[0], 'data': file[1]} for file, _ in sorted_files[:num_files]]

    return top_files
