# Nexuli MVP — Complete Build Specification

> Dit document is de enige bron van waarheid voor het bouwen van de Nexuli MVP.
> Lees dit VOLLEDIG aan het begin van elke nieuwe context window.
> Sluit elke fase af met een werkend, testbaar resultaat voordat je de volgende start.

---

## Product Omschrijving

Nexuli is een standalone web app waar gebruikers video's, audio, of tekst kunnen uploaden en een neurowetenschappelijke analyse krijgen van hoe het menselijk brein op die content reageert. Gebaseerd op Meta's TRIBE v2 brain encoding model (720 brains, 20.484 cortical vertices).

**Kernfunctie:** Drop 1 of 2 bestanden → 3D brein visualisatie → per-seconde brain activatie → emoties, aandacht, zwakke/sterke momenten → vergelijking → chat met het brein.

---

## Design Specificaties

### Kleuren
- **Achtergrond:** Puur zwart (#000000) tot diep donker (#0a0a0a)
- **Oppervlakken:** Donkergrijs (#111111, #161616, #1a1a1a)
- **Borders:** Subtiel grijs (#222222, #2a2a2a)
- **Primaire tekst:** Wit (#ffffff, #f5f5f5)
- **Secundaire tekst:** Grijs (#888888, #666666)
- **Vergelijking A (links):** Blauw (#3b82f6, #60a5fa)
- **Vergelijking B (rechts):** Rood (#ef4444, #f87171)
- **Accent/CTA:** Wit op donker, of subtiel blauw
- **Success:** Groen (#22c55e)
- **Warning:** Amber (#f59e0b)
- **Geen neon, geen glow, geen sci-fi. Luxe, clean, minimalistisch.**

### Typografie
- **Headings:** Luxe serif of premium sans-serif (bijv. "Playfair Display" voor groot, "Inter" voor UI)
- **Body:** Inter 400/500
- **Data/numbers:** JetBrains Mono of SF Mono
- **Labels:** Inter 500, 10px, uppercase, letter-spacing 0.5px

### Layout
- Mobile-first responsive (werkt op telefoon)
- Maximale breedte: 1400px gecentreerd
- Veel whitespace
- Dark mode only (geen light mode)

---

## Pagina's & Routes

```
/                   → Landing + upload interface (de hele MVP)
/analysis/[id]      → Resultaat pagina (na scoring)
/login              → Email + password login
/signup             → Email input → auto-generated password → email verzonden
/account            → Account overview, usage, plan
/pricing            → Pro plan €22/mnd
/api/*              → Backend API proxy (naar TRIBE backend)
```

---

## Features Per Prioriteit

### MUST HAVE (MVP launch)
1. Upload 1 of 2 bestanden (video/audio/text, max 90 sec)
2. Processing state: stapsgewijs + grijs brein oplichtend + email optie
3. 3D brain viewer (fsaverage5 pial mesh, per-scan navigatie)
4. Analyse panel (scores, regio's, emoties, aandacht curve, weak/peak moments)
5. Vergelijking panel (als 2 bestanden: blauw vs rood, verdict)
6. Chat met het brein (klik regio → vraag waarom)
7. Auth systeem (email + auto password + account)
8. 2 gratis analyses per week per IP (cookie tracking)
9. Cookie consent banner (verplicht accepteren voor meer dan 2/week)
10. Pro plan €22/mnd via Stripe
11. Rate limiting + usage tracking per account
12. 5 talen (NL, EN, ES, FR, DE) met vlag SVG selector
13. Mobile responsive
14. Database tables voor accounts, analyses, usage

### NICE TO HAVE (na launch)
- "Coming soon: niche insights" pagina voor Pro users
- PWA (installeerbaar als telefoon app)
- Push notifications als analyse klaar is
- Batch upload (meer dan 2 tegelijk)
- Nexuli.ai domein + SSL

### NIET IN MVP
- De 20-tab dashboard van het bestaande systeem
- Lead classification
- Pattern Vault UI
- Competitor monitoring
- Ad generation/launch
- Autonomous loop

---

## Tech Stack

| Laag | Technologie |
|------|-------------|
| Frontend | Next.js 15 + React 19 + TypeScript |
| Styling | Tailwind CSS 4 |
| 3D | React Three Fiber + @react-three/drei + Three.js |
| Auth | Custom (email + bcrypt password hashing) |
| Payments | Stripe Checkout + Webhooks |
| Database | SQLite (accounts, analyses, usage) of PostgreSQL |
| i18n | next-intl of custom JSON-based |
| Backend API | Bestaande FastAPI op port 8100 (TRIBE engine) |
| Hosting frontend | DigitalOcean droplet 159.223.14.239 |
| Hosting backend | Mock data tot Mac Mini aankomt |

---

## Database Schema

### users
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    plan TEXT DEFAULT 'free',          -- 'free' | 'pro'
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    language TEXT DEFAULT 'en',
    cookies_accepted BOOLEAN DEFAULT FALSE,
    created_at REAL DEFAULT (unixepoch()),
    last_login REAL
);
```

### analyses
```sql
CREATE TABLE analyses (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    type TEXT NOT NULL,                 -- 'single' | 'comparison'
    status TEXT DEFAULT 'processing',   -- 'processing' | 'completed' | 'failed'

    -- File A
    file_a_name TEXT,
    file_a_type TEXT,                   -- 'video' | 'audio' | 'text'
    score_a TEXT,                       -- JSON blob van TRIBE result

    -- File B (nullable voor single)
    file_b_name TEXT,
    file_b_type TEXT,
    score_b TEXT,

    -- Comparison result (nullable voor single)
    comparison TEXT,                    -- JSON blob

    -- Chat history
    chat_history TEXT,                  -- JSON array

    created_at REAL DEFAULT (unixepoch()),
    completed_at REAL
);
```

### usage_tracking
```sql
CREATE TABLE usage_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT REFERENCES users(id),
    ip_address TEXT,
    analysis_type TEXT,                 -- 'single' | 'comparison'
    analysis_id TEXT REFERENCES analyses(id),
    created_at REAL DEFAULT (unixepoch())
);
```

### ip_tracking (voor niet-ingelogde gebruikers)
```sql
CREATE TABLE ip_tracking (
    ip_address TEXT NOT NULL,
    week_start TEXT NOT NULL,           -- ISO week "2026-W14"
    analysis_count INTEGER DEFAULT 0,
    PRIMARY KEY (ip_address, week_start)
);
```

---

## Auth Flow

### Signup
```
1. User voert email in
2. Systeem genereert random password (12 chars, letters+numbers)
3. Password wordt gehasht (bcrypt) en opgeslagen
4. Email wordt verzonden met: "Je account is aangemaakt. Je wachtwoord is: [password]"
5. User is automatisch ingelogd na signup
6. JWT token in httpOnly cookie
```

### Login
```
1. User voert email + password in
2. Vergelijk met bcrypt hash
3. JWT token in httpOnly cookie
4. Redirect naar /
```

### Rate Limiting
```
Niet ingelogd:
  - 2 analyses per week per IP
  - Tracked via ip_tracking tabel
  - Na 2: "Maak een gratis account aan voor meer analyses"

Free account:
  - 2 analyses per week
  - Moet cookies accepteren
  - Na 2: "Upgrade naar Pro voor €22/mnd"

Pro account (€22/mnd):
  - 10 single analyses per week
  - 10 comparison analyses per week
  - Opslag van resultaten
  - Chat met brein functie
  - "Coming soon: niche insights"
```

---

## Stripe Integratie

### Setup
- Gebruik bestaande Stripe account
- Product: "Nexuli Pro" — €22/mnd recurring
- Stripe Checkout voor payment flow
- Webhook endpoint: /api/webhooks/stripe
- Events: checkout.session.completed, customer.subscription.deleted

### Flow
```
1. User klikt "Upgrade to Pro"
2. Redirect naar Stripe Checkout (€22/mnd)
3. Na betaling: Stripe webhook → update user.plan = 'pro'
4. User redirect terug naar /account met bevestiging
5. Bij opzegging: webhook → user.plan = 'free'
```

### Test
- Maak een test payment met Stripe test keys
- Verifieer dat webhook user.plan update

---

## i18n (5 Talen)

### Talen
| Code | Taal | Vlag SVG |
|------|------|----------|
| en | English | 🇬🇧 UK vlag |
| nl | Nederlands | 🇳🇱 NL vlag |
| es | Español | 🇪🇸 ES vlag |
| fr | Français | 🇫🇷 FR vlag |
| de | Deutsch | 🇩🇪 DE vlag |

### Implementatie
- JSON bestanden per taal: `messages/en.json`, `messages/nl.json`, etc.
- Taal selector: SVG vlaggen in een dropdown, top-right
- Taal opgeslagen in: cookie + user.language in DB
- ALLE UI tekst vertaald — geen hardcoded strings
- Brein regio namen + emotie labels ook vertaald
- Error messages vertaald

### Structuur
```json
// messages/en.json
{
  "hero": {
    "title": "See how brains respond to your content",
    "subtitle": "Upload a video, audio, or text file. Get a neuroscience-grade analysis in minutes.",
    "dropzone": "Drop your file here or click to upload",
    "analyze": "Analyze",
    "compare": "Compare two files"
  },
  "processing": {
    "step1": "Extracting audio...",
    "step2": "Transcribing speech...",
    "step3": "Analyzing video frames...",
    "step4": "Processing language...",
    "step5": "Fusing modalities...",
    "step6": "Scoring brain regions...",
    "email_prompt": "Leave your email — we'll notify you when it's ready",
    "estimated_time": "Estimated time: {minutes} minutes"
  },
  "brain": {
    "click_region": "Click a region to see what it means",
    "activation": "Activation",
    "hemisphere": "Hemisphere",
    "left": "Left",
    "right": "Right",
    "lobe": "Lobe",
    "function": "Function",
    "emotions": "Emotions triggered",
    "marketing": "Marketing insight"
  },
  "analysis": {
    "overall_score": "Overall Score",
    "hook_score": "Hook Score",
    "attention_curve": "Attention Curve",
    "brain_regions": "Brain Regions",
    "modality_mix": "Modality Mix",
    "weak_moments": "Weak Moments",
    "peak_moments": "Peak Moments",
    "emotions": "Emotions Detected"
  },
  "comparison": {
    "content_a": "Content A",
    "content_b": "Content B",
    "winner": "Winner",
    "verdict": "Verdict",
    "recommendation": "Recommendation",
    "a_wins": "A wins on",
    "b_wins": "B wins on"
  },
  "chat": {
    "placeholder": "Ask about this region... 'Why did this activate?' or 'How do I improve this?'",
    "send": "Ask",
    "intro": "Click a brain region, then ask me about it."
  },
  "auth": {
    "login": "Log in",
    "signup": "Create account",
    "email": "Email address",
    "password": "Password",
    "logout": "Log out",
    "forgot": "Forgot password?",
    "account_created": "Account created! Check your email for your password.",
    "login_failed": "Invalid email or password"
  },
  "pricing": {
    "free": "Free",
    "free_desc": "2 analyses per week",
    "pro": "Pro",
    "pro_price": "€22/month",
    "pro_desc": "10 single + 10 comparison analyses per week",
    "pro_features": [
      "Save analysis results",
      "Chat with brain function",
      "10 single analyses per week",
      "10 comparison analyses per week",
      "Niche insights (coming soon)"
    ],
    "upgrade": "Upgrade to Pro",
    "current_plan": "Current plan"
  },
  "limits": {
    "free_limit": "You've used your 2 free analyses this week",
    "create_account": "Create a free account for more",
    "upgrade_needed": "Upgrade to Pro for more analyses",
    "cookies_required": "Accept cookies to continue using Nexuli"
  },
  "cookie": {
    "title": "We use cookies",
    "description": "Nexuli uses cookies to track usage and improve your experience. Required for accounts.",
    "accept": "Accept all cookies",
    "decline": "Decline (limited to 2 analyses/week)"
  }
}
```

---

## Processing State (Terwijl TRIBE Draait)

### Visueel
```
┌────────────────────────────────────────────┐
│                                            │
│         ┌──────────────────────┐          │
│         │    GRAY 3D BRAIN     │          │
│         │   (slowly lighting   │          │
│         │    up per region)    │          │
│         └──────────────────────┘          │
│                                            │
│  ✓ Extracting audio...              done  │
│  ✓ Transcribing speech...           done  │
│  ● Analyzing video frames...    45%  ███░ │
│  ○ Processing language...       waiting   │
│  ○ Fusing modalities...         waiting   │
│  ○ Scoring brain regions...     waiting   │
│                                            │
│  Estimated time: ~7 minutes                │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ 📧 Get notified when ready           │ │
│  │ [email@example.com] [Notify me]      │ │
│  └──────────────────────────────────────┘ │
│                                            │
└────────────────────────────────────────────┘
```

### Technisch
- Backend stuurt progress via polling (GET /api/analysis/{id}/status)
- Frontend pollt elke 3 seconden
- Elke stap update de UI
- Grijs brein licht op: eerst visual (video klaar), dan auditory (audio klaar), dan language (tekst klaar), dan alles (fusion klaar)
- Email notificatie: opslaan in DB, checken bij completion, versturen via Resend API

---

## 3D Brain Viewer Specificaties

### Mesh
- fsaverage5 pial surface (801 KB .glb)
- 20.484 vertices, 40.960 triangles
- Realistisch, grijs (#555555) base

### Kleuring
- Inactief: grijs (#555555)
- Laag: blauw/paars (#6644ff)
- Midden: oranje/geel (#ffaa00)
- Hoog: hot pink/magenta (#ff44aa)
- Threshold op 0.30 — onder threshold = grijs

### Interactie
- Roteer: muisdrag
- Zoom: scroll
- Hover: tooltip met regio naam + activatie %
- Klik: side panel opent met volledig detail + chat
- Per-scan navigatie: ◀ ▶ knoppen + dots

### Vergelijking
- Content A brain: blauw accent ring/border
- Content B brain: rood accent ring/border
- Naast elkaar op desktop, gestapeld op mobile

---

## Backend API (Wat de Frontend Nodig Heeft)

De bestaande FastAPI backend op port 8100 heeft al de meeste endpoints. De frontend heeft nodig:

```
# Auth
POST /api/auth/signup          → {email} → creates account, returns JWT
POST /api/auth/login           → {email, password} → returns JWT
GET  /api/auth/me              → returns user profile

# Scoring
POST /api/score                → upload file → returns analysis_id
GET  /api/analysis/{id}/status → returns processing progress
GET  /api/analysis/{id}        → returns full results when done

# Usage
GET  /api/usage                → returns usage stats for current user/IP
GET  /api/usage/can-analyze    → returns {allowed: bool, reason: string}

# Stripe
POST /api/stripe/checkout      → creates Stripe checkout session
POST /api/webhooks/stripe      → Stripe webhook handler

# Health
GET  /api/health               → TRIBE model status
```

**NOTE:** Sommige van deze endpoints bestaan al, sommige moeten toegevoegd worden. De auth + usage + stripe endpoints zijn nieuw.

---

## Bestanden Structuur

```
/Users/sven/Desktop/nexuli-mvp/
├── package.json
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── .env.local                          (Stripe keys, Resend key, backend URL)
├── .gitignore
│
├── public/
│   ├── brain/
│   │   ├── fsaverage5_pial.glb        (kopieer van bestaand)
│   │   ├── brain_atlas.json           (kopieer van bestaand)
│   │   └── brain_regions.json         (kopieer van bestaand)
│   └── flags/
│       ├── en.svg
│       ├── nl.svg
│       ├── es.svg
│       ├── fr.svg
│       └── de.svg
│
├── messages/
│   ├── en.json
│   ├── nl.json
│   ├── es.json
│   ├── fr.json
│   └── de.json
│
├── src/
│   ├── app/
│   │   ├── layout.tsx                  (root layout, fonts, dark theme)
│   │   ├── page.tsx                    (landing + upload)
│   │   ├── globals.css                 (Tailwind + custom styles)
│   │   ├── analysis/
│   │   │   └── [id]/
│   │   │       └── page.tsx            (results page)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── signup/
│   │   │   └── page.tsx
│   │   ├── account/
│   │   │   └── page.tsx
│   │   ├── pricing/
│   │   │   └── page.tsx
│   │   └── api/
│   │       ├── auth/
│   │       │   ├── signup/route.ts
│   │       │   ├── login/route.ts
│   │       │   └── me/route.ts
│   │       ├── analyze/route.ts        (proxy naar TRIBE backend)
│   │       ├── analysis/[id]/
│   │       │   ├── status/route.ts
│   │       │   └── route.ts
│   │       ├── usage/
│   │       │   ├── route.ts
│   │       │   └── can-analyze/route.ts
│   │       ├── stripe/
│   │       │   ├── checkout/route.ts
│   │       │   └── webhook/route.ts
│   │       └── health/route.ts
│   │
│   ├── components/
│   │   ├── brain/
│   │   │   ├── BrainViewer.tsx         (3D canvas + side panel + chat)
│   │   │   ├── BrainMesh.tsx           (Three.js mesh + per-vertex coloring)
│   │   │   └── colormap.ts            (gray → blue → yellow → pink)
│   │   ├── upload/
│   │   │   ├── DropZone.tsx            (drag & drop + click upload)
│   │   │   └── FilePreview.tsx         (thumbnail + filename + duration)
│   │   ├── analysis/
│   │   │   ├── AnalysisPanel.tsx       (scores, regions, emotions)
│   │   │   ├── ComparisonPanel.tsx     (blauw vs rood verdict)
│   │   │   ├── AttentionCurve.tsx      (per-second bar chart)
│   │   │   ├── EmotionBars.tsx         (emotie intensiteit bars)
│   │   │   ├── ModalityMix.tsx         (visual/audio/text verdeling)
│   │   │   └── MomentCards.tsx         (weak + peak moment kaarten)
│   │   ├── processing/
│   │   │   ├── ProcessingState.tsx     (stappen + brein oplichtend)
│   │   │   └── EmailNotify.tsx         (email input voor notificatie)
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── SignupForm.tsx
│   │   │   └── AuthGuard.tsx           (wrapper voor pro-only features)
│   │   ├── layout/
│   │   │   ├── Header.tsx              (logo + taal selector + login)
│   │   │   ├── LanguageSelector.tsx    (vlag SVG dropdown)
│   │   │   ├── CookieBanner.tsx
│   │   │   └── Footer.tsx
│   │   └── pricing/
│   │       └── PricingCard.tsx
│   │
│   ├── lib/
│   │   ├── db.ts                       (SQLite/better-sqlite3 wrapper)
│   │   ├── auth.ts                     (JWT + bcrypt helpers)
│   │   ├── stripe.ts                   (Stripe client + helpers)
│   │   ├── i18n.ts                     (taal loading + context)
│   │   ├── usage.ts                    (rate limit checking)
│   │   └── tribe-client.ts            (HTTP client naar TRIBE backend)
│   │
│   └── types/
│       ├── analysis.ts                 (TypeScript types voor TRIBE results)
│       ├── user.ts
│       └── i18n.ts
│
└── scripts/
    └── setup-db.ts                     (create tables script)
```

---

## Bouw Fases

### FASE 1: Fundament
**Wat:** Next.js app + database + auth + i18n infra
**Bouw:**
- Next.js 15 project init met Tailwind
- Database schema (SQLite via better-sqlite3)
- Auth systeem (signup, login, JWT, middleware)
- i18n setup (5 talen JSON, taal context, vlag selector)
- Root layout (donker thema, luxe fonts, header met taal + auth)
- Cookie consent banner
- Basis pagina's (/, /login, /signup, /account, /pricing)

**Test:** Kan ik inloggen, taal switchen, cookie banner zien?
**Sluit context als:** Alle pagina's renderen, auth werkt, i18n switcht tussen 5 talen.

---

### FASE 2: Stripe + Usage Tracking
**Wat:** Betalingen + rate limiting
**Lees eerst:** FASE 1 resultaat + MVP.md
**Bouw:**
- Stripe checkout integratie (€22/mnd Pro plan)
- Stripe webhook handler (subscription created/cancelled)
- Usage tracking (per IP + per account)
- Rate limiting middleware (2/week free, 10+10/week pro)
- /api/usage/can-analyze endpoint
- Pricing pagina met Free vs Pro vergelijking
- "Upgrade to Pro" flow
- Test payment via Stripe test mode

**Test:** Kan ik een test betaling doen, wordt mijn plan geupdate, wordt usage geteld?
**Sluit context als:** Stripe test payment werkt, usage tracking telt correct, rate limits blokkeren na limiet.

---

### FASE 3: Upload + Processing State
**Wat:** File upload + processing UI
**Lees eerst:** FASE 1+2 resultaat + MVP.md
**Bouw:**
- DropZone component (drag & drop, click, file validatie)
- Max 90 seconde check (voor video: lees metadata)
- File upload naar /api/analyze
- Processing state UI:
  - 6 stappen met voortgang
  - Grijs 3D brein dat oplicht per stap
  - Geschatte tijd
  - Email notificatie optie
- Polling naar /api/analysis/{id}/status
- Mock TRIBE responses (backend nog niet live)

**Test:** Kan ik een video droppen, zie ik de processing stappen, krijg ik mock resultaten?
**Sluit context als:** Upload werkt, processing state toont alle stappen, mock resultaat verschijnt na "processing".

---

### FASE 4: 3D Brain Viewer
**Wat:** De echte 3D brain component
**Lees eerst:** FASE 1-3 resultaat + MVP.md + bestaande BrainViewer code
**Bouw:**
- BrainMesh.tsx (kopieer + pas aan van bestaand)
- BrainViewer.tsx (kopieer + pas aan)
- colormap.ts (kopieer)
- Per-scan navigatie (◀ ▶ + dots)
- Klik op regio → side panel met details
- Emotie tags per regio
- Gray base + activation coloring
- Responsive (kleiner op mobile)

**Test:** Draait het 3D brein, kan ik klikken, zie ik regio details?
**Sluit context als:** 3D brein rendert, rotatie/zoom werkt, klik toont regio info, scans navigeerbaar.

---

### FASE 5: Analysis Results Page
**Wat:** Het volledige resultaat scherm
**Lees eerst:** FASE 1-4 resultaat + MVP.md
**Bouw:**
- /analysis/[id]/page.tsx
- Single analyse layout (1 brein + analyse panel)
- Comparison layout (2 breinen + vergelijking)
- AnalysisPanel: overall score, hook score, duration
- AttentionCurve: per-seconde bar chart
- Brain regions: 12 marketing regio's met bars
- ModalityMix: visual/audio/text percentages
- EmotionBars: gedetecteerde emoties met intensiteit
- MomentCards: weak moments (rood) + peak moments (groen)
- Vergelijking: blauw vs rood, wie wint waar, verdict, aanbeveling
- Responsive layout (stack op mobile)

**Test:** Zie ik alle analyse componenten met mock data?
**Sluit context als:** Single + comparison analyse toont alle data correct, responsive werkt.

---

### FASE 6: Chat Met Het Brein
**Wat:** Interactieve chat functie
**Lees eerst:** FASE 1-5 resultaat + MVP.md
**Bouw:**
- Chat panel in de BrainViewer sidebar
- Klik op regio → automatisch context bericht
- User kan vragen stellen: "waarom activeerde dit?", "hoe verbeter ik dit?"
- Mock AI responses gebaseerd op regio metadata (brain_regions.json)
- Chat history opgeslagen in analyses tabel
- Pro-only feature guard (free users zien "Upgrade to chat with the brain")

**Test:** Kan ik klikken, vragen stellen, antwoorden krijgen?
**Sluit context als:** Chat werkt, antwoorden zijn relevant per regio, history wordt opgeslagen.

---

### FASE 7: Vertalingen Compleet
**Wat:** Alle 5 talen volledig vertaald
**Lees eerst:** FASE 1-6 resultaat + MVP.md + en.json
**Bouw:**
- nl.json (Nederlands — volledig)
- es.json (Spaans — volledig)
- fr.json (Frans — volledig)
- de.json (Duits — volledig)
- Alle brein regio namen vertaald
- Alle emotie labels vertaald
- Alle error messages vertaald
- Alle processing stappen vertaald
- Taal detectie op basis van browser (navigator.language)

**Test:** Werkt elke pagina in alle 5 talen zonder missende strings?
**Sluit context als:** Alle talen volledig, geen fallbacks naar Engels zichtbaar.

---

### FASE 8: Polish + Deploy
**Wat:** Final fixes + deployment naar droplet
**Lees eerst:** FASE 1-7 resultaat + MVP.md
**Bouw:**
- Performance optimalisatie (lazy loading, image opt)
- SEO meta tags per taal
- Error boundaries
- 404 pagina
- Loading states overal
- Mobile testing + fixes
- Build: `npm run build` — 0 errors
- Deploy naar droplet 159.223.14.239:
  - PM2 process manager
  - Nginx reverse proxy
  - SSL later (als domein gekocht)
- Connectie naar TRIBE backend (mock tot Mac Mini)

**Test:** Draait het op de droplet? Is het responsive? Geen console errors?
**Sluit context als:** App draait op droplet, alle features werken, mobile werkt.

---

## Bestaande Code Om Te Hergebruiken

Kopieer deze bestanden van het bestaande systeem:

| Van | Naar | Wat |
|-----|------|-----|
| `ai uni v3/src/components/BrainViewer/BrainViewer.tsx` | `nexuli-mvp/src/components/brain/BrainViewer.tsx` | 3D viewer (pas aan) |
| `ai uni v3/src/components/BrainViewer/BrainMesh.tsx` | `nexuli-mvp/src/components/brain/BrainMesh.tsx` | Three.js mesh |
| `ai uni v3/src/components/BrainViewer/colormap.ts` | `nexuli-mvp/src/components/brain/colormap.ts` | Vertex kleuring |
| `ai uni v3/public/brain/*` | `nexuli-mvp/public/brain/*` | GLB + atlas + regions JSON |
| `TRIBE/backend/scoring.py` | Referentie | TypeScript types afleiden |
| `TRIBE/backend/atlas.py` | Referentie | Regio namen + structuur |

---

## Mock Data (Tot Mac Mini Aankomt)

Omdat TRIBE niet draait zonder GPU, moet de frontend werken met mock data.

### Mock Score Result
Genereer realistische mock TRIBE output:
- 20.484 vertex activaties (random met hotspots per regio)
- 60 TRs (30 seconden bij 2Hz)
- Per-seconde scores voor alle 12 regio's
- 2-3 weak moments, 2-3 peak moments
- Modality mix: random maar realistisch (bijv. 35/45/20)
- Overall score: random 40-90

### Mock Processing
- Simuleer 6 stappen met delays (totaal ~15 seconden in dev, echte 5-10 min in productie)
- Stap 1-3: elk 2 seconden
- Stap 4-5: elk 3 seconden
- Stap 6: 2 seconden

---

## Hosting: Droplet 159.223.14.239

### Huidige staat
- Ubuntu 24.04 LTS
- 2 GB RAM / 2 Intel vCPUs / 90 GB Disk
- Locatie: AMS3

### Plan
- Frontend: Next.js app via PM2
- Nginx: reverse proxy op port 80/443
- Geen TRIBE backend hier (geen GPU) — dat draait op Mac Mini of GPU droplet later
- Frontend praat met mock data tot backend beschikbaar is
- SSL: later als nexuli.ai domein gekocht is

### Deploy commando's
```bash
# Op de droplet
git clone https://github.com/TheAIuniversity/nexuli-mvp.git
cd nexuli-mvp
npm install
npm run build
pm2 start npm --name nexuli -- start
```

---

## Instructies Per Context Window

### Begin van elke sessie
1. Lees MVP.md VOLLEDIG
2. Check welke fase je moet bouwen
3. Lees het resultaat van vorige fases (ls de bestanden, check of ze bestaan)
4. Bouw ALLEEN de huidige fase
5. Test aan het einde

### Einde van elke sessie
1. Verifieer dat de fase werkt (build + test)
2. Commit + push naar git
3. Noteer in MVP.md welke fase af is (voeg een ✅ toe)
4. Lijst wat de volgende sessie moet doen

### Regels
- NOOIT de hele app in één sessie bouwen — het is te groot
- NOOIT features van een latere fase toevoegen aan een eerdere
- ALTIJD testen voordat je een fase afsluit
- ALTIJD de bestaande code hergebruiken waar mogelijk
- Mock data is OK — het wordt later vervangen door echte TRIBE output
