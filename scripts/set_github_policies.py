"""Script to set GitHub policies across all repositories."""

from __future__ import annotations

import httpx
import loguru
import dynaconf


logger = loguru.logger
config = dynaconf.Dynaconf(envvar_prefix="CONFIG")

api = httpx.Client(
    base_url="https://api.github.com",
    headers={
        "Authorization": f"Bearer {config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    },
    timeout=30,
)


def list_repositories() -> list[str]:
    logger.info(f"Listing repositories for {config.GITHUB_USERNAME}")
    response = api.get("/user/repos")
    response.raise_for_status()
    return [
        repository["name"]
        for repository in response.json()
        if not repository["fork"] and not repository["archived"]
    ]


def list_forked_repositories() -> list[dict]:
    logger.info(f"Listing forked repositories for {config.GITHUB_USERNAME}")
    response = api.get("/user/repos")
    response.raise_for_status()
    return [repository["name"] for repository in response.json() if repository["fork"]]


def set_policy_disable_wiki(repository: str) -> None:
    logger.info(f"[{repository}] Disabling wiki")
    response = api.patch(
        f"/repos/{config.GITHUB_USERNAME}/{repository}",
        json={"has_wiki": False},
    )
    response.raise_for_status()
    logger.success(f"[{repository}] Wiki disabled")


def set_policy_disable_projects(repository: str) -> None:
    logger.info(f"[{repository}] Disabling projects")
    response = api.patch(
        f"/repos/{config.GITHUB_USERNAME}/{repository}",
        json={"has_projects": False},
    )
    response.raise_for_status()
    logger.success(f"[{repository}] Projects disabled")


def set_policy_disable_discussions(repository: str) -> None:
    logger.info(f"[{repository}] Disabling discussions")
    response = api.patch(
        f"/repos/{config.GITHUB_USERNAME}/{repository}",
        json={"has_discussions": False},
    )
    response.raise_for_status()
    logger.success(f"[{repository}] Discussions disabled")


def set_policy_rebase_only(repository: str) -> None:
    logger.info(f"[{repository}] Setting merge method to rebase only")
    response = api.patch(
        f"/repos/{config.GITHUB_USERNAME}/{repository}",
        json={
            "allow_merge_commit": False,
            "allow_squash_merge": False,
            "allow_rebase_merge": True,
        },
    )
    response.raise_for_status()
    logger.success(f"[{repository}] Merge method set to rebase only")


def rename_repository(repository: str, name: str) -> None:
    logger.info(f"[{repository}] Renaming to {name}")
    response = api.patch(
        f"/repos/{config.GITHUB_USERNAME}/{repository}",
        json={"name": name},
    )
    response.raise_for_status()
    logger.success(f"[{repository}] Renamed to {name}")


def set_fork_name(repository: str) -> None:
    match repository.startswith("fork-"):
        case True:
            logger.warning(f"[{repository}] Already has 'fork-' prefix, skipping")
        case False:
            rename_repository(repository, f"fork-{repository}")


if __name__ == "__main__":
    repositories = list_repositories()
    for repository in repositories:
        set_policy_disable_wiki(repository)
        set_policy_disable_projects(repository)
        set_policy_disable_discussions(repository)
        set_policy_rebase_only(repository)

    forked_repositories = list_forked_repositories()
    for repository in forked_repositories:
        set_fork_name(repository)
