# omnigraph — Lightweight Start Prompt (Brand-Alignment)

> Für schwächeres Modell: stark angeleitet, eine Aufgabe, klare Dateipfade, keine Architekturentscheidungen.

---

Lies zuerst: `../matteo-brand/PROMPT_INJECTION.md` (Brand-Regeln)
Dann: `AGENTS.md` (Projekt-Kontext)
Dann: `PROGRESS.md` (aktueller Stand — alle 9 Phasen ✅)
Dann: `BLUEPRINT.md` (für Kontext)

**Wichtig:** Omnigraph ist bereits fertig (alle Phasen completed). Du machst nur Brand-Alignment.

---

## Aufgabe: README nach matteo-brand Standard aktualisieren

### Was du tun sollst:

1. **Lies** `README.md` — ist der Brand-Regeln-konforme README? Prüfe gegen `../matteo-brand/BRAND_SYSTEM.md` §8 (README-Standard):

   - [ ] Hero-Screenshot vorhanden? → ja: `assets/screenshot.png` nutzen, nein: `<!-- Screenshot -->` Platzhalter
   - [ ] Privacy-Sektion ("Alles lokal, keine Cloud, keine Telemetrie")?
   - [ ] Vergleichstabelle (omnigraph vs Spotlight vs cbm-mcp)?
   - [ ] Cross-Promotion-Footer?
   - [ ] Badge: Dark-Mode-only, MIT, macOS, Python?

2. **Füge Cross-Promotion-Footer** ans Ende von README.md:

   ```markdown
   ---

   ## Mehr von Matteo Ise

   | Projekt | Beschreibung |
   |---------|-------------|
   | [**OpenLoom**](https://github.com/matteo-ise/open-loom) | Video aufnehmen + Meetings transkribieren |
   | [**OpenLingo**](https://github.com/matteo-ise/open-lingo) | Lokales DeepL + Grammarly |
   | [**Omnigraph**](https://github.com/matteo-ise/omnigraph) | Knowledge Graph über deinen Mac |

   **Alle Apps:** Dark-Mode · Local-first · Privacy-first · Kostenlos · Open Source (MIT)
   ```

3. **Füge Privacy-Sektion** ein (nach Features):

   ```markdown
   ## Privacy

   - **Keine Cloud** — alles läuft lokal auf deinem Mac
   - **Keine Telemetrie** — kein Phone-Home, kein Tracking
   - **Keine API-Keys** — keine Registrierung, keine Accounts
   - **Open Source (MIT)** — du siehst genau was passiert
   ```

4. **Füge Badges** unter den Titel:

   ```markdown
   <p align="center">
     <img src="https://img.shields.io/badge/Dark_Mode-only-14130F?style=flat-square" alt="Dark Mode"/>
     <img src="https://img.shields.io/badge/license-MIT-19C332?style=flat-square" alt="MIT"/>
     <img src="https://img.shields.io/badge/macOS-14%2B-000000?style=flat-square" alt="macOS"/>
     <img src="https://img.shields.io/badge/Python-3.11%2B-14130F?style=flat-square" alt="Python"/>
   </p>
   ```

5. **Prüfe** dass keine alten Namen (voicemeet/loomforge/omnilingo) im README vorkommen

### Brand-Regeln:
- README-Sprache: Deutsch (de-DE)
- KEINE Farben hartkodieren (ausser Badge-HEX in Shields.io URLs)
- Dark-Mode-only nirgends verletzen

### Verification:
- `cat README.md` — sieht gut aus, kein Unsinn
- `ruff check src/ --quiet` — keine Lint-Fehler

### Commite als: `docs: brand alignment — readme nach matteo-brand standard`

### Fallback:
- Bei Unsicherheit: Platzhalter `<!-- TODO -->` einfügen, nicht raten
- `blocked` in PROGRESS.md bei Problemen
- **NICHT** Code-Renaming, NICHT neue Features, NICHT Abhängigkeiten ändern

---

Nach dieser Aufgabe: **STOPP.** Keine weiteren Aufgaben. Aktualisiere `PROGRESS.md` und warte.
