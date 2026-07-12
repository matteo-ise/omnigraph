# BRAND UPDATE v3 — omnigraph

> ⚠️ **WICHTIG — Lies diese Datei sofort. Drittes und finales Brand-Update.**

 Wesentliche Änderung seit v2: **Granola.ai CI wurde integriert.** Die Synthese ist nun Granola × MacWhisper — Dark-Mode (MacWhisper-Pflicht) mit Granola's warmen Untertönen, Serif-Typografie, und Granola-Grün als Accent.

## Was sich geändert hat (v2 → v3)

1. **Serif-Typografie Pflicht** — `Fraunces` (display) für Headlines, `Newsreader` (body) für Body-Text. Sans-Serif (SF Pro) nur noch für UI-Controls (Buttons, Tabs, Statusbar). Granola's definierendes CI-Merkmal.
2. **Warm-Dark Palette** — kein pure `#000000` mehr, sondern `#14130F` (warm near-black mit oliv Unterton). Text ist warmes Pergament-Off-White `#F5F2E8` statt purem Weiß. Wie ein ledergebundenes Notizbuch in dimmen Bibliothek.
3. **Granola-Grün als Accent** — `#19C332` ersetzt Apple System Blue `#007AFF`. Das ist die prominenteste Granola-CI-Übernahme.
4. **Granola-Sekundärfarben** — Honig `#FEBC2E` (Warning), Coral `#FF736A` (Danger) statt Apple's kälteren Orange/Red.
5. **Editorial-Modus** — neue `.mk-cream` und `.mk-editorial` Klassen für Notes/Transcript-Panels die sich wie Papier anfühlen.
6. **Lighter Font-Weights** — 500 statt 700 für Headlines (Serif braucht weniger Weight für Impact).

## Was du tun musst

1. **Lies `../matteo-brand/BRAND_SYSTEM.md` neu** — Sektionen §4.1 (Typografie), §4.2 (Farben) wurden komplett überarbeitet.
2. **Lies `../matteo-brand/README.md` neu** + `../matteo-brand/tailwind.config.ts` + `../matteo-brand/src/styles/globals.css` — Palette und Fonts wurden geändert.
3. **Falls du das UI-Kit noch nicht eingebunden hast** — führe Aufgabe A aus v2 aus (`git submodule add ../matteo-brand src/ui-kit`).
4. **Falls du das UI-Kit schon eingebunden hast** — update das Submodule: `git submodule update --remote --merge`

## Deine Aufgaben

### Aufgabe A — Font-Integration

Falls deine App Electron/Web-UI hat:
- `globals.css` importieren (lädt Fraunces + Newsreader via Google Fonts automatisch)
- Headlines → `font-display` Klasse (Fraunces)
- Body-Text/Notes/Transcripts → `font-serif` Klasse (Newsreader) ODER `.mk-editorial` Komponenten-Klasse
- UI-Controls (Buttons, Tabs, Statusbar, Sidebar-Items) → `font-sans` (SF Pro bleibt für kompakte UI)
- Input-Felder → `font-serif` (Granola-Editor-Feel)

### Aufgabe B — Color-Migration

Falls du schon UI-Code mit Farben hast:
- `bg-bg-base` ist jetzt `#14130F` (warm), nicht mehr `#000000`
- `text-text-primary` ist jetzt `#F5F2E8` (warm parchment), nicht mehr `#FAFAFA`
- `bg-accent` ist jetzt `#19C332` (Granola green), nicht mehr `#007AFF`
- `focus:shadow-focus` ist jetzt green-tinted, nicht blue-tinted
- Falls du hartkodierte Hex-Werte hast → ersetze durch Tailwind-Token

### Aufgabe C — Editorial-Akzente

Für Content-Bereiche die sich wie ein Notizbuch/Editor anfühlen sollen (Meeting-Transcripts, Notes, Summaries, Übersetzungen):
- Nutze `.mk-cream` für Cream-Paper-Hintergrund + `.text-ink` für Text → Granola-Editor-Feel
- Oder `.mk-editorial` für serif-body auf dark background

### Aufgabe D — Brand-Alignment-Audit v3 in PROGRESS.md

Trage unter `## Brand-Alignment-Audit v3` ein:
- Welche Aufgaben A-C hast du ausgeführt?
- Welche Fonts sind jetzt aktiv?
- Wo werden Cream/Editorial-Modi genutzt?
- Was fehlt (TODO)?
- Blockers?

## Kritische Regeln

- **Breche NIE Funktionalität für Brand-Alignment.** Self-Healing, dann `blocked: brand-alignment-v3-conflict`.
- **Keine neuen externen Abhängigkeiten** außer matteo-brand und dessen Peer-Deps.
- **Granola-Grün `#19C332` ist die Accent-Farbe** — nicht Apple Blue, nicht eine eigene Wahl.
- **Serif ist Pflicht für Content** — Body-Text in Sans-Serif ist ein Brand-Verstoß.
- **Pure `#000000` ist verboten** — nutze `#14130F` (bg-bg-base).
- **Pure `#FFFFFF` ist verboten** — nutze `#F5F2E8` (text-text-primary).
- **matteo-brand ist privat** — nicht in öffentlichen Commits exponieren.

## Skill-Hinweise

- `liquid-glass-design` — falls macOS 26 Liquid Glass Features
- `design-system` — für Visual-Konsistenz-Auditing
- `coding-standards` — TypeScript/React-Konventionen
- `verification-loop` — nach jeder Korrektur prüfen
- `agentic-engineering` — generelle autonome Arbeitsmuster

## Repo-Übersicht (für Cross-Promotion-Footer)

Alle Matteo-Apps:
- **open-loom** — `https://github.com/matteo-ise/open-loom` — Video aufnehmen + Meetings transkribieren
- **open-lingo** — `https://github.com/matteo-ise/open-lingo` — Lokales DeepL + Grammarly
- **omnigraph** — `https://github.com/matteo-ise/omnigraph` — Knowledge Graph über deinen Mac

Los. Lies `../matteo-brand/PROMPT_INJECTION.md` + `../matteo-brand/BRAND_SYSTEM.md`, update das UI-Kit-Submodule falls nötig, führe Aufgaben A-D aus, trage Ergebnisse in `PROGRESS.md` ein, fahre dann mit deiner Blueprint-Phase fort.
