from sqlalchemy import BigInteger, Integer


# PostgreSQL usa BIGINT; SQLite de pruebas necesita INTEGER para autoincrementar.
ID_TYPE = BigInteger().with_variant(Integer, "sqlite")

