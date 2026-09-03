from sqlalchemy import create_engine
from urllib.parse import quote
from sqlalchemy.orm import sessionmaker
senha_codificada = quote("BATATA526!@#")

database_url = f"mysql+pymysql://root:{senha_codificada}@localhost/california_cafe"
engine = create_engine(database_url, echo=True)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db():
    return session_local()