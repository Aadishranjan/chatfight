import asyncio
import os
import sys
from html import escape
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
    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(REPO_DIR),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    output, _ = await proc.communicate()
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
        return

    msg = await update.effective_message.reply_text("Updating from upstream...")
    pull_url = _build_pull_repo_url()
    code, out = await _run_cmd("git", "pull", pull_url, UPSTREAM_BRANCH)
    safe_out = _mask_secrets(out)
    trimmed = escape(safe_out[:3500])
    status = "Update complete." if code == 0 else f"Update failed (exit {code})."
    await msg.edit_text(f"{status}\n\n<pre>{trimmed}</pre>", parse_mode="HTML")


async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_allowed(user.id if user else None):
        return

    await update.effective_message.reply_text("Restarting bot...")
    await asyncio.sleep(1)
    os.execv(sys.executable, [sys.executable, "run.py"])


def register(app):
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(CommandHandler("restart", restart_cmd))
