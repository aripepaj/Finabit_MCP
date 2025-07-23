@echo off
pip install mcp qdrant-client sentence-transformers pyodbc
REM Optional: for faster HuggingFace downloads
pip install "huggingface_hub[hf_xet]"
REM Pre-download the embedding model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2').encode('Hello world')"
echo Setup complete! You can now use the extension.
pause