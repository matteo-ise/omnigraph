# BRAND UPDATE v2 — omnigraph

> ⚠️ **WICHTIG — Lies diese Datei sofort und befolge sie. Update vom ersten Brand-Update.**

Diese Datei informiert dich über ein aktualisiertes verbindliches Brand-System. Wesentliche Änderungen seit dem letzten Update:

1. **MacWhisper-Look 1:1** — Dark-Mode-only, reines Schwarz `#000000` als Basis, eine Accent-Farbe (`#007AFF` Apple System Blue)
2. **Electron-First Stack** — Electron + React + TypeScript + Tailwind ist der Default (nicht Swift). Vibe-Coding-freundlich, KI-Codertools am schnellsten damit.
3. **`matteoise-ui-kit` ist Pflicht** — alle Apps importieren das private UI-Kit als Git Submodule. Keine Custom-Komponenten bauen — nur das Kit nutzen.
4. **Electron-Vibrancy ist Pflicht** — `titleBarStyle: 'hiddenInset'`, `vibrancy: 'under-window'`, `nativeTheme.themeSource = 'dark'`

## Was du tun musst

1. **Lies sofort `../BRAND_SYSTEM.md` neu** — Abschnitte §4.2 (Farben), §4.4 (Material), §5.7 (Electron-First), §6 (Architektur), §7 (Repo-Struktur), §11 (Quality Gates) wurden aktualisiert.
2. **Lies `../matteoise-ui-kit/README.md` und `../matteoise-ui-kit/docs/installation.md`** — das ist das UI-Kit das du nutzen musst.

## Deine Aufgaben

### Aufgabe A — UI-Kit einbinden

Wenn deine App eine UI hat (Electron/Web/React), integriere `matteoise-ui-kit`:

```bash
# Im Repo-Root ausführen
git submodule add ../matteoise-ui-kit src/ui-kit
git submodule init && git submodule update
```

In deiner `package.json`:
```json
{
  "dependencies": {
    "matteoise-ui-kit": "file:src/ui-kit"
  }
}
```

In deiner App:
```tsx
import 'matteoise-ui-kit/src/styles/globals.css'
import { AppShell, Button, Card, Sidebar, Toolbar, Modal, Toggle, Input, EmptyState, ProgressIndicator } from 'matteoise-ui-kit'
```

Falls deine App Python/CLI-only ist (omnigraph) — keine UI-Integration nötig, aber das Web-UI (falls geplant) MUSS das Kit nutzen.

### Aufgabe B — Falls Electron, Setup anpassen

Falls deine App Electron nutzt (loomforge), stelle sicher dass `electron/main.ts` (od. deine Main-Datei) diese Optionen hat (Referenz: `../matteoise-ui-kit/electron/main.ts`):

```ts
nativeTheme.themeSource = 'dark'
new BrowserWindow({
  titleBarStyle: 'hiddenInset',
  trafficLightPosition: { x: 12, y: 14 },
  vibrancy: 'under-window',
  visualEffectState: 'active',
  backgroundColor: '#000000',
  webPreferences: {
    contextIsolation: true,
    nodeIntegration: false,
    spellcheck: false,
  },
})
```

### Aufgabe C — Dark-Mode-Only Audit

Prüfe deine UI-Code (falls vorhanden):
- [ ] Keine Light-Mode-Styles, kein Theme-Toggle
- [ ] Hartkodierte Farben ersetzt durch Tailwind-Token aus `matteoise-ui-kit/tailwind.config.ts` (`bg-bg-base`, `text-text-primary`, `bg-accent`, etc.)
- [ ] SF Pro Font Stack aktiv (`-apple-system, 'SF Pro Display', 'Inter', system-ui`)
- [ ] 8pt Grid Spacing
- [ ] Apple-Easing Animations

### Aufgabe D — Brand-Alignment-Audit in PROGRESS.md

Trage in `PROGRESS.md` unter einer neuen Sektion `## Brand-Alignment-Audit v2` ein:
- Welche der Aufgaben A/B/C hast du ausgeführt?
- Was fehlt (TODO)?
- Welche Blockers (z.B. "Python-CLI-App hat keine UI, UI-Kit nicht anwendbar")?

## Kritische Regeln

- **Breche NIE Funktionalität für Brand-Alignment.** Wenn eine Korrektur Tests/Build bricht → Self-Healing (3 Fix-Versuche), dann `blocked: brand-alignment-v2-conflict` in `PROGRESS.md` und weiter.
- **Keine neuen externen Abhängigkeiten** außer `matteoise-ui-kit` und den in dessen `package.json` deklarierten Peer-Deps (electron, react, framer-motion, lucide-react).
- **Keine Code-Logik-Änderungen** für Brand-Alignment außer UI-Styling. Falls Code-Refactor nötig → TODO in `PROGRESS.md` und weiter.
- **`matteoise-ui-kit` ist privat** — nicht in öffentlichen Commits/Repos exponieren (als Submodule eingebunden ist OK, da es nur kompiliert in Builds landet).

## Repo-Übersicht (für Cross-Promotion-Footer)

Alle Matteo-Apps:
- **voicemeet** — `https://github.com/matteo-ise/voicemeet` — Lokale Meeting-Notizen mit KI
- **omnigraph** — `https://github.com/matteo-ise/omnigraph` — Knowledge Graph über deinen Mac
- **loomforge** — `https://github.com/matteo-ise/loomforge` — Open-Source-Loom-Alternative
- **omnilingo** — `https://github.com/matteo-ise/omnilingo` — Lokales DeepL + Grammarly

Verwende diese Links im Cross-Promotion-Footer deiner README (außer dem eigenen Repo).

## Skill-Hinweise

- `liquid-glass-design` — falls macOS 26 Liquid Glass Features integrate
- `coding-standards` — TypeScript/React-Konventionen
- `verification-loop` — nach jeder Korrektur prüfen
- `agentic-engineering` — generelle autonome Arbeitsmuster

Los. Lies `../BRAND_SYSTEM.md` neu, lies `../matteoise-ui-kit/README.md`, führe Aufgaben A-D aus, trage Ergebnisse in `PROGRESS.md` ein, fahre dann mit deiner Blueprint-Phase fort.
