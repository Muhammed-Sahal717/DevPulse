import os

from sqlmodel import Session, create_engine

# 1. Fetch values from the environment variables engine
DB_USER = os.getenv("DB_USER", "sahal")
DB_PASSWORD = os.getenv("DB_PASSWORD", "sahalprojects9078")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "devpulse_db")

# 2. Build the database connection string dynamically
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 2. Create the engine instance
# This handles the low-level communication pool with Docker container
engine = create_engine(DATABASE_URL, echo=True)


# 3. Create a dependency injector for FastAPI routes
# This gives each API request a fresh, isolated database session that closes when done
def get_session():
    with Session(engine) as session:
        yield session  # The yield statement allows FastAPI to manage the session lifecycle automatically
