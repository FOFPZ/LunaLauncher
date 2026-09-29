#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌙 Luna Launcher — красивый лаунчер Minecraft
Vanilla / Fabric / Forge · Свои ники · Discord Rich Presence
"""

import os
import sys
import json
import asyncio
import warnings

# Глушим безобидное предупреждение pypresence/asyncio при закрытии
warnings.filterwarnings("ignore", category=ResourceWarning)
import time
import uuid
import threading
import subprocess
import webbrowser
import shutil
import tempfile
from tkinter import filedialog, simpledialog, messagebox
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk

import minecraft_launcher_lib as mll

try:
    from pypresence import Presence
except Exception:  # pypresence не обязателен
    Presence = None

# ──────────────────────────── НАСТРОЙКИ ────────────────────────────
APP_NAME = "Luna Launcher"
APP_VERSION = "0.0.6"

# Ссылка на JSON с последней версией (для проверки обновлений). Формат:
# {"version": "0.0.5", "url": "https://.../LunaLauncher.exe", "notes": "что нового"}
# Замени ТЫ/LunaLauncher на свой GitHub-репозиторий (см. README)
UPDATE_URL = "https://raw.githubusercontent.com/ТЫ/LunaLauncher/main/latest.json"

CHANGELOG = [
    ("0.0.6", "2026-09-28", [
        "+ Окно «Настройки» (⚙ в левой панели): RAM, Java, JVM, снапшоты, Discord, ссылка обновлений",
        "+ Лог игры пишется в файл logs/latest.log, в консоли — последние 500 строк (нет лагов на модпаках)",
        "+ Ползунок RAM ограничен реальной памятью ПК, показывается рекомендуемое значение",
        "+ Discord ID и ссылка обновлений теперь меняются в настройках без пересборки exe",
        "~ Карточка версии упрощена: только загрузчик и версия",
        "~ Удаление ника — с подтверждением",
        "- Убрана строка UUID под ником",
        "- Убрана кнопка на minecraft.net в статусе Discord (можно задать свою ссылку в настройках)",
    ]),
    ("0.0.5", "2026-09-27", [
        "+ Авто‑обновление: лаунчер сам скачивает новую версию и перезапускается",
        "+ Сборки (модпаки): у каждой своя папка модов, загрузчик и версия",
        "+ Кнопки «📁 Моды» и «+ Добавить моды» — закинуть .jar в один клик",
        "+ Создание / переименование / удаление сборок",
        "~ Миры, настройки и моды каждой сборки хранятся отдельно (instances/…)",
    ]),
    ("0.0.4", "2026-09-27", [
        "+ Окно «Обновления лаунчера» с историей версий",
        "+ Проверка новой версии по ссылке (UPDATE_URL) и кнопка скачивания",
        "+ Сборка в .exe (build_exe.bat, GitHub Actions)",
        "~ Discord RPC: исправлено подключение на Windows (ProactorEventLoop)",
        "~ В консоль выводится точная причина, если Discord не подключился",
    ]),
    ("0.0.3", "2026-09-27", [
        "+ Тема Purple Moon: фиолетовые панели, сиреневый акцент",
        "+ Логотип без белого фона (прозрачный PNG) в лаунчере и Discord",
        "+ Отдельная иконка для Discord в цвет лаунчера (discord_icon.png)",
        "+ Единый Discord Application ID для всех пользователей",
        "- Убран старый логотип с белой рамкой",
    ]),
    ("0.0.2", "2026-09-27", [
        "~ Убрано предупреждение asyncio «unclosed transport» при закрытии",
        "~ Добавлены run.bat / run.sh с автоустановкой зависимостей",
        "~ README с инструкцией по настройке Discord",
    ]),
    ("0.0.1", "2026-09-27", [
        "+ Первый выпуск Luna Launcher",
        "+ Vanilla / Fabric / Forge, версии Minecraft от 1.0 до 26.3 (+ снапшоты)",
        "+ Свои ники: сохранение, выбор, удаление, оффлайн‑UUID",
        "+ Discord Rich Presence: «В лаунчере» / «Устанавливает…» / «Играет в …»",
        "+ Ползунок RAM, путь к Java и JVM‑аргументы",
        "+ Консоль с логом лаунчера и игры, прогресс‑бар загрузки",
    ]),
]
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
ASSETS = BASE_DIR / "assets"
DATA_DIR = Path.home() / ".lunalauncher"
MC_DIR = DATA_DIR / "minecraft"          # общие версии/библиотеки/ассеты
INSTANCES_DIR = DATA_DIR / "instances"   # сборки: у каждой свои mods/saves/config
CONFIG_FILE = DATA_DIR / "config.json"

# Discord: создай приложение на https://discord.com/developers/applications,
# вставь сюда Application ID и загрузи в Rich Presence → Art Assets картинку с именем "luna"
DISCORD_CLIENT_ID = "1553825001608577115"

# Палитра
# Purple Moon 🌙
BG = "#0e0a1f"
PANEL = "#160f2e"
CARD = "#221846"
ACCENT = "#9b6dff"
ACCENT_H = "#b58cff"
TEXT = "#efe9ff"
MUTED = "#9d8fc7"
OK = "#5ee1a2"
ERR = "#ff6b8a"

ctk.set_appearance_mode("dark")


# ──────────────────────────── КОНФИГ ────────────────────────────
DEFAULT_CONFIG = {
    "nickname": "Player",
    "nicknames": ["Player"],
    "loader": "Vanilla",
    "version": "",
    "profile": "Основная",
    "profiles": {"Основная": {"loader": "Vanilla", "version": ""}},
    "ram": 4,
    "show_snapshots": False,
    "discord_rpc": True,
    "java_path": "",
    "jvm_args": "",
    "discord_client_id": DISCORD_CLIENT_ID,
    "update_url": UPDATE_URL,
    "rpc_button_url": "",
    "close_on_launch": False,
}


def load_config():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            cfg.update(json.loads(CONFIG_FILE.read_text("utf-8")))
        except Exception:
            pass
    return cfg


def save_config(cfg):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), "utf-8")


def total_ram_gb() -> int:
    """Физическая память ПК в ГБ (для ограничения ползунка)"""
    try:
        if sys.platform == "win32":
            import ctypes
            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MS(); m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return max(2, round(m.ullTotalPhys / 1024 ** 3))
        return max(2, round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024 ** 3))
    except Exception:
        return 16


def offline_uuid(name: str) -> str:
    """UUID как у оффлайн-сервера: md5('OfflinePlayer:' + ник)"""
    return str(uuid.uuid3(uuid.NAMESPACE_OID, "OfflinePlayer:" + name))


# ──────────────────────────── DISCORD RPC ────────────────────────────
class DiscordRPC:
    def __init__(self, client_id, button_url=""):
        self.client_id = client_id
        self.button_url = button_url
        self.rpc = None
        self.start = int(time.time())
        self.lock = threading.Lock()

    def connect(self):
        """Возвращает None при успехе, иначе текст ошибки"""
        if Presence is None:
            return "модуль pypresence не установлен (pip install pypresence)"
        try:
            # На Windows Discord IPC работает только через ProactorEventLoop
            loop = asyncio.ProactorEventLoop() if sys.platform == "win32" else asyncio.new_event_loop()
            self.rpc = Presence(self.client_id, loop=loop)
            self.rpc.connect()
            return None
        except Exception as e:
            self.rpc = None
            return f"{type(e).__name__}: {e}"

    def update(self, details, state):
        if not self.rpc:
            return
        with self.lock:
            try:
                kw = dict(details=details, state=state, large_image="luna",
                          large_text="Luna Launcher", start=self.start)
                if self.button_url:
                    kw["buttons"] = [{"label": "🌙 Luna Launcher", "url": self.button_url}]
                self.rpc.update(**kw)
            except Exception:
                pass

    def close(self):
        if self.rpc:
            try:
                self.rpc.close()
            except Exception:
                pass
            self.rpc = None


# ──────────────────────────── ПРИЛОЖЕНИЕ ────────────────────────────
class LunaLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.title(f"🌙 {APP_NAME}")
        self.geometry("1100x680")
        self.minsize(960, 600)
        self.configure(fg_color=BG)

        self.all_versions = []       # список dict из mll
        self.versions_shown = []     # id-шники в комбобоксе
        self.busy = False
        self.game_proc = None

        self.rpc = DiscordRPC(self.cfg.get("discord_client_id") or DISCORD_CLIENT_ID,
                              self.cfg.get("rpc_button_url", ""))
        self.ram_max = total_ram_gb()
        self.log_file = None

        self._load_logo()
        self._build_ui()
        self._apply_config()

        threading.Thread(target=self._load_versions, daemon=True).start()
        if self.cfg.get("discord_rpc", True):
            threading.Thread(target=self._start_rpc, daemon=True).start()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(3000, self._silent_update_check)

    def _silent_update_check(self):
        def worker():
            url_src = self.cfg.get("update_url") or UPDATE_URL
            if not url_src or "ТЫ/" in url_src:
                return
            try:
                import urllib.request
                with urllib.request.urlopen(url_src, timeout=8) as r:
                    data = json.loads(r.read().decode("utf-8"))
                latest = data.get("version", APP_VERSION)
                if tuple(map(int, latest.split("."))) > tuple(map(int, APP_VERSION.split("."))):
                    self.after(0, lambda: self.upd_btn.configure(text=f"🔔 Доступно v{latest}!", fg_color=ACCENT))
                    self.log(f"🔔 Доступно обновление v{latest} — открой «Обновления»")
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    # ---------- логотип ----------
    def _load_logo(self):
        self.logo_img = None
        p = ASSETS / "logo.png"
        if p.exists():
            img = Image.open(p).convert("RGBA")
            self.logo_img = ctk.CTkImage(img, img, size=(120, 120))
            try:
                self.iconphoto(True, ImageTk.PhotoImage(img.resize((64, 64))))
            except Exception:
                pass

    # ---------- UI ----------
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ═══ САЙДБАР ═══
        side = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=PANEL)
        side.grid(row=0, column=0, sticky="nsw")
        side.grid_propagate(False)

        if self.logo_img:
            ctk.CTkLabel(side, image=self.logo_img, text="").pack(pady=(28, 6))
        ctk.CTkLabel(side, text="LUNA", font=("Segoe UI", 30, "bold"), text_color=TEXT).pack()
        ctk.CTkLabel(side, text="L A U N C H E R", font=("Segoe UI", 11), text_color=ACCENT).pack(pady=(0, 20))

        # Профиль / ники
        ctk.CTkLabel(side, text="ПРОФИЛЬ", font=("Segoe UI", 11, "bold"), text_color=MUTED).pack(anchor="w", padx=24)
        self.nick_var = ctk.StringVar()
        self.nick_combo = ctk.CTkComboBox(
            side, values=self.cfg["nicknames"], variable=self.nick_var,
            width=232, height=40, corner_radius=12, fg_color=CARD, border_color=CARD,
            button_color=ACCENT, button_hover_color=ACCENT_H, dropdown_fg_color=CARD,
            font=("Segoe UI", 14), command=lambda _: self._nick_changed())
        self.nick_combo.pack(padx=24, pady=(6, 6))
        self.nick_combo.bind("<FocusOut>", lambda e: self._nick_changed())
        self.nick_combo.bind("<Return>", lambda e: self._nick_changed())

        row = ctk.CTkFrame(side, fg_color="transparent")
        row.pack(padx=24, fill="x")
        ctk.CTkButton(row, text="+ Сохранить ник", width=140, height=32, corner_radius=10,
                      fg_color=CARD, hover_color="#2f2160", font=("Segoe UI", 12),
                      command=self._save_nick).pack(side="left")
        ctk.CTkButton(row, text="✕", width=40, height=32, corner_radius=10,
                      fg_color=CARD, hover_color="#4a2040", font=("Segoe UI", 12),
                      command=self._delete_nick).pack(side="right")

        # ⚙ Настройки
        ctk.CTkButton(side, text="⚙  Настройки", height=36, corner_radius=10, fg_color=CARD,
                      hover_color="#2f2160", font=("Segoe UI", 13), command=self._settings_window).pack(
            padx=24, pady=(16, 0), fill="x")

        # Статус
        self.status_dot = ctk.CTkLabel(side, text="●  Discord: подключение…", font=("Segoe UI", 12), text_color=MUTED)
        self.status_dot.pack(side="bottom", pady=(0, 8), anchor="w", padx=24)
        ctk.CTkButton(side, text="📁 Папка игры", height=34, corner_radius=10, fg_color=CARD,
                      hover_color="#2f2160", command=self._open_dir).pack(side="bottom", padx=24, pady=6, fill="x")
        self.upd_btn = ctk.CTkButton(side, text=f"🔄 Обновления · v{APP_VERSION}", height=34, corner_radius=10,
                                     fg_color=CARD, hover_color="#2f2160", command=self._changelog_window)
        self.upd_btn.pack(side="bottom", padx=24, pady=(6, 0), fill="x")

        # ═══ ОСНОВНАЯ ЧАСТЬ ═══
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=28, pady=24)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(3, weight=1)

        # Шапка
        hdr = ctk.CTkFrame(main, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew")
        self.hello_lbl = ctk.CTkLabel(hdr, text="Добро пожаловать", font=("Segoe UI", 28, "bold"), text_color=TEXT)
        self.hello_lbl.pack(anchor="w")
        ctk.CTkLabel(hdr, text="Выбери загрузчик и версию — остальное сделаем сами ✨",
                     font=("Segoe UI", 13), text_color=MUTED).pack(anchor="w")

        # Карточка выбора версии
        # Панель сборок
        pf = ctk.CTkFrame(main, fg_color=CARD, corner_radius=18)
        pf.grid(row=1, column=0, sticky="ew", pady=(18, 0))
        ctk.CTkLabel(pf, text="СБОРКА", font=("Segoe UI", 11, "bold"), text_color=MUTED).pack(
            side="left", padx=(20, 10), pady=14)
        self.profile_var = ctk.StringVar()
        self.profile_combo = ctk.CTkComboBox(
            pf, values=[], variable=self.profile_var, width=220, height=36, corner_radius=10,
            fg_color=PANEL, border_color=PANEL, button_color=ACCENT, button_hover_color=ACCENT_H,
            dropdown_fg_color=PANEL, font=("Segoe UI", 13, "bold"), state="readonly",
            command=lambda _: self._profile_selected())
        self.profile_combo.pack(side="left", pady=14)
        for txt, cmd, w in (("+ Новая", self._profile_new, 84), ("✎", self._profile_rename, 36),
                            ("🗑", self._profile_delete, 36)):
            ctk.CTkButton(pf, text=txt, width=w, height=32, corner_radius=8, fg_color=PANEL,
                          hover_color="#2f2160", font=("Segoe UI", 12), command=cmd).pack(side="left", padx=(6, 0))
        ctk.CTkButton(pf, text="+ Добавить моды", height=32, corner_radius=8, fg_color=ACCENT,
                      hover_color=ACCENT_H, font=("Segoe UI", 12, "bold"),
                      command=self._add_mods).pack(side="right", padx=(6, 20))
        ctk.CTkButton(pf, text="📁 Моды", width=90, height=32, corner_radius=8, fg_color=PANEL,
                      hover_color="#2f2160", font=("Segoe UI", 12),
                      command=lambda: self._open_path(self.instance_dir() / "mods")).pack(side="right")
        self.mods_lbl = ctk.CTkLabel(pf, text="", font=("Segoe UI", 12), text_color=MUTED)
        self.mods_lbl.pack(side="right", padx=12)

        card = ctk.CTkFrame(main, fg_color=CARD, corner_radius=18)
        card.grid(row=2, column=0, sticky="ew", pady=(10, 12))
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(card, text="ЗАГРУЗЧИК", font=("Segoe UI", 11, "bold"), text_color=MUTED).grid(
            row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        self.loader_seg = ctk.CTkSegmentedButton(
            card, values=["Vanilla", "Fabric", "Forge"], height=38, corner_radius=10,
            fg_color=PANEL, selected_color=ACCENT, selected_hover_color=ACCENT_H,
            unselected_color=PANEL, unselected_hover_color="#2f2160", font=("Segoe UI", 13, "bold"),
            command=lambda _: (self._refresh_version_list(), self._collect()))
        self.loader_seg.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))

        ctk.CTkLabel(card, text="ВЕРСИЯ MINECRAFT", font=("Segoe UI", 11, "bold"), text_color=MUTED).grid(
            row=0, column=1, sticky="w", padx=20, pady=(16, 4))
        self.version_combo = ctk.CTkComboBox(
            card, values=["загрузка…"], height=38, corner_radius=10, fg_color=PANEL, border_color=PANEL,
            button_color=ACCENT, button_hover_color=ACCENT_H, dropdown_fg_color=PANEL, font=("Segoe UI", 13),
            state="readonly", command=lambda _: self._collect())
        self.version_combo.grid(row=1, column=1, sticky="ew", padx=20, pady=(0, 16))

        self.ram_hint = ctk.CTkLabel(card, text="", font=("Segoe UI", 11), text_color=MUTED)
        self.ram_hint.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 12))

        # Консоль
        self.console = ctk.CTkTextbox(main, fg_color=PANEL, corner_radius=14, font=("Consolas", 12),
                                      text_color="#c9bff0", wrap="word")
        self.console.grid(row=3, column=0, sticky="nsew")
        self.console.configure(state="disabled")

        # Прогресс + кнопка
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        bottom.grid_columnconfigure(0, weight=1)
        self.progress_lbl = ctk.CTkLabel(bottom, text="Готов к запуску", font=("Segoe UI", 12), text_color=MUTED)
        self.progress_lbl.grid(row=0, column=0, sticky="w", padx=4)
        self.progress = ctk.CTkProgressBar(bottom, height=10, corner_radius=6, progress_color=ACCENT, fg_color=CARD)
        self.progress.grid(row=1, column=0, sticky="ew", padx=4, pady=(4, 0))
        self.progress.set(0)
        self.play_btn = ctk.CTkButton(bottom, text="▶  ИГРАТЬ", width=200, height=56, corner_radius=16,
                                      fg_color=ACCENT, hover_color=ACCENT_H, font=("Segoe UI", 18, "bold"),
                                      command=self._on_play)
        self.play_btn.grid(row=0, column=1, rowspan=2, padx=(16, 0))

        self.log(f"🌙 {APP_NAME} v{APP_VERSION} запущен")
        self.log(f"📁 Папка игры: {MC_DIR}")

    def _apply_config(self):
        self.nick_var.set(self.cfg["nickname"])
        if not self.cfg.get("profiles"):
            self.cfg["profiles"] = {"Основная": {"loader": self.cfg.get("loader", "Vanilla"),
                                                 "version": self.cfg.get("version", "")}}
        if self.cfg.get("profile") not in self.cfg["profiles"]:
            self.cfg["profile"] = next(iter(self.cfg["profiles"]))
        self._refresh_profiles()
        prof = self.cfg["profiles"][self.cfg["profile"]]
        self.cfg["loader"], self.cfg["version"] = prof.get("loader", "Vanilla"), prof.get("version", "")
        self.loader_seg.set(self.cfg.get("loader", "Vanilla"))
        self.cfg["ram"] = min(int(self.cfg.get("ram", 4)), max(1, self.ram_max - 2))
        self._update_ram_hint()
        self._nick_changed()

    # ---------- утилиты ----------
    def log(self, text, color=None):
        line = f"[{time.strftime('%H:%M:%S')}] {text}\n"
        try:
            if self.log_file is None:
                (DATA_DIR / "logs").mkdir(parents=True, exist_ok=True)
                self.log_file = open(DATA_DIR / "logs" / "latest.log", "w", encoding="utf-8")
            self.log_file.write(line); self.log_file.flush()
        except Exception:
            pass
        self._log_counter = getattr(self, "_log_counter", 0) + 1

        def _do():
            self.console.configure(state="normal")
            self.console.insert("end", line)
            if self._log_counter % 50 == 0:
                n = int(self.console.index("end-1c").split(".")[0])
                if n > 500:
                    self.console.delete("1.0", f"{n - 500}.0")
            self.console.see("end")
            self.console.configure(state="disabled")
        self.after(0, _do)

    def set_progress(self, value=None, text=None):
        def _do():
            if value is not None:
                self.progress.set(value)
            if text is not None:
                self.progress_lbl.configure(text=text)
        self.after(0, _do)

    def _collect(self):
        self.cfg["nickname"] = self.nick_var.get().strip() or "Player"
        self.cfg["loader"] = self.loader_seg.get()
        self.cfg["version"] = self.version_combo.get()
        if not self.cfg["version"].startswith("—") and self.cfg["version"] != "загрузка…":
            self.cfg["profiles"][self.cfg["profile"]] = {"loader": self.cfg["loader"], "version": self.cfg["version"]}
        save_config(self.cfg)

    def _update_ram_hint(self):
        java = Path(self.cfg.get("java_path") or "").name or "авто"
        self.ram_hint.configure(text=f"RAM: {self.cfg['ram']} ГБ из {self.ram_max}  ·  Java: {java}  ·  изменить — ⚙ Настройки")

    # ---------- ники ----------
    def _nick_changed(self):
        nick = self.nick_var.get().strip()
        if nick:
            self.hello_lbl.configure(text=f"Привет, {nick} 👋")
            self.rpc.update("В лаунчере", f"Ник: {nick}")

    def _save_nick(self):
        nick = self.nick_var.get().strip()
        if not nick:
            return
        if len(nick) > 16 or " " in nick:
            self.log("⚠ Ник должен быть до 16 символов и без пробелов", ERR)
            return
        if nick not in self.cfg["nicknames"]:
            self.cfg["nicknames"].append(nick)
            self.nick_combo.configure(values=self.cfg["nicknames"])
            self.log(f"✔ Ник «{nick}» сохранён")
        self._collect()
        self._nick_changed()

    def _delete_nick(self):
        nick = self.nick_var.get().strip()
        if nick not in self.cfg["nicknames"]:
            return
        if len(self.cfg["nicknames"]) <= 1:
            messagebox.showinfo("Ник", "Нельзя удалить последний ник")
            return
        if not messagebox.askyesno("Удалить ник", f"Удалить ник «{nick}»?"):
            return
        self.cfg["nicknames"].remove(nick)
        self.nick_combo.configure(values=self.cfg["nicknames"])
        self.nick_var.set(self.cfg["nicknames"][0])
        self._collect()
        self._nick_changed()
        self.log(f"🗑 Ник «{nick}» удалён")

    # ---------- версии ----------
    def _load_versions(self):
        self.log("⏳ Загружаю список версий…")
        try:
            self.all_versions = mll.utils.get_version_list()
            self.log(f"✔ Найдено версий: {len(self.all_versions)}")
        except Exception as e:
            self.log(f"✖ Нет интернета? Использую установленные версии. ({e})", ERR)
            try:
                self.all_versions = [{"id": v["id"], "type": v["type"]}
                                     for v in mll.utils.get_installed_versions(str(MC_DIR))]
            except Exception:
                self.all_versions = []
        self.after(0, self._refresh_version_list)

    def _refresh_version_list(self):
        loader = self.loader_seg.get()
        show_snap = self.cfg.get("show_snapshots", False)
        ids = []
        for v in self.all_versions:
            vid = v["id"]
            vtype = v.get("type", "release")
            if vtype == "release" or (show_snap and vtype == "snapshot"):
                ids.append(vid)
        if loader == "Fabric":
            try:
                ok = {v["version"] for v in mll.fabric.get_all_minecraft_versions()
                      if show_snap or v.get("stable", True)}
                ids = [i for i in ids if i in ok]
            except Exception:
                pass
        elif loader == "Forge":
            try:
                forge_list = mll.forge.list_forge_versions()
                ok = {f.split("-")[0] for f in forge_list}
                ids = [i for i in ids if i in ok]
            except Exception:
                pass
        if not ids:
            ids = ["— нет версий —"]
        self.versions_shown = ids
        self.version_combo.configure(values=ids)
        prev = self.cfg.get("version")
        self.version_combo.set(prev if prev in ids else ids[0])
        self.log(f"📦 {loader}: доступно версий — {len(ids)} (от {ids[-1]} до {ids[0]})")

    # ---------- Discord ----------
    def _start_rpc(self):
        err = self.rpc.connect()
        if err is None:
            self.after(0, lambda: self.status_dot.configure(text="●  Discord: подключён", text_color=OK))
            self.rpc.update("В лаунчере", f"Ник: {self.nick_var.get()}")
            self.log("🎮 Discord Rich Presence подключён")
        else:
            self.after(0, lambda: self.status_dot.configure(text="●  Discord: не найден", text_color=ERR))
            self.log(f"ℹ Discord RPC не подключился: {err}")
            self.log("   Проверь: Discord запущен (не браузерная версия), в настройках Discord →"
                     " Активность → включено «Отображать текущую активность»")

    def _toggle_rpc(self):
        if self.cfg.get("discord_rpc", True):
            threading.Thread(target=self._start_rpc, daemon=True).start()
        else:
            self.rpc.close()
            self.status_dot.configure(text="●  Discord: выключен", text_color=MUTED)

    # ---------- настройки ----------
    def _settings_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Настройки")
        win.geometry("600x640")
        win.configure(fg_color=BG)
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="⚙ Настройки", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(
            anchor="w", padx=24, pady=(20, 6))
        box = ctk.CTkScrollableFrame(win, fg_color=PANEL, corner_radius=14)
        box.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        def section(t):
            ctk.CTkLabel(box, text=t, font=("Segoe UI", 11, "bold"), text_color=ACCENT_H).pack(
                anchor="w", padx=16, pady=(16, 4))

        def entry(label, key, placeholder=""):
            ctk.CTkLabel(box, text=label, font=("Segoe UI", 12), text_color=TEXT).pack(anchor="w", padx=16)
            e = ctk.CTkEntry(box, fg_color=CARD, border_color=CARD, height=34, placeholder_text=placeholder)
            e.insert(0, str(self.cfg.get(key, "")))
            e.pack(fill="x", padx=16, pady=(2, 6))
            return e

        # Игра
        section("ИГРА")
        rec = max(2, min(8, self.ram_max // 2))
        ramf = ctk.CTkFrame(box, fg_color="transparent"); ramf.pack(fill="x", padx=16)
        ram_lbl = ctk.CTkLabel(ramf, text=f"Память: {self.cfg['ram']} ГБ", font=("Segoe UI", 12), text_color=TEXT)
        ram_lbl.pack(side="left")
        ctk.CTkLabel(ramf, text=f"рекомендуется {rec} ГБ · в ПК {self.ram_max} ГБ", font=("Segoe UI", 11),
                     text_color=MUTED).pack(side="right")
        ram_max = max(2, self.ram_max - 2)
        ram = ctk.CTkSlider(box, from_=1, to=ram_max, number_of_steps=ram_max - 1, progress_color=ACCENT,
                            button_color=ACCENT, button_hover_color=ACCENT_H,
                            command=lambda v: ram_lbl.configure(text=f"Память: {int(v)} ГБ"))
        ram.set(min(self.cfg["ram"], ram_max)); ram.pack(fill="x", padx=16, pady=(4, 8))
        java = entry("Путь к java.exe (пусто = авто):", "java_path", "C:\\Program Files\\Java\\jdk-21\\bin\\java.exe")
        jvm = entry("Дополнительные аргументы JVM:", "jvm_args", "-XX:+UseG1GC")
        snap = ctk.CTkSwitch(box, text="Показывать снапшоты в списке версий", progress_color=ACCENT)
        snap.pack(anchor="w", padx=16, pady=4)
        if self.cfg.get("show_snapshots"): snap.select()
        close_sw = ctk.CTkSwitch(box, text="Сворачивать лаунчер при запуске игры", progress_color=ACCENT)
        close_sw.pack(anchor="w", padx=16, pady=4)
        if self.cfg.get("close_on_launch"): close_sw.select()

        # Discord
        section("DISCORD")
        rpc_sw = ctk.CTkSwitch(box, text="Discord Rich Presence", progress_color=ACCENT)
        rpc_sw.pack(anchor="w", padx=16, pady=4)
        if self.cfg.get("discord_rpc", True): rpc_sw.select()
        cid = entry("Discord Application ID:", "discord_client_id")
        burl = entry("Ссылка кнопки в статусе (пусто = без кнопки):", "rpc_button_url", "https://discord.gg/...")

        # Обновления
        section("ОБНОВЛЕНИЯ")
        uurl = entry("Ссылка на latest.json:", "update_url", "https://raw.githubusercontent.com/…/latest.json")

        ctk.CTkLabel(box, text=f"Папка данных: {DATA_DIR}", font=("Segoe UI", 11), text_color=MUTED).pack(
            anchor="w", padx=16, pady=(16, 8))

        def save():
            old_rpc = (self.cfg.get("discord_rpc", True), self.cfg.get("discord_client_id"), self.cfg.get("rpc_button_url"))
            self.cfg["ram"] = int(ram.get())
            self.cfg["java_path"] = java.get().strip()
            self.cfg["jvm_args"] = jvm.get().strip()
            self.cfg["show_snapshots"] = bool(snap.get())
            self.cfg["close_on_launch"] = bool(close_sw.get())
            self.cfg["discord_rpc"] = bool(rpc_sw.get())
            self.cfg["discord_client_id"] = cid.get().strip() or DISCORD_CLIENT_ID
            self.cfg["rpc_button_url"] = burl.get().strip()
            self.cfg["update_url"] = uurl.get().strip()
            save_config(self.cfg)
            self._update_ram_hint()
            self._refresh_version_list()
            if old_rpc != (self.cfg["discord_rpc"], self.cfg["discord_client_id"], self.cfg["rpc_button_url"]):
                self.rpc.close()
                self.rpc = DiscordRPC(self.cfg["discord_client_id"], self.cfg["rpc_button_url"])
                self._toggle_rpc()
            self.log("✔ Настройки сохранены")
            win.destroy()

        ctk.CTkButton(win, text="Сохранить", fg_color=ACCENT, hover_color=ACCENT_H, height=40,
                      corner_radius=10, font=("Segoe UI", 14, "bold"), command=save).pack(pady=(0, 16))

    # ---------- сборки ----------
    def instance_dir(self) -> Path:
        safe = "".join(c for c in self.cfg["profile"] if c not in '\\/:*?"<>|').strip() or "default"
        d = INSTANCES_DIR / safe
        (d / "mods").mkdir(parents=True, exist_ok=True)
        return d

    def _refresh_profiles(self):
        names = list(self.cfg["profiles"].keys())
        self.profile_combo.configure(values=names)
        self.profile_var.set(self.cfg["profile"])
        self._update_mods_label()

    def _update_mods_label(self):
        try:
            n = len([f for f in (self.instance_dir() / "mods").glob("*.jar")])
            self.mods_lbl.configure(text=f"модов: {n}")
        except Exception:
            self.mods_lbl.configure(text="")

    def _profile_selected(self):
        name = self.profile_var.get()
        if name not in self.cfg["profiles"]:
            return
        self.cfg["profile"] = name
        prof = self.cfg["profiles"][name]
        self.cfg["loader"], self.cfg["version"] = prof.get("loader", "Vanilla"), prof.get("version", "")
        self.loader_seg.set(self.cfg["loader"])
        self._refresh_version_list()
        self._update_mods_label()
        save_config(self.cfg)
        self.log(f"📦 Сборка: {name} ({self.cfg['loader']} {self.cfg['version'] or '—'})")

    def _profile_new(self):
        name = simpledialog.askstring("Новая сборка", "Название сборки:", parent=self)
        if not name:
            return
        name = name.strip()
        if name in self.cfg["profiles"]:
            messagebox.showwarning("Сборка", "Такая сборка уже есть")
            return
        self._collect()
        self.cfg["profiles"][name] = {"loader": self.loader_seg.get(), "version": self.version_combo.get()}
        self.cfg["profile"] = name
        self._refresh_profiles()
        self.instance_dir()
        save_config(self.cfg)
        self.log(f"✔ Сборка «{name}» создана — кидай моды в 📁 Моды")

    def _profile_rename(self):
        old = self.cfg["profile"]
        new = simpledialog.askstring("Переименовать", "Новое название:", initialvalue=old, parent=self)
        if not new or new.strip() == old:
            return
        new = new.strip()
        if new in self.cfg["profiles"]:
            messagebox.showwarning("Сборка", "Такая сборка уже есть")
            return
        old_dir = self.instance_dir()
        self.cfg["profiles"][new] = self.cfg["profiles"].pop(old)
        self.cfg["profile"] = new
        new_dir = self.instance_dir()
        try:
            if old_dir.exists() and old_dir != new_dir:
                shutil.rmtree(new_dir, ignore_errors=True)
                shutil.move(str(old_dir), str(new_dir))
        except Exception as e:
            self.log(f"⚠ Не удалось переместить папку сборки: {e}")
        self._refresh_profiles()
        save_config(self.cfg)

    def _profile_delete(self):
        name = self.cfg["profile"]
        if len(self.cfg["profiles"]) <= 1:
            messagebox.showinfo("Сборка", "Нельзя удалить последнюю сборку")
            return
        if not messagebox.askyesno("Удалить сборку", f"Удалить «{name}» вместе с модами и мирами?"):
            return
        d = self.instance_dir()
        self.cfg["profiles"].pop(name)
        self.cfg["profile"] = next(iter(self.cfg["profiles"]))
        shutil.rmtree(d, ignore_errors=True)
        self._refresh_profiles()
        self._profile_selected()
        self.log(f"🗑 Сборка «{name}» удалена")

    def _add_mods(self):
        files = filedialog.askopenfilenames(title="Выбери моды (.jar)", filetypes=[("Моды Minecraft", "*.jar"), ("Все файлы", "*.*")])
        if not files:
            return
        dst = self.instance_dir() / "mods"
        n = 0
        for f in files:
            try:
                shutil.copy2(f, dst / Path(f).name)
                n += 1
            except Exception as e:
                self.log(f"⚠ {Path(f).name}: {e}")
        self._update_mods_label()
        self.log(f"✔ Добавлено модов: {n} → {dst}")
        if self.loader_seg.get() == "Vanilla":
            self.log("ℹ Для модов выбери загрузчик Fabric или Forge")

    def _open_path(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(path)  # type: ignore
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

    # ---------- обновления ----------
    def _changelog_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Обновления лаунчера")
        win.geometry("620x560")
        win.configure(fg_color=BG)
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="🌙 Обновления Luna Launcher", font=("Segoe UI", 22, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=24, pady=(20, 2))
        self.upd_info = ctk.CTkLabel(win, text=f"Текущая версия: {APP_VERSION}", font=("Segoe UI", 12),
                                     text_color=MUTED)
        self.upd_info.pack(anchor="w", padx=24)
        box = ctk.CTkScrollableFrame(win, fg_color=PANEL, corner_radius=14)
        box.pack(fill="both", expand=True, padx=20, pady=14)
        for ver, date, items in CHANGELOG:
            head = ctk.CTkFrame(box, fg_color="transparent")
            head.pack(fill="x", padx=12, pady=(12, 2))
            tag = "ТЕКУЩАЯ" if ver == APP_VERSION else ""
            ctk.CTkLabel(head, text=f"v{ver}", font=("Segoe UI", 16, "bold"), text_color=ACCENT_H).pack(side="left")
            ctk.CTkLabel(head, text=f"   {date}   {tag}", font=("Segoe UI", 11), text_color=MUTED).pack(side="left")
            for it in items:
                color = OK if it.startswith("+") else ERR if it.startswith("-") else "#f0c674"
                row = ctk.CTkFrame(box, fg_color="transparent")
                row.pack(fill="x", padx=20)
                ctk.CTkLabel(row, text=it[0], font=("Consolas", 13, "bold"), text_color=color, width=16).pack(side="left")
                ctk.CTkLabel(row, text=it[1:].strip(), font=("Segoe UI", 12), text_color=TEXT,
                             wraplength=520, justify="left").pack(side="left", anchor="w")
        legend = ctk.CTkLabel(win, text="+ добавлено    − убрано    ~ изменено", font=("Segoe UI", 11), text_color=MUTED)
        legend.pack(pady=(0, 6))
        self.upd_check_btn = ctk.CTkButton(win, text="Проверить обновления", fg_color=ACCENT, hover_color=ACCENT_H,
                                           height=38, corner_radius=10, command=self._check_updates)
        self.upd_check_btn.pack(pady=(0, 16))

    def _check_updates(self):
        def worker():
            url_src = self.cfg.get("update_url") or UPDATE_URL
            if not url_src or "ТЫ/" in url_src:
                self.after(0, lambda: self.upd_info.configure(text="Ссылка обновлений не настроена — задай её в ⚙ Настройках", text_color=ERR))
                return
            try:
                import urllib.request
                with urllib.request.urlopen(url_src, timeout=8) as r:
                    data = json.loads(r.read().decode("utf-8"))
                latest = data.get("version", APP_VERSION)
                def vt(v): return tuple(int(x) for x in v.split("."))
                if vt(latest) > vt(APP_VERSION):
                    url = data.get("url", "")
                    self.after(0, lambda: (self.upd_info.configure(
                        text=f"Доступна новая версия {latest}! " + (data.get("notes") or ""), text_color=OK),
                        self.upd_check_btn.configure(text=f"⬇ Обновить до v{latest}",
                                                     command=lambda: self._download_update(url, latest))))
                    self.log(f"🔔 Доступно обновление v{latest}")
                else:
                    self.after(0, lambda: self.upd_info.configure(text=f"У тебя последняя версия ({APP_VERSION}) ✔", text_color=OK))
            except Exception as e:
                self.after(0, lambda: self.upd_info.configure(text=f"Не удалось проверить: {e}", text_color=ERR))
        threading.Thread(target=worker, daemon=True).start()

    def _download_update(self, url, latest):
        """Скачивает новый exe, подменяет себя и перезапускается"""
        if not getattr(sys, "frozen", False):
            webbrowser.open(url)
            self.log("ℹ Авто‑обновление работает только в exe‑версии; открыл ссылку в браузере")
            return
        self.upd_check_btn.configure(state="disabled", text="Скачивание…")

        def worker():
            try:
                import urllib.request
                exe = Path(sys.executable)
                new = exe.with_name(exe.stem + "_new.exe")
                req = urllib.request.Request(url, headers={"User-Agent": "LunaLauncher"})
                with urllib.request.urlopen(req, timeout=30) as r, open(new, "wb") as f:
                    total = int(r.headers.get("Content-Length") or 0)
                    done = 0
                    while True:
                        chunk = r.read(1024 * 256)
                        if not chunk:
                            break
                        f.write(chunk)
                        done += len(chunk)
                        if total:
                            pct = done * 100 // total
                            self.after(0, lambda p=pct: self.upd_check_btn.configure(text=f"Скачивание… {p}%"))
                            self.set_progress(done / total, f"Обновление v{latest}: {done // 1048576} / {total // 1048576} МБ")
                if new.stat().st_size < 1_000_000:
                    raise RuntimeError("файл слишком маленький — неверная ссылка?")
                # bat: ждём закрытия, заменяем, запускаем
                bat = Path(tempfile.gettempdir()) / "luna_update.bat"
                bat.write_text(
                    "@echo off\r\n"
                    ":wait\r\n"
                    "timeout /t 1 /nobreak >nul\r\n"
                    f'del "{exe}" >nul 2>&1\r\n'
                    f'if exist "{exe}" goto wait\r\n'
                    f'move /y "{new}" "{exe}" >nul\r\n'
                    f'start "" "{exe}"\r\n'
                    'del "%~f0"\r\n', encoding="cp866")
                self.log(f"✔ Обновление v{latest} скачано, перезапускаюсь…")
                self.after(0, lambda: self.upd_info.configure(text="Перезапуск…", text_color=OK))
                time.sleep(1)
                subprocess.Popen(["cmd", "/c", str(bat)], creationflags=0x08000000)
                self.after(200, self._on_close)
            except Exception as e:
                self.log(f"✖ Ошибка обновления: {e}")
                self.after(0, lambda: (self.upd_info.configure(text=f"Ошибка: {e}", text_color=ERR),
                                       self.upd_check_btn.configure(state="normal", text="Повторить")))
        threading.Thread(target=worker, daemon=True).start()

    def _open_dir(self):
        MC_DIR.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(MC_DIR)  # type: ignore
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(MC_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(MC_DIR)])

    # ---------- запуск ----------
    def _on_play(self):
        if self.busy:
            return
        self._collect()
        ver = self.cfg["version"]
        if not ver or ver.startswith("—"):
            self.log("⚠ Выбери версию", ERR)
            return
        self.busy = True
        self.play_btn.configure(state="disabled", text="⏳  ПОДГОТОВКА")
        threading.Thread(target=self._install_and_launch, daemon=True).start()

    def _callback(self):
        st = {"max": 1}

        def set_status(s):
            self.set_progress(text=s)
            self.log("   " + s)

        def set_max(m):
            st["max"] = max(m, 1)

        def set_prog(p):
            self.set_progress(value=p / st["max"])
        return {"setStatus": set_status, "setMax": set_max, "setProgress": set_prog}

    def _install_and_launch(self):
        loader, mc_ver, nick = self.cfg["loader"], self.cfg["version"], self.cfg["nickname"]
        MC_DIR.mkdir(parents=True, exist_ok=True)
        cb = self._callback()
        try:
            self.rpc.update(f"Устанавливает {loader} {mc_ver}", f"Ник: {nick}")
            self.log(f"🚀 {loader} {mc_ver} · ник {nick}")

            if loader == "Vanilla":
                mll.install.install_minecraft_version(mc_ver, str(MC_DIR), callback=cb)
                launch_id = mc_ver
            elif loader == "Fabric":
                mll.fabric.install_fabric(mc_ver, str(MC_DIR), callback=cb)
                launch_id = self._find_installed(lambda i: i.startswith("fabric-loader") and i.endswith("-" + mc_ver))
            else:  # Forge
                fv = mll.forge.find_forge_version(mc_ver)
                if not fv:
                    raise RuntimeError(f"Forge для {mc_ver} не найден")
                launch_id = mll.forge.forge_to_installed_version(fv)
                if not self._is_installed(launch_id):
                    if not mll.forge.supports_automatic_install(fv):
                        self.log("ℹ Эта версия Forge не ставится автоматически — запускаю установщик…")
                        mll.forge.run_forge_installer(fv)
                    else:
                        mll.forge.install_forge_version(fv, str(MC_DIR), callback=cb)
                    launch_id = self._find_installed(lambda i: mc_ver in i and "forge" in i.lower()) or launch_id

            if not launch_id:
                raise RuntimeError("Не удалось определить установленную версию")

            ram = int(self.cfg["ram"])
            jvm = [f"-Xmx{ram}G", f"-Xms{min(ram, 2)}G"] + (self.cfg.get("jvm_args") or "").split()
            options = {
                "username": nick,
                "uuid": offline_uuid(nick),
                "token": "0",
                "jvmArguments": jvm,
                "launcherName": APP_NAME,
                "launcherVersion": APP_VERSION,
                "gameDirectory": str(self.instance_dir()),
            }
            if self.cfg.get("java_path"):
                options["executablePath"] = self.cfg["java_path"]

            cmd = mll.command.get_minecraft_command(launch_id, str(MC_DIR), options)
            self.set_progress(1, f"Запуск {launch_id}…")
            self.log(f"▶ Запуск {launch_id}")
            self.rpc.update(f"Играет в {loader} {mc_ver}", f"Ник: {nick}")
            self.after(0, lambda: self.play_btn.configure(text="🎮  В ИГРЕ"))
            if self.cfg.get("close_on_launch"):
                self.after(2000, self.iconify)

            self.log(f"📁 Сборка «{self.cfg['profile']}»: {self.instance_dir()}")
            self.game_proc = subprocess.Popen(cmd, cwd=str(self.instance_dir()), stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, text=True, errors="replace")
            for line in self.game_proc.stdout:
                line = line.rstrip()
                if line:
                    self.log(line)
            code = self.game_proc.wait()
            self.log(f"⏹ Игра закрыта (код {code})")
            if self.cfg.get("close_on_launch"):
                self.after(0, self.deiconify)
        except Exception as e:
            self.log(f"✖ Ошибка: {e}", ERR)
            self.set_progress(0, "Ошибка — смотри лог")
        finally:
            self.busy = False
            self.game_proc = None
            self.rpc.update("В лаунчере", f"Ник: {nick}")
            self.set_progress(0, "Готов к запуску")
            self.after(0, lambda: self.play_btn.configure(state="normal", text="▶  ИГРАТЬ"))

    def _is_installed(self, vid):
        return any(v["id"] == vid for v in mll.utils.get_installed_versions(str(MC_DIR)))

    def _find_installed(self, pred):
        found = [v["id"] for v in mll.utils.get_installed_versions(str(MC_DIR)) if pred(v["id"])]
        return sorted(found)[-1] if found else None

    def _on_close(self):
        try:
            self._collect()
        except Exception:
            pass
        self.rpc.close()
        self.destroy()


if __name__ == "__main__":
    app = LunaLauncher()
    app.mainloop()
