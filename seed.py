import random
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select
from database import engine
from models import User, Project, Task, DailyLog
from security import hash_password

def seed_db():
    with Session(engine) as session:
        # 1. Get or create a dummy user
        user = session.exec(select(User)).first()
        if not user:
            print("No user found. Creating a dummy user (dummy@example.com / password123)...")
            user = User(
                email="dummy@example.com",
                hashed_password=hash_password("password123")
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"Created user: {user.email}")
        else:
            print(f"Using existing user: {user.email}")
        
        # 2. Create a dummy project
        project = Project(
            name="Dummy DevPulse Project",
            description="A very dummy project injected for testing UI components",
            repository_url="https://github.com/dummy/repo",
            user_id=user.id
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        print(f"Created project: {project.name} (ID: {project.id})")

        # 3. Create dummy tasks
        tasks = [
            Task(title="Design database schema", status="DONE", project_id=project.id, time_spent=2.5),
            Task(title="Setup FastAPI backend", status="DONE", project_id=project.id, time_spent=4.0),
            Task(title="Implement Kanban drag & drop", status="IN_PROGRESS", project_id=project.id, session_start_time=datetime.now(timezone.utc) - timedelta(minutes=45)),
            Task(title="Refactor shadcn components", status="IN_PROGRESS", project_id=project.id),
            Task(title="Write unit tests for UI", status="TODO", project_id=project.id),
            Task(title="Optimize background webhook aggregator", status="TODO", project_id=project.id),
            Task(title="Dockerize the application", status="TODO", project_id=project.id),
        ]
        session.add_all(tasks)

        # 4. Create dummy logs
        now = datetime.now(timezone.utc)
        logs = []
        for i in range(5):
            logs.append(
                DailyLog(
                    date=now - timedelta(days=i),
                    lines_written=random.randint(100, 500),
                    hours_spent=round(random.uniform(2.0, 8.0), 1),
                    bugs_resolved=random.randint(0, 5),
                    summary=f"This is a dummy log for day {i} ago. Worked on some very dummy features and resolved a few dummy bugs. Synced from Github.",
                    project_id=project.id
                )
            )
        session.add_all(logs)

        session.commit()
        print("Successfully injected dummy data!")

if __name__ == "__main__":
    seed_db()
