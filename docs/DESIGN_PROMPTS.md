# Design prompts — for Nano Banana 2 and for Claude

Copy-paste prompts for designing Leiko post templates and the artwork that goes
into them. Two tools, two different jobs:

- **Claude** designs and builds the **templates** — layout, type, token slots,
  as HTML/CSS that renders crisply at any size. This is how `leiko_template_v2.html`
  was built, and it is the right tool for anything with text in it.
- **Nano Banana 2** generates **imagery only** — backgrounds, textures, scene
  photography — that sits *behind* those templates. It never sets type and it
  never invents the product.

> **Why this split.** Image models render type badly and invent product details.
> Every card that has ever looked like Leiko was designed as code over real
> product photography. That is the system's strength and §1 protects it.

---

## 1. The three hard rules (read before generating anything)

1. **Never AI-generate the Leiko device, a wrist wearing it, a screen, or a
   reading.** A fake product image misrepresents a health device — that is a
   compliance and trust breach, not a style choice. Product imagery comes from
   real photographs, full stop. The only permitted model involvement is a
   *composite*, where real product photos are attached as reference and the
   model is told to copy them exactly (§4.2).
2. **Never AI-generate medical scenes** — clinics, stethoscopes, doctors,
   patients, hospital rooms — or people presented as clinicians.
3. **The existing three cards are LOCKED.** `masters/blank_1a|1b|1c.png`,
   `leiko_template_v2.html`, the fonts and the colours do not change. Only the
   eleven token slots change, weekly, via `copy/copy_issueN.json`. Everything
   below is for **new formats** the card system does not cover — carousels,
   reel covers, Status frames — not for redesigning what works.

Also standing: cheap-model imagery is banned for published assets. If you are
generating for something that will go out, use the flagship tier
(Nano Banana Pro / Nano Banana 2), never a draft model.

---

## 2. The Leiko design system

Paste this block into any design prompt so the output matches what already
exists. Values are taken from the locked template.

```text
LEIKO DESIGN SYSTEM

Colours (exact):
  Navy    #0A1E3C   primary text, dark panels
  Coral   #FF6B5B   the single accent — one idea per layout, never decoration
  Cream   #F6F1E7   text on navy, warm off-white
  Card background: warm off-white paper, near #F6F1E7, with a soft gradient

Type:
  Archivo — weight 900 for the LEIKO wordmark and big stats; 800 for fact
    headlines. Wordmark is letter-spaced .34em, uppercase.
  Instrument Serif — regular and italic. Used large: the headline serif, the
    italic connective word in a stat ("6 in 10" — "in" is italic serif), and
    the gift headline. This is the brand's warmth.
  Space Grotesk — 400/500/700. Body copy, kickers, labels, the URL.
  Section labels (MYTH / FACT): Archivo 900, letter-spacing .3em, uppercase.

Scale on a 1080x1350 card (multiply by 2 when rendering at 2160x2700):
  Big stat 300px / line-height .8 / letter-spacing -.05em
  Italic connective 170px    Headline serif 78px
  Myth quote (italic serif) 96px    Gift headline 184px / line-height .9
  Fact headline 62px    Body 34px    Kicker 44px    Labels 19-26px

Layout:
  Side margin 72px. Bottom margin 64px. Text blocks max-width ~760px.
  Coral divider rule: 210x12px under a stat.
  Strikethrough on a myth: 7px coral bar, rotated -3deg, sitting on line 2.
  Generous empty space — the product photo occupies the lower-right third and
  must never be crowded by type.

Voice in layout: calm, editorial, confident. Closer to a good magazine than to
an ad. No gradients on text, no drop shadows, no glow, no badge clutter, no
stock-photo gloss.

Sizes:
  Feed card / carousel slide  1080x1350  (render 2x = 2160x2700)
  Vertical (reel cover, WhatsApp Status, TikTok)  1080x1920 (2x = 2160x3840)
  Square (Facebook text post)  1080x1080
```

---

## 3. Prompts for Claude — building templates

### 3.1 A new format template

```text
You are designing a new post template for Leiko, a wrist blood-pressure device
with a real inflating cuff. Positioning: "Blood pressure, measured — not
guessed."

Read docs/COPY_RULES.md and docs/DESIGN_PROMPTS.md §1 before you start, then
match the design system in §2 exactly — the new format must look like it came
from the same studio as leiko_template_v2.html.

FORMAT TO BUILD: [carousel slide | reel cover | WhatsApp Status frame |
Facebook text post]
CANVAS: [1080x1350 | 1080x1920 | 1080x1080], rendered at 2x.
PURPOSE: [e.g. "slide 1 of a 5-slide carousel that busts one myth"]

BUILD IT AS: a single self-contained HTML file with inline CSS, in the same
shape as leiko_template_v2.html — one wrapper div per screen carrying
data-screen-label, {{TOKEN}} placeholders for every piece of text, and
data-slot on each text element. It must render correctly under
generate_v3.py's Playwright screenshot path with no changes to that script.

TOKEN SLOTS: define the fewest that do the job, name them in the existing
style (CAPS_WITH_UNDERSCORES), and state a hard character or line limit for
each. Limits are not suggestions — they are what stops copy from breaking the
layout, and the linter will enforce the ones I ask it to.

IMAGERY: leave a defined region for a real product photograph or a generated
BACKGROUND (never a generated product). Specify the region's position and size
so the photo can be dropped in without reflowing type.

DELIVER:
  1. the HTML file
  2. a token table: slot name, what it is for, hard limit
  3. one filled example using real Leiko copy that obeys COPY_RULES
  4. a note on what to add to leiko_lint.py's LIMITS so the new slots are
     enforced — propose it, do not weaken any existing rule

Do not alter masters/, the existing template, the fonts, or the colours.
```

### 3.2 Reviewing a design before it ships

```text
Review this Leiko layout against docs/DESIGN_PROMPTS.md §2 and
docs/COPY_RULES.md. Check, in order:
  1. Any banned language in the visible copy — regulatory or certification
     terms of any kind, fear language, outcome promises, "smartwatch" or
     "cuffless" used for Leiko, any interpretation of a reading (no "normal",
     no thresholds).
  2. Any AI-generated device, wrist, screen, reading, or medical scene (§1) —
     an automatic fail.
  3. Type: correct families and weights, the coral used once as one idea, no
     shadows or glow, wordmark letter-spacing .34em.
  4. Legibility at thumbnail size — a feed post is judged at 120px wide first.
  5. Whether it looks like the same brand as the three locked cards.
Report each as pass/fail with the specific fix. Do not rewrite the layout.
```

---

## 4. Prompts for Nano Banana 2 — imagery only

Always append the negative block (§4.3).

### 4.1 Background / abstract art (no product, no people — the safe default)

```text
A premium editorial background for a health-brand social post. Warm off-white
paper tone (#F6F1E7) with a soft, barely-there gradient, like light falling
across a studio wall. Subtle organic movement in the lower third — a gentle
blush of soft coral (#FF6B5B) at very low opacity, diffuse, like pigment in
water, never a hard shape. Deep navy (#0A1E3C) reserved for a calm block of
negative space in the [upper|lower] area where type will sit.

Mood: calm, expensive, medical-adjacent but never clinical. Editorial, like a
considered print magazine spread. Enormous empty space — this is a backdrop,
not a picture. Nothing to look at directly.

No text, no letters, no numbers, no logos, no watermarks. No objects. No
people. No devices. No screens. Flat, even lighting. 4K, sharp, no grain.
Aspect ratio [4:5 | 9:16 | 1:1].
```

### 4.2 Product composite — ONLY with real photos attached

Attach 2–4 real Leiko photographs as reference images before running this. The
photos are the product truth; the prompt must never assert a colour, finish, or
material of its own, because the model obeys text over pixels and will drift.

```text
Use the attached photographs as the exact and only source of truth for the
product. Reproduce the device precisely as photographed — same case shape,
same finish, same strap, same proportions, same details. Do not redesign,
restyle, embellish, or "improve" any part of it. Do not change its colour.

Place it into this scene: [e.g. "resting on a warm walnut surface beside a
folded linen cloth, morning light from the left"].

The device screen must be OFF and completely dark — no interface, no numbers,
no glow, no reading of any kind visible. This is mandatory.

Style: warm editorial product photography. Soft natural directional light,
gentle shadow, shallow depth of field. Warm off-white and cream palette
(#F6F1E7), navy and soft coral accents only if they occur naturally in the
props. Generous negative space in the [upper left] third for type.

No text, no logos, no watermarks, no UI. No hands, no wrists, no people.
4K, photographic, sharp.
```

### 4.3 The negative block — append to every image prompt

```text
NEGATIVE / NEVER: any blood-pressure reading, systolic/diastolic numbers, mmHg,
or any screen content whatsoever · any illuminated or active device screen ·
any invented wearable, watch, or medical device not present in the attached
reference photos · wrists, hands, arms, or any person wearing the device ·
doctors, nurses, clinicians, lab coats, stethoscopes, hospitals, clinics,
examination rooms · pill bottles, syringes, medical charts · any text, letters,
numbers, logos, watermarks, badges, seals, certificates, or approval marks ·
distressed or anxious expressions · red alert colours or warning iconography ·
stock-photo gloss, HDR, heavy vignette, lens flare, plastic skin.
```

### 4.4 Scene ideas that are safe and on-brand

Non-product, non-people scenes that carry the brand without touching §1: a
Sunday morning table with two cups and a phone face-down · a market stall at
opening, warm light, no faces · a doorway with keys and a folded newspaper ·
linen and walnut textures · an empty chair by a window with soft morning light.
These illustrate the *feeling* — family, routine, care — while the product
itself always comes from a real photograph.

---

## 5. What happens to the output

Nothing here shortcuts the gates. Whatever a template or an image produces:

1. Copy goes into `copy/copy_issueN.json` and through `python leiko_lint.py`.
2. Render with `python generate_v3.py` (PNG + JPEG, 2160×2700).
3. Send with `python leiko_ingest.py` — it lands as **needs_review** and only
   the founder approves it. Nothing in this repo publishes anything.
4. The website's vision gate independently checks the artwork and hard-blocks
   any regulatory text, any "cuffless" wording, or any visible reading. An
   `image:` prefixed hit means the picture must change — re-writing copy will
   not fix it.

Real photographs from the brand footage drive always beat a generated
background. Use generation for what a photo cannot give you, not as the
default.
