from sqlmodel import Session, create_engine

# 1. Define PostgreSQL connection string
# Format: postgresql://[user]:[password]@[host]:[port]/[database_name]
DATABASE_URL = "postgresql://sahal:sahalprojects9078@localhost:5432/devpulse_db"

# 2. Create the engine instance
# This handles the low-level communication pool with Docker container
engine = create_engine(DATABASE_URL, echo=True)


# 3. Create a dependency injector for FastAPI routes
# This gives each API request a fresh, isolated database session that closes when done
def get_session():
    with Session(engine) as session:
        yield session  # The yield statement allows FastAPI to manage the session lifecycle automatically
