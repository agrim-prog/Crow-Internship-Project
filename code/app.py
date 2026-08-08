# Streamlit interface. Calls the same call_and_parse_pipeline function from
# Week 3 - this file doesn't reimplement any extraction logic, it just
# gives it a face.

import os
import sys
import json

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.dirname(__file__))
from call_and_parse import call_and_parse_pipeline, LABELS

st.set_page_config(page_title="Crow Lease Abstractor", page_icon="⌘", layout="wide")

# Hero grid, 1:1 with usecrow.ai: a 50x50 lattice of 50-unit squares
# (viewBox 0 0 2500 2500) scaled to cover the hero via xMidYMid slice.
_GRID_RECTS = "".join(
    '<rect x="%d" y="%d" width="50" height="50"/>' % (x * 50, y * 50)
    for y in range(50)
    for x in range(50)
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Type stack and rendering, 1:1 with usecrow.ai (Inter + antialiasing; the
   smoothing is what keeps weights looking as light as they do on the site). */
html, body, [class*="css"], .stApp,
.stApp p, .stApp li, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp select,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span,
.crow-header, .crow-header span, .eyebrow, h1.headline, .subhead,
.result-card, .field-label, .flag-badge, .missing-text {
    font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
html, body, .stApp {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #0D0D0D;
}

[data-testid="stMainBlockContainer"], .stMainBlockContainer, .block-container {
    max-width: 1180px;
    padding-top: 3rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Let the grid show through Streamlit's own chrome, and keep its fixed
   top header from painting over the Crow bar. */
[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 90;
}
[data-testid="stToolbar"], [data-testid="stStatusWidget"],
[data-testid="stDecoration"], #MainMenu {
    display: none !important;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"], .stMain,
[data-testid="stMainBlockContainer"], .block-container {
    background: transparent !important;
}
.stApp { background: #FFFFFF !important; }

/* Grid lives only in the hero: it is painted by the hero block itself,
   so it ends exactly where the tool section begins. */
[data-testid="stElementContainer"]:has(.skyline-wrap) {
    position: relative;
    z-index: 0;
}
/* Grid, 1:1 with usecrow.ai: an SVG lattice of 50x50 cells stretched to
   cover the hero (xMidYMid slice), hairline strokes at 8% black, dissolving
   radially from the center so the sides and outer edges fade to white. */
.hero-grid {
    position: absolute;
    top: -300px;
    bottom: 0;
    left: calc(50% - 50vw);
    right: calc(50% - 50vw);
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
}
.hero-grid svg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    mask-image: radial-gradient(circle at center, white, transparent 85%);
    -webkit-mask-image: radial-gradient(circle at center, white, transparent 85%);
}
.hero-grid rect {
    fill: transparent;
    stroke: rgba(0, 0, 0, 0.08);
}

/* Skyline: 1:1 with usecrow.ai — two stacked silhouette layers, full-bleed
   and stretched to the viewport width (preserveAspectRatio="none"), with the
   ground dissolve done by masking the whole stack rather than painting white
   over it, so the grid stays visible through the fade. */
.skyline-wrap {
    position: relative;
    width: 100vw;
    margin: 64px 0 0 calc(50% - 50vw);
    pointer-events: none;
    mask-image: linear-gradient(to bottom, #000 0%, #000 65%, transparent 100%);
    -webkit-mask-image: linear-gradient(to bottom, #000 0%, #000 65%, transparent 100%);
}
/* Back layer: hazy distant blocks, pinned to the ground line. */
.skyline-back {
    position: absolute;
    left: 0; right: 0; bottom: 0;
    width: 100%;
    height: clamp(90px, 13vw, 170px);
    display: block;
    color: rgba(15, 15, 15, 0.055);
}
/* Front layer: darker towers, sets the wrapper's height. */
.skyline-front {
    position: relative;
    width: 100%;
    height: clamp(120px, 17vw, 220px);
    display: block;
    color: rgba(15, 15, 15, 0.13);
}

/* Tool section (the one st.columns row): solid white full-bleed band that
   covers the grid, with a faded hairline divider at its top edge. */
[data-testid="stHorizontalBlock"] {
    position: relative;
    z-index: 0;
    margin-top: 28px;
    padding: 64px 0 72px 0;
}
[data-testid="stHorizontalBlock"]::before {
    content: "";
    position: absolute;
    top: 0; bottom: 0;
    left: calc(50% - 50vw);
    right: calc(50% - 50vw);
    background: #FFFFFF;
    z-index: -1;
}
[data-testid="stHorizontalBlock"]::after {
    content: "";
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: min(900px, 92%);
    height: 1px;
    background: linear-gradient(90deg,
        rgba(0,0,0,0) 0%, #D9D9D9 15%, #D9D9D9 85%, rgba(0,0,0,0) 100%);
}

/* The bar gets its own st.markdown block so it is not inside the hero's
   element container: that one is a stacking context (position/z-index above),
   which would cap the bar's z-index inside it and let the tool band and the
   how-it-works section paint over it on scroll. Its own container is taken out
   of flow so it contributes no height or vertical-block gap. */
[data-testid="stElementContainer"]:has(.crow-header) {
    position: absolute;
    height: 0;
    margin: 0;
}

/* Nav bar, 1:1 with usecrow.ai's glass card: 40% black over a 24px backdrop
   blur with a hairline white border, so the grid and content show through it.
   The site has no separate top-blur band — this backdrop-filter IS the blur. */
.crow-header {
    position: fixed;
    top: 24px;
    left: 50%;
    transform: translateX(-50%);
    width: min(1120px, calc(100vw - 64px));
    z-index: 100;
    background: rgba(0, 0, 0, 0.40);
    -webkit-backdrop-filter: blur(24px);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 16px;
    padding: 16px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.3s;
    max-width: 100%;
}
/* Nav type = text-2xl font-bold (title) and text-sm font-semibold (button). */
.crow-header .crow-title {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 700;
    line-height: 32px;
    letter-spacing: normal;
}
.crow-cta {
    background: #FFFFFF;
    color: #000000;
    font-size: 14px;
    font-weight: 600;
    line-height: 20px;
    padding: 10px 20px;
    border: 1px solid #FFFFFF;
    border-radius: 0;
    display: inline-block;
    transition: all 0.3s;
    pointer-events: auto;
    cursor: default;
}
.crow-cta:hover { background: transparent; color: #FFFFFF; }

/* Hero type, resolved from usecrow.ai's compiled Tailwind cascade. Sizes step
   at the 640/768/1024 breakpoints exactly as theirs do; base values below.
   Eyebrow = text-sm font-medium uppercase tracking-[0.18em] text-gray-500. */
.eyebrow {
    text-align: center;
    color: #6B7280;
    font-size: 14px;
    font-weight: 500;
    line-height: 20px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 126px;
}
/* Headline = text-3xl/4xl/5xl/6xl + tracking-tight, weight 400 (their
   `font-seminormal` class is never emitted, so it inherits the body weight). */
h1.headline {
    text-align: center;
    font-size: 30px;
    font-weight: 400;
    letter-spacing: -0.025em;
    line-height: 1.1;
    color: #000000;
    margin: 10px 0 26px 0;
}
/* Subhead = text-base/lg/xl, gray-600, max-w-2xl. */
.subhead {
    text-align: center;
    color: #4B5563;
    font-size: 16px;
    font-weight: 400;
    line-height: 1.625;
    max-width: 672px;
    margin: 0 auto 56px auto;
}
@media (min-width: 640px) {
    h1.headline { font-size: 36px; line-height: 40px; }
    .subhead { font-size: 18px; line-height: 28px; }
}
@media (min-width: 768px) {
    h1.headline { font-size: 48px; line-height: 1; }
    .subhead { font-size: 20px; line-height: 28px; }
}
@media (min-width: 1024px) {
    h1.headline { font-size: 60px; line-height: 1; }
}

/* Primary button = text-base sm:text-lg font-semibold, square corners. */
div.stButton > button {
    background: #0A0A0A !important;
    color: white !important;
    border-radius: 0 !important;
    padding: 12px 24px !important;
    font-size: 16px !important;
    line-height: 24px !important;
    font-weight: 600 !important;
    letter-spacing: normal !important;
    border: none !important;
    cursor: pointer !important;
    transition: background 0.2s ease, transform 0.12s ease, box-shadow 0.2s ease !important;
}
/* Without these the button is a flat black rectangle that gives no sign it can
   be pressed: lift on hover, sink on press, visible ring on keyboard focus. */
div.stButton > button:hover {
    background: #262626 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
}
div.stButton > button:active {
    background: #000000 !important;
    transform: translateY(0);
    box-shadow: none;
}
div.stButton > button:focus-visible {
    outline: 2px solid #0A0A0A !important;
    outline-offset: 3px !important;
}
@media (min-width: 640px) {
    div.stButton > button {
        padding: 16px 32px !important;
        font-size: 18px !important;
        line-height: 28px !important;
    }
}

/* Working state, rendered into a placeholder directly under the button so the
   feedback lands where the click did. Both parts are pure CSS animation, so
   they keep moving while Python is blocked on the API call: an indeterminate
   segment on the button's bottom edge, over label text swept by a light band.
   One row per phase — reading, then writing — the finished one settling into
   .is-done while the next takes over. */
.working { margin-top: 0; }
.working-row + .working-row { margin-top: 18px; }
.working-bar {
    position: relative;
    height: 2px;
    width: 100%;
    background: #EDEDED;
    overflow: hidden;
}
.working-bar span {
    position: absolute;
    top: 0; bottom: 0; left: 0;
    width: 35%;
    background: linear-gradient(90deg, #34D399 0%, #2DD4BF 50%, #22D3EE 100%);
    animation: crow-indeterminate 1.25s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}
@keyframes crow-indeterminate {
    from { transform: translateX(-100%); }
    to   { transform: translateX(286%); }
}
.working-text {
    margin-top: 12px;
    font-size: 15px;
    font-weight: 500;
    line-height: 20px;
    background: linear-gradient(90deg,
        #9CA3AF 0%, #9CA3AF 35%, #0A0A0A 50%, #9CA3AF 65%, #9CA3AF 100%);
    background-size: 250% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: crow-shimmer 1.8s linear infinite;
}
@keyframes crow-shimmer {
    from { background-position: 100% 0; }
    to   { background-position: 0% 0; }
}
/* A finished phase stops moving: the bar fills and dims, the label settles to
   a flat grey so the live phase below it is the only thing in motion. */
.working-bar span.is-done {
    width: 100%;
    animation: none;
    opacity: 0.4;
}
.working-text.is-done {
    animation: none;
    background: none;
    color: #6B7280;
}
/* Anyone who has asked the OS to calm motion down still gets a clear state,
   just a steady one. */
@media (prefers-reduced-motion: reduce) {
    .working-bar span {
        animation: none;
        width: 100%;
    }
    .working-text {
        animation: none;
        background: none;
        color: #0A0A0A;
    }
}

/* "How it works", 1:1 with usecrow.ai's "How we work" band: centered
   eyebrow / heading / description over a single bordered 3-up grid. Its
   closing hairline is the one the tool section already paints at its top;
   the opening one below mirrors it. The 96px gap above the eyebrow is split
   into margin + padding so the rule sits 64px clear of the text, the same
   offset the tool section gives its own. */
.how-section {
    position: relative;
    margin: 32px 0 96px 0;
    padding-top: 64px;
}
.how-section::before {
    content: "";
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: min(900px, 92%);
    height: 1px;
    background: linear-gradient(90deg,
        rgba(0,0,0,0) 0%, #D9D9D9 15%, #D9D9D9 85%, rgba(0,0,0,0) 100%);
}
.how-section .eyebrow { margin-top: 0; }
/* Heading = text-3xl/4xl/5xl tracking-tight, same weight as the hero headline. */
h2.how-heading {
    text-align: center;
    font-size: 30px;
    font-weight: 400;
    letter-spacing: -0.025em;
    line-height: 1.1;
    color: #000000;
    margin: 10px 0 26px 0;
}
.how-sub {
    text-align: center;
    color: #4B5563;
    font-size: 16px;
    font-weight: 400;
    line-height: 1.625;
    max-width: 672px;
    margin: 0 auto 56px auto;
}
.how-grid {
    display: grid;
    grid-template-columns: 1fr;
    border: 1px solid #E5E7EB;
}
.how-cell { padding: 32px 28px 40px 28px; }
.how-cell + .how-cell { border-top: 1px solid #E5E7EB; }
/* Step label = text-sm, body color; heading = text-xl/2xl font-bold. */
.how-step {
    font-size: 14px;
    font-weight: 400;
    line-height: 20px;
    color: #0D0D0D;
    margin-bottom: 28px;
}
.how-section .how-cell h3 {
    font-size: 20px;
    font-weight: 700;
    line-height: 28px;
    letter-spacing: -0.02em;
    color: #000000;
    margin: 0 0 14px 0;
    padding: 0;
}
.how-section .how-cell p {
    font-size: 16px;
    font-weight: 400;
    line-height: 1.625;
    color: #4B5563;
    margin: 0;
}
@media (min-width: 640px) {
    h2.how-heading { font-size: 36px; line-height: 40px; }
    .how-sub { font-size: 18px; line-height: 28px; }
}
@media (min-width: 768px) {
    h2.how-heading { font-size: 48px; line-height: 1; }
    .how-sub { font-size: 20px; line-height: 28px; }
    .how-grid { grid-template-columns: repeat(3, 1fr); }
    .how-cell + .how-cell { border-top: none; border-left: 1px solid #E5E7EB; }
    .how-section .how-cell h3 { font-size: 24px; line-height: 32px; }
}

.result-card {
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
}
.field-label {
    font-size: 12px; color: #888; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.04em;
}
.flag-badge {
    display: inline-block; background: #FDECEC; color: #B3261E;
    font-size: 11px; font-weight: 600; padding: 2px 8px;
    border-radius: 12px; margin-left: 8px;
}
.missing-text { color: #A16207; font-style: italic; }
</style>

<div class="hero-grid" aria-hidden="true"><svg viewBox="0 0 2500 2500" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">__GRID_RECTS__</svg></div>
<div class="eyebrow">Internal Prototype</div>
<h1 class="headline">Automated Lease Abstraction</h1>
<div class="subhead">Paste or upload a commercial lease and get its key terms back as a clean, structured summary, tested against 10 sample leases at 100% field accuracy.</div>
<div class="skyline-wrap" aria-hidden="true">
<svg class="skyline-back" viewBox="0 0 1920 200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
  <path fill="currentColor" d="M0,200 V140 H90 V100 L130,70 L170,100 V125 H250 V90 H320 V115 H400 V75 H470 V105 H540 V60 H620 V95 H700 V120 H780 V85 H860 V110 H940 V70 H1020 V100 H1100 V125 H1180 V90 H1260 V115 H1340 V80 H1420 V105 H1500 V70 H1580 V100 L1620,65 L1660,100 V120 H1740 V90 H1820 V115 H1920 V200 Z"/>
</svg>
<svg class="skyline-front" viewBox="0 0 1920 220" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
  <path fill="currentColor" d="M0,220 V170 H70 V140 H130 V90 H155 V60 H170 V40 H180 V60 H195 V90 H220 V120 H280 V90 H310 V50 H340 V90 H370 V70 H440 V110 H510 L550,15 L590,110 V120 H660 V150 H720 V80 H740 V60 H750 V45 H760 V25 H770 V45 H780 V60 H790 V80 H810 V140 H880 V100 H940 V60 H960 V40 H990 V60 H1010 V160 H1080 V110 H1140 V90 H1170 V60 H1185 V40 H1195 V60 H1210 V90 H1240 V140 H1310 V100 H1380 L1415,55 L1450,100 V150 H1520 V90 H1540 V60 H1580 V90 H1600 V120 H1670 V60 H1740 V140 H1820 V100 H1880 V170 H1920 V220 Z"/>
  <rect fill="currentColor" x="174" y="10" width="2.5" height="30"/>
  <rect fill="currentColor" x="764" y="0" width="2" height="25"/>
  <rect fill="currentColor" x="974" y="8" width="2.5" height="32"/>
  <rect fill="currentColor" x="1189" y="15" width="2" height="25"/>
</svg>
</div>
""".replace("__GRID_RECTS__", _GRID_RECTS), unsafe_allow_html=True)

st.markdown(
    '<div class="crow-header"><span class="crow-title">Crow</span>'
    '<span class="crow-cta">Lease Abstractor</span></div>',
    unsafe_allow_html=True,
)

# Separate block from the hero on purpose: the grid is sized to the element
# container that holds the skyline, so anything appended there would be
# painted over by it.
st.markdown("""
<section class="how-section" aria-labelledby="how-heading">
<div class="eyebrow">How it works</div>
<h2 class="how-heading" id="how-heading">Three steps from a raw lease to structured data.</h2>
<div class="how-sub">There is no template to fill in and nothing to key by hand. Drop the document in, let the model read it end to end, and get the eight fields an abstract actually needs, with anything ambiguous marked for a human.</div>
<div class="how-grid">
  <div class="how-cell">
    <div class="how-step">Step 1</div>
    <h3>Drop in the lease</h3>
    <p>Paste the lease text or pick one of the 10 sample documents. No formatting, cleanup, or page tagging first. The raw text is enough.</p>
  </div>
  <div class="how-cell">
    <div class="how-step">Step 2</div>
    <h3>Extract the key terms</h3>
    <p>The model reads the full document and returns eight fields as structured JSON: tenant, address, rent, term, escalation, CAM, and renewal.</p>
  </div>
  <div class="how-cell">
    <div class="how-step">Step 3</div>
    <h3>Review and export</h3>
    <p>Anything the lease states loosely comes back flagged for review, alongside the key provisions. The finished abstract downloads as JSON.</p>
  </div>
</div>
</section>
""", unsafe_allow_html=True)

# st.markdown strips <script>, so the scroll-progress bar is installed from a
# zero-height component iframe, which is same-origin and can reach the parent page.
#
# NOTE: Streamlit prints a deprecation notice for components.html on every run
# and lists a removal date that has already passed, so a future release will
# take this away. That's the main reason streamlit is pinned in
# requirements.txt - unpinning it can delete this call and the progress bar
# with it. The suggested replacement, st.iframe, is NOT a drop-in: it takes a
# src URL, not an HTML string. The real migration is
# st.html(..., unsafe_allow_javascript=True), but st.html isn't iframed and
# runs the markup through DOMPurify, so it needs testing rather than a
# find-and-replace. window.parent below keeps working either way, since
# window.parent === window at the top level.
components.html("""
<script>
(function () {
    const doc = window.parent.document;
    if (doc.getElementById("crow-scroll-progress")) return;

    const bar = doc.createElement("div");
    bar.id = "crow-scroll-progress";
    bar.style.cssText = [
        "position:fixed", "top:0", "left:0", "height:2px", "width:100%",
        "z-index:2147483647", "pointer-events:none", "will-change:clip-path",
        "clip-path:inset(0 100% 0 0)",
        // usecrow.ai brand ramp: emerald-400 -> teal-400 -> cyan-400
        "background:linear-gradient(90deg,#34D399 0%,#2DD4BF 50%,#22D3EE 100%)"
    ].join(";");
    doc.body.appendChild(bar);

    function scroller() {
        return doc.querySelector('[data-testid="stMain"]')
            || doc.querySelector('section.main')
            || doc.scrollingElement;
    }

    // Scroll events fire faster and more unevenly than frames, so the raw ratio
    // is eased toward on each animation frame instead of applied directly.
    let target = 0, shown = 0, frame = null;

    function measure() {
        const el = scroller();
        if (!el) return;
        const max = el.scrollHeight - el.clientHeight;
        target = max > 0 ? el.scrollTop / max : 0;
        if (frame === null) frame = window.parent.requestAnimationFrame(tick);
    }
    function tick() {
        shown += (target - shown) * 0.06;
        if (Math.abs(target - shown) < 0.0002) shown = target;
        bar.style.clipPath = "inset(0 " + (100 - shown * 100) + "% 0 0)";
        frame = shown === target ? null : window.parent.requestAnimationFrame(tick);
    }

    doc.addEventListener("scroll", measure, {capture: true, passive: true});
    window.parent.addEventListener("resize", measure);
    setTimeout(measure, 300);
    measure();
})();
</script>
""", height=0)

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.warning("ANTHROPIC_API_KEY is not set. Set it in your terminal before running this app.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
sample_files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".txt")) if os.path.isdir(DATA_DIR) else []

if "abstraction" not in st.session_state:
    st.session_state.abstraction = None


def start_new_lease():
    st.session_state.abstraction = None
    st.session_state.sample_choice = "Paste my own"
    st.session_state.lease_input = ""


col_input, col_result = st.columns(2)

with col_input:
    st.subheader("Document")

    choice = st.selectbox("Try a sample lease, or paste your own below:",
                           ["Paste my own"] + sample_files, key="sample_choice")

    if choice == "Paste my own":
        lease_text = st.text_area("Lease text", height=400, key="lease_input")
    else:
        lease_text = open(os.path.join(DATA_DIR, choice)).read()
        st.text_area("Lease text", value=lease_text, height=400, disabled=True)

    run = st.button("Abstract this lease", type="primary", use_container_width=True)
    # Claimed inside the column so the working state renders under the button.
    # A st.spinner here would sit below the whole columns row, off screen.
    status_slot = st.empty()

def _phase(label, done=False):
    """One progress row: a bar over its label, either running or finished."""
    flag = ' class="is-done"' if done else ""
    text_class = "working-text is-done" if done else "working-text"
    return (
        '<div class="working-row">'
        f'<div class="working-bar"><span{flag}></span></div>'
        f'<div class="{text_class}">{"✓ " if done else ""}{label}</div>'
        "</div>"
    )


def _status(*rows):
    return ('<div class="working" role="status" aria-live="polite">'
            + "".join(rows) + "</div>")


if run:
    if not lease_text.strip():
        st.session_state.abstraction = ("empty", None, [])
    else:
        status_slot.markdown(_status(_phase("Reading the lease")),
                             unsafe_allow_html=True)

        # Fires the moment the first token lands: the model is done reading and
        # has started writing, so the first row settles and the second starts.
        def reading_done():
            status_slot.markdown(_status(
                _phase("Reading done", done=True),
                _phase("Writing the abstraction"),
            ), unsafe_allow_html=True)

        result, problems = call_and_parse_pipeline(lease_text,
                                                   on_first_token=reading_done)
        status_slot.empty()
        st.session_state.abstraction = ("done", result, problems)

with col_result:
    st.subheader("Result")

    if st.session_state.abstraction is None:
        st.caption("Run a lease to see the result here.")
    else:
        status, result, problems = st.session_state.abstraction

        if status == "empty":
            st.warning("Paste or select a lease first.")
        elif result is None:
            st.error("Couldn't parse a result from this document. " + "; ".join(problems))
            st.button("Start a new lease", on_click=start_new_lease, use_container_width=True)
        else:
            flags = result.get("review_flags") or {}

            for key, label in LABELS.items():
                value = result.get(key)
                flag_name = f"{key}_unclear"
                is_flagged = flags.get(flag_name, False)
                if key in ("lease_start", "lease_end"):
                    is_flagged = is_flagged or flags.get("date_conflict", False)

                if value is None:
                    content = '<span class="missing-text">Not found in document</span>'
                else:
                    v = f"${value:,.2f}" if key == "monthly_rent" else str(value)
                    badge = '<span class="flag-badge">NEEDS REVIEW</span>' if is_flagged else ""
                    content = f"{v}{badge}"

                st.markdown(f"""
<div class="result-card">
    <div class="field-label">{label}</div>
    <div style="font-size:15px; margin-top:2px;">{content}</div>
</div>
""", unsafe_allow_html=True)

            provisions = result.get("key_provisions") or []
            if provisions:
                st.markdown("**Key provisions**")
                for item in provisions:
                    st.markdown(f"- {item}")

            notes = result.get("uncertainty_notes")
            if notes:
                st.info(f"Notes: {notes}")

            if problems:
                st.warning("Validation issues: " + "; ".join(problems))

            st.download_button(
                "Download as JSON",
                data=json.dumps(result, indent=2),
                file_name="lease_abstract.json",
                mime="application/json",
            )

            st.button("Start a new lease", on_click=start_new_lease, use_container_width=True)

            with st.expander("Raw JSON"):
                st.json(result)
