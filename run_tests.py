"""Простой запуск UI-тестов на macOS/Linux.

Первый запуск подготавливает локальное окружение и устанавливает Chromium.
Последующие запуски сразу переходят к тестам.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
SETUP_MARKER = VENV_DIR / ".autotests-ready"
REQUIREMENTS = ROOT / "requirements.txt"


def venv_python() -> Path:
    return VENV_DIR / "bin" / "python"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def prepare(force: bool = False) -> Path:
    requirements_hash = hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()
    python = venv_python()
    if not python.exists():
        print("Первый запуск: создаю окружение для автотестов…")
        venv.create(VENV_DIR, with_pip=True)

    setup_is_current = (
        SETUP_MARKER.exists()
        and SETUP_MARKER.read_text(encoding="utf-8").strip() == requirements_hash
    )
    if force or not setup_is_current:
        print("Устанавливаю зависимости…")
        run([str(python), "-m", "pip", "install", "-r", "requirements.txt"])
        print("Устанавливаю браузер Chromium…")
        run([str(python), "-m", "playwright", "install", "chromium"])
        SETUP_MARKER.write_text(requirements_hash, encoding="utf-8")

    return python


def main() -> int:
    parser = argparse.ArgumentParser(description="Подготовить и запустить UI-автотесты")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="запустить без видимого окна браузера",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--desktop", action="store_true", help="только desktop-тесты")
    group.add_argument("--mobile", action="store_true", help="только mobile-тесты")
    parser.add_argument(
        "--setup",
        action="store_true",
        help="заново установить зависимости и Chromium",
    )
    args, pytest_args = parser.parse_known_args()

    if sys.version_info < (3, 10):
        parser.error("нужен Python 3.10 или новее")

    try:
        python = prepare(force=args.setup)
        command = [str(python), "-m", "pytest", "--browser", "chromium"]
        if not args.headless:
            command.append("--headed")
        if args.desktop:
            command.extend(["-m", "desktop"])
        elif args.mobile:
            command.extend(["-m", "mobile"])
        command.extend(pytest_args)

        print("Запускаю автотесты…")
        run(command)
    except subprocess.CalledProcessError as error:
        return error.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
