"""Script to update README with GitHub stats and notable contributions."""

from __future__ import annotations

import os
import re
import pathlib
import datetime
import dataclasses

import httpx
import loguru


logger = loguru.logger

NOTABLE_LIMIT = 10
NOTABLE_MIN_STARS = 100
NOTABLE_MAX_PAGES = 5
MILLION = 1_000_000
THOUSAND = 1_000


@dataclasses.dataclass(frozen=True)
class Stats:
    stars: int
    commits: int
    pull_requests: int
    issues: int


def create_client() -> httpx.Client:
    return httpx.Client(
        base_url="https://api.github.com",
        headers={
            "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )


def graphql(client: httpx.Client, query: str, variables: dict | None = None) -> dict:
    response = client.post("/graphql", json={"query": query, "variables": variables or {}})
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        msg = f"GraphQL errors: {data['errors']}"
        raise RuntimeError(msg)

    return data["data"]


def fetch_stars(client: httpx.Client, username: str) -> int:
    query = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        repositories(ownerAffiliations: OWNER, isFork: false, first: 100, after: $cursor) {
          nodes { stargazerCount }
          pageInfo { hasNextPage endCursor }
        }
      }
    }
    """
    total = 0
    cursor = None

    while True:
        data = graphql(client, query, {"login": username, "cursor": cursor})
        repos = data["user"]["repositories"]
        total += sum(r["stargazerCount"] for r in repos["nodes"])
        if not repos["pageInfo"]["hasNextPage"]:
            break

        cursor = repos["pageInfo"]["endCursor"]

    return total


def fetch_account_year(client: httpx.Client, username: str) -> int:
    query = "query($login: String!) { user(login: $login) { createdAt } }"
    data = graphql(client, query, {"login": username})
    return datetime.datetime.fromisoformat(data["user"]["createdAt"]).year


def fetch_commits(client: httpx.Client, username: str) -> int:
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    total = 0
    start_year = fetch_account_year(client, username)
    current_year = datetime.datetime.now(datetime.UTC).year

    for year in range(start_year, current_year + 1):
        data = graphql(
            client,
            query,
            {
                "login": username,
                "from": f"{year}-01-01T00:00:00Z",
                "to": f"{year}-12-31T23:59:59Z",
            },
        )
        cc = data["user"]["contributionsCollection"]
        total += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]

    return total


def fetch_activity(client: httpx.Client, username: str) -> tuple[int, int]:
    query = """
    query($login: String!) {
      user(login: $login) {
        pullRequests { totalCount }
        issues { totalCount }
      }
    }
    """
    data = graphql(client, query, {"login": username})
    user = data["user"]
    return (
        user["pullRequests"]["totalCount"],
        user["issues"]["totalCount"],
    )


def fetch_notable_contributions(client: httpx.Client, username: str) -> list[dict]:
    query = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        pullRequests(
          states: MERGED
          first: 100
          after: $cursor
          orderBy: {field: CREATED_AT, direction: DESC}
        ) {
          pageInfo { hasNextPage endCursor }
          nodes {
            repository {
              nameWithOwner
              url
              stargazerCount
              owner { login }
            }
          }
        }
      }
    }
    """
    contributions: list[dict] = []
    seen_repos: set[str] = set()
    cursor = None

    for _ in range(NOTABLE_MAX_PAGES):
        data = graphql(client, query, {"login": username, "cursor": cursor})
        prs = data["user"]["pullRequests"]

        for pr in prs["nodes"]:
            repo = pr["repository"]
            if repo["owner"]["login"].lower() == username.lower():
                continue

            if repo["stargazerCount"] < NOTABLE_MIN_STARS:
                continue

            repo_name = repo["nameWithOwner"]
            if repo_name in seen_repos:
                continue

            seen_repos.add(repo_name)
            contributions.append(
                {
                    "repo": repo_name,
                    "repo_url": repo["url"],
                    "stars": repo["stargazerCount"],
                },
            )

        if not prs["pageInfo"]["hasNextPage"]:
            break

        cursor = prs["pageInfo"]["endCursor"]

    contributions.sort(key=lambda c: c["stars"], reverse=True)
    return contributions[:NOTABLE_LIMIT]


def fmt(n: int) -> str:
    if n >= MILLION:
        return f"{n / MILLION:.1f}M"

    if n >= THOUSAND:
        return f"{n / THOUSAND:.1f}k"

    return str(n)


def render_stats(stats: Stats) -> str:
    lines = [
        "## Stats",
        "",
        f"- ⭐ Stars: **{fmt(stats.stars)}**",
        f"- 💻 Commits: **{fmt(stats.commits)}**",
        f"- 🔀 Pull Requests: **{fmt(stats.pull_requests)}**",
        f"- 🐛 Issues: **{fmt(stats.issues)}**",
    ]
    return "\n".join(lines)


def render_notable(contributions: list[dict]) -> str:
    lines = ["## Notable Contributions", ""]
    if not contributions:
        lines.append("*No notable contributions found.*")
        return "\n".join(lines)

    lines.extend(
        f"- [{c['repo']}]({c['repo_url']}) ⭐ {fmt(c['stars'])}"
        for c in contributions
    )
    return "\n".join(lines)


def render_updated() -> str:
    updated = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
    return f"*Updated: {updated}*"


def update_readme(path: str, stats_md: str, notable_md: str, updated_md: str) -> None:
    readme = pathlib.Path(path)
    content = readme.read_text()

    content = re.sub(
        r"<!-- STATS:START -->.*?<!-- STATS:END -->",
        f"<!-- STATS:START -->\n{stats_md}\n<!-- STATS:END -->",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"<!-- NOTABLE:START -->.*?<!-- NOTABLE:END -->",
        f"<!-- NOTABLE:START -->\n{notable_md}\n<!-- NOTABLE:END -->",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"<!-- UPDATED:START -->.*?<!-- UPDATED:END -->",
        f"<!-- UPDATED:START -->\n{updated_md}\n<!-- UPDATED:END -->",
        content,
        flags=re.DOTALL,
    )

    readme.write_text(content)


if __name__ == "__main__":
    username: str = os.environ["GITHUB_REPOSITORY_OWNER"]

    with create_client() as client:
        logger.info("Fetching stars...")
        stars = fetch_stars(client, username)
        logger.info(f"Stars: {stars}")

        logger.info("Fetching commits...")
        commits = fetch_commits(client, username)
        logger.info(f"Commits: {commits}")

        logger.info("Fetching PRs and issues...")
        pull_requests, issues = fetch_activity(client, username)
        logger.info(f"PRs: {pull_requests}, Issues: {issues}")

        logger.info("Fetching notable contributions...")
        notable = fetch_notable_contributions(client, username)
        logger.info(f"Found {len(notable)} notable contributions")

    stats = Stats(
        stars=stars,
        commits=commits,
        pull_requests=pull_requests,
        issues=issues,
    )

    update_readme("README.md", render_stats(stats), render_notable(notable), render_updated())
    logger.success("README updated successfully")
