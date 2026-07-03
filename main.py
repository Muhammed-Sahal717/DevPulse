from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, SQLModel, select

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
    project_data: ProjectCreate,
    session: Session = Depends(
        get_session
    ),  # This line uses FastAPI's dependency injection to provide a database session to the route handler
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


# GET ALL PROJECTS (With Professional Pagination)
@app.get("/projects", response_model=list[Project])
def read_projects(
    offset: int = 0,  # Default starting point for pagination, offset=0 means start from the first record
    limit: int = Query(
        default=10, le=100
    ),  # Default 10 records, maximum 100, le means "less than or equal to"
    session: Session = Depends(get_session),
):
    # 1. Construct an SQL SELECT statement
    statement = (
        select(Project).offset(offset).limit(limit)
    )  # It means "skip the first 'offset' records and then take the next 'limit' records"

    # 2. Execute the query against PostgreSQL and collect the results
    projects = session.exec(
        statement
    ).all()  # The .all() method fetches all the results of the executed query and returns them as a list of Project objects

    # 3. Return the array list
    return projects


# GET A SINGLE PROJECT BY ID (With Clean Error Handling)
@app.get("/projects/{project_id}", response_model=Project)
def read_project(project_id: int, session: Session = Depends(get_session)):
    # This line uses FastAPI's dependency injection to provide a database session to the route handler

    # 1. Search the table directly using the primary key ID
    project = session.get(Project, project_id) # Can search by primary key directly, and also returns None if the record doesn't exist

    # 2. DEFENSIVE PROGRAMMING: If the ID doesn't exist, raise a clean HTTP 404 Exception
    if not project:
        raise HTTPException(
            status_code=404, detail=f"Project with ID {project_id} not found"
        )

    # 3. Otherwise, return the target record data
    return project
