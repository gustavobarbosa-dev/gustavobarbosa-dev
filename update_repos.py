import urllib.request
import json
import os
import sys

USERNAME = "gustavobarbosa-dev"
API_URL = f"https://api.github.com/users/{USERNAME}/repos?sort=updated&direction=desc&per_page=20"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

LANGUAGE_COLORS = {
    "Python": "3776AB",
    "TypeScript": "3178C6",
    "JavaScript": "F7DF1E",
    "HTML": "E34F26",
    "CSS": "1572B6",
    "Java": "ED8B00",
}

START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"


def fetch_latest_repos():
    req = urllib.request.Request(API_URL)
    req.add_header("User-Agent", "Mozilla/5.0")
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"token {GITHUB_TOKEN}")

    try:
        with urllib.request.urlopen(req) as response:
            repos = json.loads(response.read().decode())
        repos = [r for r in repos if not r["fork"] and r["name"] != USERNAME]
        repos.sort(key=lambda r: r["pushed_at"], reverse=True)
        return repos[:4]
    except Exception as e:
        print(f"ERROR: failed to reach the GitHub API: {e}")
        return []


def generate_projects_table(repos):
    if not repos:
        return "_No public repositories to list yet._"

    rows = ["| Project | Language | Description |", "| --- | --- | --- |"]
    for repo in repos:
        name = repo["name"]
        url = repo["html_url"]
        description = (repo["description"] or "No description provided.").replace("|", "/")
        language = repo["language"] or "—"
        color = LANGUAGE_COLORS.get(language, "6E7681")
        badge = (
            f'![{language}](https://img.shields.io/badge/-{language}-{color}?style=flat-square&logoColor=white)'
            if language != "—"
            else "—"
        )
        rows.append(f"| [{name}]({url}) | {badge} | {description} |")

    return "\n".join(rows)


def update_readme(table_markdown):
    filename = "README.md"
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found at repository root.")
        sys.exit(1)

    with open(filename, "r", encoding="utf-8") as file:
        readme = file.read()

    start_idx = readme.find(START_MARKER)
    end_idx = readme.find(END_MARKER)

    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        print("ERROR: README.md is missing the PROJECTS markers.")
        sys.exit(1)

    before_section = readme[: start_idx + len(START_MARKER)]
    after_section = readme[end_idx:]

    new_readme = f"{before_section}\n{table_markdown}\n{after_section}"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(new_readme)

    print("README.md updated with the latest projects.")


if __name__ == "__main__":
    print("Fetching latest repositories...")
    repos = fetch_latest_repos()
    table = generate_projects_table(repos)
    update_readme(table)
    print("Done.")
