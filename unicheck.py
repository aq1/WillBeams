from pipeline.unicheck import run_server
from pipeline.kvstorage.postgres import PostgresKV


if __name__ == '__main__':
    run_server(PostgresKV())
