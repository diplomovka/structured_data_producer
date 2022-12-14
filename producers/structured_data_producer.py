# created based on: https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/avro_producer.py

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka import SerializingProducer
import settings

def structured_data_to_dict(structured_data, ctx):
    return dict(data_hash=structured_data.data_hash, table_name=structured_data.table_name,
                insert_query=structured_data.insert_query, columns_names=structured_data.columns_names,
                table_creation_queries=structured_data.table_creation_queries)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message {msg.key()} delivered to {msg.topic()} [{msg.partition()}, {msg.offset()}]')

def set_up_producer():
    schema_registry_conf = {'url': settings.SCHEMA_REGISTRY_URL}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    with open(settings.STRUCTURED_DATA_SCHEMA_PATH, 'r', encoding=settings.AVRO_FILES_ENCODING) as f:
        schema_str = f.read()

    avro_serializer = AvroSerializer(schema_registry_client,
                                     schema_str,
                                     structured_data_to_dict)

    producer_conf = {
        'bootstrap.servers': settings.BOOTSTRAP_SERVERS,
        'key.serializer': StringSerializer(settings.ENCODING),
        'value.serializer': avro_serializer
    }

    return SerializingProducer(producer_conf)
