# BRAND UPDATE — omnigraph

> ⚠️ **WICHTIG — Lies diese Datei sofort und befolge sie.**

Diese Datei informiert dich über ein neues verbindliches Brand-System für dieses Repo. Du musst deine weitere Arbeit an diesem Repo anpassen.

## Was passiert ist

Matteo hat ein zentrales Brand-System definiert, das für alle seine Open-Source-Projekte verbindlich ist. Dieses Repo muss dem folgen. Die Master-Datei liegt eine Ebene höher:

**Lies sofort:** `../BRAND_SYSTEM.md`

Diese Datei definiert verbindlich:
- §1 Identity & Mission
- §2 Target Audience (Deutschsprachige End-User + Developer)
- §3 Brand Voice & Tone (freundlich, kompetent, nicht enthusiastisch, Du-Form)
- §4 Visual Design Language (Apple DNA: SF Pro, System Colors, 8pt Grid, NSVisualEffectView)
- §5 UX Principles (Simplicity, Default Works, Privacy als Feature, German UI)
- §6 App-Architecture Patterns (Menubar, Window, Sidecar)
- §7 Repo-Struktur (verbindliche Files)
- §8 README-Standard (Template)
- §9 GitHub Repo Meta (Topics, Description, Avatar)
- §10 Cross-Promotion (Footer mit Verweis auf andere Matteo-Apps)
- §11 Quality Gates (vor jedem Release)
- §12 Naming Conventions
- §13 Was zu tun ist (genau dein Fall)

## Deine Aufgabe

Führe §13 aus:

1. **Audit:** Lese dein aktuelles Repo gegen `BRAND_SYSTEM.md` §7, §8, §11. Liste alle Abweichungen in `PROGRESS.md` unter einer neuen Sektion `## Brand-Alignment-Audit`.
2. **Korrektur-Plan:** Erstelle einen atomaren Korrektur-Plan in `PROGRESS.md`.
3. **Ausführung:** Korrigiere Abweichungen, commite als `chore: align with brand system — <what>` (oder mehrere kleine Commits falls viel zu tun).
4. **Verifikation:** Prüfe erneut gegen §11. Trage Ergebnisse in `PROGRESS.md` ein.
5. **Weiterarbeit:** Fahre mit deiner nächsten Blueprint-Phase fort, aber befolge das Brand-System für alle weiteren Commits.

## Kritische Regeln

- **Breche NIE Funktionalität für Brand-Alignment.** Wenn eine Korrektur Tests/Build bricht → Self-Healing (3 Fix-Versuche), dann `blocked: brand-alignment-conflict` in `PROGRESS.md` und weiter.
- **Keine Code-Logik-Änderungen** für Brand-Alignment. Nur Markdown, Config, YAML, CI-Files. Falls UI-Strings auf Deutsch übersetzt werden müssen oder Code-Änderungen nötig sind → TODO in `PROGRESS.md` markieren und weiter.
- **Keine neuen externen Abhängigkeiten** für Brand-Alignment installieren.
- **Brand-System befolgen** für alle Commits ab jetzt — nicht nur für die Korrektur-Commits.

## Repo-übersicht (für Cross-Promotion-Footer)

Alle Matteo-Apps:
- **voicemeet** — `https://github.com/matteo-ise/voicemeet` — Lokale Meeting-Notizen mit KI
- **omnigraph** — `https://github.com/matteo-ise/omnigraph` — Knowledge Graph über deinen Mac
- **loomforge** — `https://github.com/matteo-ise/loomforge` — Open-Source-Loom-Alternative
- **omnilingo** — `https://github.com/matteo-ise/omnilingo` — Lokales DeepL + Grammarly

Verwende diese Links im Cross-Promotion-Footer deiner README (außer dem eigenen Repo).

## Quick-Check — Was wahrscheinlich fehlt

Gegen `BRAND_SYSTEM.md` §7 prüfen:

- [ ] README.md hat Hero-Screenshot-Sektion (oder Placeholder mit `![Hero-Screenshot](docs/screenshots/hero.png)`)
- [ ] README.md hat Privacy-Sektion ("Läuft vollständig lokal. Keine Daten verlassen dein Gerät. Keine Cloud. Keine Telemetrie.")
- [ ] README.md hat Vergleichstabelle (gegen max. 3 Konkurrenten)
- [ ] README.md hat Cross-Promotion-Footer (siehe oben)
- [ ] README.md hat "Installation für Nicht-Developer" VOR "Build aus Source"
- [ ] CONTRIBUTING.md existiert (kurz, freundlich, auf Deutsch)
- [ ] ROADMAP.md existiert (v1.1, v1.2, v2.0)
- [ ] CHANGELOG.md existiert (Keep a Changelog Format)
- [ ] ATTRIBUTION.md existiert (Fork-Vermerke, genutzte Libs + Lizenzen)
- [ ] CODE_OF_CONDUCT.md existiert (Contributor Covenant 2.1)
- [ ] .github/ISSUE_TEMPLATE/bug-report.md + feature-request.md existieren
- [ ] .github/workflows/ci.yml existiert und läuft
- [ ] .github/PULL_REQUEST_TEMPLATE.md existiert
- [ ] docs/architecture.md existiert (Diagramm + Erklärung)
- [ ] docs/screenshots/ Ordner existiert (Placeholder ok falls App noch nicht fertig)
- [ ] LICENSE ist MIT
- [ ] Keine Emojis in README-Headlines
- [ ] Keine Badge-Suppe oben (max. 3: License, macOS-Version, Build-Status)

Fehlendes → erstellen, Abweichendes → korrigieren, alles als `chore: align with brand system` Commits.

Los. Lies `../BRAND_SYSTEM.md`, führe den Audit aus, korrigiere, commite, trage in `PROGRESS.md` ein, fahre dann mit deiner Blueprint-Phase fort.
