import httpx
from urllib.parse import urlparse
from sqlmodel import Session, create_engine
from models import Project
from database import DATABASE_URL

bg_engine = create_engine(DATABASE_URL)


async def fetch_mock_repository_stats(project_id: int):  # Keeping your function name identical
    """Asynchronously fetches real live repository statistics from the official GitHub API."""
    print(f"\n[BACKGROUND WORKER] 📡 Fetching LIVE data for Project ID: {project_id}...")

    # 1. Fetch the project and its URL from the database
    with Session(bg_engine) as session:
        project = session.get(Project, project_id)
        if not project or not project.repository_url:
            return
        repo_url = project.repository_url

    try:
        # 2. Parse the repository URL path (e.g., /muhammed-sahal717/devpulse)
        url_path = urlparse(repo_url).path.strip("/")
        path_parts = url_path.split("/")

        if len(path_parts) < 2:
            print("[BACKGROUND WORKER] ❌ Invalid GitHub URL format.")
            return

        username, repo_name = path_parts[0], path_parts[1]

        # 3. Build the target GitHub API endpoints
        repo_api_url = f"https://api.github.com/repos/{username}/{repo_name}"
        commits_api_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"

        # 4. Asynchronously call the live GitHub API endpoints
        async with httpx.AsyncClient() as client:
            # Fetch repository details (stars & issues)
            repo_response = await client.get(repo_api_url)
            # Fetch latest commits list
            commits_response = await client.get(commits_api_url)

        if repo_response.status_code == 200:
            repo_data = repo_response.json()
            
            # Extract real production statistics
            real_stars = repo_data.get("stargazers_count", 0)
            real_issues = repo_data.get("open_issues_count", 0)
            
            # Extract the latest commit message text safely
            real_commit_msg = "No commits found"
            if commits_response.status_code == 200 and len(commits_response.json()) > 0:
                real_commit_msg = commits_response.json()[0].get("commit", {}).get("message", "No message")

            # 5. Open database context and save the production telemetry metrics
            with Session(bg_engine) as session:
                db_project = session.get(Project, project_id)
                if db_project:
                    db_project.stars_count = real_stars
                    db_project.open_issues_count = real_issues
                    db_project.last_commit_message = real_commit_msg.split("\n")[0]  # First line only

                    session.add(db_project)
                    session.commit()
                    print(f"[BACKGROUND WORKER] ✅ Real metrics successfully synced for Project {project_id}!\n")
        else:
            print(f"[BACKGROUND WORKER] ❌ GitHub API responded with status: {repo_response.status_code}")

    except Exception as e:
        print(f"[BACKGROUND WORKER] ❌ Network error while connecting to GitHub: {e}")