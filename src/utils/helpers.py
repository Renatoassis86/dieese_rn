import hashlib
from pathlib import Path

def get_file_hash(file_path: Path) -> str:
    """
    Gera o hash SHA-256 de um arquivo para fins de rastreabilidade e versionamento.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Lê o arquivo em blocos para não sobrecarregar a memória
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def create_metadata(file_path: Path, source_url: str, provider: str) -> dict:
    """
    Gera um dicionário de metadados para acompanhar os arquivos da camada Bronze.
    """
    import datetime
    return {
        "file_name": file_path.name,
        "provider": provider,
        "source_url": source_url,
        "extraction_timestamp": datetime.datetime.now().isoformat(),
        "file_hash": get_file_hash(file_path),
        "file_size_bytes": file_path.stat().st_size
    }
