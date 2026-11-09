# SprichDe

German learning app starter, built with Flutter and organized by feature.

> **Muhim:** hozir ishlaydigan versiya — `admin-panel/` papkasidagi **PWA** (HTML/CSS/JS).
> Uni `run_app.py` orqali ishga tushiring; `lib/` papkasi esa hali tugallanmagan Flutter skeleti
> (Flutter SDK va `android/` papkasi kerak). Batafsil: `admin-panel/README.md`.

## Project structure

- `lib/app.dart` — app shell and bottom navigation
- `lib/core/theme/` — shared visual theme
- `lib/features/home/` — learning dashboard
- `lib/features/lessons/` — lesson model, sample content, and lesson list
- `lib/features/vocabulary/` — vocabulary cards
- `lib/features/practice/` — interactive multiple-choice practice

## Run

Install Flutter, open this folder as a Flutter project, then run `flutter pub get` and start the app on an emulator or device.

The initial screens use sample in-memory content. Persistence, audio pronunciation, user accounts, and progress tracking can be added as separate services when the product requirements are defined.

