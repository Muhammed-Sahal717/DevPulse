from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session

from database import engine, get_session

# Import models so SQLModel registers them
from models import Project, ProjectCreate

app = FastAPI(
    title="DevPulse",
    description="The core backend API engine for the DevPulse Developer Dashboard",
    version="0.1.0",
)


# This event runner triggers exactly when the API boots up
@app.on_event("startup")
def on_startup():
    # This creates our tables in PostgreSQL if they don't exist yet!
    SQLModel.metadata.create_all(engine)


@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Welcome to the DevPulse Backend Core Engine",
    }


# NEW ROUTE: Create a brand new project record
@app.post("/projects", response_model=Project, status_code=201)
def create_project(
    project_data: ProjectCreate, session: Session = Depends(get_session) # This line uses FastAPI's dependency injection to provide a database session to the route handler
):
    # 1. Convert the inbound ProjectCreate validation object into a true Project DB entry
    db_project = Project.model_validate(project_data)

    # 2. Stage the object inside our current database session transaction
    session.add(db_project)

    # 3. Write it out to the physical PostgreSQL database
    session.commit()

    # 4. Refresh our local variable so it grabs the DB-generated ID and timestamp
    session.refresh(db_project)

    # 5. Return the full database record back to the frontend
    return db_project
