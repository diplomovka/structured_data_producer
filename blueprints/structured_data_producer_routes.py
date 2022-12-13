import settings
from flask import Blueprint
from flask import request, jsonify
from uuid import uuid4
from hashlib import sha256
from pathlib import Path
from producers.structured_data_producer import set_up_producer, delivery_report
from serialization_classes.structured_data import StructuredData
from parsers.sql_dump_parser import parse_queries

producer = set_up_producer()

structured_data_producer_routes = Blueprint('structured_data_producer_routes', __name__)

@structured_data_producer_routes.route('/upload', methods=['POST'])
def upload_sql_dump():
    # handling sql dump source: https://roytuts.com/python-flask-rest-api-file-upload/
    if 'sql_dump' not in request.files:
        res = jsonify({
            'message': 'There is no sql dump in request.'
        })
        res.status_code = 400
        return res

    sql_dump = request.files['sql_dump']
    if sql_dump.filename == '' or not Path(sql_dump.filename).suffix == '.sql':
        res = jsonify({
            'message': 'No sql dump file was uploaded.'
        })
        res.status_code = 400
        return res

    file_content_bytes = sql_dump.read()

    tables_data, ordered_table_names = parse_queries(file_content_bytes.decode('utf-8'))

    produce_structured_data(ordered_table_names, tables_data)

    res = jsonify({
        'message': 'Structured data were successfully uploaded.'
    })
    res.status_code = 200
    return res


def produce_structured_data(ordered_table_names, tables_data):
    for table_name in ordered_table_names:
        table_data = tables_data[table_name]

        producer.poll(0.0)
        
        if table_data.get_total_insert_queries() == 0:
            # There might be a case, when one table has foreign key of the other,
            # but table which is refered by foreign key doesn't have data.
            # In this scenario, data lake has to create it's table, even though it doesn't have data, because it is referenced
            structured_data = StructuredData(data_hash=None, table_name=table_name, insert_query=None,
                columns_names=table_data.columns_names, table_creation_queries=table_data.table_creation_queries)

        else:
            # first insert query will be send with all sql queries required for table creation
            first_insert_query = table_data.get_first_insert_query()

            data_hash = sha256(first_insert_query.encode('utf-8')).hexdigest()
            structured_data = StructuredData(data_hash=data_hash, table_name=table_name, insert_query=first_insert_query,
                columns_names=table_data.columns_names, table_creation_queries=table_data.table_creation_queries)

            producer.produce(topic=settings.STRUCTURED_DATA_TOPIC, key=str(uuid4()),
                                value=structured_data, on_delivery=delivery_report)

            for insert_query in table_data.insert_queries:
                producer.poll(0.0)

                data_hash = sha256(insert_query.encode('utf-8')).hexdigest()
                structured_data = StructuredData(data_hash=data_hash, table_name=table_name, insert_query=insert_query,
                    columns_names=table_data.columns_names, table_creation_queries=[])

                producer.produce(topic=settings.STRUCTURED_DATA_TOPIC, key=str(uuid4()),
                                value=structured_data, on_delivery=delivery_report)
    
    producer.flush()