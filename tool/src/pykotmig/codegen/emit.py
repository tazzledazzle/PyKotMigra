from __future__ import annotations

import os
import shutil
from importlib import resources
from pathlib import Path
from typing import Any, Literal

from pykotmig.ir import AnalysisRoot

from pykotmig.codegen.load import assert_ready_for_codegen
from pykotmig.codegen.openapi_kotlin import (
    emit_generated_readme,
    emit_models_kotlin,
    emit_order_api_application,
    emit_order_api_application_test,
    emit_order_api_build_gradle_kts,
    emit_order_api_config,
    emit_order_api_koin,
    emit_order_api_main,
    emit_order_api_notify_client,
    emit_order_api_order_store,
    emit_settings_gradle_kts,
    emit_status_hub_application,
    emit_status_hub_application_test,
    emit_status_hub_build_gradle_kts,
    emit_status_hub_main,
    main_class_for_package,
    validate_openapi_for_profile,
)

Profile = Literal["status-hub", "order-api"]


def _copy_tree(src: Any, dest: Path) -> None:
    for child in src.iterdir():
        target = dest / child.name
        if child.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            _copy_tree(child, target)
        else:
            target.write_bytes(child.read_bytes())


def _kotlin_root(out: Path, kotlin_package: str) -> Path:
    return out / "src/main/kotlin" / Path(*kotlin_package.split("."))


def _kotlin_test_root(out: Path, kotlin_package: str) -> Path:
    return out / "src/test/kotlin" / Path(*kotlin_package.split("."))


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def emit_project(
    analysis: AnalysisRoot,
    *,
    out: Path,
    kotlin_package: str,
    project_name: str,
    profile: Profile,
    force: bool,
    allow_errors: bool,
) -> None:
    assert_ready_for_codegen(analysis, allow_errors=allow_errors)
    openapi = analysis.openapi
    assert openapi is not None
    validate_openapi_for_profile(openapi, profile)

    if out.exists() and force:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    tmpl = resources.files("pykotmig.templates.ktor")
    _copy_tree(tmpl, out)

    gradlew = out / "gradlew"
    if gradlew.is_file():
        gradlew.chmod(0o755)

    main = _kotlin_root(out, kotlin_package)
    test = _kotlin_test_root(out, kotlin_package)
    main.mkdir(parents=True, exist_ok=True)
    test.mkdir(parents=True, exist_ok=True)

    models = emit_models_kotlin(openapi, kotlin_package)
    _write_text(main / "GeneratedModels.kt", models)

    if profile == "status-hub":
        gradle = emit_status_hub_build_gradle_kts(openapi)
        _write_text(main / "Application.kt", emit_status_hub_application(kotlin_package, openapi))
        _write_text(main / "Main.kt", emit_status_hub_main(kotlin_package))
        _write_text(test / "ApplicationTest.kt", emit_status_hub_application_test(kotlin_package))
    elif profile == "order-api":
        gradle = emit_order_api_build_gradle_kts(openapi)
        _write_text(main / "Config.kt", emit_order_api_config(kotlin_package))
        _write_text(main / "OrderStore.kt", emit_order_api_order_store(kotlin_package))
        _write_text(main / "NotifyClient.kt", emit_order_api_notify_client(kotlin_package))
        _write_text(main / "Koin.kt", emit_order_api_koin(kotlin_package))
        _write_text(main / "Application.kt", emit_order_api_application(kotlin_package, openapi))
        _write_text(main / "Main.kt", emit_order_api_main(kotlin_package))
        _write_text(test / "ApplicationTest.kt", emit_order_api_application_test(kotlin_package))
    else:  # pragma: no cover
        raise ValueError(profile)

    mc = main_class_for_package(kotlin_package)
    _write_text(out / "build.gradle.kts", gradle.replace("__MAIN_CLASS__", mc))
    _write_text(out / "settings.gradle.kts", emit_settings_gradle_kts(project_name))
    _write_text(out / "README.md", emit_generated_readme(project_name, profile))
