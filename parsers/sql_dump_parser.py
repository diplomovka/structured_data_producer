import re

class TableData:
    def __init__(self):
        self.table_creation_queries = []
        self.insert_queries = []
        self.columns_names = []

    def add_insert_query(self, sql_query):
        self.insert_queries.append(sql_query)

    def add_table_query(self, sql_query):
        self.table_creation_queries.append(sql_query)

    def set_columns_names(self, columns_names):
        self.columns_names = columns_names

    def get_first_insert_query(self):
        return self.insert_queries.pop(0)

    def get_total_insert_queries(self):
        return len(self.insert_queries)


def clean_query(sql_query, query_start):
    index = sql_query.index(query_start)
    sql_query = sql_query[index:] + ';'
    sql_query = sql_query.replace('\n', '')

    return sql_query


def get_table_name_from_query(sql_query, query_start):
    table_name = sql_query[len(query_start):].split(' ')[0]
    table_name.strip()

    return table_name


def extract_columns_names(sql_query):
    result = re.search(r'\(.*\)', sql_query)
    defined_cols = result.group()
    defined_cols = defined_cols.replace('(', '', 1)

    split = defined_cols.split(',')
    column_names = []
    for defined_col in split:
        defined_col = defined_col.strip()
        col = defined_col.split(' ')[0]
        column_names.append(col)

    return column_names


def parse_queries(sql_dump):
    tables_data = {}
    ordered_table_names = []
    sql_dump_split = sql_dump.split(';')

    query_starts = ['CREATE TABLE ', 'INSERT INTO ', 'ALTER TABLE ONLY ']

    for sql_query in sql_dump_split:
        for query_start in query_starts:
            if query_start not in sql_query:
                continue

            sql_query = clean_query(sql_query, query_start)

            table_name = get_table_name_from_query(sql_query, query_start)

            if table_name not in tables_data:
                ordered_table_names.append(table_name)
                tables_data[table_name] = TableData()

            # SHOULD send creation table without insert???
            if query_start == 'INSERT INTO ':
                tables_data[table_name].add_insert_query(sql_query)

            elif query_start == 'CREATE TABLE ':
                columns_names = extract_columns_names(sql_query)
                tables_data[table_name].set_columns_names(columns_names)
                tables_data[table_name].add_table_query(sql_query)

            else:
                tables_data[table_name].add_table_query(sql_query)

            break

    return tables_data, ordered_table_names
