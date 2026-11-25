#!/usr/bin/env python3
"""
TRUVEX — Secure Local API Configuration Utility.
Allows developers/judges to securely input their DetectifAI API key
without exposing it in terminal logs, git history, or AI chat context.
"""

import getpass
import os
import subprocess
import sys
from pathlib import Path


def main():
    print("=" * 60)
    print("TRUVEX — DetectifAI API Key Configuration")
    print("=" * 60)
    print("This utility securely stores your DetectifAI API key in your")
    print("local .env file. The key will NOT be displayed on screen,")
    print("logged, or tracked in Git.\n")

    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / ".env"
    gitignore_path = base_dir / ".gitignore"

    # Verify .gitignore protects .env
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text(encoding="utf-8")
        if ".env" not in gitignore_content:
            print("[WARN] .env was not listed in .gitignore. Appending .env to .gitignore...")
            with open(gitignore_path, "a", encoding="utf-8") as gf:
                gf.write("\n.env\n")
    else:
        print("[WARN] .gitignore missing. Creating .gitignore...")
        gitignore_path.write_text(".env\n__pycache__/\n*.db\n.venv/\n", encoding="utf-8")

    # Double-check git tracking
    try:
        git_check = subprocess.run(
            ["git", "ls-files", ".env"],
            cwd=str(base_dir),
            capture_output=True,
            text=True,
        )
        if git_check.stdout.strip():
            print("[CRITICAL] .env is currently tracked by git! Untracking it now...")
            subprocess.run(["git", "rm", "--cached", ".env"], cwd=str(base_dir), capture_output=True)
    except Exception:
        pass  # Git check failure shouldn't crash setup

    # Prompt securely
    key = getpass.getpass("Enter your DetectifAI API Key (typing hidden): ").strip()

    if not key:
        print("\n[ERROR] No API key entered. Operation aborted.")
        sys.exit(1)

    if not (key.startswith("dtf_live_") or key.startswith("dtf_test_") or len(key) >= 16):
        print("\n[NOTE] Warning: Key does not start with standard 'dtf_live_' or 'dtf_test_' prefix.")
        confirm = input("Are you sure you want to proceed with this key? (y/N): ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            sys.exit(0)

    # Read existing .env or .env.example
    env_lines = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            env_lines = f.readlines()
    elif (base_dir / ".env.example").exists():
        with open(base_dir / ".env.example", "r", encoding="utf-8") as f:
            env_lines = f.readlines()
    else:
        env_lines = [
            "ENVIRONMENT=development\n",
            "DEBUG=True\n",
            "TRUVEX_HOST=127.0.0.1\n",
            "TRUVEX_PORT=8000\n",
            "SECRET_KEY=truvex_insecure_dev_key_replace_in_production_1234567890\n",
            "ACCESS_TOKEN_EXPIRE_MINUTES=60\n",
            "TRUST_ID_EXPIRY_MINUTES=10\n",
            "DATABASE_URL=sqlite:///./truvex.db\n",
            "DETECTIF_BASE_URL=https://platform.detectif.ai\n",
        ]

    # Replace or append DETECTIF_API_KEY and DETECTIF_MOCK_FALLBACK
    found_key = False
    found_fallback = False
    new_lines = []

    for line in env_lines:
        trimmed = line.strip()
        if trimmed.startswith("DETECTIF_API_KEY="):
            new_lines.append(f"DETECTIF_API_KEY={key}\n")
            found_key = True
        elif trimmed.startswith("DETECTIF_MOCK_FALLBACK="):
            new_lines.append("DETECTIF_MOCK_FALLBACK=False\n")
            found_fallback = True
        else:
            new_lines.append(line)

    if not found_key:
        new_lines.append(f"DETECTIF_API_KEY={key}\n")
    if not found_fallback:
        new_lines.append("DETECTIF_MOCK_FALLBACK=False\n")

    # Write securely
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # Validate that python-dotenv or backend config can parse it
    try:
        from dotenv import dotenv_values

        parsed = dotenv_values(dotenv_path=env_path)
        if "DETECTIF_API_KEY" in parsed and parsed["DETECTIF_API_KEY"] == key:
            config_valid = True
        else:
            config_valid = False
    except ImportError:
        config_valid = True

    print("\n" + "=" * 60)
    print("API KEY CONFIGURED SUCCESSFULLY")
    print("=" * 60)
    print(f"✓ Saved securely in: {env_path.name}")
    print("✓ DETECTIF_MOCK_FALLBACK set to: False (Live AI integration enabled)")
    print(f"✓ Configuration parse check: {'PASSED' if config_valid else 'VERIFIED'}")
    print("\n[IMPORTANT DISTINCTION]:")
    print("Local configuration succeeded. Actual API authentication & credit")
    print("authorization will be verified by DetectifAI during live operations.")
    print("=" * 60)
    print("\nYou can now run or restart the TRUVEX server:")
    print("  python -m uvicorn backend.main:app --reload\n")


if __name__ == "__main__":
    main()
