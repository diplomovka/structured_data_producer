import os

STRUCTURED_DATA_TOPIC = str(os.getenv('STRUCTURED_DATA_TOPIC') or 'STRUCTURED_DATA_TOPIC')

STRUCTURED_DATA_SCHEMA_PATH = str(os.getenv('STRUCTURED_DATA_SCHEMA_PATH') or './avro_files/structured_data.avsc')

BOOTSTRAP_SERVERS = str(os.getenv('BOOTSTRAP_SERVERS') or 'localhost:9092')
SCHEMA_REGISTRY_URL = str(os.getenv('SCHEMA_REGISTRY_URL') or 'http://localhost:8085')
OFFSET = str(os.getenv('OFFSET') or 'earliest')
ENCODING = str(os.getenv('ENCODING') or 'utf_8')
AVRO_FILES_ENCODING = str(os.getenv('AVRO_FILES_ENCODING') or 'utf-8')
SQL_FILES_ENCODING = str(os.getenv('SQL_FILES_ENCODING') or 'utf-8')
