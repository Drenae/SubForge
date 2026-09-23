# Subforge app

## Run the app

### uv

Run as a desktop app:

```bash
uv run flet run
```

Run as a web app:

```bash
uv run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/).

## Build the app

### Android

```bash
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```bash
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```bash
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```bash
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```bash
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).

### Web

```bash
flet build web -v
```

For more details on building Web app, refer to the [Web Packaging Guide](https://flet.dev/docs/publish/web/).

## OCR PGS sous Windows

L'OCR requiert [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html), installé séparément et accessible dans le `PATH` Windows. Installez aussi les données de langue souhaitées, notamment `fra` pour le français ; vérifiez avec `tesseract --list-langs` dans PowerShell. SubForge utilise FFmpeg pour extraire les pistes PGS en `.sup` avant l'OCR ; Tesseract ne dépend pas de Subtitle Edit.

Dans **Traitements**, choisissez un `.sup`, la langue OCR, puis lancez la reconnaissance. Relisez et corrigez le SRT affiché avant de l'enregistrer. Une confiance faible ou un texte vide est signalé dans le résumé. L'export refuse de remplacer un fichier existant.
