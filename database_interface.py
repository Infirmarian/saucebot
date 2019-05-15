import sqlalchemy
import os
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DATABASE = os.environ['DB_NAME']
CLOUD_SQL_CONN_NAME = os.environ['PSQL_CLOUD_INSTANCE']

db_pool = sqlalchemy.create_engine(
    sqlalchemy.engine.url.URL(
        drivername='postgres+pg8000',
        username=DB_USER,
        password=DB_PASSWORD,
        database=DATABASE,
        query={
            'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(CLOUD_SQL_CONN_NAME)
        }
    ),
)

def execute_query(query, results=False):
    rs = None
    with db_pool.connect() as conn:
        exe = conn.execute(query)
        if results:
            rs = exe.fetchall()
    return rs
