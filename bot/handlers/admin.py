import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from config import OWNER_ID, EXTRA_OWNER_IDS, UPSTREAM_REPO, UPSTREAM_BRANCH, GIT_TOKEN

REPO_DIR = Path(__file__).resolve().parents[2]
ALLOWED_ADMIN_IDS = {OWNER_ID, *EXTRA_OWNER_IDS}


def _is_allowed(user_id: int | None) -> bool:
    return bool(user_id and user_id in ALLOWED_ADMIN_IDS)


async def _run_cmd(*args: str) -> tuple[int, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(REPO_DIR),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        output, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return 124, "Command timed out after 60s."
    text = (output or b"").decode("utf-8", errors="replace").strip()
    if not text:
        text = "(no output)"
    return proc.returncode, text


def _build_pull_repo_url() -> str:
    if not GIT_TOKEN:
        return UPSTREAM_REPO

    parsed = urlparse(UPSTREAM_REPO)
    if parsed.scheme != "https":
        return UPSTREAM_REPO
    if not parsed.netloc:
        return UPSTREAM_REPO

    auth_netloc = f"x-access-token:{GIT_TOKEN}@{parsed.netloc}"
    return urlunparse((parsed.scheme, auth_netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))


def _mask_secrets(text: str) -> str:
    if not GIT_TOKEN:
        return text
    return text.replace(GIT_TOKEN, "***")


async def update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_allowed(user.id if user else None):
        await update.effective_message.reply_text("You are not allowed to use this command.")
        return

    msg = await update.effective_message.reply_text("Updating from upstream...")
    pull_url = _build_pull_repo_url()
    code, out = await _run_cmd("git", "pull", pull_url, UPSTREAM_BRANCH)
    safe_out = _mask_secrets(out)
    trimmed = safe_out[:3500]
    if code == 0:
        text = (
            f"✅ Update successful from {UPSTREAM_BRANCH}.\n\n"
            f"{trimmed}\n\n"
            "♻️ Restarting bot..."
        )
        await msg.edit_text(text)
        await asyncio.sleep(1)
        os.execv(sys.executable, [sys.executable, "run.py"])
        return

    await msg.edit_text(
        f"❌ Update failed (exit {code}).\n\n{trimmed}"
    )


async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_allowed(user.id if user else None):
        await update.effective_message.reply_text("You are not allowed to use this command.")
        return

    await update.effective_message.reply_text("Restarting bot...")
    await asyncio.sleep(1)
    os.execv(sys.executable, [sys.executable, "run.py"])


def register(app):
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(CommandHandler("restart", restart_cmd))
