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

## Application Windows autonome

Après un `git pull`, l'environnement de développement existant ne se met pas à jour automatiquement. Pour lancer le code source, exécutez une fois `\.venv\Scripts\python.exe -m pip install -e .` depuis `E:\SubForge`, puis `flet run`. Cette commande installe les bibliothèques Python nécessaires dans le `.venv` du projet ; elle ne demande pas d'installer Tesseract ou un autre logiciel à part.

Le build Windows intègre l’OCR, ses modèles, FFmpeg et FFprobe. Aucun de ces logiciels ne doit être installé séparément sur le PC qui utilisera l’application.

Pour préparer les exécutables FFmpeg dans le projet puis construire l’application, lancer `scripts\build_windows.ps1` depuis PowerShell. Le script télécharge une archive FFmpeg pour Windows **au moment du build**, vérifie sa somme SHA-256 et place `ffmpeg.exe` et `ffprobe.exe` dans les ressources embarquées. Aucun téléchargement n’est effectué par l’application distribuée. Voir [la page du fournisseur des builds FFmpeg](https://www.gyan.dev/ffmpeg/builds/) pour la licence et le code source correspondant.

Pendant le développement, `flet run` utilisera les exécutables embarqués si `scripts\prepare_windows_tools.ps1` a déjà été lancé, sinon ceux présents dans le `PATH` du développeur. Les dépendances Python du projet sont installées dans son environnement virtuel au build.

## OCR PGS intégré

L'OCR utilise RapidOCR et ONNX Runtime. Les modèles français et multilingues sont fournis avec les dépendances Python du projet : aucun Tesseract, paquet de langue ou téléchargement au lancement n'est nécessaire. Le modèle fonctionne automatiquement, sans réglage de langue.

Dans **Conversion**, choisissez un `.sup`, lancez la reconnaissance et corrigez le SRT avant de l'enregistrer. Les résultats de faible confiance sont signalés. L'export UTF-8 refuse d'écraser un fichier existant.

### OCR de plusieurs épisodes

Sélectionnez les pistes PGS voulues dans **Accueil**, choisissez un dossier de sortie dans **Conversion**, puis cliquez sur **Convertir les PGS sélectionnés en SRT**. SubForge extrait chaque piste dans un dossier temporaire, crée un SRT UTF-8 avec un nom unique et continue si une piste échoue. Le rapport indique les fichiers produits et le nombre de répliques dont la reconnaissance est incertaine. Relisez les SRT produits avant de les utiliser. Le bouton d'annulation arrête le lot après la piste en cours.

La page **Extraction** enregistre séparément les pistes cochées dans **Accueil** dans leur format d'origine, sans OCR ni conversion.
