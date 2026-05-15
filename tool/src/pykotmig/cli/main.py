from __future__ import annotations

import shlex
import sys
from pathlib import Path

import typer

from pykotmig.analyze import run_analyze

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command("analyze")
def analyze_cmd(
    project_root: Path = typer.Option(
        ...,
        "--project-root",
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Root of the Python project (contains pyproject.toml and src/).",
    ),
    app: str = typer.Option(
        ...,
        "--app",
        help="FastAPI app as module:attr (e.g. order_api.app:app). Trusted local import.",
    ),
    out: Path = typer.Option(
        ...,
        "--out",
        help="Write analysis.json to this path.",
    ),
    force: bool = typer.Option(False, "--force", help="Bypass incremental parse cache."),
    mypy: bool = typer.Option(False, "--mypy", help="Run mypy on src/ (requires mypy on PATH)."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Do not write --out or update parse cache; print analysis JSON to stdout. "
        "For Ollama OpenAPI, prints request debug to stderr and skips the HTTP call.",
    ),
) -> None:
    """Scan src/**/*.py, merge OpenAPI from --app, emit analysis.json."""
    pr = project_root.resolve()
    if not (pr / "pyproject.toml").is_file():
        typer.secho("No pyproject.toml under --project-root.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    if not (pr / "src").is_dir():
        typer.secho("No src/ directory under --project-root.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    result = run_analyze(pr, app, force=force, mypy_enable=mypy, argv=sys.argv, dry_run=dry_run)
    payload = result.model_dump_json(indent=2)
    if dry_run:
        typer.echo(payload)
        typer.secho(
            f"[dry-run] skipped writing {out} ({len(result.files)} files, openapi={'yes' if result.openapi else 'no'}).",
            fg=typer.colors.YELLOW,
            err=True,
        )
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        typer.secho(
            f"Wrote {out} ({len(result.files)} files, openapi={'yes' if result.openapi else 'no'}).",
            fg=typer.colors.GREEN,
        )


@app.command("generate")
def generate_cmd(
    analysis: Path = typer.Option(
        ...,
        "--analysis",
        exists=True,
        file_okay=True,
        dir_okay=False,
        help="Path to analysis.json from pykotmig analyze.",
    ),
    out: Path = typer.Option(
        ...,
        "--out",
        help="Output directory for the Gradle + Kotlin project.",
    ),
    kotlin_package: str = typer.Option(
        ...,
        "--kotlin-package",
        help="Kotlin package for generated sources (e.g. dev.pykotmig.gen.statushub).",
    ),
    profile: str = typer.Option(
        ...,
        "--profile",
        help="codegen profile: status-hub or order-api.",
    ),
    project_name: str = typer.Option(
        "generated",
        "--project-name",
        help="Gradle rootProject.name / folder label.",
    ),
    force: bool = typer.Option(False, "--force", help="Delete existing --out before writing."),
    allow_errors: bool = typer.Option(
        False,
        "--allow-errors",
        help="Allow codegen even if analysis.json lists errors (unsafe).",
    ),
) -> None:
    """Emit a Ktor + Gradle project from analysis.json."""
    from pykotmig.codegen.emit import emit_project
    from pykotmig.codegen.load import CodegenError, load_analysis

    if profile not in ("status-hub", "order-api"):
        typer.secho("--profile must be status-hub or order-api.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    try:
        root = load_analysis(analysis)
        emit_project(
            root,
            out=out.resolve(),
            kotlin_package=kotlin_package,
            project_name=project_name,
            profile=profile,  # type: ignore[arg-type]
            force=force,
            allow_errors=allow_errors,
        )
    except CodegenError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from e

    typer.secho(f"Wrote Kotlin project to {out.resolve()} (profile={profile}).", fg=typer.colors.GREEN)


@app.command("verify")
def verify_cmd(
    project: Path = typer.Option(
        ...,
        "--project",
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Generated Gradle project root (contains gradlew).",
    ),
    gradle_args: str = typer.Option(
        "test --no-daemon -q",
        "--gradle-args",
        help='Arguments passed to gradlew after the wrapper (shell-style, e.g. "build --no-daemon").',
    ),
    llm: bool = typer.Option(
        False,
        "--llm",
        help="On failure, call an OpenAI-compatible chat API and apply returned file patches (needs API key).",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="With --llm: call the model, then print Gradle log, context files, user JSON, and full proposed "
        "file contents to stderr (nothing is written to the project).",
    ),
    max_rounds: int = typer.Option(
        3,
        "--max-rounds",
        min=1,
        max=20,
        help="Maximum LLM fix rounds (each round runs Gradle, then may apply patches).",
    ),
    llm_model: str = typer.Option(
        "gpt-4o-mini",
        "--llm-model",
        help="Model id for the chat completions endpoint when using --llm.",
    ),
) -> None:
    """Run Gradle on a generated project; optionally loop with a cloud LLM to fix build errors."""
    from pykotmig.verify_loop import verify_with_optional_llm

    args = shlex.split(gradle_args)
    code = verify_with_optional_llm(
        project.resolve(),
        gradle_args=args,
        max_rounds=max_rounds,
        use_llm=llm,
        llm_model=llm_model,
        dry_run=dry_run,
    )
    if code != 0:
        raise typer.Exit(code=code)


def main() -> None:
    app()
