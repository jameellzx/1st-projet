"""Generate ck-ec-* Shopify sections (layout clone of ecomposer demo 6481, RTL Arabic) into a Dawn theme.
Usage: python gen.py <theme>/sections"""
import json, sys, os

OUT = sys.argv[1]

# ---------------------------------------------------------------- shared parts
def rng(id, label, mn, mx, step, default, unit=None):
    s = {"type": "range", "id": id, "label": label, "min": mn, "max": mx, "step": step, "default": default}
    if unit:
        s["unit"] = unit
    return s

def color(id, label, default):
    return {"type": "color", "id": id, "label": label, "default": default}

def sel(id, label, default, opts):
    return {"type": "select", "id": id, "label": label, "default": default,
            "options": [{"value": v, "label": l} for v, l in opts]}

def chk(id, label, default):
    return {"type": "checkbox", "id": id, "label": label, "default": default}

def hdr(t):
    return {"type": "header", "content": t}

D = dict(
    bg="#ffffff", fg="#222222", heading_color="#000000",
    btn_bg="#000000", btn_fg="#ffffff", btn_hover="#333333", btn_border="#000000", btn_border_w=0,
    h_size=32, h_size_m=26, h_weight=800, h_lh=1.2, h_tt="none",
    b_size=16, b_size_m=15, b_lh=1.4,
    btn_size=14, btn_px=24, btn_py=12, btn_weight=700, btn_tt="uppercase",
    pad_top=64, pad_bottom=64, pad_top_m=40, pad_bottom_m=40,
    width=1200, align="center", full=False, gutter=20, radius=0,
)

def common_settings(d):
    return [
        hdr("Colors"),
        {"type": "color_scheme", "id": "color_scheme", "label": "Color scheme", "default": "scheme-1"},
        color("background_color", "Background", d["bg"]),
        color("text_color", "Text", d["fg"]),
        color("heading_color", "Heading", d["heading_color"]),
        color("button_background", "Button background", d["btn_bg"]),
        color("button_text", "Button text", d["btn_fg"]),
        color("button_hover_background", "Button hover background", d["btn_hover"]),
        color("button_border", "Button border", d["btn_border"]),
        rng("button_border_width", "Button border width", 0, 6, 1, d["btn_border_w"], "px"),
        hdr("Typography"),
        {"type": "font_picker", "id": "heading_font", "label": "Heading font", "default": "dm_sans_n5"},
        {"type": "font_picker", "id": "body_font", "label": "Body font", "default": "dm_sans_n4"},
        rng("heading_size", "Heading size (desktop)", 12, 112, 2, d["h_size"], "px"),
        rng("heading_size_mobile", "Heading size (mobile)", 12, 72, 2, d["h_size_m"], "px"),
        rng("heading_weight", "Heading weight", 100, 900, 100, d["h_weight"]),
        rng("heading_line_height", "Heading line height", 0.8, 2, 0.1, d["h_lh"]),
        rng("heading_letter_spacing", "Heading letter spacing", -1, 3, 0.1, 0, "em"),
        sel("heading_text_transform", "Heading case", d["h_tt"],
            [("none", "As typed"), ("uppercase", "UPPERCASE"), ("capitalize", "Capitalize")]),
        rng("body_size", "Text size (desktop)", 10, 30, 1, d["b_size"], "px"),
        rng("body_size_mobile", "Text size (mobile)", 10, 26, 1, d["b_size_m"], "px"),
        rng("body_line_height", "Text line height", 1, 2.2, 0.1, d["b_lh"]),
        rng("button_size", "Button text size", 10, 24, 1, d["btn_size"], "px"),
        rng("button_weight", "Button weight", 100, 900, 100, d["btn_weight"]),
        sel("button_text_transform", "Button case", d["btn_tt"],
            [("none", "As typed"), ("uppercase", "UPPERCASE")]),
        rng("button_letter_spacing", "Button letter spacing", -1, 3, 0.1, 0, "em"),
        hdr("Layout"),
        rng("padding_top", "Top padding (desktop)", 0, 200, 2, d["pad_top"], "px"),
        rng("padding_bottom", "Bottom padding (desktop)", 0, 200, 2, d["pad_bottom"], "px"),
        rng("padding_top_mobile", "Top padding (mobile)", 0, 160, 2, d["pad_top_m"], "px"),
        rng("padding_bottom_mobile", "Bottom padding (mobile)", 0, 160, 2, d["pad_bottom_m"], "px"),
        rng("content_width", "Content width", 600, 2000, 20, d["width"], "px"),
        rng("side_padding", "Side padding", 0, 80, 2, d["gutter"], "px"),
        chk("full_width", "Full width", d["full"]),
        sel("text_alignment", "Text alignment", d["align"],
            [("left", "Left"), ("center", "Center"), ("right", "Right")]),
        rng("corner_radius", "Corner radius", 0, 40, 2, d["radius"], "px"),
        rng("button_padding_x", "Button side padding", 4, 64, 2, d["btn_px"], "px"),
        rng("button_padding_y", "Button height padding", 4, 32, 2, d["btn_py"], "px"),
        hdr("Small parts"),
        rng("small_text_size", "Small text size", 10, 20, 1, 12, "px"),
        rng("large_text_size", "Large text size", 12, 40, 1, 18, "px"),
        rng("chip_padding_x", "Badge side padding", 4, 30, 1, 12, "px"),
        rng("chip_padding_y", "Badge height padding", 0, 12, 1, 3, "px"),
        rng("number_size", "Number circle size", 20, 60, 1, 34, "px"),
        hdr("Visibility and animation"),
        chk("show_on_desktop", "Show on desktop", True),
        chk("show_on_mobile", "Show on mobile", True),
        sel("animation_style", "Entrance animation", "none",
            [("none", "None"), ("fade", "Fade in"), ("slide", "Slide up")]),
        rng("animation_duration", "Animation duration", 0, 1500, 50, 600, "ms"),
        rng("animation_distance", "Slide distance", 0, 80, 4, 24, "px"),
    ]

COMMON_VARS = """
    --ck-bg: {{ section.settings.background_color }};
    --ck-fg: {{ section.settings.text_color }};
    --ck-heading-color: {{ section.settings.heading_color }};
    --ck-btn-bg: {{ section.settings.button_background }};
    --ck-btn-fg: {{ section.settings.button_text }};
    --ck-btn-bg-hover: {{ section.settings.button_hover_background }};
    --ck-btn-border: {{ section.settings.button_border }};
    --ck-btn-border-w: {{ section.settings.button_border_width }}px;
    --ck-h-size: {{ section.settings.heading_size }}px;
    --ck-h-size-m: {{ section.settings.heading_size_mobile }}px;
    --ck-h-weight: {{ section.settings.heading_weight }};
    --ck-h-lh: {{ section.settings.heading_line_height }};
    --ck-h-ls: {{ section.settings.heading_letter_spacing }}em;
    --ck-h-tt: {{ section.settings.heading_text_transform }};
    --ck-b-size: {{ section.settings.body_size }}px;
    --ck-b-size-m: {{ section.settings.body_size_mobile }}px;
    --ck-b-lh: {{ section.settings.body_line_height }};
    --ck-btn-size: {{ section.settings.button_size }}px;
    --ck-btn-weight: {{ section.settings.button_weight }};
    --ck-btn-tt: {{ section.settings.button_text_transform }};
    --ck-btn-ls: {{ section.settings.button_letter_spacing }}em;
    --ck-pad-top: {{ section.settings.padding_top }}px;
    --ck-pad-bottom: {{ section.settings.padding_bottom }}px;
    --ck-pad-top-m: {{ section.settings.padding_top_mobile }}px;
    --ck-pad-bottom-m: {{ section.settings.padding_bottom_mobile }}px;
    --ck-max-width: {{ section.settings.content_width }}px;
    --ck-gutter: {{ section.settings.side_padding }}px;
    --ck-align: {{ section.settings.text_alignment }};
    --ck-radius: {{ section.settings.corner_radius }}px;
    --ck-btn-px: {{ section.settings.button_padding_x }}px;
    --ck-btn-py: {{ section.settings.button_padding_y }}px;
    --ck-anim-dur: {{ section.settings.animation_duration }}ms;
    --ck-anim-distance: {{ section.settings.animation_distance }}px;
    --ck-small: {{ section.settings.small_text_size }}px;
    --ck-large: {{ section.settings.large_text_size }}px;
    --ck-chip-px: {{ section.settings.chip_padding_x }}px;
    --ck-chip-py: {{ section.settings.chip_padding_y }}px;
    --ck-num-size: {{ section.settings.number_size }}px;"""

COMMON_CSS = """
.{C} { background: var(--ck-bg); color: var(--ck-fg); font-family: var(--ck-body-font); font-size: var(--ck-b-size-m); line-height: var(--ck-b-lh); padding-top: var(--ck-pad-top-m); padding-bottom: var(--ck-pad-bottom-m); text-align: var(--ck-align); }
.{C} ck-scroller { display: block; }
.{C} .ck-inner { max-width: var(--ck-max-width); margin: 0 auto; padding-left: var(--ck-gutter); padding-right: var(--ck-gutter); }
.{C}[data-full-width] .ck-inner { max-width: 100%; }
.{C} .ck-heading { font-family: var(--ck-heading-font); font-size: var(--ck-h-size-m); font-weight: var(--ck-h-weight); line-height: var(--ck-h-lh); letter-spacing: var(--ck-h-ls); text-transform: var(--ck-h-tt); color: var(--ck-heading-color); margin: 0; }
.{C} .ck-text p { margin: 0; }
.{C} .ck-btn { display: inline-block; background: var(--ck-btn-bg); color: var(--ck-btn-fg); border: var(--ck-btn-border-w) solid var(--ck-btn-border); border-radius: var(--ck-radius); padding: var(--ck-btn-py) var(--ck-btn-px); font-family: var(--ck-body-font); font-size: var(--ck-btn-size); font-weight: var(--ck-btn-weight); text-transform: var(--ck-btn-tt); letter-spacing: var(--ck-btn-ls); line-height: 1.2; text-decoration: none; cursor: pointer; transition: background-color var(--ck-anim-dur) ease; }
.{C} .ck-btn:hover { background: var(--ck-btn-bg-hover); }
.{C}[data-animate="fade"] .ck-inner { animation: ck-fade var(--ck-anim-dur) ease both; }
.{C}[data-animate="slide"] .ck-inner { animation: ck-slide var(--ck-anim-dur) ease both; }
@keyframes ck-fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes ck-slide { from { opacity: 0; transform: translateY(var(--ck-anim-distance)); } to { opacity: 1; transform: none; } }
@media screen and (max-width: 749px) { .{C}[data-hide-mobile] { display: none; } }
@media screen and (min-width: 750px) {
  .{C} { font-size: var(--ck-b-size); padding-top: var(--ck-pad-top); padding-bottom: var(--ck-pad-bottom); }
  .{C} .ck-heading { font-size: var(--ck-h-size); }
  .{C}[data-hide-desktop] { display: none; }
}
/* reduced motion must beat every animation rule above, including Dawn's */
@media (prefers-reduced-motion: reduce) { .{C} * { animation: none !important; transition: none !important; } }
"""

FONT_STYLE = """{%- liquid
  assign hf = section.settings.heading_font
  assign bf = section.settings.body_font
-%}
<style>
  #shopify-section-{{ section.id }} {
    --ck-heading-font: {{ hf.family }}, var(--ck-ar-font, sans-serif), {{ hf.fallback_families }};
    --ck-body-font: {{ bf.family }}, var(--ck-ar-font, sans-serif), {{ bf.fallback_families }};
  }
  {{ hf | font_face: font_display: 'swap' }}
  {{ bf | font_face: font_display: 'swap' }}
</style>
"""

WRAP_ATTRS = """ data-animate="{{ section.settings.animation_style }}"
  {%- if section.settings.full_width %} data-full-width{% endif %}
  {%- unless section.settings.show_on_mobile %} data-hide-mobile{% endunless %}
  {%- unless section.settings.show_on_desktop %} data-hide-desktop{% endunless %}"""

SLIDER_JS = """
if (!customElements.get('ck-slider')) {
  class CkSlider extends HTMLElement {
    connectedCallback() {
      this.slides = [...this.querySelectorAll('[data-slide]')];
      this.dots = [...this.querySelectorAll('[data-dot]')];
      this.index = 0;
      this.loop = this.dataset.loop !== 'false';
      this.interval = Number(this.dataset.interval || 0) * 1000;
      this.prev = this.querySelector('[data-prev]');
      this.next = this.querySelector('[data-next]');
      this.onPrev = () => this.go(this.index - 1);
      this.onNext = () => this.go(this.index + 1);
      this.onEnter = () => this.stop();
      this.onLeave = () => this.start();
      this.prev && this.prev.addEventListener('click', this.onPrev);
      this.next && this.next.addEventListener('click', this.onNext);
      this.dots.forEach((dot, i) => dot.addEventListener('click', () => { this.go(i); this.start(); }));
      this.addEventListener('mouseenter', this.onEnter);
      this.addEventListener('mouseleave', this.onLeave);
      this.go(0);
      this.start();
    }
    disconnectedCallback() {
      this.stop();
      this.prev && this.prev.removeEventListener('click', this.onPrev);
      this.next && this.next.removeEventListener('click', this.onNext);
      this.removeEventListener('mouseenter', this.onEnter);
      this.removeEventListener('mouseleave', this.onLeave);
    }
    go(i) {
      const n = this.slides.length;
      if (!n) return;
      if (i < 0) i = this.loop ? n - 1 : 0;
      if (i >= n) i = this.loop ? 0 : n - 1;
      this.index = i;
      this.slides.forEach((s, k) => { s.classList.toggle('is-active', k === i); s.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
      this.dots.forEach((d, k) => { d.classList.toggle('is-active', k === i); d.setAttribute('aria-current', k === i ? 'true' : 'false'); });
    }
    start() {
      this.stop();
      const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (this.dataset.autoplay === 'true' && this.interval > 0 && this.slides.length > 1 && !reduce) {
        this.timer = setInterval(() => this.go(this.index + 1), this.interval);
      }
    }
    stop() { clearInterval(this.timer); }
  }
  customElements.define('ck-slider', CkSlider);
  document.addEventListener('shopify:block:select', (e) => {
    const slider = e.target.closest('ck-slider');
    if (!slider || !slider.slides) return;
    const i = slider.slides.indexOf(e.target);
    if (i > -1) { slider.stop(); slider.go(i); }
  });
  document.addEventListener('shopify:block:deselect', (e) => {
    const slider = e.target.closest('ck-slider');
    if (slider && slider.start) slider.start();
  });
}
document.addEventListener('shopify:section:load', () => {});
document.addEventListener('shopify:section:unload', () => {});
"""

ARROW_L = '<svg viewBox="0 0 24 24" width="100%" height="100%" aria-hidden="true" focusable="false"><path d="M15 4 7 12l8 8" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24" width="100%" height="100%" aria-hidden="true" focusable="false"><path d="m9 4 8 8-8 8" fill="none" stroke="currentColor" stroke-width="2"/></svg>'


def build(cls, name, body, extra_vars, extra_settings, css, js, blocks=None, max_blocks=None,
          preset_blocks=None, d=None, tag="section", extra_attrs=""):
    d = {**D, **(d or {})}
    schema = {"name": name, "tag": tag, "class": "ck-section",
              "settings": extra_settings + common_settings(d)}
    if blocks:
        schema["blocks"] = blocks
        if max_blocks:
            schema["max_blocks"] = max_blocks
    schema["presets"] = [{"name": name, **({"blocks": preset_blocks} if preset_blocks else {})}]
    for st in schema["settings"] + [x for bl in schema.get("blocks", []) for x in bl["settings"]]:
        if st.get("default") == "":
            del st["default"]  # Shopify rejects blank defaults
    text = FONT_STYLE
    text += '<div class="color-{{ section.settings.color_scheme }} ck-scheme">\n'
    text += f'<div class="{cls}" style="{COMMON_VARS}{extra_vars}\n  "{WRAP_ATTRS}{extra_attrs}\n>\n'
    text += body.strip("\n") + "\n</div>\n</div>\n\n"
    text += "{% stylesheet %}" + COMMON_CSS.replace("{C}", cls) + css.replace("{C}", cls) + "{% endstylesheet %}\n\n"
    text += "{% javascript %}" + (js or "\ndocument.addEventListener('shopify:section:load', () => {});\ndocument.addEventListener('shopify:section:unload', () => {});\n") + "{% endjavascript %}\n\n"
    text += "{% schema %}\n" + json.dumps(schema, indent=2, ensure_ascii=False) + "\n{% endschema %}\n"
    path = os.path.join(OUT, f"{cls}.liquid")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote", path)


def img_tag(expr, cls, widths="375, 550, 750, 1100, 1500, 2000", sizes="100vw", loading="lazy"):
    return (f"{{{{ {expr} | image_url: width: 2400 | image_tag: widths: '{widths}', sizes: '{sizes}', "
            f"class: '{cls}', loading: {loading} }}}}")


# =====================================================================
# ecomposer 6481 clone (RTL Arabic) - shared extras
# =====================================================================
D.update(dict(
    fg="#686868", heading_color="#000000", btn_hover="#333333",
    h_size=32, h_size_m=24, h_weight=500, h_lh=1.2,
    b_size=14, b_size_m=14, b_lh=1.7,
    btn_size=15, btn_px=32, btn_py=12, btn_weight=700, btn_tt="none",
    pad_top=50, pad_bottom=50, pad_top_m=30, pad_bottom_m=30,
    width=1440, gutter=50, align="center", radius=30,
))


def img_settings(prefix="", label="Image", asset="", alt=""):
    return [
        {"type": "image_picker", "id": f"{prefix}image", "label": label},
        {"type": "text", "id": f"{prefix}image_asset", "label": f"{label}: fallback theme asset (file in assets/)", "default": asset},
        {"type": "text", "id": f"{prefix}image_alt", "label": f"{label}: alt text", "default": alt},
    ]


def pic(obj, cls, prefix="", sizes="(min-width: 990px) 50vw, 100vw", loading="lazy"):
    """Image from the picker, else the theme-asset fallback, else a placeholder."""
    s = f"{obj}.settings.{prefix}"
    return (
        f"{{%- if {s}image != blank -%}}"
        f"{{{{ {s}image | image_url: width: 1600 | image_tag: widths: '375, 550, 750, 1100, 1500', sizes: '{sizes}', class: '{cls}', loading: '{loading}', alt: {s}image_alt }}}}"
        f"{{%- elsif {s}image_asset != blank -%}}"
        f"<img src=\"{{{{ {s}image_asset | asset_url }}}}\" class=\"{cls}\" alt=\"{{{{ {s}image_alt | escape }}}}\" loading=\"{loading}\">"
        f"{{%- else -%}}{{{{ 'image' | placeholder_svg_tag: '{cls}' }}}}{{%- endif -%}}"
    )


def proof(obj):
    s = f"{obj}.settings."
    return (f"{{%- if {s}show_proof -%}}<span class=\"ck-proof\">{{{{ settings.ck_proof_label }}}}"
            f"{{%- if {s}proof_note != blank %}} {{{{ {s}proof_note }}}}{{% endif -%}}</span>{{%- endif -%}}")


def proof_settings(show=False, note=""):
    return [chk("show_proof", "Show 'needs proof from brand' placeholder", show),
            {"type": "text", "id": "proof_note", "label": "What proof is missing", "default": note}]


PROOF_VARS = """
    --ck-proof-fg: {{ section.settings.proof_color }};
    --ck-proof-bg: {{ section.settings.proof_background }};"""
PROOF_SETTINGS = [hdr("Placeholder chips"), color("proof_color", "Placeholder text", "#B4532A"),
                  color("proof_background", "Placeholder background", "#FFF4E8")]
PROOF_CSS = """
.{C} .ck-proof { display: inline-block; margin: var(--ck-proof-gap, 6px) 0 0; padding: var(--ck-chip-py) var(--ck-chip-px); border: 1px dashed var(--ck-proof-fg); border-radius: var(--ck-radius); background: var(--ck-proof-bg); color: var(--ck-proof-fg); font-size: var(--ck-small); line-height: 1.6; }
"""

HEAD = """
{%- if section.settings.heading != blank or section.settings.subheading != blank -%}
<div class="ck-head">
  {%- if section.settings.heading != blank -%}<h2 class="ck-heading">{{ section.settings.heading }}</h2>{%- endif -%}
  {%- if section.settings.subheading != blank -%}<div class="ck-text ck-sub">{{ section.settings.subheading }}</div>{%- endif -%}
</div>
{%- endif -%}
"""
HEAD_VARS = """
    --ck-head-gap: {{ section.settings.head_gap }}px;
    --ck-sub-gap: {{ section.settings.sub_gap }}px;"""
HEAD_CSS = """
.{C} .ck-head { margin-bottom: var(--ck-head-gap); }
.{C} .ck-sub { margin-top: var(--ck-sub-gap); }
"""


def head_settings(heading="", sub="", gap=50):
    return [hdr("Heading"),
            {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": heading or "Heading"},
            {"type": "richtext", "id": "subheading", "label": "Subheading", **({"default": sub} if sub else {})},
            rng("head_gap", "Space under heading", 0, 100, 2, gap, "px"),
            rng("sub_gap", "Space between heading and subheading", 0, 40, 1, 10, "px")]


SCROLL_JS = """
if (!customElements.get('ck-scroller')) {
  class CkScroller extends HTMLElement {
    connectedCallback() {
      this.track = this.querySelector('[data-track]');
      this.prev = this.querySelector('[data-prev]');
      this.next = this.querySelector('[data-next]');
      this.step = (d) => {
        if (!this.track) return;
        const card = this.track.firstElementChild;
        const w = card ? card.getBoundingClientRect().width : this.track.clientWidth;
        const rtl = getComputedStyle(this.track).direction === 'rtl' ? -1 : 1;
        const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.track.scrollBy({ left: d * rtl * w, behavior: reduce ? 'auto' : 'smooth' });
      };
      this.onPrev = () => this.step(-1);
      this.onNext = () => this.step(1);
      this.prev && this.prev.addEventListener('click', this.onPrev);
      this.next && this.next.addEventListener('click', this.onNext);
    }
    disconnectedCallback() {
      this.prev && this.prev.removeEventListener('click', this.onPrev);
      this.next && this.next.removeEventListener('click', this.onNext);
    }
  }
  customElements.define('ck-scroller', CkScroller);
}
document.addEventListener('shopify:section:load', () => {});
document.addEventListener('shopify:section:unload', () => {});
"""

ARROWS = """
{%- if section.settings.show_arrows -%}
<div class="ck-arrows">
  <button type="button" class="ck-arrow" data-prev aria-label="{{ section.settings.previous_label | escape }}">""" + ARROW_R + """</button>
  <button type="button" class="ck-arrow" data-next aria-label="{{ section.settings.next_label | escape }}">""" + ARROW_L + """</button>
</div>
{%- endif -%}
"""
ARROW_VARS = """
    --ck-arrow-bg: {{ section.settings.arrow_background }};
    --ck-arrow-fg: {{ section.settings.arrow_color }};
    --ck-arrow-size: {{ section.settings.arrow_size }}px;"""
ARROW_CSS = """
.{C} .ck-arrows { display: flex; justify-content: center; gap: calc(var(--ck-arrow-size) / 3); margin-bottom: calc(var(--ck-arrow-size) / 2); }
.{C} .ck-arrow { width: var(--ck-arrow-size); height: var(--ck-arrow-size); border: 0; border-radius: 50%; background: var(--ck-arrow-bg); color: var(--ck-arrow-fg); padding: calc(var(--ck-arrow-size) / 4); cursor: pointer; }
@media screen and (min-width: 990px) { .{C}[data-arrows-desktop="false"] .ck-arrows { display: none; } }
"""


def arrow_settings():
    return [hdr("Arrows"), chk("show_arrows", "Show arrows", True),
            chk("arrows_desktop", "Show arrows on desktop too", False),
            color("arrow_background", "Arrow background", "#9B9B9B"), color("arrow_color", "Arrow icon", "#FFFFFF"),
            rng("arrow_size", "Arrow size", 20, 60, 2, 28, "px"),
            {"type": "text", "id": "previous_label", "label": "Previous label (screen readers)", "default": "السابق"},
            {"type": "text", "id": "next_label", "label": "Next label (screen readers)", "default": "التالي"}]


def cols(d, t, m, mx=6):
    return [rng("columns_desktop", "Columns (desktop)", 1, mx, 1, d), rng("columns_tablet", "Columns (tablet)", 1, 4, 1, t),
            rng("columns_mobile", "Columns (mobile)", 1, 4, 1, m)]


COLS_VARS = """
    --ck-cols: {{ section.settings.columns_desktop }};
    --ck-cols-tablet: {{ section.settings.columns_tablet }};
    --ck-cols-mobile: {{ section.settings.columns_mobile }};
    --ck-gap: {{ section.settings.gap }}px;"""

# =============================================================== HERO
hero_body = """
<div class="ck-inner ck-hero" data-media="{{ section.settings.media_position }}">
  <div class="ck-hero__text">
    {%- if section.settings.heading != blank -%}<h1 class="ck-heading">{{ section.settings.heading }}</h1>{%- endif -%}
    {%- if section.settings.text != blank -%}<div class="ck-text ck-hero__sub">{{ section.settings.text }}</div>{%- endif -%}
    <div class="ck-hero__actions">
      {%- if section.settings.button_label != blank -%}<a class="ck-btn" href="{{ section.settings.button_link | default: routes.all_products_collection_url }}">{{ section.settings.button_label | escape }}</a>{%- endif -%}
      {%- if section.settings.link2_label != blank -%}<a class="ck-hero__link" href="{{ section.settings.link2_link | default: '#' }}">{{ section.settings.link2_label | escape }}</a>{%- endif -%}
    </div>
  </div>
  <div class="ck-hero__media">""" + pic("section", "ck-hero__img", sizes="(min-width: 990px) 40vw, 100vw", loading="eager") + """</div>
</div>
"""
hero_vars = """
    --ck-minh: {{ section.settings.min_height }}px;
    --ck-media-w: {{ section.settings.media_width }}%;
    --ck-text-gap: {{ section.settings.text_gap }}px;
    --ck-gap: {{ section.settings.gap }}px;
    --ck-valign: {{ section.settings.vertical_alignment }};
    --ck-align-m: {{ section.settings.text_alignment_mobile }};
    --ck-link-color: {{ section.settings.link_color }};"""
hero_settings = [
    hdr("Content"),
    {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "Heading"},
    {"type": "richtext", "id": "text", "label": "Text"},
    {"type": "text", "id": "button_label", "label": "Button label", "default": "Shop"},
    {"type": "url", "id": "button_link", "label": "Button link"},
    {"type": "text", "id": "link2_label", "label": "Second link label"},
    {"type": "url", "id": "link2_link", "label": "Second link"},
    color("link_color", "Second link color", "#000000"),
    *img_settings(asset="ec-hero.png"),
    hdr("Hero layout"),
    sel("media_position", "Image position (desktop)", "end", [("end", "After text"), ("start", "Before text")]),
    rng("media_width", "Image column width", 20, 70, 1, 40, "%"),
    rng("min_height", "Minimum height (desktop)", 200, 1000, 10, 720, "px"),
    rng("gap", "Gap between text and image", 0, 120, 2, 40, "px"),
    rng("text_gap", "Space between text items", 0, 60, 2, 24, "px"),
    sel("vertical_alignment", "Text vertical position", "center", [("flex-start", "Top"), ("center", "Middle"), ("flex-end", "Bottom")]),
    sel("text_alignment_mobile", "Text alignment (mobile)", "center", [("start", "Start"), ("center", "Center"), ("end", "End")]),
]
hero_css = """
.{C} .ck-hero { display: flex; flex-direction: column; gap: var(--ck-gap); }
.{C} .ck-hero__text { display: flex; flex-direction: column; gap: var(--ck-text-gap); text-align: var(--ck-align-m); align-items: center; order: 2; }
.{C} .ck-hero__media { order: 1; }
.{C} .ck-hero__img { display: block; width: 100%; height: auto; }
.{C} .ck-hero__actions { display: flex; flex-wrap: wrap; gap: var(--ck-text-gap); align-items: center; justify-content: center; }
.{C} .ck-hero__link { color: var(--ck-link-color); font-weight: var(--ck-btn-weight); }
@media screen and (min-width: 990px) {
  .{C} .ck-hero { flex-direction: row; align-items: stretch; min-height: var(--ck-minh); }
  .{C} .ck-hero__text { flex: 1; justify-content: var(--ck-valign); text-align: var(--ck-align); align-items: flex-start; order: 1; }
  .{C} .ck-hero__actions { justify-content: flex-start; }
  .{C} .ck-hero__media { flex: 0 0 var(--ck-media-w); display: flex; align-items: flex-end; order: 2; }
  .{C} .ck-hero[data-media="start"] .ck-hero__media { order: 0; }
}
"""
build("ck-ec-hero", "EC: hero", hero_body, hero_vars, hero_settings, hero_css, None,
      d=dict(bg="#FFE3D7", h_size=64, h_size_m=26, h_lh=1.2, pad_top=0, pad_bottom=0, pad_top_m=0, pad_bottom_m=30, align="right"))

# =============================================================== MARQUEE
marquee_body = """
<div class="ck-marquee__viewport" aria-label="{{ section.settings.aria_label | escape }}">
  <div class="ck-marquee__track">
    {%- for i in (1..section.settings.repeat_count) -%}
      <div class="ck-marquee__group"{% unless forloop.first %} aria-hidden="true"{% endunless %}>
        {%- for block in section.blocks -%}
          <span class="ck-marquee__item" style="{% if block.settings.item_color != blank %}--ck-item-color: {{ block.settings.item_color }};{% endif %}" {% if forloop.parentloop.first %}{{ block.shopify_attributes }}{% endif %}>
            {%- if block.settings.link != blank -%}<a href="{{ block.settings.link }}">{{ block.settings.text | escape }}</a>{%- else -%}{{ block.settings.text | escape }}{%- endif -%}
          </span>
          <span class="ck-marquee__sep" aria-hidden="true">""" + pic("section", "ck-marquee__icon", prefix="sep_", sizes="64px") + """</span>
        {%- endfor -%}
      </div>
    {%- endfor -%}
  </div>
</div>
"""
marquee_vars = """
    --ck-marquee-dur: {{ section.settings.speed }}s;
    --ck-marquee-dir: {{ section.settings.direction }};
    --ck-item-gap: {{ section.settings.item_gap }}px;
    --ck-icon-size: {{ section.settings.icon_size }}px;
    --ck-marquee-play: {% if section.settings.pause_on_hover %}paused{% else %}running{% endif %};"""
marquee_settings = [
    hdr("Scrolling text"),
    *img_settings("sep_", "Separator icon", "ec-star.png", ""),
    rng("icon_size", "Icon size", 8, 64, 2, 32, "px"),
    rng("speed", "Seconds per loop", 5, 120, 5, 40, "s"),
    sel("direction", "Direction", "normal", [("normal", "Right to left"), ("reverse", "Left to right")]),
    chk("pause_on_hover", "Pause on hover", True),
    rng("item_gap", "Space between items", 4, 60, 1, 30, "px"),
    rng("repeat_count", "Repeat text", 2, 8, 1, 4),
    {"type": "text", "id": "aria_label", "label": "Screen reader label", "default": "مزايا المتجر"},
]
marquee_blocks = [{"type": "item", "name": "Text item", "settings": [
    {"type": "text", "id": "text", "label": "Text", "default": "نص"},
    {"type": "url", "id": "link", "label": "Link"},
    {"type": "color", "id": "item_color", "label": "Text color (optional)"},
]}]
marquee_css = """
.{C} .ck-marquee__viewport { overflow: hidden; white-space: nowrap; direction: ltr; }
.{C} .ck-marquee__track { display: inline-flex; animation: ck-marquee var(--ck-marquee-dur) linear infinite; animation-direction: var(--ck-marquee-dir); }
.{C} .ck-marquee__viewport:hover .ck-marquee__track { animation-play-state: var(--ck-marquee-play); }
.{C} .ck-marquee__group { display: inline-flex; align-items: center; flex-shrink: 0; }
.{C} .ck-marquee__item { padding: 0 var(--ck-item-gap); font-family: var(--ck-heading-font); font-size: var(--ck-h-size-m); font-weight: var(--ck-h-weight); line-height: var(--ck-h-lh); color: var(--ck-item-color, var(--ck-heading-color)); direction: rtl; }
.{C} .ck-marquee__item a { color: inherit; text-decoration: none; }
.{C} .ck-marquee__sep { display: inline-flex; }
.{C} .ck-marquee__icon { width: var(--ck-icon-size); height: var(--ck-icon-size); object-fit: contain; display: block; }
@keyframes ck-marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
@media screen and (min-width: 750px) { .{C} .ck-marquee__item { font-size: var(--ck-h-size); } }
"""
build("ck-ec-marquee", "EC: scrolling text", marquee_body, marquee_vars, marquee_settings, marquee_css, None,
      blocks=marquee_blocks, max_blocks=12, preset_blocks=[{"type": "item"}, {"type": "item"}],
      d=dict(bg="#F4C2C2", pad_top=20, pad_bottom=20, pad_top_m=12, pad_bottom_m=12, h_size=32, h_size_m=18, full=True, gutter=0))

# =============================================================== QUOTES (new, same design language)
quotes_body = """
<div class="ck-inner">
  """ + HEAD + """
  <div class="ck-quotes">
    {%- for block in section.blocks -%}
      <blockquote class="ck-quote" style="{% if block.settings.card_background != blank %}--ck-card-bg: {{ block.settings.card_background }};{% endif %}{% if block.settings.card_text != blank %}--ck-card-fg: {{ block.settings.card_text }};{% endif %}" {{ block.shopify_attributes }}>{{ block.settings.text }}</blockquote>
    {%- endfor -%}
  </div>
  {%- if section.settings.footer_text != blank -%}<div class="ck-text ck-quotes__foot">{{ section.settings.footer_text }}</div>{%- endif -%}
</div>
"""
quotes_vars = HEAD_VARS + COLS_VARS + """
    --ck-card-pad: {{ section.settings.card_padding }}px;
    --ck-card-radius: {{ section.settings.card_radius }}px;
    --ck-quote-size: {{ section.settings.quote_size }}px;
    --ck-quote-size-m: {{ section.settings.quote_size_mobile }}px;
    --ck-card-bg-d: {{ section.settings.card_background }};
    --ck-card-fg-d: {{ section.settings.card_text }};
    --ck-foot-gap: {{ section.settings.footer_gap }}px;
    --ck-foot-color: {{ section.settings.footer_color }};"""
quotes_settings = head_settings() + [
    hdr("Quote cards"), *cols(4, 2, 1),
    rng("gap", "Gap", 0, 60, 2, 24, "px"),
    rng("card_padding", "Card padding", 0, 60, 2, 28, "px"),
    rng("card_radius", "Card corner radius", 0, 60, 2, 20, "px"),
    rng("quote_size", "Quote size (desktop)", 12, 40, 1, 20, "px"),
    rng("quote_size_mobile", "Quote size (mobile)", 12, 32, 1, 18, "px"),
    color("card_background", "Card background", "#FFFFFF"),
    color("card_text", "Card text", "#000000"),
    {"type": "richtext", "id": "footer_text", "label": "Line under the cards"},
    rng("footer_gap", "Space above line", 0, 80, 2, 40, "px"),
    color("footer_color", "Line color", "#000000"),
]
quotes_blocks = [{"type": "quote", "name": "Quote", "settings": [
    {"type": "inline_richtext", "id": "text", "label": "Quote", "default": "«…»"},
    {"type": "color", "id": "card_background", "label": "Card background (optional)"},
    {"type": "color", "id": "card_text", "label": "Card text (optional)"},
]}]
quotes_css = HEAD_CSS + """
.{C} .ck-quotes { display: grid; gap: var(--ck-gap); grid-template-columns: repeat(var(--ck-cols-mobile), minmax(0, 1fr)); }
.{C} .ck-quote { margin: 0; padding: var(--ck-card-pad); border-radius: var(--ck-card-radius); background: var(--ck-card-bg, var(--ck-card-bg-d)); color: var(--ck-card-fg, var(--ck-card-fg-d)); font-family: var(--ck-heading-font); font-size: var(--ck-quote-size-m); font-weight: var(--ck-h-weight); line-height: var(--ck-h-lh); display: flex; align-items: center; justify-content: center; }
.{C} .ck-quotes__foot { margin-top: var(--ck-foot-gap); color: var(--ck-foot-color); font-size: var(--ck-large); }
@media screen and (min-width: 750px) { .{C} .ck-quotes { grid-template-columns: repeat(var(--ck-cols-tablet), minmax(0, 1fr)); } .{C} .ck-quote { font-size: var(--ck-quote-size); } }
@media screen and (min-width: 990px) { .{C} .ck-quotes { grid-template-columns: repeat(var(--ck-cols), minmax(0, 1fr)); } }
"""
build("ck-ec-quotes", "EC: quote strip", quotes_body, quotes_vars, quotes_settings, quotes_css, None,
      blocks=quotes_blocks, max_blocks=8, preset_blocks=[{"type": "quote"}] * 4, d=dict(bg="#FFF5E5"))

# =============================================================== SPLIT (promo panel + image)
split_body = """
<div class="ck-inner">
  <div class="ck-split" data-media="{{ section.settings.media_position }}">
    <div class="ck-split__panel">
      {%- if section.settings.badge_text != blank -%}<span class="ck-badge">{{ section.settings.badge_text | escape }}</span>{%- endif -%}
      {%- if section.settings.heading != blank -%}<h2 class="ck-heading">{{ section.settings.heading }}</h2>{%- endif -%}
      {%- if section.settings.text != blank -%}<div class="ck-text ck-split__body">{{ section.settings.text }}</div>{%- endif -%}
      {%- for block in section.blocks -%}
        {%- case block.type -%}
          {%- when 'step' -%}
            <div class="ck-step" {{ block.shopify_attributes }}>
              <span class="ck-step__num">{{ block.settings.number | escape }}</span>
              <div class="ck-step__body">
                {%- if block.settings.title != blank -%}<strong class="ck-step__title">{{ block.settings.title }}</strong>{%- endif -%}
                <div class="ck-text">{{ block.settings.text }}</div>
              </div>
            </div>
          {%- when 'timeline' -%}
            <div class="ck-tl{% if block.settings.is_header %} ck-tl--head{% endif %}" style="{% if block.settings.row_color != blank %}--ck-row: {{ block.settings.row_color }};{% endif %}" {{ block.shopify_attributes }}>
              <span class="ck-tl__label">{{ block.settings.label }}</span>
              <span class="ck-tl__cell">{{ block.settings.stage_1 }}</span>
              <span class="ck-tl__cell">{{ block.settings.stage_2 }}</span>
              <span class="ck-tl__cell">{{ block.settings.stage_3 }}</span>
            </div>
          {%- when 'note' -%}
            <div class="ck-note ck-text ck-note--{{ block.settings.style }}" {{ block.shopify_attributes }}>{{ block.settings.text }}""" + proof("block") + """</div>
        {%- endcase -%}
      {%- endfor -%}
      <div class="ck-split__actions">
        {%- if section.settings.button_label != blank -%}<a class="ck-btn" href="{{ section.settings.button_link | default: routes.all_products_collection_url }}">{{ section.settings.button_label | escape }}</a>{%- endif -%}
        {%- if section.settings.link2_label != blank -%}<a class="ck-split__link" href="{{ section.settings.link2_link | default: '#' }}">{{ section.settings.link2_label | escape }}</a>{%- endif -%}
      </div>
    </div>
    <div class="ck-split__media">""" + pic("section", "ck-split__img") + """</div>
  </div>
</div>
"""
split_vars = """
    --ck-panel-w: {{ section.settings.panel_width }}%;
    --ck-panel-bg: {{ section.settings.panel_background }};
    --ck-media-bg: {{ section.settings.media_background }};
    --ck-panel-radius: {{ section.settings.panel_radius }}px;
    --ck-panel-pad: {{ section.settings.panel_padding }}px;
    --ck-panel-pad-m: {{ section.settings.panel_padding_mobile }}px;
    --ck-minh: {{ section.settings.min_height }}px;
    --ck-media-h-m: {{ section.settings.media_height_mobile }}px;
    --ck-gap: {{ section.settings.gap }}px;
    --ck-item-gap: {{ section.settings.item_gap }}px;
    --ck-fit: {{ section.settings.image_fit }};
    --ck-badge-bg: {{ section.settings.badge_background }};
    --ck-badge-fg: {{ section.settings.badge_color }};
    --ck-accent: {{ section.settings.accent_color }};
    --ck-panel-align: {{ section.settings.panel_alignment }};
    --ck-panel-max: {{ section.settings.panel_text_width }}px;""" + PROOF_VARS
split_settings = [
    hdr("Content"),
    {"type": "text", "id": "badge_text", "label": "Badge"},
    {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "Heading"},
    {"type": "richtext", "id": "text", "label": "Text"},
    {"type": "text", "id": "button_label", "label": "Button label", "default": "Shop Now"},
    {"type": "url", "id": "button_link", "label": "Button link"},
    {"type": "text", "id": "link2_label", "label": "Second link label"},
    {"type": "url", "id": "link2_link", "label": "Second link"},
    *img_settings(asset="ec-promo.png"),
    sel("image_fit", "Image fit", "cover", [("cover", "Fill"), ("contain", "Fit")]),
    hdr("Panel"),
    sel("media_position", "Image position (desktop)", "end", [("end", "After panel"), ("start", "Before panel")]),
    rng("panel_width", "Panel width (desktop)", 30, 80, 1, 61, "%"),
    rng("panel_text_width", "Panel text max width", 300, 1000, 10, 760, "px"),
    sel("panel_alignment", "Panel text alignment", "center", [("start", "Start"), ("center", "Center"), ("end", "End")]),
    color("panel_background", "Panel background", "#F5F5DC"),
    color("media_background", "Image background", "#FFE3D7"),
    rng("panel_radius", "Panel corner radius", 0, 60, 2, 20, "px"),
    rng("panel_padding", "Panel padding (desktop)", 0, 120, 2, 60, "px"),
    rng("panel_padding_mobile", "Panel padding (mobile)", 0, 60, 2, 24, "px"),
    rng("min_height", "Minimum height (desktop)", 0, 1000, 10, 460, "px"),
    rng("media_height_mobile", "Image height (mobile)", 120, 600, 10, 220, "px"),
    rng("gap", "Gap between panel and image", 0, 60, 2, 24, "px"),
    rng("item_gap", "Space between panel items", 0, 60, 2, 18, "px"),
    color("badge_background", "Badge background", "#FF9494"),
    color("badge_color", "Badge text", "#FFFFFF"),
    color("accent_color", "Step number / timeline accent", "#000000"),
] + PROOF_SETTINGS
split_blocks = [
    {"type": "step", "name": "Step", "settings": [
        {"type": "text", "id": "number", "label": "Number", "default": "1"},
        {"type": "inline_richtext", "id": "title", "label": "Title", "default": "Step"},
        {"type": "richtext", "id": "text", "label": "Text"}]},
    {"type": "timeline", "name": "Timeline row", "settings": [
        chk("is_header", "This is the header row", False),
        {"type": "inline_richtext", "id": "label", "label": "Row label", "default": "Row"},
        {"type": "inline_richtext", "id": "stage_1", "label": "Stage 1", "default": "1"},
        {"type": "inline_richtext", "id": "stage_2", "label": "Stage 2", "default": "2"},
        {"type": "inline_richtext", "id": "stage_3", "label": "Stage 3", "default": "3"},
        {"type": "color", "id": "row_color", "label": "Row color (optional)"}]},
    {"type": "note", "name": "Note", "settings": [
        {"type": "richtext", "id": "text", "label": "Text"},
        sel("style", "Style", "plain", [("plain", "Plain"), ("box", "Boxed"), ("big", "Large quote")]),
        *proof_settings()]},
]
split_css = PROOF_CSS + """
.{C} .ck-split { display: flex; flex-direction: column; gap: var(--ck-gap); }
.{C} .ck-split__panel { order: 2; background: var(--ck-panel-bg); border-radius: var(--ck-panel-radius); padding: var(--ck-panel-pad-m); display: flex; flex-direction: column; gap: var(--ck-item-gap); align-items: center; justify-content: center; text-align: var(--ck-panel-align); }
.{C} .ck-split__panel > * { width: 100%; max-width: var(--ck-panel-max); }
.{C} .ck-split__panel > .ck-badge { width: auto; }
.{C} .ck-split__media { order: 1; background: var(--ck-media-bg); border-radius: var(--ck-panel-radius); overflow: hidden; height: var(--ck-media-h-m); }
.{C} .ck-split__img { width: 100%; height: 100%; object-fit: var(--ck-fit); display: block; }
.{C} .ck-badge { display: inline-block; background: var(--ck-badge-bg); color: var(--ck-badge-fg); border-radius: var(--ck-radius); padding: var(--ck-chip-py) var(--ck-chip-px); font-weight: var(--ck-btn-weight); font-size: var(--ck-large); }
.{C} .ck-split__actions { display: flex; flex-wrap: wrap; gap: var(--ck-item-gap); align-items: center; justify-content: center; }
.{C} .ck-split__link { color: var(--ck-heading-color); font-weight: var(--ck-btn-weight); }
.{C} .ck-step { display: flex; gap: var(--ck-item-gap); text-align: start; align-items: flex-start; }
.{C} .ck-step__num { flex: 0 0 auto; width: var(--ck-num-size); height: var(--ck-num-size); border-radius: 50%; background: var(--ck-accent); color: var(--ck-panel-bg); display: inline-flex; align-items: center; justify-content: center; font-weight: var(--ck-btn-weight); }
.{C} .ck-step__title { color: var(--ck-heading-color); display: block; }
.{C} .ck-tl { display: grid; grid-template-columns: 1.4fr repeat(3, minmax(0, 1fr)); gap: 1px; background: var(--ck-row, transparent); border-radius: var(--ck-radius); overflow: hidden; text-align: center; font-size: var(--ck-small); }
.{C} .ck-tl > span { background: var(--ck-bg); padding: var(--ck-chip-px) var(--ck-chip-py); }
.{C} .ck-tl__label { font-weight: var(--ck-btn-weight); color: var(--ck-heading-color); }
.{C} .ck-tl--head > span { background: transparent; color: var(--ck-accent); font-weight: var(--ck-btn-weight); }
.{C} .ck-note--box { background: var(--ck-bg); border-radius: var(--ck-panel-radius); padding: var(--ck-panel-pad-m); }
.{C} .ck-note--big { font-family: var(--ck-heading-font); font-size: var(--ck-large); color: var(--ck-heading-color); }
@media screen and (min-width: 990px) {
  .{C} .ck-split { flex-direction: row; min-height: var(--ck-minh); }
  .{C} .ck-split__panel { flex: 0 0 calc(var(--ck-panel-w) - var(--ck-gap) / 2); padding: var(--ck-panel-pad); order: 1; }
  .{C} .ck-split__media { flex: 1; height: auto; order: 2; }
  .{C} .ck-split[data-media="start"] .ck-split__media { order: 0; }
}
"""
build("ck-ec-split", "EC: promo panel + image", split_body, split_vars, split_settings, split_css, None,
      blocks=split_blocks, max_blocks=12, d=dict(h_size=36, h_size_m=24, pad_top=0, pad_bottom=12, pad_top_m=0, pad_bottom_m=12, gutter=36))

# =============================================================== CARDS (benefits / old way / proof / offer)
cards_body = """
<div class="ck-inner">
  """ + HEAD + """
  {%- if section.settings.intro != blank -%}<div class="ck-text ck-cards__intro">{{ section.settings.intro }}</div>{%- endif -%}
  <div class="ck-cards" data-shape="{{ section.settings.image_shape }}">
    {%- for block in section.blocks -%}
      <div class="ck-card{% if block.settings.dashed %} ck-card--dashed{% endif %}" style="{% if block.settings.card_background != blank %}--ck-card-bg: {{ block.settings.card_background }};{% endif %}" {{ block.shopify_attributes }}>
        {%- if block.settings.image != blank or block.settings.image_asset != blank -%}
          <div class="ck-card__media">""" + pic("block", "ck-card__img", sizes="240px") + """</div>
        {%- endif -%}
        {%- if block.settings.number != blank -%}<span class="ck-card__num">{{ block.settings.number | escape }}</span>{%- endif -%}
        {%- if block.settings.title != blank -%}<h3 class="ck-card__title">{{ block.settings.title }}</h3>{%- endif -%}
        {%- if block.settings.text != blank -%}<div class="ck-text ck-card__text">{{ block.settings.text }}</div>{%- endif -%}
        """ + proof("block") + """
        {%- if block.settings.link_label != blank -%}<a class="ck-card__link" href="{{ block.settings.link | default: '#' }}">{{ block.settings.link_label | escape }}</a>{%- endif -%}
      </div>
    {%- endfor -%}
  </div>
  {%- if section.settings.footer_text != blank -%}<div class="ck-text ck-cards__foot">{{ section.settings.footer_text }}</div>{%- endif -%}
  {%- if section.settings.button_label != blank -%}<div class="ck-cards__cta"><a class="ck-btn" href="{{ section.settings.button_link | default: routes.all_products_collection_url }}">{{ section.settings.button_label | escape }}</a></div>{%- endif -%}
</div>
"""
cards_vars = HEAD_VARS + COLS_VARS + PROOF_VARS + """
    --ck-img-size: {{ section.settings.image_size }}px;
    --ck-img-size-m: {{ section.settings.image_size_mobile }}px;
    --ck-card-pad: {{ section.settings.card_padding }}px;
    --ck-card-radius: {{ section.settings.card_radius }}px;
    --ck-card-bg-d: {{ section.settings.card_background }};
    --ck-card-border: {{ section.settings.card_border }};
    --ck-card-align: {{ section.settings.card_alignment }};
    --ck-title-size: {{ section.settings.title_size }}px;
    --ck-title-size-m: {{ section.settings.title_size_mobile }}px;
    --ck-title-weight: {{ section.settings.title_weight }};
    --ck-num-bg: {{ section.settings.number_background }};
    --ck-num-fg: {{ section.settings.number_color }};
    --ck-item-gap: {{ section.settings.item_gap }}px;
    --ck-foot-gap: {{ section.settings.footer_gap }}px;
    --ck-foot-color: {{ section.settings.footer_color }};
    --ck-intro-w: {{ section.settings.intro_width }}px;"""
cards_settings = head_settings(gap=40) + [
    {"type": "richtext", "id": "intro", "label": "Intro text"},
    rng("intro_width", "Intro max width", 300, 1200, 10, 760, "px"),
    hdr("Cards"), *cols(3, 2, 1),
    rng("gap", "Gap", 0, 60, 2, 24, "px"),
    rng("item_gap", "Space inside card", 0, 40, 1, 12, "px"),
    sel("image_shape", "Image shape", "circle", [("circle", "Circle"), ("rounded", "Rounded"), ("square", "Square")]),
    rng("image_size", "Image size (desktop)", 60, 400, 4, 200, "px"),
    rng("image_size_mobile", "Image size (mobile)", 60, 300, 4, 180, "px"),
    rng("card_padding", "Card padding", 0, 60, 2, 0, "px"),
    rng("card_radius", "Card corner radius", 0, 60, 2, 20, "px"),
    color("card_background", "Card background", "rgba(0,0,0,0)"),
    color("card_border", "Dashed card border", "#B4532A"),
    sel("card_alignment", "Card text alignment", "center", [("start", "Start"), ("center", "Center")]),
    rng("title_size", "Card title size (desktop)", 12, 40, 1, 24, "px"),
    rng("title_size_mobile", "Card title size (mobile)", 12, 32, 1, 20, "px"),
    rng("title_weight", "Card title weight", 100, 900, 100, 700),
    color("number_background", "Number badge background", "#000000"),
    color("number_color", "Number badge text", "#FFFFFF"),
    {"type": "richtext", "id": "footer_text", "label": "Line under the cards"},
    rng("footer_gap", "Space above line and button", 0, 80, 2, 30, "px"),
    color("footer_color", "Line color", "#000000"),
    {"type": "text", "id": "button_label", "label": "Button label"},
    {"type": "url", "id": "button_link", "label": "Button link"},
] + PROOF_SETTINGS
cards_blocks = [{"type": "card", "name": "Card", "settings": [
    *img_settings(),
    {"type": "text", "id": "number", "label": "Number badge"},
    {"type": "inline_richtext", "id": "title", "label": "Title", "default": "Title"},
    {"type": "richtext", "id": "text", "label": "Text"},
    {"type": "text", "id": "link_label", "label": "Link label"},
    {"type": "url", "id": "link", "label": "Link"},
    {"type": "color", "id": "card_background", "label": "Card background (optional)"},
    chk("dashed", "Dashed placeholder card", False),
    *proof_settings()]}]
cards_css = HEAD_CSS + PROOF_CSS + """
.{C} .ck-cards__intro { max-width: var(--ck-intro-w); margin: 0 auto var(--ck-head-gap); }
.{C} .ck-cards { display: grid; gap: var(--ck-gap); grid-template-columns: repeat(var(--ck-cols-mobile), minmax(0, 1fr)); }
.{C} .ck-card { display: flex; flex-direction: column; align-items: var(--ck-card-align); text-align: var(--ck-card-align); gap: var(--ck-item-gap); padding: var(--ck-card-pad); border-radius: var(--ck-card-radius); background: var(--ck-card-bg, var(--ck-card-bg-d)); }
.{C} .ck-card--dashed { border: 2px dashed var(--ck-card-border); }
.{C} .ck-card__media { width: var(--ck-img-size-m); max-width: 100%; aspect-ratio: 1; overflow: hidden; border-radius: var(--ck-card-radius); }
.{C} .ck-cards[data-shape="circle"] .ck-card__media { border-radius: 50%; }
.{C} .ck-cards[data-shape="square"] .ck-card__media { border-radius: 0; }
.{C} .ck-card__img { width: 100%; height: 100%; object-fit: cover; display: block; }
.{C} .ck-card__num { display: inline-flex; align-items: center; justify-content: center; min-width: var(--ck-num-size); height: var(--ck-num-size); border-radius: 50%; background: var(--ck-num-bg); color: var(--ck-num-fg); font-weight: var(--ck-btn-weight); }
.{C} .ck-card__title { margin: 0; font-family: var(--ck-heading-font); font-size: var(--ck-title-size-m); font-weight: var(--ck-title-weight); line-height: var(--ck-h-lh); color: var(--ck-heading-color); }
.{C} .ck-card__link { color: var(--ck-heading-color); font-weight: var(--ck-btn-weight); }
.{C} .ck-cards__foot { margin-top: var(--ck-foot-gap); color: var(--ck-foot-color); font-size: var(--ck-large); }
.{C} .ck-cards__cta { margin-top: var(--ck-foot-gap); }
@media screen and (min-width: 750px) { .{C} .ck-cards { grid-template-columns: repeat(var(--ck-cols-tablet), minmax(0, 1fr)); } }
@media screen and (min-width: 990px) {
  .{C} .ck-cards { grid-template-columns: repeat(var(--ck-cols), minmax(0, 1fr)); }
  .{C} .ck-card__media { width: var(--ck-img-size); }
  .{C} .ck-card__title { font-size: var(--ck-title-size); }
}
"""
build("ck-ec-cards", "EC: cards", cards_body, cards_vars, cards_settings, cards_css, None,
      blocks=cards_blocks, max_blocks=12, preset_blocks=[{"type": "card"}] * 3, d=dict(bg="#FFF5E5"))

# =============================================================== CATEGORIES (ovals)
cat_body = """
<ck-scroller class="ck-inner">
  """ + HEAD + """{%- if section.settings.layout == 'slider' -%}""" + ARROWS + """{%- endif -%}
  <div class="ck-cats" data-shape="{{ section.settings.image_shape }}" data-layout="{{ section.settings.layout }}" data-track>
    {%- for block in section.blocks -%}
      <a class="ck-cat" href="{{ block.settings.link | default: routes.collections_url }}" {{ block.shopify_attributes }}>
        <span class="ck-cat__media">""" + pic("block", "ck-cat__img", sizes="(min-width: 990px) 25vw, 50vw") + """</span>
        {%- if block.settings.title != blank -%}<span class="ck-cat__title">{{ block.settings.title }}</span>{%- endif -%}
        {%- if block.settings.text != blank -%}<span class="ck-cat__text">{{ block.settings.text }}</span>{%- endif -%}
      </a>
    {%- endfor -%}
  </div>
</ck-scroller>
"""
cat_vars = HEAD_VARS + COLS_VARS + ARROW_VARS + """
    --ck-ratio: {{ section.settings.image_ratio }}%;
    --ck-title-size: {{ section.settings.title_size }}px;
    --ck-title-size-m: {{ section.settings.title_size_mobile }}px;
    --ck-row-gap: {{ section.settings.row_gap }}px;
    --ck-text-gap: {{ section.settings.text_gap }}px;"""
cat_settings = head_settings() + [
    hdr("Categories"),
    sel("layout", "Layout (tablet and desktop; mobile always wraps)", "slider", [("slider", "One row, scroll sideways"), ("grid", "Wrap into rows")]),
    *cols(4, 3, 2, 8),
    rng("gap", "Column gap", 0, 60, 1, 24, "px"),
    rng("row_gap", "Row gap", 0, 80, 2, 40, "px"),
    rng("text_gap", "Space under image", 0, 40, 1, 20, "px"),
    sel("image_shape", "Image shape", "oval", [("oval", "Oval"), ("rounded", "Rounded"), ("square", "Square")]),
    rng("image_ratio", "Image height (% of width)", 50, 200, 2, 126, "%"),
    rng("title_size", "Title size (desktop)", 12, 36, 1, 20, "px"),
    rng("title_size_mobile", "Title size (mobile)", 12, 30, 1, 16, "px"),
] + arrow_settings()
cat_blocks = [{"type": "category", "name": "Category", "settings": [
    *img_settings(), {"type": "inline_richtext", "id": "title", "label": "Title", "default": "Category"},
    {"type": "inline_richtext", "id": "text", "label": "Text"}, {"type": "url", "id": "link", "label": "Link"}]}]
cat_css = HEAD_CSS + ARROW_CSS + """
.{C} .ck-cats { display: flex; flex-wrap: wrap; justify-content: center; column-gap: var(--ck-gap); row-gap: var(--ck-row-gap); --ck-c: var(--ck-cols-mobile); }
.{C} .ck-cat { flex: 0 0 calc((100% - var(--ck-gap) * (var(--ck-c) - 1)) / var(--ck-c)); display: flex; flex-direction: column; align-items: center; text-decoration: none; color: var(--ck-fg); }
.{C} .ck-cat__media { position: relative; width: 100%; padding-top: var(--ck-ratio); overflow: hidden; border-radius: var(--ck-radius); margin-bottom: var(--ck-text-gap); }
.{C} .ck-cats[data-shape="oval"] .ck-cat__media { border-radius: 50%; }
.{C} .ck-cats[data-shape="square"] .ck-cat__media { border-radius: 0; }
.{C} .ck-cat__img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.{C} .ck-cat__title { font-family: var(--ck-heading-font); font-size: var(--ck-title-size-m); font-weight: var(--ck-h-weight); color: var(--ck-heading-color); line-height: var(--ck-h-lh); }
@media screen and (max-width: 749px) { .{C} .ck-arrows { display: none; } }
@media screen and (min-width: 750px) {
  .{C} .ck-cats { --ck-c: var(--ck-cols-tablet); }
  .{C} .ck-cats[data-layout="slider"] { flex-wrap: nowrap; justify-content: flex-start; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
  .{C} .ck-cats[data-layout="slider"]::-webkit-scrollbar { display: none; }
  .{C} .ck-cats[data-layout="slider"] .ck-cat { scroll-snap-align: start; }
}
@media screen and (min-width: 990px) { .{C} .ck-cats { --ck-c: var(--ck-cols); } .{C} .ck-cat__title { font-size: var(--ck-title-size); } }
"""
build("ck-ec-categories", "EC: categories", cat_body, cat_vars, cat_settings, cat_css, SCROLL_JS,
      blocks=cat_blocks, max_blocks=12, preset_blocks=[{"type": "category"}] * 4,
      extra_attrs=' data-arrows-desktop="{{ section.settings.arrows_desktop }}"')

# =============================================================== PRODUCTS (slider grid)
prod_body = """
<ck-scroller class="ck-inner">
  """ + HEAD + ARROWS + """
  <div class="ck-prods" data-track>
    {%- if section.settings.collection != blank -%}
      {%- for product in section.settings.collection.products limit: section.settings.products_to_show -%}
        <div class="ck-prod">
          <a class="ck-prod__media" href="{{ product.url }}">
            {%- if product.featured_image -%}{{ product.featured_image | image_url: width: 800 | image_tag: widths: '275, 400, 550, 800', sizes: '(min-width: 990px) 25vw, 70vw', class: 'ck-prod__img', loading: 'lazy' }}{%- else -%}{{ 'product-1' | placeholder_svg_tag: 'ck-prod__img' }}{%- endif -%}
            {%- if product.compare_at_price > product.price and section.settings.show_sale_badge -%}<span class="ck-prod__badge">-{{ product.compare_at_price | minus: product.price | times: 100 | divided_by: product.compare_at_price }}%</span>{%- endif -%}
          </a>
          {%- if section.settings.show_vendor -%}<span class="ck-prod__vendor">{{ product.vendor | escape }}</span>{%- endif -%}
          <a class="ck-prod__title" href="{{ product.url }}">{{ product.title | escape }}</a>
          <span class="ck-prod__price">
            {%- if product.compare_at_price > product.price -%}<s class="ck-prod__compare">{{ product.compare_at_price | money }}</s> <span class="ck-prod__sale">{{ product.price | money }}</span>{%- else -%}{{ product.price | money }}{%- endif -%}
          </span>
        </div>
      {%- endfor -%}
    {%- else -%}
      {%- for block in section.blocks -%}
        <div class="ck-prod" {{ block.shopify_attributes }}>
          <a class="ck-prod__media" href="{{ block.settings.link | default: '#' }}">
            """ + pic("block", "ck-prod__img", sizes="(min-width: 990px) 25vw, 70vw") + """
            {%- if block.settings.badge != blank and section.settings.show_sale_badge -%}<span class="ck-prod__badge">{{ block.settings.badge | escape }}</span>{%- endif -%}
          </a>
          {%- if section.settings.show_vendor and block.settings.vendor != blank -%}<span class="ck-prod__vendor">{{ block.settings.vendor | escape }}</span>{%- endif -%}
          <a class="ck-prod__title" href="{{ block.settings.link | default: '#' }}">{{ block.settings.title }}</a>
          {%- if block.settings.details != blank -%}<div class="ck-text ck-prod__details">{{ block.settings.details }}</div>{%- endif -%}
          """ + proof("block") + """
          <span class="ck-prod__price">
            {%- if block.settings.compare_price != blank -%}<s class="ck-prod__compare">{{ block.settings.compare_price | escape }}</s> <span class="ck-prod__sale">{{ block.settings.price | escape }}</span>{%- else -%}{{ block.settings.price | escape }}{%- endif -%}
          </span>
          {%- if section.settings.price_note != blank -%}<span class="ck-prod__note">{{ section.settings.price_note | escape }}</span>{%- endif -%}
          {%- if section.settings.button_label != blank or section.settings.button2_label != blank -%}
          <div class="ck-prod__actions">
            {%- if section.settings.button_label != blank -%}<a class="ck-btn ck-btn--sm" href="{{ block.settings.link | default: '#' }}">{{ section.settings.button_label | escape }}</a>{%- endif -%}
            {%- if section.settings.button2_label != blank -%}<a class="ck-prod__link" href="{{ section.settings.button2_link | default: '#' }}">{{ section.settings.button2_label | escape }}</a>{%- endif -%}
          </div>
          {%- endif -%}
        </div>
      {%- endfor -%}
    {%- endif -%}
  </div>
  {%- if section.settings.footer_text != blank -%}<div class="ck-text ck-prods__foot">{{ section.settings.footer_text }}</div>{%- endif -%}
</ck-scroller>
"""
prod_vars = HEAD_VARS + COLS_VARS + ARROW_VARS + PROOF_VARS + """
    --ck-ratio: {{ section.settings.image_ratio }}%;
    --ck-img-fit: {{ section.settings.image_fit }};
    --ck-title-size: {{ section.settings.title_size }}px;
    --ck-vendor-color: {{ section.settings.vendor_color }};
    --ck-price-color: {{ section.settings.price_color }};
    --ck-sale-color: {{ section.settings.sale_color }};
    --ck-compare-color: {{ section.settings.compare_color }};
    --ck-badge-bg: {{ section.settings.badge_background }};
    --ck-badge-fg: {{ section.settings.badge_color }};
    --ck-note-color: {{ section.settings.note_color }};
    --ck-item-gap: {{ section.settings.item_gap }}px;
    --ck-foot-gap: {{ section.settings.footer_gap }}px;"""
prod_settings = head_settings() + [
    hdr("Products"),
    {"type": "collection", "id": "collection", "label": "Collection (empty = demo cards below)"},
    rng("products_to_show", "Products from collection", 2, 16, 1, 8),
    *cols(4, 3, 1),
    rng("gap", "Gap", 0, 60, 1, 30, "px"),
    rng("item_gap", "Space inside card", 0, 30, 1, 6, "px"),
    rng("image_ratio", "Image height (% of width)", 50, 160, 2, 100, "%"),
    sel("image_fit", "Image fit", "cover", [("cover", "Fill"), ("contain", "Fit")]),
    rng("title_size", "Title size", 12, 28, 1, 16, "px"),
    chk("show_vendor", "Show brand line", True),
    chk("show_sale_badge", "Show badge", True),
    color("vendor_color", "Brand line color", "#7E7E7E"),
    color("price_color", "Price", "#000000"),
    color("sale_color", "Sale price", "#FF7C7C"),
    color("compare_color", "Old price", "#B0B0B0"),
    color("badge_background", "Badge background", "#F4C2C2"),
    color("badge_color", "Badge text", "#000000"),
    {"type": "text", "id": "price_note", "label": "Note under price (demo cards)"},
    color("note_color", "Note color", "#B4532A"),
    {"type": "text", "id": "button_label", "label": "Card button label (demo cards)"},
    {"type": "text", "id": "button2_label", "label": "Card second link label (demo cards)"},
    {"type": "url", "id": "button2_link", "label": "Card second link"},
    {"type": "richtext", "id": "footer_text", "label": "Line under the products"},
    rng("footer_gap", "Space above line", 0, 80, 2, 30, "px"),
] + arrow_settings() + PROOF_SETTINGS
prod_blocks = [{"type": "product", "name": "Demo product card", "settings": [
    *img_settings(), {"type": "text", "id": "badge", "label": "Badge"},
    {"type": "text", "id": "vendor", "label": "Brand line"},
    {"type": "inline_richtext", "id": "title", "label": "Title", "default": "Product"},
    {"type": "richtext", "id": "details", "label": "Details"},
    {"type": "text", "id": "price", "label": "Price", "default": "0"},
    {"type": "text", "id": "compare_price", "label": "Old price"},
    {"type": "url", "id": "link", "label": "Link"},
    *proof_settings()]}]
prod_css = HEAD_CSS + ARROW_CSS + PROOF_CSS + """
.{C} .ck-prods { display: grid; grid-auto-flow: column; grid-auto-columns: calc((100% - var(--ck-gap) * (var(--ck-cols-mobile) - 1)) / var(--ck-cols-mobile) * 0.8); gap: var(--ck-gap); overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
.{C} .ck-prods::-webkit-scrollbar { display: none; }
.{C} .ck-prod { scroll-snap-align: start; display: flex; flex-direction: column; align-items: center; gap: var(--ck-item-gap); }
.{C} .ck-prod__media { position: relative; display: block; width: 100%; padding-top: var(--ck-ratio); overflow: hidden; margin-bottom: var(--ck-item-gap); }
.{C} .ck-prod__img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: var(--ck-img-fit); }
.{C} .ck-prod__badge { position: absolute; top: var(--ck-item-gap); inset-inline-start: var(--ck-item-gap); background: var(--ck-badge-bg); color: var(--ck-badge-fg); border-radius: var(--ck-radius); padding: var(--ck-chip-py) var(--ck-chip-px); font-size: var(--ck-small); line-height: 1.5; }
.{C} .ck-prod__vendor { color: var(--ck-vendor-color); font-weight: var(--ck-btn-weight); text-transform: uppercase; font-size: var(--ck-small); }
.{C} .ck-prod__title { color: var(--ck-heading-color); font-family: var(--ck-heading-font); font-size: var(--ck-title-size); font-weight: var(--ck-btn-weight); text-decoration: none; }
.{C} .ck-prod__details { font-size: var(--ck-small); line-height: 1.6; }
.{C} .ck-prod__price { color: var(--ck-price-color); font-weight: var(--ck-btn-weight); font-size: var(--ck-title-size); }
.{C} .ck-prod__compare { color: var(--ck-compare-color); }
.{C} .ck-prod__sale { color: var(--ck-sale-color); }
.{C} .ck-prod__note { color: var(--ck-note-color); font-size: var(--ck-small); }
.{C} .ck-prod__actions { display: flex; flex-wrap: wrap; gap: var(--ck-item-gap) calc(var(--ck-item-gap) * 3); align-items: center; justify-content: center; margin-top: var(--ck-item-gap); }
.{C} .ck-btn--sm { padding: calc(var(--ck-btn-py) * 0.7) calc(var(--ck-btn-px) * 0.7); }
.{C} .ck-prod__link { color: var(--ck-heading-color); font-weight: var(--ck-btn-weight); }
.{C} .ck-prods__foot { margin-top: var(--ck-foot-gap); color: var(--ck-heading-color); }
@media screen and (min-width: 750px) { .{C} .ck-prods { grid-auto-columns: calc((100% - var(--ck-gap) * (var(--ck-cols-tablet) - 1)) / var(--ck-cols-tablet)); } }
@media screen and (min-width: 990px) { .{C} .ck-prods { grid-auto-columns: calc((100% - var(--ck-gap) * (var(--ck-cols) - 1)) / var(--ck-cols)); } }
"""
build("ck-ec-products", "EC: product slider", prod_body, prod_vars, prod_settings, prod_css, SCROLL_JS,
      blocks=prod_blocks, max_blocks=16, preset_blocks=[{"type": "product"}] * 4,
      extra_attrs=' data-arrows-desktop="{{ section.settings.arrows_desktop }}"')

# =============================================================== FEATURED (image card + product panel)
feat_body = """
<div class="ck-inner">
  <div class="ck-feat" data-media="{{ section.settings.media_position }}">
    <div class="ck-feat__side">""" + pic("section", "ck-feat__side-img", prefix="side_") + """</div>
    <div class="ck-feat__panel">
      <div class="ck-feat__product">""" + pic("section", "ck-feat__img", sizes="(min-width: 990px) 25vw, 80vw") + """</div>
      <div class="ck-feat__info">
        {%- if section.settings.tag != blank -%}<span class="ck-feat__tag">{{ section.settings.tag | escape }}</span>{%- endif -%}
        {%- if section.settings.product != blank -%}
          <h2 class="ck-feat__title">{{ section.settings.product.title | escape }}</h2>
          {%- if section.settings.text != blank -%}<div class="ck-text">{{ section.settings.text }}</div>{%- endif -%}
          <span class="ck-feat__price"><span class="ck-feat__sale">{{ section.settings.product.price | money }}</span>{% if section.settings.product.compare_at_price > section.settings.product.price %} <s class="ck-feat__compare">{{ section.settings.product.compare_at_price | money }}</s>{% endif %}</span>
          {%- assign btn_url = section.settings.product.url -%}
        {%- else -%}
          {%- if section.settings.title != blank -%}<h2 class="ck-feat__title">{{ section.settings.title }}</h2>{%- endif -%}
          {%- if section.settings.text != blank -%}<div class="ck-text">{{ section.settings.text }}</div>{%- endif -%}
          <span class="ck-feat__price"><span class="ck-feat__sale">{{ section.settings.price | escape }}</span>{% if section.settings.compare_price != blank %} <s class="ck-feat__compare">{{ section.settings.compare_price | escape }}</s>{% endif %}</span>
          {%- assign btn_url = section.settings.button_link | default: routes.all_products_collection_url -%}
        {%- endif -%}
        {%- if section.settings.price_note != blank -%}<span class="ck-feat__note">{{ section.settings.price_note | escape }}</span>{%- endif -%}
        """ + proof("section") + """
        {%- if section.settings.button_label != blank -%}<a class="ck-btn ck-feat__btn" href="{{ btn_url }}"><svg viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true" focusable="false"><path d="M6 7h12l-1 13H7L6 7Zm3 0a3 3 0 0 1 6 0" fill="none" stroke="currentColor" stroke-width="2"/></svg>{{ section.settings.button_label | escape }}</a>{%- endif -%}
      </div>
    </div>
  </div>
</div>
"""
feat_vars = PROOF_VARS + """
    --ck-side-w: {{ section.settings.side_width }}%;
    --ck-side-bg: {{ section.settings.side_background }};
    --ck-panel-bg: {{ section.settings.panel_background }};
    --ck-panel-radius: {{ section.settings.panel_radius }}px;
    --ck-panel-pad: {{ section.settings.panel_padding }}px;
    --ck-panel-pad-m: {{ section.settings.panel_padding_mobile }}px;
    --ck-minh: {{ section.settings.min_height }}px;
    --ck-side-h-m: {{ section.settings.side_height_mobile }}px;
    --ck-gap: {{ section.settings.gap }}px;
    --ck-item-gap: {{ section.settings.item_gap }}px;
    --ck-img-w: {{ section.settings.product_image_width }}px;
    --ck-tag-bg: {{ section.settings.tag_background }};
    --ck-tag-fg: {{ section.settings.tag_color }};
    --ck-title-size: {{ section.settings.title_size }}px;
    --ck-sale-color: {{ section.settings.sale_color }};
    --ck-compare-color: {{ section.settings.compare_color }};
    --ck-note-color: {{ section.settings.note_color }};"""
feat_settings = [
    hdr("Product"),
    {"type": "product", "id": "product", "label": "Product (empty = text below)"},
    {"type": "text", "id": "tag", "label": "Tag", "default": "Tag"},
    {"type": "inline_richtext", "id": "title", "label": "Title", "default": "Product"},
    {"type": "richtext", "id": "text", "label": "Text"},
    {"type": "text", "id": "price", "label": "Price", "default": "0"},
    {"type": "text", "id": "compare_price", "label": "Old price"},
    {"type": "text", "id": "price_note", "label": "Note under price"},
    {"type": "text", "id": "button_label", "label": "Button label", "default": "Add to cart"},
    {"type": "url", "id": "button_link", "label": "Button link (no product picked)"},
    *proof_settings(),
    *img_settings(label="Product image", asset="ec-featured.png"),
    *img_settings("side_", "Side image", "ec-hand.png"),
    hdr("Featured layout"),
    sel("media_position", "Side image position (desktop)", "start", [("start", "Before panel"), ("end", "After panel")]),
    rng("side_width", "Side image width", 20, 60, 1, 38, "%"),
    rng("product_image_width", "Product image width", 120, 500, 10, 320, "px"),
    color("side_background", "Side image background", "#E5DCCB"),
    color("panel_background", "Panel background", "#E6E6FA"),
    rng("panel_radius", "Corner radius", 0, 60, 2, 20, "px"),
    rng("panel_padding", "Panel padding (desktop)", 0, 120, 2, 50, "px"),
    rng("panel_padding_mobile", "Panel padding (mobile)", 0, 60, 2, 20, "px"),
    rng("min_height", "Minimum height (desktop)", 0, 1000, 10, 470, "px"),
    rng("side_height_mobile", "Side image height (mobile)", 120, 600, 10, 220, "px"),
    rng("gap", "Gap", 0, 60, 2, 24, "px"),
    rng("item_gap", "Space between items", 0, 40, 1, 14, "px"),
    color("tag_background", "Tag background", "#B9AC8A"),
    color("tag_color", "Tag text", "#FFFFFF"),
    rng("title_size", "Title size", 14, 40, 1, 24, "px"),
    color("sale_color", "Price color", "#FF7C7C"),
    color("compare_color", "Old price color", "#B0B0B0"),
    color("note_color", "Note color", "#B4532A"),
] + PROOF_SETTINGS
feat_css = PROOF_CSS + """
.{C} .ck-feat { display: flex; flex-direction: column; gap: var(--ck-gap); text-align: start; }
.{C} .ck-feat__side { background: var(--ck-side-bg); border-radius: var(--ck-panel-radius); overflow: hidden; height: var(--ck-side-h-m); }
.{C} .ck-feat__side-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.{C} .ck-feat__panel { background: var(--ck-panel-bg); border-radius: var(--ck-panel-radius); padding: var(--ck-panel-pad-m); display: flex; flex-direction: column; gap: var(--ck-gap); align-items: center; }
.{C} .ck-feat__product { width: var(--ck-img-w); max-width: 100%; }
.{C} .ck-feat__img { width: 100%; height: auto; display: block; }
.{C} .ck-feat__info { display: flex; flex-direction: column; gap: var(--ck-item-gap); align-items: flex-start; flex: 1; }
.{C} .ck-feat__tag { background: var(--ck-tag-bg); color: var(--ck-tag-fg); border-radius: var(--ck-radius); padding: var(--ck-chip-py) var(--ck-chip-px); font-weight: var(--ck-btn-weight); }
.{C} .ck-feat__title { margin: 0; font-family: var(--ck-heading-font); font-size: var(--ck-title-size); font-weight: var(--ck-btn-weight); color: var(--ck-heading-color); line-height: var(--ck-h-lh); }
.{C} .ck-feat__price { font-size: var(--ck-large); font-weight: var(--ck-btn-weight); }
.{C} .ck-feat__sale { color: var(--ck-sale-color); }
.{C} .ck-feat__compare { color: var(--ck-compare-color); }
.{C} .ck-feat__note { color: var(--ck-note-color); font-size: var(--ck-small); }
.{C} .ck-feat__btn { display: inline-flex; align-items: center; gap: var(--ck-chip-px); }
@media screen and (min-width: 990px) {
  .{C} .ck-feat { flex-direction: row; min-height: var(--ck-minh); }
  .{C} .ck-feat__side { flex: 0 0 calc(var(--ck-side-w) - var(--ck-gap) / 2); height: auto; }
  .{C} .ck-feat[data-media="end"] .ck-feat__side { order: 2; }
  .{C} .ck-feat__panel { flex: 1; flex-direction: row; padding: var(--ck-panel-pad); }
}
"""
build("ck-ec-featured", "EC: featured product", feat_body, feat_vars, feat_settings, feat_css, None,
      d=dict(pad_top=0, pad_bottom=50, pad_top_m=0, gutter=36))

# =============================================================== FAQ
faq_body = """
<div class="ck-inner">
  """ + HEAD + """
  <div class="ck-faq">
    {%- for block in section.blocks -%}
      <details class="ck-faq__item" {% if forloop.first and section.settings.open_first %}open{% endif %} {{ block.shopify_attributes }}>
        <summary class="ck-faq__q">{{ block.settings.question }}<span class="ck-faq__icon" aria-hidden="true"></span></summary>
        <div class="ck-text ck-faq__a">{{ block.settings.answer }}""" + proof("block") + """</div>
      </details>
    {%- endfor -%}
  </div>
</div>
"""
faq_vars = HEAD_VARS + PROOF_VARS + """
    --ck-faq-w: {{ section.settings.list_width }}px;
    --ck-q-size: {{ section.settings.question_size }}px;
    --ck-q-size-m: {{ section.settings.question_size_mobile }}px;
    --ck-row-pad: {{ section.settings.row_padding }}px;
    --ck-line: {{ section.settings.line_color }};
    --ck-item-bg: {{ section.settings.item_background }};
    --ck-item-radius: {{ section.settings.item_radius }}px;
    --ck-gap: {{ section.settings.gap }}px;"""
faq_settings = head_settings() + [
    hdr("Questions"),
    chk("open_first", "Open the first question", True),
    rng("list_width", "List max width", 400, 1400, 10, 900, "px"),
    rng("question_size", "Question size (desktop)", 12, 32, 1, 18, "px"),
    rng("question_size_mobile", "Question size (mobile)", 12, 28, 1, 16, "px"),
    rng("row_padding", "Row padding", 4, 40, 1, 20, "px"),
    rng("gap", "Gap between rows", 0, 30, 1, 12, "px"),
    color("line_color", "Icon color", "#000000"),
    color("item_background", "Row background", "#FFF5E5"),
    rng("item_radius", "Row corner radius", 0, 40, 1, 16, "px"),
] + PROOF_SETTINGS
faq_blocks = [{"type": "qa", "name": "Question", "settings": [
    {"type": "inline_richtext", "id": "question", "label": "Question", "default": "Question?"},
    {"type": "richtext", "id": "answer", "label": "Answer"}, *proof_settings()]}]
faq_css = HEAD_CSS + PROOF_CSS + """
.{C} .ck-faq { max-width: var(--ck-faq-w); margin: 0 auto; display: grid; gap: var(--ck-gap); text-align: start; }
.{C} .ck-faq__item { background: var(--ck-item-bg); border-radius: var(--ck-item-radius); }
.{C} .ck-faq__q { list-style: none; cursor: pointer; display: flex; justify-content: space-between; align-items: center; gap: var(--ck-row-pad); padding: var(--ck-row-pad); font-family: var(--ck-heading-font); font-size: var(--ck-q-size-m); font-weight: var(--ck-h-weight); color: var(--ck-heading-color); }
.{C} .ck-faq__q::-webkit-details-marker { display: none; }
.{C} .ck-faq__icon { position: relative; flex: 0 0 auto; width: var(--ck-small); height: var(--ck-small); }
.{C} .ck-faq__icon::before, .{C} .ck-faq__icon::after { content: ""; position: absolute; inset: 45% 0 auto; height: 2px; background: var(--ck-line); transition: transform var(--ck-anim-dur) ease; }
.{C} .ck-faq__icon::after { transform: rotate(90deg); }
.{C} .ck-faq__item[open] .ck-faq__icon::after { transform: rotate(0deg); }
.{C} .ck-faq__a { padding: 0 var(--ck-row-pad) var(--ck-row-pad); }
@media screen and (min-width: 750px) { .{C} .ck-faq__q { font-size: var(--ck-q-size); } }
"""
build("ck-ec-faq", "EC: FAQ", faq_body, faq_vars, faq_settings, faq_css, None,
      blocks=faq_blocks, max_blocks=20, preset_blocks=[{"type": "qa"}] * 3)

# =============================================================== GALLERY (Instagram)
gal_body = """
<ck-scroller class="ck-inner">
  """ + HEAD + """
  <div class="ck-gal" data-track>
    {%- for block in section.blocks -%}
      <a class="ck-gal__item" href="{{ block.settings.link | default: section.settings.profile_link | default: '#' }}" {{ block.shopify_attributes }}>""" + pic("block", "ck-gal__img", sizes="(min-width: 990px) 20vw, 50vw") + """</a>
    {%- endfor -%}
  </div>
</ck-scroller>
"""
gal_vars = HEAD_VARS + COLS_VARS + """
    --ck-ratio: {{ section.settings.image_ratio }}%;
    --ck-img-radius: {{ section.settings.image_radius }}px;"""
gal_settings = head_settings() + [
    hdr("Gallery"), *cols(5, 3, 2, 8),
    rng("gap", "Gap", 0, 60, 1, 24, "px"),
    rng("image_ratio", "Image height (% of width)", 50, 160, 2, 100, "%"),
    rng("image_radius", "Image corner radius", 0, 60, 1, 20, "px"),
    {"type": "url", "id": "profile_link", "label": "Profile link (used when a photo has no link)"},
]
gal_blocks = [{"type": "photo", "name": "Photo", "settings": [*img_settings(), {"type": "url", "id": "link", "label": "Link"}]}]
gal_css = HEAD_CSS + """
.{C} .ck-gal { display: grid; grid-auto-flow: column; grid-auto-columns: calc((100% - var(--ck-gap) * (var(--ck-cols-mobile) - 1)) / var(--ck-cols-mobile)); gap: var(--ck-gap); overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
.{C} .ck-gal::-webkit-scrollbar { display: none; }
.{C} .ck-gal__item { position: relative; display: block; padding-top: var(--ck-ratio); border-radius: var(--ck-img-radius); overflow: hidden; scroll-snap-align: start; }
.{C} .ck-gal__img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform var(--ck-anim-dur) ease; }
.{C} .ck-gal__item:hover .ck-gal__img { transform: scale(1.05); }
@media screen and (min-width: 750px) { .{C} .ck-gal { grid-auto-columns: calc((100% - var(--ck-gap) * (var(--ck-cols-tablet) - 1)) / var(--ck-cols-tablet)); } }
@media screen and (min-width: 990px) { .{C} .ck-gal { grid-auto-columns: calc((100% - var(--ck-gap) * (var(--ck-cols) - 1)) / var(--ck-cols)); } }
"""
build("ck-ec-gallery", "EC: photo gallery", gal_body, gal_vars, gal_settings, gal_css, SCROLL_JS,
      blocks=gal_blocks, max_blocks=12, preset_blocks=[{"type": "photo"}] * 5)

# =============================================================== NEWSLETTER
nl_body = """
<div class="ck-inner ck-nl" data-media="{{ section.settings.media_position }}">
  <div class="ck-nl__media">""" + pic("section", "ck-nl__img", sizes="(min-width: 990px) 40vw, 100vw") + """</div>
  <div class="ck-nl__content">
    {%- if section.settings.kicker != blank -%}<p class="ck-nl__kicker">{{ section.settings.kicker | escape }}</p>{%- endif -%}
    {%- if section.settings.heading != blank -%}<h2 class="ck-heading">{{ section.settings.heading }}</h2>{%- endif -%}
    {%- if section.settings.text != blank -%}<div class="ck-text">{{ section.settings.text }}</div>{%- endif -%}
    {%- form 'customer', class: 'ck-nl__form' -%}
      <input type="hidden" name="contact[tags]" value="newsletter">
      {%- if form.posted_successfully? -%}
        <p class="ck-nl__ok">{{ section.settings.success_message | escape }}</p>
      {%- else -%}
        <div class="ck-nl__field">
          <input class="ck-nl__input" type="email" name="contact[email]" required autocomplete="email" placeholder="{{ section.settings.placeholder | escape }}" aria-label="{{ section.settings.placeholder | escape }}">
          <button class="ck-btn ck-nl__btn" type="submit">{{ section.settings.button_label | escape }}</button>
        </div>
      {%- endif -%}
    {%- endform -%}
  </div>
</div>
"""
nl_vars = """
    --ck-media-w: {{ section.settings.media_width }}%;
    --ck-gap: {{ section.settings.gap }}px;
    --ck-kicker-size: {{ section.settings.kicker_size }}px;
    --ck-input-border: {{ section.settings.input_border }};
    --ck-input-bg: {{ section.settings.input_background }};
    --ck-form-w: {{ section.settings.form_width }}px;
    --ck-media-offset: {{ section.settings.media_offset }}px;"""
nl_settings = [
    hdr("Content"),
    {"type": "text", "id": "kicker", "label": "Small heading", "default": "Stay Updated"},
    {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "With Our Newsletter"},
    {"type": "richtext", "id": "text", "label": "Text"},
    {"type": "text", "id": "placeholder", "label": "Email placeholder", "default": "Email address"},
    {"type": "text", "id": "button_label", "label": "Button label", "default": "Sign Up"},
    {"type": "text", "id": "success_message", "label": "Success message", "default": "Thanks!"},
    *img_settings(asset="ec-newsletter.png"),
    hdr("Newsletter layout"),
    sel("media_position", "Image position (desktop)", "start", [("start", "Before text"), ("end", "After text")]),
    rng("media_width", "Image width", 20, 60, 1, 40, "%"),
    rng("media_offset", "Image overhang below section", 0, 120, 2, 50, "px"),
    rng("gap", "Gap", 0, 160, 2, 120, "px"),
    rng("form_width", "Form max width", 200, 800, 10, 400, "px"),
    rng("kicker_size", "Small heading size", 12, 40, 1, 24, "px"),
    color("input_border", "Input border", "#E5E5E5"),
    color("input_background", "Input background", "#FFFFFF"),
]
nl_css = """
.{C} .ck-nl { display: flex; flex-direction: column; gap: var(--ck-gap); align-items: center; }
.{C} .ck-nl__media { width: 100%; }
.{C} .ck-nl__img { width: 100%; height: auto; display: block; }
.{C} .ck-nl__content { flex: 1; text-align: var(--ck-align); }
.{C} .ck-nl__kicker { margin: 0; font-family: var(--ck-heading-font); font-size: calc(var(--ck-kicker-size) * 0.75); color: var(--ck-heading-color); }
.{C} .ck-nl__form { margin-top: var(--ck-btn-py); max-width: var(--ck-form-w); }
.{C} .ck-nl__field { display: flex; align-items: center; border: 1px solid var(--ck-input-border); background: var(--ck-input-bg); border-radius: var(--ck-radius); padding: var(--ck-chip-py); }
.{C} .ck-nl__input { flex: 1; min-width: 0; border: 0; background: transparent; font: inherit; color: inherit; padding: 0 var(--ck-btn-py); }
.{C} .ck-nl__input:focus { outline: none; }
.{C} .ck-nl__field:focus-within { outline: 2px solid var(--ck-heading-color); }
@media screen and (min-width: 990px) {
  .{C} .ck-nl { flex-direction: row; }
  .{C} .ck-nl__media { flex: 0 0 var(--ck-media-w); margin-bottom: calc(var(--ck-media-offset) * -1); align-self: flex-end; }
  .{C} .ck-nl[data-media="end"] .ck-nl__media { order: 2; }
  .{C} .ck-nl__kicker { font-size: var(--ck-kicker-size); }
}
"""
build("ck-ec-newsletter", "EC: newsletter", nl_body, nl_vars, nl_settings, nl_css, None,
      d=dict(bg="#FFECE1", h_size=64, h_size_m=30, h_weight=400, pad_top=60, pad_bottom=50, align="right", gutter=36))
