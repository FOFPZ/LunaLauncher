<div align="center">

<img src="assets/discord_icon.png" width="140" alt="Luna Launcher">

# 🌙 Luna Launcher

**Красивый и лёгкий лаунчер Minecraft в стиле Purple Moon**

Vanilla · Fabric · Forge &nbsp;|&nbsp; версии 1.0 → 26.3 &nbsp;|&nbsp; свои ники &nbsp;|&nbsp; сборки с модами &nbsp;|&nbsp; Discord Rich Presence &nbsp;|&nbsp; авто‑обновление

[![Version](https://img.shields.io/badge/version-0.1.1-9b6dff?style=for-the-badge)](#-история-версий)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-221846?style=for-the-badge&logo=windows)](#-установка)
[![Python](https://img.shields.io/badge/python-3.10%2B-160f2e?style=for-the-badge&logo=python)](#-запуск-из-исходников)
[![License](https://img.shields.io/badge/license-MIT-5ee1a2?style=for-the-badge)](LICENSE)

[Скачать](#-установка) • [Возможности](#-возможности) • [Сборки и моды](#-сборки-и-моды) • [Discord](#-discord-rich-presence) • [Сборка exe](#-сборка-exe) • [FAQ](#-faq)

</div>

---

## ✨ Возможности

| | |
|---|---|
| 🎮 **Все загрузчики** | Vanilla, Fabric и Forge — переключение одной кнопкой, установка полностью автоматическая |
| 📜 **Все версии** | От **1.0** до **26.3**, плюс снапшоты по галочке. Список подтягивается напрямую с серверов Mojang |
| 👤 **Свои ники** | Сохраняй сколько угодно ников и переключайся между ними. Оффлайн‑UUID как на обычных серверах |
| 📦 **Сборки (модпаки)** | У каждой сборки своя папка модов, миров и настроек. Моды добавляются в один клик |
| 💬 **Discord Rich Presence** | Друзья видят «Играет в Luna Launcher», версию, загрузчик и ник |
| 🔄 **Авто‑обновление** | Лаунчер сам скачивает новую версию и перезапускается — ничего качать вручную не нужно |
| ⚙ **Настройки в одном окне** | RAM (с учётом памяти ПК), Java, JVM, Discord ID, ссылка обновлений — без пересборки exe |
| 🖥 **Консоль и логи** | Последние 500 строк в окне, полный лог в `logs/latest.log` |
| 🌙 **Purple Moon** | Тёмная фиолетовая тема, скруглённые карточки, ничего лишнего |

<div align="center">
<img src="assets/preview_on_purple.png" width="600" alt="Logo preview">
</div>

---

## 📥 Установка

**Готовый exe (рекомендуется)**

1. Скачай `LunaLauncher.exe` из [последнего релиза](../../releases/latest).
2. Положи в любую папку и запусти. Python устанавливать **не нужно**.
3. Для самой игры нужна **Java 17 или 21** — [скачать Temurin](https://adoptium.net/).

> ⚠️ Windows SmartScreen может показать «Система защитила ваш компьютер» — это стандартное предупреждение для любых неподписанных программ. Нажми **Подробнее → Выполнить в любом случае**.

Все файлы игры и настройки хранятся в `C:\Users\<ты>\.lunalauncher\`.

**Запуск из исходников**

```bash
git clone https://github.com/ТЫ/LunaLauncher.git
cd LunaLauncher
pip install -r requirements.txt
python luna_launcher.py
```

<details>
<summary>Для разработчиков: скрипты</summary>

- `run.bat` / `run.sh` — запуск из исходников с автоустановкой зависимостей
- `build_exe.bat` — сборка exe одним кликом
</details>

---

## 🚀 Быстрый старт

1. Впиши ник слева → **+ Сохранить ник**
2. Выбери загрузчик (**Vanilla / Fabric / Forge**) и версию
3. При желании открой **⚙ Настройки** — RAM (ограничен памятью твоего ПК), Java, JVM
4. Жми **▶ ИГРАТЬ** — лаунчер сам скачает всё нужное и запустит игру

---

## 📦 Сборки и моды

Панель **СБОРКА** над выбором версии — это модпаки.

- **+ Новая** — создать сборку; она запоминает свой загрузчик и версию
- **📁 Моды** — открыть папку модов этой сборки
- **+ Добавить моды** — выбрать `.jar` файлы, лаунчер скопирует их сам
- **✎** переименовать, **🗑** удалить

Каждая сборка живёт в отдельной папке:

```
.lunalauncher/
├── minecraft/            ← общие версии, библиотеки, ассеты (качаются один раз)
└── instances/
    ├── Основная/
    ├── RPG-сборка/       ← Forge 1.20.1
    │   ├── mods/
    │   ├── saves/
    │   └── config/
    └── PvP/              ← Fabric 26.3
        └── mods/
```

Моды одной сборки никогда не пересекаются с другой. Для модов выбирай **Fabric** или **Forge** — на Vanilla они не загрузятся.

---

## 💬 Discord Rich Presence

Работает из коробки: запусти Discord (приложение, не браузер), затем лаунчер. В левой панели загорится **● Discord: подключён**.

Что видят друзья:

| Состояние | Строка в Discord |
|---|---|
| В лаунчере | `В лаунчере` · `Ник: Nik` |
| Установка | `Устанавливает Fabric 26.3` · `Ник: Nik` |
| В игре | `Играет в Fabric 26.3` · `Ник: Nik` + таймер |

Если статус не появляется: *Настройки Discord → Активность → Конфиденциальность активности → «Отображать текущую активность как статус»* должно быть включено, а статус не «Невидимый».

---

## 🛠 Технологии

- [Python 3](https://python.org) + [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — интерфейс
- [minecraft-launcher-lib](https://codeberg.org/JakobDev/minecraft-launcher-lib) — установка и запуск Minecraft, Fabric, Forge
- [pypresence](https://github.com/qwertyquerty/pypresence) — Discord Rich Presence
- [Pillow](https://python-pillow.org) — графика
- [PyInstaller](https://pyinstaller.org) — сборка в exe

---

## ❓ FAQ

**Игра не запускается / сразу закрывается**
Посмотри консоль в лаунчере — последние строки покажут причину. Чаще всего: не хватает RAM (уменьши ползунок), нет Java 17/21, или мод не подходит к версии.

**Forge для старой версии не ставится**
Для очень старых версий Forge лаунчер откроет официальный установщик — просто нажми в нём *Install client*.

**Discord показывает «не найден»**
Discord должен быть запущен как программа до старта лаунчера. Сними и снова поставь галочку «Discord Rich Presence».

**Где мои миры?**
`C:\Users\<ты>\.lunalauncher\instances\<сборка>\saves\`

**Можно играть на лицензионных серверах?**
Нет — лаунчер работает в оффлайн‑режиме (без аккаунта Microsoft), подходит для одиночной игры и серверов с `online-mode=false`.

---

## 📄 Лицензия

MIT — делай что хочешь, только оставь упоминание автора.
*Luna Launcher не связан с Mojang Studios и Microsoft. Minecraft — торговая марка Mojang Studios.*

<div align="center">

Сделано с 💜 под луной

</div>
