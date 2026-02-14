import psycopg
from psycopg.rows import dict_row
from typing import List
from consulta_ecom.models.product import ProductSchema
from consulta_ecom.utils.logger import setup_logger
import os

class DatabaseManager:
    def __init__(self):
        self.logger = setup_logger("DatabaseManager")
        # Dados vindos do seu .env.prd 
        self.conn_info = (
            f"host={os.getenv('PG_HOST')} "
            f"port={os.getenv('PG_PORT')} "
            f"dbname={os.getenv('PG_DB')} "
            f"user={os.getenv('PG_USER')} "
            f"password={os.getenv('PG_PASSWORD')}"
        )

    def init_db(self):
        """Cria a tabela se não existir (DDL de infra)"""
        with psycopg.connect(self.conn_info) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS results (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        price NUMERIC(10,2),
                        url TEXT UNIQUE NOT NULL,
                        image TEXT,
                        source VARCHAR(50),
                        page INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
        self.logger.info("Infraestrutura de banco verificada/criada.")

    def save_products(self, products: List[ProductSchema]):
        """Insere produtos usando a técnica de Upsert (evita duplicatas pela URL)"""
        with psycopg.connect(self.conn_info) as conn:
            with conn.cursor() as cur:
                with cur.copy("COPY results (title, price, url, image, source, page) FROM STDIN") as copy:
                    for p in products:
                        copy.write_row((p.title, p.price, p.url, p.image, p.source, p.page))
                conn.commit()
        self.logger.info(f"{len(products)} produtos processados no banco.")