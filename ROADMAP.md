# SubForge — Roadmap

SubForge est une application Windows développée avec Flet permettant d'analyser, filtrer, extraire et convertir les pistes de sous-titres contenues dans des fichiers vidéo, principalement MKV.

## Objectif V1

La V1 doit permettre un workflow complet :

**Importer des MKV → analyser les pistes → filtrer/sélectionner → extraire → OCR des sous-titres image → exporter en SRT.**

L'application doit fonctionner aussi bien sur un épisode unique que sur une saison complète.

---

## Phase 1 — Fondations

- [x] Définir une architecture modulaire.
- [x] Séparer UI, logique, modèles et services.
- [x] Mettre en place la navigation principale.
- [x] Créer le thème visuel de SubForge.
- [x] Centraliser la configuration de l'application.
- [x] Détecter automatiquement FFmpeg et FFprobe.
- [x] Afficher clairement leur disponibilité/version.
- [x] Préparer la gestion centralisée des erreurs et logs.
- [x] Préparer les tests unitaires des services indépendants de l'UI.

### Architecture cible initiale

```text
src/
├── app/
│   ├── views/
│   ├── components/
│   ├── models/
│   ├── services/
│   ├── state/
│   ├── utils/
│   └── config/
└── assets/

tests/
```

L'architecture pourra évoluer si les besoins réels du projet le justifient.

---

## Phase 2 — Import des médias

- [x] Sélection d'un fichier vidéo.
- [x] Sélection multiple.
- [ ] Drag & drop.
- [x] Import d'un dossier/saison.
- [x] Validation des fichiers pris en charge.
- [x] Liste des médias chargés.
- [x] Suppression individuelle ou globale de la sélection.
- [x] Gestion des fichiers invalides ou inaccessibles.

---

## Phase 3 — Analyse avec FFprobe

- [x] Exécuter FFprobe sans bloquer l'interface.
- [x] Parser proprement sa sortie JSON.
- [x] Identifier toutes les pistes de sous-titres.
- [ ] Récupérer pour chaque piste :
  - index ;
  - codec ;
  - langue ;
  - titre ;
  - disposition Forced ;
  - disposition Default ;
  - informations utiles disponibles dans les tags.
- [ ] Support initial :
  - PGS / HDMV PGS ;
  - SRT / SubRip ;
  - ASS ;
  - SSA ;
  - VobSub.
- [x] Gérer les langues/tags absents ou incorrects.
- [x] Conserver les informations séparément pour chaque média.

---

## Phase 4 — Interface des pistes

- [x] Afficher les médias et leurs pistes de sous-titres.
- [x] Sélection individuelle des pistes.
- [x] Sélection/désélection globale.
- [x] Afficher clairement :
  - langue ;
  - format ;
  - Forced ;
  - Default ;
  - titre ;
  - index.
- [x] Distinguer visuellement les pistes forcées.
- [x] Prévoir une interface utilisable avec beaucoup d'épisodes et de pistes.

---

## Phase 5 — Filtres

- [x] Filtre par langue.
- [x] Filtre par codec/format.
- [x] Filtre Forced.
- [x] Filtre Full/non Forced.
- [x] Filtre Default.
- [x] Combinaison de plusieurs filtres.
- [x] Application des filtres à tous les médias chargés.
- [x] Sélection manuelle toujours possible après filtrage.
- [x] Premier cas d'usage prioritaire : **Français + Forced**.

---

## Phase 6 — Extraction

- [x] Extraction avec FFmpeg sans réencodage.
- [x] Extraction d'une ou plusieurs pistes.
- [x] Traitement de plusieurs médias.
- [x] Choix du dossier de destination.
- [x] Nommage automatique et lisible.
- [x] Prévention des écrasements accidentels.
- [x] Progression par fichier et progression globale.
- [x] Possibilité d'annuler une opération.
- [x] Journal d'activité.
- [x] Rapport des réussites et erreurs.
- [x] Conserver le format original lors d'une simple extraction.

Exemple de nomenclature :

```text
Loki.S01E01_fra_FORCED_PGS.sup
Loki.S01E01_fra_FULL_PGS.sup
```

---

## Phase 7 — OCR

Objectif principal : convertir les sous-titres basés sur des images en texte.

- [x] Étudier et choisir le moteur OCR adapté au projet.
- [x] Intégrer le moteur retenu sans dépendre de Subtitle Edit.
- [x] PGS → SRT.
- [ ] VobSub → SRT si techniquement pertinent.
- [x] Choix de la langue OCR.
- [x] Prétraitement des images si nécessaire.
- [x] Préserver précisément les timecodes.
- [x] Afficher la progression OCR.
- [x] Détecter/signaler les résultats incertains.
- [x] Prévisualiser le texte reconnu.
- [x] Permettre la correction avant export.
- [x] Export UTF-8 en SRT.
- [x] Traitement OCR par lot.

---

## Phase 8 — Conversion et nettoyage

- [ ] Conversion des formats texte utiles.
- [ ] SRT ↔ ASS/SSA si pertinent.
- [ ] Nettoyage configurable du résultat OCR.
- [ ] Gestion des espaces et retours à la ligne.
- [ ] Correction de motifs OCR récurrents.
- [ ] Conservation stricte des timecodes.
- [ ] Vérification de la validité du fichier produit.

---

## Phase 9 — Traitement par lot

- [ ] Traiter une saison complète en une opération.
- [ ] Appliquer les mêmes filtres à tous les épisodes.
- [ ] Extraire automatiquement les pistes correspondantes.
- [ ] Enchaîner extraction + OCR lorsque demandé.
- [ ] Continuer le lot lorsqu'un fichier échoue.
- [ ] Résumé final :
  - fichiers traités ;
  - pistes extraites ;
  - conversions réussies ;
  - erreurs.

---

## Phase 10 — Profils

Créer des profils réutilisables, par exemple :

- [ ] Français Forced.
- [ ] Français complet.
- [ ] Tous les PGS.
- [ ] Tous les sous-titres français.
- [ ] Profils personnalisés.
- [ ] Sauvegarde persistante.
- [ ] Modification/suppression.
- [ ] Profil par défaut optionnel.

---

## Phase 11 — Paramètres et finition

- [ ] Dossier de sortie par défaut.
- [ ] Chemins personnalisés vers FFmpeg/FFprobe.
- [ ] Langue OCR par défaut.
- [ ] Préférences de nommage.
- [ ] Paramètres persistants.
- [ ] Gestion des dépendances externes manquantes.
- [ ] Messages d'erreur compréhensibles.
- [ ] Interface cohérente et responsive.
- [ ] Icône et identité visuelle SubForge.
- [ ] README utilisateur.

---

## Phase 12 — Build Windows / V1

- [ ] Tests sur Windows 10.
- [ ] Vérifier le comportement sur des MKV 1080p et 2160p.
- [ ] Tester des lots importants.
- [ ] Vérifier PGS, SRT, ASS/SSA et VobSub.
- [ ] Vérifier les fichiers avec tags de langue incomplets.
- [ ] Vérifier Forced/Default.
- [ ] Build Windows.
- [ ] Tester l'application hors environnement de développement.
- [ ] Documenter l'installation et les dépendances.
- [ ] Tag/release V1.

---

## Principes du projet

- Ne jamais réencoder la vidéo ou l'audio pour extraire des sous-titres.
- FFprobe sert à l'analyse ; FFmpeg sert principalement à l'extraction/conversion adaptée.
- Les traitements lourds ne doivent jamais bloquer l'interface Flet.
- Les données d'analyse doivent rester indépendantes de l'UI.
- Le traitement par lot doit être prévu dès l'architecture initiale.
- Ne pas modifier les versions de Flet, Flutter ou Python sans décision explicite.
- Privilégier des services testables indépendamment de l'interface.
- Avancer phase par phase et garder `main` fonctionnelle.

---

## Environnement initial

- Windows 10 AMD64
- Flet 1.0.1
- Flutter 3.44.8
- Python 3.10.11
- Repository : Drenae/SubForge
