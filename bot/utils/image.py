# Copyright (c) 2026 Aadish Ranjan
# Location: India
#
# All rights reserved.
#
# This code is the intellectual property of Aadish Ranjan.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Project: aadishranjan35@gmail.com



from PIL import Image, ImageDraw, ImageFont

# ---------- FONTS ----------
FONT_TITLE = ImageFont.truetype("assets/fonts/dejavu-sans.bold.ttf", 56)
FONT_NAME  = ImageFont.truetype("assets/fonts/dejavu-sans.bold.ttf", 28)
FONT_SCORE = ImageFont.truetype("assets/fonts/dejavu-sans.bold.ttf", 26)

WIDTH  = 1100
HEIGHT = 650

BG_COLOR = (25, 5, 8)
CARD_BG  = (45, 10, 15)
BAR_CLR  = (190, 70, 80)
TEXT_CLR = (255, 255, 255)
MUTED    = (180, 180, 180)


def leaderboard_image(data, title="LEADERBOARD"):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # ---------- OPTIONAL BACKGROUND ----------
    try:
        bg = Image.open("assets/bg.png").resize((WIDTH, HEIGHT)).convert("RGBA")
        img.paste(bg, (0, 0), bg)
        draw = ImageDraw.Draw(img)
    except:
        pass

    # ---------- TITLE ----------
    draw.text((WIDTH//2 - 180, 30), title, font=FONT_TITLE, fill=TEXT_CLR)

    # ---------- CARD ----------
    card_x1, card_y1 = 50, 120
    card_x2, card_y2 = WIDTH - 50, HEIGHT - 50
    draw.rounded_rectangle(
        [card_x1, card_y1, card_x2, card_y2],
        radius=30,
        fill=CARD_BG,
        outline=(120, 40, 50),
        width=3
    )

    if not data:
        draw.text((WIDTH//2 - 100, HEIGHT//2),
                  "No data available",
                  font=FONT_NAME,
                  fill=MUTED)
    else:
        max_score = max(u["count"] for u in data)

        start_y = card_y1 + 40
        bar_x   = card_x1 + 260
        bar_max = card_x2 - bar_x - 40

        for i, u in enumerate(data[:10], start=1):
            y = start_y + (i - 1) * 45

            name = u["name"][:16]
            score = u["count"]

            # NAME
            draw.text((card_x1 + 30, y), name, font=FONT_NAME, fill=TEXT_CLR)

            # BAR WIDTH
            bar_w = int((score / max_score) * bar_max)

            # BAR
            draw.rounded_rectangle(
                [bar_x, y + 4, bar_x + bar_w, y + 30],
                radius=15,
                fill=BAR_CLR
            )

            # SCORE TEXT ON BAR (Pillow 10+ safe)
            score_text = str(score)
            bbox = draw.textbbox((0, 0), score_text, font=FONT_SCORE)
            tw = bbox[2] - bbox[0]

            draw.text(
                (bar_x + bar_w - tw - 15, y + 6),
                score_text,
                font=FONT_SCORE,
                fill=TEXT_CLR
            )


    path = "resource/leaderboard.png"
    img.save(path)
    return path



# ©️ Copyright Reserved - @aadishranjan  Aadish Ranjan

# ===========================================
# ©️ 2026 Aadish Ranjan (@Aadishranjan)
# 🔗 GitHub : https://github.com/Aadishranjan/chatfight
# 📢 Telegram Channel : https://t.me/YutaxBots
# ===========================================


# ❤️ Love From Chatfight Bot Team