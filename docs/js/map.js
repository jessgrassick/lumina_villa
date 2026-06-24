/**
 * LuminaMap — Custom illustrated neighbourhood map
 * Lumina Villa Bali / Location page component
 *
 * Usage:
 *   LuminaMap.init('container-id')
 *
 * No external dependencies. Pure vanilla JS + SVG.
 */

(function (global) {
  'use strict';

  // ─── Brand tokens ────────────────────────────────────────────────────────────
  const T = {
    ink:      '#13162B',
    ink2:     '#1B2040',
    ink3:     '#252B4E',
    gold:     '#C9A227',
    goldSoft: '#DFC472',
    bone:     '#F7F3EA',
    text:     '#2B2A2E',
    textSoft: '#5C5A60',
  };

  // ─── Category definitions ─────────────────────────────────────────────────
  const CATEGORIES = [
    { id: 'villa',     label: 'Lumina Villa', color: T.gold,      icon: 'villa'     },
    { id: 'beach',     label: 'Beaches',      color: '#4BA3C7',   icon: 'beach'     },
    { id: 'surf',      label: 'Surf',         color: '#2BBFAD',   icon: 'surf'      },
    { id: 'food',      label: 'Food & Cafes', color: '#E07B39',   icon: 'food'      },
    { id: 'yoga',      label: 'Yoga',         color: '#9B6FBE',   icon: 'yoga'      },
    { id: 'nightlife', label: 'Nightlife',    color: '#D4557A',   icon: 'nightlife' },
    { id: 'temple',    label: 'Temples',      color: T.gold,      icon: 'temple'    },
    { id: 'transport', label: 'Transport',    color: '#8A8FA8',   icon: 'transport' },
  ];

  // ─── Points of interest ───────────────────────────────────────────────────
  // x / y are percentages (0–100) within the map container
  // Orientation: North = top, West = left
  // Villa sits at roughly centre-north; beaches sweep south/southwest; Tanah Lot far west
  const POIS = [
    {
      id:       'lumina',
      category: 'villa',
      name:     'Lumina Villa',
      x:        52, y: 28,
      distance: 'Your home base',
      desc:     'Babakan Kubu — the quiet rice field edge of Canggu. Mornings are still.',
      isPrimary: true,
    },
    // Beaches
    {
      id:       'echo-beach',
      category: 'beach',
      name:     'Echo Beach',
      x:        22, y: 52,
      distance: '8 min by scooter',
      desc:     'The most local-feeling beach in Canggu. Good warungs right on the sand.',
    },
    {
      id:       'berawa',
      category: 'beach',
      name:     'Berawa Beach',
      x:        34, y: 63,
      distance: '5 min by scooter',
      desc:     'More sheltered, beginner-friendly shore. Finns and Mrs Sippy nearby.',
    },
    {
      id:       'batu-bolong',
      category: 'beach',
      name:     'Batu Bolong Beach',
      x:        53, y: 73,
      distance: '10 min by scooter',
      desc:     'The heart of Canggu surf culture. Lively beach scene and strong break.',
    },
    // Surf
    {
      id:       'echo-surf',
      category: 'surf',
      name:     'Echo Beach Surf',
      x:        17, y: 57,
      distance: '8 min by scooter',
      desc:     'Right-hander over reef. Best for experienced surfers. Board hire on the beach.',
    },
    {
      id:       'berawa-surf',
      category: 'surf',
      name:     'Berawa Surf (Beginners)',
      x:        30, y: 69,
      distance: '5 min by scooter',
      desc:     'Slower, more forgiving break. Surf schools run daily lessons here.',
    },
    // Food
    {
      id:       'brunch-cafes',
      category: 'food',
      name:     'Brunch Cafes',
      x:        62, y: 58,
      distance: '8–10 min by scooter',
      desc:     'Machinery, Nude, Crate — Canggu has more good brunch spots per block than anywhere in SE Asia.',
    },
    {
      id:       'warungs',
      category: 'food',
      name:     'Local Warungs',
      x:        48, y: 44,
      distance: '2 min by scooter',
      desc:     'Nasi goreng, mie goreng, fresh juice — 30,000 IDR and always good. The real Bali.',
    },
    {
      id:       'fine-dining',
      category: 'food',
      name:     'Fine Dining Strip',
      x:        58, y: 66,
      distance: '10 min by scooter',
      desc:     'Nook, Watercress, Betelnut — proper restaurant dining without going into Seminyak.',
    },
    // Yoga
    {
      id:       'the-practice',
      category: 'yoga',
      name:     'The Practice',
      x:        70, y: 48,
      distance: '10 min by scooter',
      desc:     'Canggu\'s most well-known studio. Multiple yoga, breathwork and meditation classes daily.',
    },
    {
      id:       'samadi',
      category: 'yoga',
      name:     'Samadi',
      x:        64, y: 42,
      distance: '8 min by scooter',
      desc:     'Yoga centre and Sunday organic market. A Canggu institution.',
    },
    {
      id:       'desa-seni',
      category: 'yoga',
      name:     'Desa Seni',
      x:        38, y: 40,
      distance: '5 min by scooter',
      desc:     'Village of restored Javanese houses. Classes in an extraordinary traditional setting.',
    },
    // Nightlife
    {
      id:       'old-mans',
      category: 'nightlife',
      name:     "Old Man's",
      x:        56, y: 78,
      distance: '10 min by scooter',
      desc:     'The quintessential Canggu beach bar. Cold Bintang, beach sunsets, easy crowd.',
    },
    {
      id:       'finns',
      category: 'nightlife',
      name:     "Finns Beach Club",
      x:        29, y: 60,
      distance: '6 min by scooter',
      desc:     'Berawa\'s flagship beach club. Full nights, pool, DJ — and you come home to quiet.',
    },
    {
      id:       'la-brisa',
      category: 'nightlife',
      name:     'La Brisa',
      x:        20, y: 63,
      distance: '8 min by scooter',
      desc:     'The most beautiful beach bar in Canggu. Driftwood structure, sundowners, live music.',
    },
    // Temples
    {
      id:       'tanah-lot',
      category: 'temple',
      name:     'Tanah Lot',
      x:        6, y: 42,
      distance: '20 min by scooter',
      desc:     'The most dramatic sea temple in Bali. Go at sunset — it is genuinely spectacular.',
      badge:    '20 min',
    },
    // Transport
    {
      id:       'airport',
      category: 'transport',
      name:     'Ngurah Rai Airport',
      x:        84, y: 88,
      distance: '45 min by car',
      desc:     'Complimentary airport transfer included with every booking. Share your flight details with the concierge.',
      badge:    '45 min',
      isOffMap: true,
    },
  ];

  // ─── SVG icon paths ───────────────────────────────────────────────────────
  function getIconPath(type, size) {
    const s = size || 14;
    const h = s / 2;
    switch (type) {
      case 'villa':
        return `<path d="M${h} 2 L${s-2} ${h+1} L${s-2} ${s-2} L2 ${s-2} Z" fill="currentColor" opacity="0.9"/>
                <rect x="${h-1.5}" y="${h}" width="3" height="${h-2}" fill="${T.ink}" opacity="0.7"/>`;
      case 'beach':
        return `<circle cx="${h}" cy="${h}" r="${h-2}" fill="currentColor" opacity="0.9"/>
                <path d="M${h-3} ${h+1} Q${h} ${h-3} ${h+3} ${h+1}" stroke="${T.ink}" stroke-width="1.2" fill="none" opacity="0.6"/>`;
      case 'surf':
        return `<ellipse cx="${h}" cy="${h}" rx="${h-2}" ry="${h-3}" fill="currentColor" opacity="0.9" transform="rotate(-30,${h},${h})"/>`;
      case 'food':
        return `<path d="M${h-2} 2 L${h-2} ${s-2} M${h+2} 2 L${h+2} ${s-2} M${h} ${h} L${h} ${s-2}" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>`;
      case 'yoga':
        return `<circle cx="${h}" cy="4" r="2" fill="currentColor"/>
                <path d="M${h} 6 L${h-3} 10 M${h} 6 L${h+3} 10 M${h} 6 L${h} 11" stroke="currentColor" stroke-width="1.3" fill="none" stroke-linecap="round"/>`;
      case 'nightlife':
        return `<path d="M4 2 L${s-2} 2 L${s-4} 7 Q${h} ${s-1} 4 7 Z" fill="currentColor" opacity="0.9"/>`;
      case 'temple':
        return `<path d="M${h} 2 L${s-2} 8 L${s-3} ${s-2} L3 ${s-2} L3 8 Z" fill="currentColor" opacity="0.9"/>
                <rect x="${h-1}" y="3" width="2" height="4" fill="${T.ink}" opacity="0.5"/>`;
      case 'transport':
        return `<rect x="2" y="${h-1}" width="${s-4}" height="${h+1}" rx="2" fill="currentColor" opacity="0.85"/>
                <circle cx="5" cy="${s-3}" r="1.5" fill="${T.ink}" opacity="0.7"/>
                <circle cx="${s-5}" cy="${s-3}" r="1.5" fill="${T.ink}" opacity="0.7"/>`;
      default:
        return `<circle cx="${h}" cy="${h}" r="${h-2}" fill="currentColor"/>`;
    }
  }

  // ─── Render map terrain SVG background ───────────────────────────────────
  function buildTerrainSVG(w, h) {
    // Painterly rice-field + coastline backdrop
    return `
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 800 500" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <defs>
    <radialGradient id="lm-sky" cx="55%" cy="30%" r="70%">
      <stop offset="0%"   stop-color="#1e2547"/>
      <stop offset="100%" stop-color="#0d1020"/>
    </radialGradient>
    <radialGradient id="lm-glow" cx="52%" cy="28%" r="18%">
      <stop offset="0%"   stop-color="${T.gold}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="${T.gold}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="lm-sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#1a3a5c"/>
      <stop offset="100%" stop-color="#0e2035"/>
    </linearGradient>
    <linearGradient id="lm-land-n" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#1a2a1a"/>
      <stop offset="100%" stop-color="#1c2e1c"/>
    </linearGradient>
    <linearGradient id="lm-land-s" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#1c2e1c"/>
      <stop offset="100%" stop-color="#162414"/>
    </linearGradient>
    <filter id="lm-blur-sm">
      <feGaussianBlur stdDeviation="1.5"/>
    </filter>
    <filter id="lm-blur-md">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
    <pattern id="lm-rice" x="0" y="0" width="28" height="20" patternUnits="userSpaceOnUse" patternTransform="rotate(8)">
      <line x1="0" y1="10" x2="28" y2="10" stroke="#2a4a2a" stroke-width="0.6" opacity="0.55"/>
      <line x1="0" y1="0"  x2="28" y2="0"  stroke="#2a4a2a" stroke-width="0.6" opacity="0.35"/>
    </pattern>
    <pattern id="lm-rice2" x="0" y="0" width="22" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(-5)">
      <line x1="0" y1="8"  x2="22" y2="8"  stroke="#334433" stroke-width="0.7" opacity="0.5"/>
    </pattern>
    <clipPath id="lm-clip">
      <rect width="800" height="500"/>
    </clipPath>
  </defs>

  <g clip-path="url(#lm-clip)">
    <!-- Base sky/ocean -->
    <rect width="800" height="500" fill="url(#lm-sky)"/>

    <!-- Ocean (south/southwest — bottom-left quadrant) -->
    <path d="M0 320 Q80 310 160 330 Q220 345 280 360 Q360 380 440 400 Q520 418 620 430 Q700 440 800 450 L800 500 L0 500 Z"
          fill="url(#lm-sea)" opacity="0.95"/>

    <!-- Ocean shimmer lines -->
    <path d="M10 370 Q100 365 180 378" stroke="#2a5580" stroke-width="1" fill="none" opacity="0.4" filter="url(#lm-blur-sm)"/>
    <path d="M0 390 Q120 382 220 395" stroke="#2a5580" stroke-width="0.8" fill="none" opacity="0.35" filter="url(#lm-blur-sm)"/>
    <path d="M60 410 Q180 403 300 414" stroke="#2a5580" stroke-width="0.8" fill="none" opacity="0.3" filter="url(#lm-blur-sm)"/>

    <!-- Main landmass - north zone -->
    <path d="M0 0 L800 0 L800 320 Q680 300 580 290 Q460 278 360 285 Q260 292 160 300 Q80 308 0 320 Z"
          fill="url(#lm-land-n)"/>

    <!-- Rice field texture — centre-north (villa area) -->
    <path d="M320 60 Q420 50 520 65 Q580 72 620 90 Q600 160 560 200 Q500 220 420 215 Q360 210 320 195 Q290 175 285 140 Q288 95 320 60 Z"
          fill="url(#lm-rice)" opacity="0.8"/>
    <path d="M320 60 Q420 50 520 65 Q580 72 620 90 Q600 160 560 200 Q500 220 420 215 Q360 210 320 195 Q290 175 285 140 Q288 95 320 60 Z"
          fill="#1d321d" opacity="0.45"/>

    <!-- Rice field sheen -->
    <path d="M350 80 Q430 72 500 84 Q530 90 545 110 Q525 150 490 168 Q445 178 400 175 Q368 170 352 155 Q340 138 342 108 Z"
          fill="#253a25" opacity="0.4"/>

    <!-- Rice terraces west -->
    <path d="M0 120 Q50 100 130 110 Q180 118 220 140 Q200 200 160 230 Q110 250 50 240 Q20 230 0 215 Z"
          fill="url(#lm-rice2)" opacity="0.7"/>
    <path d="M0 120 Q50 100 130 110 Q180 118 220 140 Q200 200 160 230 Q110 250 50 240 Q20 230 0 215 Z"
          fill="#1e301e" opacity="0.5"/>

    <!-- Mid-land — south strip (coastal, busier) -->
    <path d="M0 290 Q100 278 200 285 Q300 290 400 295 Q500 298 600 292 Q680 288 800 282 L800 330 Q680 320 580 316 Q460 312 360 318 Q250 324 150 330 Q80 334 0 330 Z"
          fill="#182818" opacity="0.7"/>

    <!-- Coastal fringe — where beach meets land -->
    <path d="M0 316 Q90 308 180 318 Q270 328 370 330 Q460 332 560 326 Q660 320 780 312 Q790 312 800 313 L800 344 Q680 338 560 344 Q440 350 340 348 Q220 344 120 350 Q60 352 0 348 Z"
          fill="#1a2e1a" opacity="0.6"/>

    <!-- Coastline detail — gentle beach -->
    <path d="M0 340 Q80 334 160 342 Q260 352 380 352 Q480 350 580 344 Q680 338 800 334"
          stroke="#c4a87a" stroke-width="1.2" fill="none" opacity="0.3" filter="url(#lm-blur-sm)"/>
    <path d="M0 348 Q100 342 200 349 Q300 356 420 356 Q520 354 620 348 Q700 344 800 340"
          stroke="#c4a87a" stroke-width="0.8" fill="none" opacity="0.2" filter="url(#lm-blur-sm)"/>

    <!-- Distant western land (Tanah Lot direction) -->
    <path d="M0 180 Q30 160 80 155 Q110 152 130 165 Q150 178 140 210 Q120 240 80 248 Q40 252 0 245 Z"
          fill="#1c301c" opacity="0.6"/>

    <!-- Road network — subtle lines -->
    <!-- Main north-south road -->
    <path d="M520 0 Q515 60 510 140 Q505 220 500 300 Q498 340 496 380"
          stroke="#2a3a2a" stroke-width="2.5" fill="none" opacity="0.5"/>
    <!-- East-west connector -->
    <path d="M100 200 Q200 195 300 198 Q400 200 500 198 Q600 196 720 195"
          stroke="#2a3a2a" stroke-width="2" fill="none" opacity="0.4"/>
    <!-- Coastal road -->
    <path d="M0 305 Q100 298 200 302 Q320 307 440 308 Q560 308 680 302 Q750 298 800 295"
          stroke="#2e3e2e" stroke-width="2" fill="none" opacity="0.45"/>
    <!-- Babakan Kubu lane — slightly lighter, the quiet one -->
    <path d="M460 28 Q458 80 455 140 Q452 180 450 220"
          stroke="#344434" stroke-width="1.5" fill="none" opacity="0.6"/>

    <!-- Villa glow pulse origin -->
    <circle cx="416" cy="140" r="40" fill="url(#lm-glow)"/>

    <!-- Atmospheric haze on horizon -->
    <path d="M0 0 L800 0 L800 40 Q600 50 400 45 Q200 40 0 48 Z"
          fill="#0d1020" opacity="0.3"/>

    <!-- Stars / ambient specks far north -->
    <circle cx="120" cy="18" r="0.8" fill="#DFC472" opacity="0.5"/>
    <circle cx="240" cy="12" r="0.6" fill="#DFC472" opacity="0.4"/>
    <circle cx="360" cy="22" r="0.7" fill="#DFC472" opacity="0.4"/>
    <circle cx="600" cy="14" r="0.8" fill="#DFC472" opacity="0.45"/>
    <circle cx="720" cy="20" r="0.6" fill="#DFC472" opacity="0.35"/>
    <circle cx="680" cy="8"  r="0.5" fill="#fff"    opacity="0.3"/>
    <circle cx="180" cy="9"  r="0.5" fill="#fff"    opacity="0.28"/>
  </g>
</svg>`;
  }

  // ─── Compass rose ─────────────────────────────────────────────────────────
  function buildCompass() {
    return `
<svg class="lm-compass" viewBox="0 0 48 48" width="48" height="48" aria-label="Compass: North is up">
  <circle cx="24" cy="24" r="22" fill="${T.ink2}" stroke="${T.gold}" stroke-width="0.8" opacity="0.85"/>
  <path d="M24 6 L27 20 L24 18 L21 20 Z" fill="${T.gold}"/>
  <path d="M24 42 L21 28 L24 30 L27 28 Z" fill="${T.textSoft}"/>
  <path d="M6 24 L20 21 L18 24 L20 27 Z" fill="${T.textSoft}"/>
  <path d="M42 24 L28 27 L30 24 L28 21 Z" fill="${T.textSoft}"/>
  <circle cx="24" cy="24" r="2.5" fill="${T.gold}" opacity="0.7"/>
  <text x="24" y="11" text-anchor="middle" font-size="5.5" fill="${T.gold}" font-family="Inter,sans-serif" font-weight="700">N</text>
</svg>`;
  }

  // ─── Build scale label ────────────────────────────────────────────────────
  function buildScale() {
    return `<div class="lm-scale" aria-label="Approximate scale">
  <div class="lm-scale__bar"></div>
  <span class="lm-scale__label">~2 km</span>
</div>`;
  }

  // ─── Build filter bar ─────────────────────────────────────────────────────
  function buildFilterBar(activeSet) {
    const filters = CATEGORIES.filter(c => c.id !== 'villa');
    return filters.map(cat => {
      const active = activeSet.has(cat.id) ? 'lm-filter--active' : '';
      return `<button
        class="lm-filter ${active}"
        data-category="${cat.id}"
        style="--cat-color:${cat.color}"
        aria-pressed="${activeSet.has(cat.id)}"
        title="Toggle ${cat.label}"
      >
        <span class="lm-filter__dot"></span>
        <span class="lm-filter__label">${cat.label}</span>
      </button>`;
    }).join('');
  }

  // ─── Build a single pin ───────────────────────────────────────────────────
  function buildPin(poi, catDef) {
    const isPrimary = poi.isPrimary;
    const isOffMap  = poi.isOffMap;
    const size      = isPrimary ? 22 : 14;
    const cls       = [
      'lm-pin',
      `lm-pin--${poi.category}`,
      isPrimary ? 'lm-pin--primary' : '',
      isOffMap  ? 'lm-pin--offmap'  : '',
    ].filter(Boolean).join(' ');

    const badge = poi.badge
      ? `<span class="lm-pin__badge">${poi.badge}</span>`
      : '';

    const label = isPrimary
      ? `<span class="lm-pin__label lm-pin__label--primary">${poi.name}</span>`
      : '';

    return `
<div
  class="${cls}"
  style="left:${poi.x}%;top:${poi.y}%;--cat-color:${catDef.color};--pin-size:${size}px"
  data-poi="${poi.id}"
  role="button"
  tabindex="0"
  aria-label="${poi.name} — ${poi.distance}"
>
  <div class="lm-pin__marker">
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" aria-hidden="true" style="color:${catDef.color}">
      ${getIconPath(catDef.icon, size)}
    </svg>
    ${isPrimary ? `<span class="lm-pin__pulse"></span>` : ''}
  </div>
  ${badge}
  ${label}
</div>`;
  }

  // ─── Build tooltip ────────────────────────────────────────────────────────
  function buildTooltip() {
    return `
<div class="lm-tooltip" id="lm-tooltip" role="tooltip" aria-live="polite" hidden>
  <button class="lm-tooltip__close" aria-label="Close">&times;</button>
  <div class="lm-tooltip__cat">
    <span class="lm-tooltip__cat-dot"></span>
    <span class="lm-tooltip__cat-label"></span>
  </div>
  <h3 class="lm-tooltip__name"></h3>
  <p class="lm-tooltip__distance"></p>
  <p class="lm-tooltip__desc"></p>
</div>`;
  }

  // ─── Stylesheet ───────────────────────────────────────────────────────────
  const CSS = `
/* ── LuminaMap component styles ──────────────────────────── */
.lm-wrap {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
  --ink: ${T.ink};
  --gold: ${T.gold};
  --gold-soft: ${T.goldSoft};
  --bone: ${T.bone};
  --text: ${T.text};
  --text-soft: ${T.textSoft};
}

/* Filter bar */
.lm-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  padding: 0 2px;
}

.lm-filter {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 13px 6px 10px;
  border-radius: 999px;
  border: 1.5px solid rgba(255,255,255,0.1);
  background: rgba(19,22,43,0.75);
  color: rgba(239,233,220,0.65);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: all 0.18s ease;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  user-select: none;
}

.lm-filter:hover {
  border-color: var(--cat-color);
  color: #fff;
  background: rgba(19,22,43,0.9);
}

.lm-filter--active {
  border-color: var(--cat-color);
  background: rgba(19,22,43,0.92);
  color: #fff;
}

.lm-filter__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cat-color);
  flex-shrink: 0;
  transition: transform 0.18s ease;
}

.lm-filter--active .lm-filter__dot {
  box-shadow: 0 0 0 2px rgba(255,255,255,0.15), 0 0 6px var(--cat-color);
}

.lm-filter__label {
  white-space: nowrap;
}

/* Map container */
.lm-map {
  position: relative;
  width: 100%;
  height: 500px;
  border-radius: 16px;
  overflow: hidden;
  background: ${T.ink};
  box-shadow:
    0 24px 64px -20px rgba(10,12,24,0.7),
    0 0 0 1px rgba(201,162,39,0.2);
  cursor: default;
}

.lm-terrain {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.lm-terrain svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

/* Vignette */
.lm-map::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 50%, transparent 55%, rgba(10,12,22,0.55) 100%);
  pointer-events: none;
  z-index: 1;
  border-radius: 16px;
}

/* Heading overlay */
.lm-map-title {
  position: absolute;
  top: 18px;
  left: 22px;
  z-index: 10;
  pointer-events: none;
}

.lm-map-title__eyebrow {
  font-size: 0.62rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: ${T.gold};
  font-weight: 700;
  display: block;
  margin-bottom: 3px;
}

.lm-map-title__heading {
  font-size: 0.88rem;
  font-weight: 600;
  color: rgba(239,233,220,0.85);
  display: block;
}

/* Compass + scale */
.lm-compass {
  position: absolute;
  bottom: 18px;
  right: 18px;
  z-index: 10;
  opacity: 0.8;
  pointer-events: none;
}

.lm-scale {
  position: absolute;
  bottom: 22px;
  left: 22px;
  z-index: 10;
  pointer-events: none;
  display: flex;
  align-items: center;
  gap: 7px;
}

.lm-scale__bar {
  width: 52px;
  height: 3px;
  background: linear-gradient(to right, ${T.gold}, ${T.goldSoft});
  border-radius: 2px;
  opacity: 0.65;
  position: relative;
}

.lm-scale__bar::before,
.lm-scale__bar::after {
  content: '';
  position: absolute;
  top: -3px;
  width: 1.5px;
  height: 9px;
  background: ${T.gold};
  opacity: 0.65;
}

.lm-scale__bar::before { left: 0; }
.lm-scale__bar::after  { right: 0; }

.lm-scale__label {
  font-size: 0.62rem;
  color: rgba(239,233,220,0.55);
  letter-spacing: 0.06em;
}

/* Pins */
.lm-pin {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 5;
  cursor: pointer;
  transition: opacity 0.22s ease, transform 0.18s ease;
}

.lm-pin:focus-visible {
  outline: 2px solid ${T.gold};
  outline-offset: 4px;
  border-radius: 4px;
}

.lm-pin--hidden {
  opacity: 0;
  pointer-events: none;
}

.lm-pin__marker {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--pin-size);
  height: var(--pin-size);
  border-radius: 50%;
  background: rgba(19,22,43,0.82);
  border: 1.5px solid var(--cat-color);
  box-shadow: 0 2px 10px rgba(0,0,0,0.5), 0 0 0 0 var(--cat-color);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
}

.lm-pin--primary .lm-pin__marker {
  width: var(--pin-size);
  height: var(--pin-size);
  border-width: 2px;
  background: rgba(19,22,43,0.9);
  box-shadow:
    0 4px 18px rgba(0,0,0,0.6),
    0 0 0 4px rgba(201,162,39,0.15);
}

.lm-pin:hover .lm-pin__marker,
.lm-pin--active .lm-pin__marker {
  transform: scale(1.25);
  box-shadow:
    0 4px 16px rgba(0,0,0,0.5),
    0 0 0 3px var(--cat-color),
    0 0 16px var(--cat-color);
}

/* Pulse rings on villa pin */
.lm-pin__pulse {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 1.5px solid ${T.gold};
  animation: lm-pulse 2.4s ease-out infinite;
  pointer-events: none;
}

.lm-pin__pulse::after {
  content: '';
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  border: 1px solid ${T.gold};
  animation: lm-pulse 2.4s ease-out 0.8s infinite;
}

@keyframes lm-pulse {
  0%   { opacity: 0.8; transform: scale(0.85); }
  70%  { opacity: 0; transform: scale(1.6); }
  100% { opacity: 0; transform: scale(1.6); }
}

/* Pin badge (distance callout) */
.lm-pin__badge {
  position: absolute;
  top: -9px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--cat-color);
  color: ${T.ink};
  font-size: 0.55rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  padding: 2px 5px;
  border-radius: 4px;
  white-space: nowrap;
  pointer-events: none;
  box-shadow: 0 2px 6px rgba(0,0,0,0.4);
}

/* Pin label (villa only) */
.lm-pin__label {
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: ${T.goldSoft};
  text-shadow: 0 1px 4px rgba(0,0,0,0.9);
  pointer-events: none;
}

/* Off-map indicator arrow */
.lm-pin--offmap .lm-pin__marker::after {
  content: '↗';
  position: absolute;
  top: -2px;
  right: -8px;
  font-size: 9px;
  color: var(--cat-color);
  opacity: 0.8;
}

/* Tooltip */
.lm-tooltip {
  position: absolute;
  z-index: 20;
  min-width: 210px;
  max-width: 260px;
  background: rgba(13,15,28,0.96);
  border: 1px solid rgba(201,162,39,0.35);
  border-radius: 12px;
  padding: 14px 16px;
  pointer-events: auto;
  box-shadow:
    0 16px 40px -8px rgba(0,0,0,0.7),
    0 0 0 1px rgba(201,162,39,0.1);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  animation: lm-tip-in 0.18s ease both;
}

@keyframes lm-tip-in {
  from { opacity: 0; transform: translateY(4px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)  scale(1); }
}

.lm-tooltip__close {
  position: absolute;
  top: 8px;
  right: 10px;
  background: transparent;
  border: none;
  color: rgba(239,233,220,0.4);
  font-size: 1rem;
  cursor: pointer;
  padding: 2px 5px;
  line-height: 1;
  border-radius: 4px;
  transition: color 0.15s, background 0.15s;
}

.lm-tooltip__close:hover {
  color: #fff;
  background: rgba(255,255,255,0.08);
}

.lm-tooltip__cat {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.lm-tooltip__cat-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.lm-tooltip__cat-label {
  font-size: 0.62rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(239,233,220,0.5);
  font-weight: 700;
}

.lm-tooltip__name {
  font-size: 0.92rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 5px;
  line-height: 1.2;
  padding-right: 16px;
}

.lm-tooltip__distance {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  margin: 0 0 7px;
}

.lm-tooltip__desc {
  font-size: 0.74rem;
  color: rgba(239,233,220,0.65);
  line-height: 1.55;
  margin: 0;
}

/* Legend strip at bottom of map */
.lm-legend {
  display: none; /* only shown on very small screens as fallback */
}

/* Responsive */
@media (max-width: 600px) {
  .lm-map { height: 380px; }
  .lm-tooltip { min-width: 180px; max-width: 220px; }
  .lm-filter__label { display: none; }
  .lm-filter { padding: 7px; border-radius: 50%; }
  .lm-filter__dot { width: 10px; height: 10px; }
  .lm-filters { gap: 7px; }
}

@media (max-width: 400px) {
  .lm-map { height: 320px; }
}
`;

  // ─── Inject styles once ───────────────────────────────────────────────────
  let stylesInjected = false;

  function injectStyles() {
    if (stylesInjected) return;
    const style = document.createElement('style');
    style.id = 'lm-styles';
    style.textContent = CSS;
    document.head.appendChild(style);
    stylesInjected = true;
  }

  // ─── Main init function ───────────────────────────────────────────────────
  function init(containerId) {
    injectStyles();

    const host = typeof containerId === 'string'
      ? document.getElementById(containerId)
      : containerId;

    if (!host) {
      console.warn('[LuminaMap] Container not found:', containerId);
      return;
    }

    // All categories active by default (except villa, always shown)
    const activeCategories = new Set(CATEGORIES.map(c => c.id));

    // ── Build HTML ────────────────────────────────────────────────────────
    const catMap = {};
    CATEGORIES.forEach(c => { catMap[c.id] = c; });

    const pinsHTML = POIS.map(poi => buildPin(poi, catMap[poi.category])).join('');

    host.innerHTML = `
<div class="lm-wrap">
  <div class="lm-filters" role="group" aria-label="Filter map by category">
    ${buildFilterBar(activeCategories)}
  </div>
  <div class="lm-map" id="lm-map-canvas" role="region" aria-label="Interactive neighbourhood map — Canggu area">
    <div class="lm-terrain">${buildTerrainSVG()}</div>
    <div class="lm-map-title" aria-hidden="true">
      <span class="lm-map-title__eyebrow">Neighbourhood</span>
      <span class="lm-map-title__heading">Canggu &amp; Surrounds</span>
    </div>
    ${pinsHTML}
    ${buildTooltip()}
    ${buildCompass()}
    ${buildScale()}
  </div>
</div>`;

    // ── State ─────────────────────────────────────────────────────────────
    const mapEl     = host.querySelector('.lm-map');
    const tooltip   = host.querySelector('.lm-tooltip');
    const filterBtns = host.querySelectorAll('.lm-filter');
    let activePinEl = null;
    let currentPoi  = null;

    // ── Tooltip positioning ───────────────────────────────────────────────
    function positionTooltip(pinEl) {
      const mapRect = mapEl.getBoundingClientRect();
      const pinRect = pinEl.getBoundingClientRect();

      const pinCx = pinRect.left + pinRect.width  / 2 - mapRect.left;
      const pinCy = pinRect.top  + pinRect.height / 2 - mapRect.top;

      const tipW = 240;
      const tipH = 140;
      const pad  = 12;

      let left = pinCx + 14;
      let top  = pinCy - tipH / 2;

      // Flip left if too close to right edge
      if (left + tipW + pad > mapRect.width) {
        left = pinCx - tipW - 14;
      }
      // Clamp top
      top = Math.max(pad, Math.min(top, mapRect.height - tipH - pad));
      // Clamp left
      left = Math.max(pad, left);

      tooltip.style.left = left + 'px';
      tooltip.style.top  = top  + 'px';
    }

    // ── Show tooltip ──────────────────────────────────────────────────────
    function showTooltip(poi, pinEl) {
      const cat = catMap[poi.category];

      // Populate
      tooltip.querySelector('.lm-tooltip__cat-dot').style.background  = cat.color;
      tooltip.querySelector('.lm-tooltip__cat-label').textContent      = cat.label;
      tooltip.querySelector('.lm-tooltip__name').textContent           = poi.name;
      tooltip.querySelector('.lm-tooltip__distance').textContent       = poi.distance;
      tooltip.querySelector('.lm-tooltip__distance').style.color       = cat.color;
      tooltip.querySelector('.lm-tooltip__desc').textContent           = poi.desc;

      // Deactivate previous
      if (activePinEl && activePinEl !== pinEl) {
        activePinEl.classList.remove('lm-pin--active');
      }

      pinEl.classList.add('lm-pin--active');
      activePinEl = pinEl;
      currentPoi  = poi;

      tooltip.removeAttribute('hidden');
      positionTooltip(pinEl);
    }

    // ── Hide tooltip ──────────────────────────────────────────────────────
    function hideTooltip() {
      tooltip.setAttribute('hidden', '');
      if (activePinEl) {
        activePinEl.classList.remove('lm-pin--active');
        activePinEl = null;
      }
      currentPoi = null;
    }

    // ── Update pin visibility ─────────────────────────────────────────────
    function updatePinVisibility() {
      host.querySelectorAll('.lm-pin').forEach(pinEl => {
        const poiId = pinEl.dataset.poi;
        const poi   = POIS.find(p => p.id === poiId);
        if (!poi) return;

        const visible = poi.isPrimary || activeCategories.has(poi.category);
        pinEl.classList.toggle('lm-pin--hidden', !visible);

        // If active tooltip's pin was hidden, close it
        if (!visible && activePinEl === pinEl) {
          hideTooltip();
        }
      });
    }

    // ── Pin click / keyboard ──────────────────────────────────────────────
    host.querySelectorAll('.lm-pin').forEach(pinEl => {
      function activate(e) {
        e.stopPropagation();
        const poiId = pinEl.dataset.poi;
        const poi   = POIS.find(p => p.id === poiId);
        if (!poi) return;

        if (activePinEl === pinEl) {
          hideTooltip();
        } else {
          showTooltip(poi, pinEl);
        }
      }

      pinEl.addEventListener('click', activate);
      pinEl.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          activate(e);
        }
        if (e.key === 'Escape') hideTooltip();
      });
    });

    // ── Close tooltip on map background click ─────────────────────────────
    mapEl.addEventListener('click', e => {
      if (!e.target.closest('.lm-pin') && !e.target.closest('.lm-tooltip')) {
        hideTooltip();
      }
    });

    // ── Tooltip close button ──────────────────────────────────────────────
    tooltip.querySelector('.lm-tooltip__close').addEventListener('click', e => {
      e.stopPropagation();
      hideTooltip();
    });

    // ── Escape closes tooltip ─────────────────────────────────────────────
    host.addEventListener('keydown', e => {
      if (e.key === 'Escape') hideTooltip();
    });

    // ── Filter toggles ────────────────────────────────────────────────────
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const cat = btn.dataset.category;
        if (activeCategories.has(cat)) {
          activeCategories.delete(cat);
          btn.classList.remove('lm-filter--active');
          btn.setAttribute('aria-pressed', 'false');
        } else {
          activeCategories.add(cat);
          btn.classList.add('lm-filter--active');
          btn.setAttribute('aria-pressed', 'true');
        }
        updatePinVisibility();
      });
    });

    // ── Reposition tooltip on resize ──────────────────────────────────────
    const ro = new ResizeObserver(() => {
      if (activePinEl && currentPoi) {
        positionTooltip(activePinEl);
      }
    });
    ro.observe(mapEl);

    // Return a small API for external use
    return {
      showPoi: id => {
        const pinEl = host.querySelector(`[data-poi="${id}"]`);
        const poi   = POIS.find(p => p.id === id);
        if (pinEl && poi) showTooltip(poi, pinEl);
      },
      hideTip: hideTooltip,
      destroy: () => {
        ro.disconnect();
        host.innerHTML = '';
      },
    };
  }

  // ─── Public API ───────────────────────────────────────────────────────────
  global.LuminaMap = {
    init,
    POIS,
    CATEGORIES,
  };

}(typeof window !== 'undefined' ? window : this));
