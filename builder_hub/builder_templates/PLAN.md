# Template Library Plan

Design briefs for the industry-organized template library. This doc is the source of truth for
what gets built; it is not consumed by code. Each brief below is authored first, then turned into
a real fixture group in this directory (same pipeline as `lull`, `keys`, `verge`).

Rules that apply to every template:

- Each template is a `template_group` of 3-4 pages: home, products/services, about, contact
  (page names adapt to the business, e.g. "menu" is the products page of a restaurant).
- Each template must own a distinct **structural archetype**: nav shape, hero shape, section
  shapes and footer must differ from every other shipped group. Distinct fonts and palettes are
  not enough. See the archetype registry below.
- Palette is 5-7 named `Builder Variable` colors with light + dark hex values. Dark-first
  templates set `dark_value: None` and `color-scheme: dark` in group CSS (the `verge` pattern).
- Fonts come from Google Fonts. Italics need a CSS `@import ...:ital@0;1` client script,
  the built-in font loader only carries `wght`.
- Imagery hotlinks `images.unsplash.com` (established pattern across groups).
- Codenames are unique single words. Taken: commit, field, fronds, husk, keys, lull, mono, nook,
  quill, verge, verso. Retired, do not reuse: forge, grain, copper, ware, beacon, signal.

## Archetype registry (shipped groups)

| Group  | Archetype |
|--------|-----------|
| fronds | earthy starter, standard hero + sections |
| mono   | dark oversized-type portfolio |
| verso  | ultra minimal fixed sidebar |
| husk   | warm centered single column |
| quill  | clean editorial blog, article layouts |
| commit | vivid conference: countdown, speaker grid, tickets |
| lull   | arch photo hero + circle rows, weekly schedule |
| nook   | full-viewport overlay chapters |
| keys   | fixed-sidebar app shell, listings as rows |
| field  | newspaper three-column front page, drop caps |
| verge  | dark type-over-photo, rotated posters, tour list |

| hem    | hairline viewport frame, corner nav, numbered ledger rows |
| silk   | dark mirrored 50/50 splits, stacked monogram nav, numeral collection |
| tulle  | layered offset tissue panels, script overlays, pill nav, RSVP card footer |
| denim  | bordered cells, marquee tickers, rotated stickers, checkerboard grid |
| pleat  | magazine spreads with folio bars, paired portrait+detail images, colophon |

New briefs must claim an archetype not on this list, and the list grows as templates ship.

## Category matrix

Industry categories replace the current gallery taxonomy (Marketing / Editorial / Portfolio /
Local business). Existing groups get re-tagged into these when the first new template ships.
Five template slots per category, each with a different theme.

### Education (trustworthy blues and greens, friendly)
| Codename | Theme | Concept |
|----------|-------|---------|
| slate    | light | K-12 school, calm blue, term dates and admissions |
| quad     | bright | university department, bold collegiate color blocking |
| crayon   | pastel | preschool / daycare, soft primaries, rounded shapes |
| atlas    | editorial | online academy, course catalog as a syllabus |
| chalk    | dark | exam-prep / coaching institute, chalkboard green-black |

### Fashion (high contrast, editorial, photo-led) — BUILT Jul 2026, orders 13-17
| Codename | Theme | Concept |
|----------|-------|---------|
| hem      | minimal | atelier / tailor, white space, hairline type (built: 3 pages) |
| silk     | dark | evening-wear label, black with champagne accents (built: 4 pages) |
| tulle    | pastel | bridal boutique, blush and ivory (built: 3 pages) |
| denim    | bright | streetwear drop site, saturated color, big product tiles (built: 4 pages) |
| pleat    | editorial | seasonal lookbook, magazine spreads (built: 3 pages) |

### Food & Beverage (warm ambers, creams, deep reds)
| Codename | Theme | Concept |
|----------|-------|---------|
| ember    | dark | wood-fire fine dining, charcoal and ember orange (first build, brief below) |
| crumb    | light minimal | artisan bakery, flour white, one warm accent |
| scoop    | bright pastel | gelato café, candy colors, playful shapes |
| graze    | editorial | farm-to-table restaurant, producer stories |
| zest     | sunshine | street-food brand, citrus yellow, bold stickers |

### Manufacturing & Industrial (steel blue, gray, safety-orange accents)
| Codename | Theme | Concept |
|----------|-------|---------|
| girder   | light | steel fabricator, blueprint blues, spec tables |
| lathe    | dark | precision CNC shop, machined gray, tolerance callouts |
| crate    | bright | packaging / logistics, kraft brown and safety orange |
| weld     | bold | metalworks, industrial black-yellow hazard accents |
| gauge    | minimal | engineering consultancy, gray scale, one blue accent |

### Professional Services (navy, slate, restrained accents)
| Codename | Theme | Concept |
|----------|-------|---------|
| ledger   | light | accounting firm, crisp white, forest green accent |
| counsel  | dark | law firm, deep navy, serif authority |
| compass  | bright | management consulting, confident color, case results |
| docket   | editorial | boutique legal practice, document-like layouts |
| mint     | pastel | payroll / HR services, mint and cream, friendly |

### Health & Wellness (sage, soft neutrals, calm)
| Codename | Theme | Concept |
|----------|-------|---------|
| sage     | pastel | day spa, sage green, soft arcs |
| pulse    | bright | fitness studio, energetic red-coral, class grid |
| haven    | light | therapy practice, warm neutrals, gentle type |
| align    | minimal | physiotherapy / chiropractic, clinical white, teal |
| tonic    | dark | strength gym, near-black, electric lime |

### Travel & Hospitality (sky, sand, saturated and photo-forward)
| Codename | Theme | Concept |
|----------|-------|---------|
| drift    | light | travel agency, sky blue, itinerary cards |
| dune     | pastel | desert resort, sand and terracotta |
| fjord    | dark | adventure tour operator, deep teal, expedition log |
| plaza    | bright | city hotel, jewel tones, amenity grid |
| tide     | minimal | coastal B&B, sea glass, quiet type |

### Technology / SaaS (electric accents on dark or clean white)
| Codename | Theme | Concept |
|----------|-------|---------|
| hex      | dark | developer tool, terminal black, syntax-highlight accents |
| orbit    | bright | product landing, gradient accents, feature orbits |
| prism    | light | SaaS marketing site, white with prismatic gradients |
| stack    | minimal | B2B platform, gray scale, integration logos |
| neon     | bold | startup launch, electric violet on off-black |

## Brief schema

Every template gets one YAML brief in this doc before it is built. The fields map 1:1 onto the
fixture pipeline artifacts:

```yaml
codename:      # unique single word, becomes template_group and page-name prefix
category:      # industry category above, goes into template.json categories
title:         # display title, goes into template.json
description:   # one line for template.json
theme:         # light | dark | bright | pastel | minimal | editorial | sunshine | bold
concept: >     # short pitch of the fictional business the template portrays
palette:       # maps to Builder Variable rows (name, value, dark_value)
  - {name: paper, value: "#FFFFFF", dark_value: "#111111"}   # dark-first: dark_value: null
fonts:
  display:     # Google Font for headlines
  body:        # Google Font for copy
archetype: >   # the unique structural skeleton: nav, hero, section shapes, footer
imagery: >     # Unsplash art direction and example search terms
pages:         # 3-4 pages; route "/" is the home page
  - name:      # <codename>_<page>
    route:
    title:
    sections:  # ordered section-by-section outline
```

## Brief: ember (Food & Beverage, dark)

```yaml
codename: ember
category: Food & Beverage
title: Ember
description: A dark wood-fire restaurant with a framed menu card and course strip.
theme: dark
concept: >
  Ember is a 24-seat wood-fired tasting room. Everything is cooked over a single open hearth.
  The site should feel like the room: dim, warm, unhurried. Candlelit photography, generous
  spacing, a single flame-orange accent used sparingly. The primary conversion is a table
  reservation, so hours and the reserve action stay visible on every page.
palette:            # dark-first, dark_value: null on all rows, color-scheme: dark in group CSS
  - {name: char,  value: "#141110", dark_value: null}   # page background, warm charcoal
  - {name: smoke, value: "#201B18", dark_value: null}   # raised surfaces, cards
  - {name: bone,  value: "#EDE4D6", dark_value: null}   # primary text, warm cream
  - {name: ash,   value: "#9E9486", dark_value: null}   # muted text, captions
  - {name: seam,  value: "#382F29", dark_value: null}   # hairlines, borders, menu frame
  - {name: flame, value: "#E2571B", dark_value: null}   # accent: links, reserve CTA, numerals
fonts:
  display: Fraunces        # high-contrast warm serif; italic needs the ital @import script
  body: Figtree
archetype: >
  Printed-menu-card structure. Nav is a hairline top bar with links split left and right of a
  centered wordmark, reserve button far right. Home hero is full viewport, split 60/40: left is
  the stacked oversized serif wordmark over a one-line promise, right is a full-bleed hearth
  photo; a thin rule under the hero carries hours and address as a single running line. Courses
  appear as a horizontal scroll-snap strip with large roman numerals (I, II, III). The menu page
  is a centered menu-card column inside a double hairline frame (seam color), dish left, price
  right. Footer is a full-width reservation banner with an oversized serif line, then a
  three-column info row. No other group uses framed-card sections or a numbered snap strip.
imagery: >
  Moody, low-key, warm-toned Unsplash photography. Open-fire kitchens, plated dishes on dark
  ceramics, candlelit tables, chef hands at the pass. Searches: "wood fired cooking", "fine
  dining dark", "plated dish dark background", "restaurant candlelight interior". Avoid bright
  daylight shots; every image should sit comfortably on the char background.
pages:
  - name: ember_home
    route: /
    title: Ember, wood-fired tasting room
    sections:
      - Hero: split wordmark + hearth photo, reserve button, hours/address rule underneath
      - Tonight at the hearth: three signature dishes as photo cards on smoke surfaces
      - The courses: horizontal snap strip, roman numerals, one line per course
      - Ambiance band: full-width interior photo with a short pull quote in Fraunces italic
      - Reserve banner footer: oversized "Reserve a table", phone, address, hours columns
  - name: ember_menu
    route: /menu
    title: Menu
    sections:
      - Page header: small-caps "Menu", date line, one-line note on sourcing
      - Tasting menu: double hairline framed card, seven numbered courses, price for the set
      - A la carte: two framed columns (hearth / garden), dish name left, price right
      - Wine note: short paragraph on the list, ash-colored, with a flame link to enquire
      - Reserve banner footer (shared component)
  - name: ember_about
    route: /about
    title: About
    sections:
      - Opening statement: full-width serif paragraph on cooking with fire
      - Chef story: portrait photo beside two columns of copy
      - Philosophy row: three short principles (fire, seasons, patience) with roman numerals
      - Team strip: small portraits with name and role captions
      - Reserve banner footer (shared component)
  - name: ember_contact
    route: /contact
    title: Contact
    sections:
      - Reservation block: hours table on smoke surface, phone and email as flame links
      - Find us: address, directions note, landmark photo (no embedded map)
      - Private dining: short paragraph and enquiry mailto CTA
      - Reserve banner footer (shared component)
components: [ember_nav, ember_reserve_footer]
```

## Brief: hem (Fashion, minimal)

```yaml
codename: hem
category: Fashion
title: Hem
description: A minimal atelier site framed by a hairline border, with numbered services.
theme: minimal
concept: >
  Hem is a made-to-measure atelier. Quiet luxury: warm off-whites, one clay accent, huge
  whitespace. The site sits inside a fixed hairline frame, like a garment seam around the
  viewport. Conversion is a fitting appointment.
palette:
  - {name: paper, value: "#FAF9F7", dark_value: "#171512"}
  - {name: ink,   value: "#1C1A17", dark_value: "#EDEAE4"}
  - {name: muted, value: "#8B857C", dark_value: "#948E84"}
  - {name: line,  value: "#E7E3DC", dark_value: "#2B2823"}
  - {name: clay,  value: "#A56B46", dark_value: "#C08D63"}
  - {name: wash,  value: "#F1EEE9", dark_value: "#201D19"}
fonts: {display: Cormorant Garamond, body: Karla}   # italic via @import script
archetype: >
  Hairline viewport frame (fixed inset border on every page). Nav lives inside the frame
  corners: brand top-left, links top-right, no bar. Hero is mostly whitespace: giant lowercase
  serif wordmark anchored bottom-left, one small offset portrait top-right. Sections are
  numbered ledger rows (No. 01 / 02 / 03) with hairline top rules and off-center two-column
  bodies. Footer is a single centered line inside the frame. No other group frames the viewport
  or numbers its sections.
imagery: >
  Tailoring close-ups, fabric bolts, pinned muslin, quiet studio corners. Warm light, muted
  tones. Searches: "tailor atelier", "fabric texture", "sewing studio", "minimal clothing rail".
pages:
  - {name: hem_home, route: /, sections: [corner nav + framed whitespace hero, numbered craft rows (cut, cloth, finish), single large studio image band, appointment line footer]}
  - {name: hem_services, route: /services, sections: [page header with No. index, made-to-measure / alterations / wardrobe edit as ledger rows with prices, process timeline as numbered hairline list, appointment line footer]}
  - {name: hem_studio, route: /studio, sections: [about the cutter (portrait + two-column story), studio images pair, visit block (hours, address, fitting appointment mailto), footer]}
components: [hem_frame_nav, hem_footer_line]
```

## Brief: silk (Fashion, dark)

```yaml
codename: silk
category: Fashion
title: Silk
description: A dark evening-wear house with mirrored splits and a champagne hairline.
theme: dark
concept: >
  Silk is an evening-wear label: bias-cut gowns, black-tie tailoring. Near-black pages, ivory
  type, one champagne accent. Composed, symmetrical, slow. Conversion is a private appointment.
palette:            # dark-first, dark_value: null, color-scheme: dark
  - {name: noir,      value: "#0D0B09", dark_value: null}
  - {name: onyx,      value: "#171310", dark_value: null}
  - {name: ivory,     value: "#F2EBDD", dark_value: null}
  - {name: fog,       value: "#A2937D", dark_value: null}
  - {name: seam,      value: "#2E2820", dark_value: null}
  - {name: champagne, value: "#C9A15E", dark_value: null}
fonts: {display: Italiana, body: Jost}
archetype: >
  Mirrored 50/50 splits. Nav is centered and stacked: monogram above a letterspaced links row,
  hairline below. Every section is a half/half split that alternates image side, divided by a
  champagne hairline down the center. Collection pieces are tall runway-crop images with roman
  numeral captions. Footer is a centered monogram over a small-caps address line. No other
  group is built from alternating center-ruled splits.
imagery: >
  Evening gowns, black tailoring, low-key editorial portraits. Deep shadows, warm highlights.
  Searches: "evening gown dark", "black dress editorial", "suit low key portrait".
pages:
  - {name: silk_home, route: /, sections: [stacked monogram nav, split hero (gown photo / house statement), three mirrored feature splits (gowns, tailoring, appointments), champagne pull-quote, monogram footer]}
  - {name: silk_collection, route: /collection, sections: [collection header with season line, runway-crop pieces as alternating splits with numerals and fabric notes, price-on-request note, monogram footer]}
  - {name: silk_house, route: /house, sections: [house story split (portrait / two columns), craft principles as numeral rows, atelier image split, monogram footer]}
  - {name: silk_appointments, route: /appointments, sections: [appointment statement, private fitting details split (hours+address / what to expect), enquiry mailto CTA, monogram footer]}
components: [silk_nav, silk_footer]
```

## Brief: tulle (Fashion, pastel)

```yaml
codename: tulle
category: Fashion
title: Tulle
description: A blush bridal boutique with layered tissue panels and script accents.
theme: pastel
concept: >
  Tulle is a bridal boutique. Blush, ivory, rosewood. Soft and layered, like tissue paper in a
  dress box; script italic accents like a handwritten invitation. Conversion is booking a
  try-on appointment.
palette:
  - {name: pearl,    value: "#FCF9F7", dark_value: "#1E1917"}
  - {name: cocoa,    value: "#453A36", dark_value: "#EFE6E1"}
  - {name: blush,    value: "#F6E4DF", dark_value: "#2A211F"}
  - {name: rosewood, value: "#B76E79", dark_value: "#D4939D"}
  - {name: fawn,     value: "#A6968F", dark_value: "#9C8D86"}
  - {name: veil,     value: "#F0E1DB", dark_value: "#322724"}
fonts: {display: Playfair Display, script: Parisienne, body: Mulish}
archetype: >
  Layered tissue panels: sections are overlapping offset rounded panels (blush on pearl,
  shifted up into the previous section) with script words floating over corners. Nav is a soft
  pill centered near the top. Hero is a centered invitation: script line, serif headline,
  small-caps date-style subline, one arched-corner photo behind offset panels. Dresses are
  offset alternating cards, each a panel with a script number. Footer is an RSVP card: bordered
  invitation block with centered type. Lull owns arches and circles; tulle owns offset
  overlapping panels and script overlays.
imagery: >
  Wedding dresses, veils, bouquets, soft-focus bridal portraits. Airy, bright, blush-toned.
  Searches: "wedding dress boutique", "bridal veil", "bouquet pastel", "bride soft light".
pages:
  - {name: tulle_home, route: /, sections: [pill nav, invitation hero with layered panels, three signature dress cards (script numbers), kind-words quote panel, RSVP footer card]}
  - {name: tulle_dresses, route: /dresses, sections: [collection header with script accent, offset alternating dress panels (silhouette, fabric, price band), fittings note panel, RSVP footer card]}
  - {name: tulle_visit, route: /visit, sections: [boutique story panel pair (photo + copy), what-to-expect list as soft rows, visit card (hours, address, appointment mailto), RSVP footer card]}
components: [tulle_nav, tulle_rsvp_footer]
```

## Brief: denim (Fashion, bright)

```yaml
codename: denim
category: Fashion
title: Denim
description: A loud streetwear drop site with thick borders, tickers and price stickers.
theme: bright
concept: >
  Denim is a streetwear label that sells in drops. Chalk background, indigo ink, denim blues,
  stitch-orange accents. Everything boxed in thick 2px borders, marquee tickers, rotated price
  stickers. Loud but organized. Conversion is shop-the-drop.
palette:
  - {name: chalk,  value: "#F5F4EF", dark_value: "#12141D"}
  - {name: indigo, value: "#1B2A6B", dark_value: "#E8EBF7"}
  - {name: sky,    value: "#DCE4F7", dark_value: "#1D2440"}
  - {name: cobalt, value: "#3552C8", dark_value: "#7A93E8"}
  - {name: stitch, value: "#FF6A2B", dark_value: "#FF8B55"}
  - {name: slate,  value: "#6B7398", dark_value: "#8A91B0"}
fonts: {display: Archivo Black, body: Space Grotesk}
archetype: >
  Boxed-cell chaos. Nav is a row of bordered cells (each link its own box, cart cell filled
  stitch-orange). A marquee ticker strip runs under the nav and again mid-page. Hero is a giant
  boxed wordmark with a rotated NEW DROP sticker overlapping the corner. Products are a
  checkerboard grid of bordered tiles, alternating photo tiles and sky-filled text tiles, each
  photo tile carrying a rotated price sticker. Footer is stacked oversized outlined link rows.
  No other group uses bordered cells, tickers or sticker rotation.
imagery: >
  Denim stacks, sneakers, tees on racks, streetwear looks. Punchy daylight. Searches: "denim
  jeans stack", "sneakers product", "streetwear look", "clothing rack shop".
pages:
  - {name: denim_home, route: /, sections: [cell nav + ticker, boxed wordmark hero with sticker, drop 04 checkerboard (6 tiles), fit guide split boxes, mailing-list bar, stacked-links footer]}
  - {name: denim_drops, route: /drops, sections: [drops header cells (04 live / 03 archive), full product checkerboard with price stickers, sizing table box, stacked-links footer]}
  - {name: denim_story, route: /story, sections: [boxed manifesto in oversized caps, factory photo strip with captions cells, timeline as ticker rows, stacked-links footer]}
  - {name: denim_stockists, route: /stockists, sections: [stockists header, city list as bordered ledger rows, wholesale enquiry box with mailto, stacked-links footer]}
components: [denim_nav, denim_footer]
```

## Brief: pleat (Fashion, editorial)

```yaml
codename: pleat
category: Fashion
title: Pleat
description: An editorial lookbook shot as magazine spreads with folio bars.
theme: editorial
concept: >
  Pleat is a seasonal lookbook, presented like a fashion magazine issue: folio bar with issue
  and date, numbered looks as full spreads, oversized Bodoni italics, one crimson accent.
  Made for labels that shoot seasonal campaigns. Conversion is a stockist/press enquiry.
palette:
  - {name: page,    value: "#FFFFFF", dark_value: "#131313"}
  - {name: ink,     value: "#101010", dark_value: "#F2F2F2"}
  - {name: stone,   value: "#757068", dark_value: "#A09A92"}
  - {name: rule,    value: "#E2E0DC", dark_value: "#2E2C29"}
  - {name: crimson, value: "#B3202C", dark_value: "#E04654"}
  - {name: cream,   value: "#F5F3EF", dark_value: "#1C1B19"}
fonts: {display: Bodoni Moda, body: Work Sans}   # italic via @import script
archetype: >
  Magazine spreads. Nav is a folio bar: issue number left, brand centered in Bodoni, date
  right, double rule beneath. Home opens as a cover: oversized italic masthead over a cover
  photo with crimson cover lines. Each look is a spread section: folio line (LOOK 01 / 12), a
  portrait image paired with a detail crop, and an oversized italic caption; spreads separated
  by double rules with page numbers. Footer is a colophon block: masthead, credits columns,
  crimson enquiry line. Field owns newspaper columns and quill owns blog lists; pleat owns
  paired-image spreads with folio furniture.
imagery: >
  Editorial fashion portraits with matching detail crops. Studio and street, strong styling.
  Searches: "fashion editorial portrait", "model street style", "fashion detail fabric".
pages:
  - {name: pleat_home, route: /, sections: [folio nav, cover with masthead + cover lines, contents line, looks 01-03 as spreads, crimson subscribe/enquiry band, colophon footer]}
  - {name: pleat_looks, route: /looks, sections: [issue contents header, looks 01-06 as full spreads with credits, stockist note, colophon footer]}
  - {name: pleat_studio, route: /studio, sections: [about the studio spread (portrait + manifesto), services in folio rows (campaign, lookbook, casting), press + contact block with mailto, colophon footer]}
components: [pleat_folio_nav, pleat_colophon]
```

## Follow-ups

- Author the `ember` fixture group from the brief: dev-mode authoring, `sync_builder_templates`,
  preview webp at 2560x1440, mobile audit (scrollWidth scan at 1440/1024/768/390, flexBasis
  check on stacked panes).
- Re-tag the 11 shipped groups' `template.json` categories into the industry taxonomy when the
  first new template ships (fronds/commit/verge -> closest vertical or General, mono/husk/verso
  -> Portfolio stays? decide then).
- Expand briefs category by category after ember validates the schema, one fully detailed brief
  per template before building it.
