"""Generate ck-* Shopify sections (Tubby-style layout clone) into a Dawn theme."""
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
        {"type": "font_picker", "id": "heading_font", "label": "Heading font", "default": "nunito_n8"},
        {"type": "font_picker", "id": "body_font", "label": "Body font", "default": "nunito_n4"},
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
        rng("padding_top", "Top padding (desktop)", 0, 200, 4, d["pad_top"], "px"),
        rng("padding_bottom", "Bottom padding (desktop)", 0, 200, 4, d["pad_bottom"], "px"),
        rng("padding_top_mobile", "Top padding (mobile)", 0, 160, 4, d["pad_top_m"], "px"),
        rng("padding_bottom_mobile", "Bottom padding (mobile)", 0, 160, 4, d["pad_bottom_m"], "px"),
        rng("content_width", "Content width", 600, 2000, 20, d["width"], "px"),
        rng("side_padding", "Side padding", 0, 80, 4, d["gutter"], "px"),
        chk("full_width", "Full width", d["full"]),
        sel("text_alignment", "Text alignment", d["align"],
            [("left", "Left"), ("center", "Center"), ("right", "Right")]),
        rng("corner_radius", "Corner radius", 0, 40, 2, d["radius"], "px"),
        rng("button_padding_x", "Button side padding", 4, 64, 2, d["btn_px"], "px"),
        rng("button_padding_y", "Button height padding", 4, 32, 2, d["btn_py"], "px"),
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
    --ck-anim-distance: {{ section.settings.animation_distance }}px;"""

COMMON_CSS = """
.{C} { background: var(--ck-bg); color: var(--ck-fg); font-family: var(--ck-body-font); font-size: var(--ck-b-size-m); line-height: var(--ck-b-lh); padding-top: var(--ck-pad-top-m); padding-bottom: var(--ck-pad-bottom-m); text-align: var(--ck-align); }
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
    --ck-heading-font: {{ hf.family }}, {{ hf.fallback_families }};
    --ck-body-font: {{ bf.family }}, {{ bf.fallback_families }};
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


# ================================================================ 1. HERO
hero_body = """
<ck-slider class="ck-hero__slider" data-autoplay="{{ section.settings.autoplay }}" data-interval="{{ section.settings.autoplay_interval }}" data-loop="{{ section.settings.loop }}">
  <div class="ck-hero__track">
    {%- for block in section.blocks -%}
      {%- liquid
        if forloop.first
          assign img_loading = 'eager'
        else
          assign img_loading = 'lazy'
        endif
      -%}
      <div
        class="ck-hero__slide{% if forloop.first %} is-active{% endif %}{% if block.settings.image_mobile != blank %} has-mobile{% endif %}"
        data-slide
        data-pos="{{ block.settings.content_position }}"
        style="
          {%- if block.settings.slide_text_color != blank %}--ck-slide-fg: {{ block.settings.slide_text_color }};{% endif -%}
          {%- if block.settings.slide_heading_color != blank %}--ck-slide-heading: {{ block.settings.slide_heading_color }};{% endif -%}
          --ck-slide-overlay: {{ block.settings.overlay_opacity | divided_by: 100.0 }};
          --ck-slide-text-max: {{ block.settings.text_max_width }}px;
        "
        {{ block.shopify_attributes }}
      >
        {%- if block.settings.image != blank -%}
          """ + img_tag("block.settings.image", "ck-hero__img ck-hero__img--desk", "750, 1100, 1500, 2000, 2400", "100vw", "img_loading") + """
        {%- else -%}
          {{ 'lifestyle-1' | placeholder_svg_tag: 'ck-hero__img ck-hero__img--desk ck-hero__ph' }}
        {%- endif -%}
        {%- if block.settings.image_mobile != blank -%}
          """ + img_tag("block.settings.image_mobile", "ck-hero__img ck-hero__img--mob", "375, 550, 750, 1100", "100vw", "img_loading") + """
        {%- endif -%}
        <div class="ck-hero__content">
          {%- if block.settings.heading != blank -%}
            <h2 class="ck-heading">{{ block.settings.heading }}</h2>
          {%- endif -%}
          {%- if block.settings.text != blank -%}
            <div class="ck-text ck-hero__text">{{ block.settings.text }}</div>
          {%- endif -%}
          {%- if block.settings.button_label != blank -%}
            <a class="ck-btn ck-hero__btn" href="{{ block.settings.button_link | default: routes.all_products_collection_url }}">{{ block.settings.button_label | escape }}</a>
          {%- endif -%}
        </div>
      </div>
    {%- endfor -%}
  </div>
  {%- if section.settings.show_arrows and section.blocks.size > 1 -%}
    <button type="button" class="ck-hero__arrow ck-hero__arrow--prev" data-prev aria-label="{{ section.settings.previous_label | escape }}">""" + ARROW_L + """</button>
    <button type="button" class="ck-hero__arrow ck-hero__arrow--next" data-next aria-label="{{ section.settings.next_label | escape }}">""" + ARROW_R + """</button>
  {%- endif -%}
  {%- if section.settings.show_dots and section.blocks.size > 1 -%}
    <div class="ck-hero__dots">
      {%- for block in section.blocks -%}
        <button type="button" class="ck-hero__dot{% if forloop.first %} is-active{% endif %}" data-dot aria-label="{{ section.settings.next_label | escape }} {{ forloop.index }}"></button>
      {%- endfor -%}
    </div>
  {%- endif -%}
</ck-slider>
"""
hero_vars = """
    --ck-h-desktop: {{ section.settings.height_desktop }}vh;
    --ck-h-mobile: {{ section.settings.height_mobile }}vh;
    --ck-content-offset: {{ section.settings.content_offset }}%;
    --ck-valign: {{ section.settings.vertical_alignment }};
    --ck-speed: {{ section.settings.transition_speed }}ms;
    --ck-overlay-color: {{ section.settings.overlay_color }};
    --ck-arrow-color: {{ section.settings.arrow_color }};
    --ck-arrow-size: {{ section.settings.arrow_size }}px;
    --ck-dot-color: {{ section.settings.dot_color }};
    --ck-dot-size: {{ section.settings.dot_size }}px;
    --ck-text-gap: {{ section.settings.text_gap }}px;"""
hero_settings = [
    hdr("Slideshow"),
    rng("height_desktop", "Height (desktop)", 30, 100, 5, 90, "vh"),
    rng("height_mobile", "Height (mobile)", 30, 100, 5, 75, "vh"),
    sel("vertical_alignment", "Content vertical position", "center",
        [("flex-start", "Top"), ("center", "Middle"), ("flex-end", "Bottom")]),
    rng("content_offset", "Content side offset", 0, 30, 1, 5, "%"),
    rng("text_gap", "Space between text items", 0, 48, 2, 16, "px"),
    color("overlay_color", "Image overlay color", "#000000"),
    chk("autoplay", "Autoplay", True),
    rng("autoplay_interval", "Autoplay interval", 2, 12, 1, 6, "s"),
    rng("transition_speed", "Transition speed", 100, 1500, 50, 600, "ms"),
    chk("loop", "Loop slides", True),
    chk("show_arrows", "Show arrows", True),
    chk("show_dots", "Show dots", True),
    color("arrow_color", "Arrow color", "#000000"),
    rng("arrow_size", "Arrow size", 16, 64, 2, 32, "px"),
    color("dot_color", "Dot color", "#000000"),
    rng("dot_size", "Dot size", 4, 20, 1, 8, "px"),
    {"type": "text", "id": "previous_label", "label": "Previous button label (screen readers)", "default": "Previous slide"},
    {"type": "text", "id": "next_label", "label": "Next button label (screen readers)", "default": "Next slide"},
]
hero_blocks = [{
    "type": "slide", "name": "Slide",
    "settings": [
        {"type": "image_picker", "id": "image", "label": "Image (desktop)"},
        {"type": "image_picker", "id": "image_mobile", "label": "Image (mobile)"},
        {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "Your big headline goes here"},
        {"type": "richtext", "id": "text", "label": "Text", "default": "<p>One short line about your offer or newest products.</p>"},
        {"type": "text", "id": "button_label", "label": "Button label", "default": "Shop now"},
        {"type": "url", "id": "button_link", "label": "Button link"},
        sel("content_position", "Content position", "left", [("left", "Left"), ("center", "Center"), ("right", "Right")]),
        rng("text_max_width", "Text max width", 240, 900, 20, 520, "px"),
        {"type": "color", "id": "slide_text_color", "label": "Text color (optional)"},
        {"type": "color", "id": "slide_heading_color", "label": "Heading color (optional)"},
        rng("overlay_opacity", "Overlay opacity", 0, 90, 5, 0, "%"),
    ],
}]
hero_css = """
.{C} .ck-hero__slider { display: block; position: relative; }
.{C} .ck-hero__track { position: relative; height: var(--ck-h-mobile); overflow: hidden; }
.{C} .ck-hero__slide { position: absolute; inset: 0; display: flex; align-items: var(--ck-valign); opacity: 0; visibility: hidden; transition: opacity var(--ck-speed) ease, visibility var(--ck-speed) ease; color: var(--ck-slide-fg, var(--ck-fg)); text-align: left; }
.{C} .ck-hero__slide.is-active { opacity: 1; visibility: visible; }
.{C} .ck-hero__slide::after { content: ""; position: absolute; inset: 0; background: var(--ck-overlay-color); opacity: var(--ck-slide-overlay); pointer-events: none; }
.{C} .ck-hero__img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.{C} .ck-hero__ph { background: var(--ck-bg); }
.{C} .ck-hero__slide.has-mobile .ck-hero__img--desk { display: none; }
.{C} .ck-hero__content { position: relative; z-index: 1; width: 100%; max-width: var(--ck-slide-text-max); padding: var(--ck-gutter); margin-left: var(--ck-content-offset); }
.{C} .ck-hero__slide[data-pos="center"] { justify-content: center; text-align: center; }
.{C} .ck-hero__slide[data-pos="center"] .ck-hero__content { margin-left: auto; margin-right: auto; }
.{C} .ck-hero__slide[data-pos="right"] { justify-content: flex-end; }
.{C} .ck-hero__slide[data-pos="right"] .ck-hero__content { margin-left: auto; margin-right: var(--ck-content-offset); }
.{C} .ck-hero__slide .ck-heading { color: var(--ck-slide-heading, var(--ck-heading-color)); }
.{C} .ck-hero__text { margin-top: var(--ck-text-gap); }
.{C} .ck-hero__btn { margin-top: var(--ck-text-gap); }
.{C} .ck-hero__arrow { position: absolute; top: 50%; transform: translateY(-50%); z-index: 2; width: var(--ck-arrow-size); height: var(--ck-arrow-size); padding: 0; border: 0; background: none; color: var(--ck-arrow-color); cursor: pointer; }
.{C} .ck-hero__arrow--prev { left: var(--ck-gutter); }
.{C} .ck-hero__arrow--next { right: var(--ck-gutter); }
.{C} .ck-hero__dots { position: absolute; left: 0; right: 0; bottom: var(--ck-gutter); z-index: 2; display: flex; justify-content: center; gap: var(--ck-dot-size); }
.{C} .ck-hero__dot { width: var(--ck-dot-size); height: var(--ck-dot-size); padding: 0; border: 0; border-radius: 50%; background: var(--ck-dot-color); opacity: 0.35; cursor: pointer; }
.{C} .ck-hero__dot.is-active { opacity: 1; }
@media screen and (max-width: 749px) {
  .{C} .ck-hero__img--mob { display: block; }
}
@media screen and (min-width: 750px) {
  .{C} .ck-hero__track { height: var(--ck-h-desktop); }
  .{C} .ck-hero__img--mob { display: none; }
  .{C} .ck-hero__slide.has-mobile .ck-hero__img--desk { display: block; }
}
"""
build("ck-hero-carousel", "Clone: hero slideshow", hero_body, hero_vars, hero_settings, hero_css, SLIDER_JS,
      blocks=hero_blocks, max_blocks=6, preset_blocks=[{"type": "slide"}, {"type": "slide"}, {"type": "slide"}],
      d=dict(h_size=56, h_size_m=34, h_tt="uppercase", h_lh=1.1, b_size=20, b_size_m=16,
             pad_top=0, pad_bottom=0, pad_top_m=0, pad_bottom_m=0, full=True, gutter=24, width=1600))

# ================================================================ 2. MARQUEE
marquee_body = """
<div class="ck-marquee__viewport" aria-label="{{ section.settings.aria_label | escape }}">
  <div class="ck-marquee__track">
    {%- for i in (1..section.settings.repeat_count) -%}
      <div class="ck-marquee__group"{% unless forloop.first %} aria-hidden="true"{% endunless %}>
        {%- for block in section.blocks -%}
          <span class="ck-marquee__item" style="{% if block.settings.item_color != blank %}--ck-item-color: {{ block.settings.item_color }};{% endif %}" {% if forloop.parentloop.first %}{{ block.shopify_attributes }}{% endif %}>
            {%- if block.settings.link != blank -%}<a href="{{ block.settings.link }}">{{ block.settings.text | escape }}</a>{%- else -%}{{ block.settings.text | escape }}{%- endif -%}
          </span>
          <span class="ck-marquee__sep" aria-hidden="true">{{ section.settings.separator | escape }}</span>
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
    --ck-marquee-play: {% if section.settings.pause_on_hover %}paused{% else %}running{% endif %};"""
marquee_settings = [
    hdr("Scrolling text"),
    {"type": "text", "id": "separator", "label": "Separator", "default": "•"},
    rng("speed", "Seconds per loop", 5, 120, 5, 40, "s"),
    sel("direction", "Direction", "normal", [("normal", "Right to left"), ("reverse", "Left to right")]),
    chk("pause_on_hover", "Pause on hover", True),
    rng("item_gap", "Space between items", 4, 60, 2, 12, "px"),
    rng("repeat_count", "Repeat text", 2, 8, 1, 4),
    {"type": "text", "id": "aria_label", "label": "Screen reader label", "default": "Product highlights"},
]
marquee_blocks = [{"type": "item", "name": "Text item", "settings": [
    {"type": "text", "id": "text", "label": "Text", "default": "Highlight"},
    {"type": "url", "id": "link", "label": "Link"},
    {"type": "color", "id": "item_color", "label": "Text color (optional)"},
]}]
marquee_css = """
.{C} .ck-marquee__viewport { overflow: hidden; white-space: nowrap; }
.{C} .ck-marquee__track { display: inline-flex; animation: ck-marquee var(--ck-marquee-dur) linear infinite; animation-direction: var(--ck-marquee-dir); }
.{C} .ck-marquee__viewport:hover .ck-marquee__track { animation-play-state: var(--ck-marquee-play); }
.{C} .ck-marquee__group { display: inline-flex; align-items: center; flex-shrink: 0; }
.{C} .ck-marquee__item, .{C} .ck-marquee__sep { padding: 0 var(--ck-item-gap); font-weight: var(--ck-btn-weight); text-transform: var(--ck-btn-tt); letter-spacing: var(--ck-btn-ls); }
.{C} .ck-marquee__item { color: var(--ck-item-color, var(--ck-fg)); }
.{C} .ck-marquee__item a { color: inherit; text-decoration: none; }
@keyframes ck-marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
"""
build("ck-marquee", "Clone: scrolling text", marquee_body, marquee_vars, marquee_settings, marquee_css, None,
      blocks=marquee_blocks, max_blocks=12,
      preset_blocks=[{"type": "item", "settings": {"text": t}} for t in ["Dairy free", "Paraben free", "Fragrance free", "SLS free"]],
      d=dict(bg="#F9DE6E", fg="#000000", pad_top=8, pad_bottom=8, pad_top_m=8, pad_bottom_m=8,
             b_size=14, b_size_m=13, full=True, width=1600))

# ================================================================ 3. PROMO BANNER
banner_body = """
<div class="ck-banner__media">
  {%- if section.settings.image != blank -%}
    """ + img_tag("section.settings.image", "ck-banner__img ck-banner__img--desk", "750, 1100, 1500, 2000, 2400") + """
  {%- else -%}
    {{ 'hero-apparel-1' | placeholder_svg_tag: 'ck-banner__img ck-banner__img--desk' }}
  {%- endif -%}
  {%- if section.settings.image_mobile != blank -%}
    """ + img_tag("section.settings.image_mobile", "ck-banner__img ck-banner__img--mob", "375, 550, 750, 1100") + """
  {%- endif -%}
</div>
<div class="ck-inner ck-banner__inner" data-pos="{{ section.settings.content_position }}">
  <div class="ck-banner__content">
    {%- if section.settings.heading != blank -%}<h2 class="ck-heading">{{ section.settings.heading }}</h2>{%- endif -%}
    {%- if section.settings.text != blank -%}<div class="ck-text ck-banner__text">{{ section.settings.text }}</div>{%- endif -%}
    {%- if section.settings.button_label != blank -%}<a class="ck-btn ck-banner__btn" href="{{ section.settings.button_link | default: routes.all_products_collection_url }}">{{ section.settings.button_label | escape }}</a>{%- endif -%}
  </div>
</div>
"""
banner_vars = """
    --ck-min-h: {{ section.settings.min_height_desktop }}px;
    --ck-min-h-m: {{ section.settings.min_height_mobile }}px;
    --ck-content-w: {{ section.settings.content_box_width }}px;
    --ck-text-gap: {{ section.settings.text_gap }}px;
    --ck-valign: {{ section.settings.vertical_alignment }};"""
banner_settings = [
    hdr("Banner"),
    {"type": "image_picker", "id": "image", "label": "Background image (desktop)"},
    {"type": "image_picker", "id": "image_mobile", "label": "Background image (mobile)"},
    {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "A special offer headline"},
    {"type": "richtext", "id": "text", "label": "Text", "default": "<p>Short supporting line about the offer.</p>"},
    {"type": "text", "id": "button_label", "label": "Button label", "default": "While supplies last"},
    {"type": "url", "id": "button_link", "label": "Button link"},
    sel("content_position", "Content position", "right", [("left", "Left"), ("center", "Center"), ("right", "Right")]),
    sel("vertical_alignment", "Content vertical position", "center", [("flex-start", "Top"), ("center", "Middle"), ("flex-end", "Bottom")]),
    rng("min_height_desktop", "Height (desktop)", 200, 900, 10, 420, "px"),
    rng("min_height_mobile", "Height (mobile)", 200, 900, 10, 520, "px"),
    rng("content_box_width", "Text box width", 240, 800, 20, 440, "px"),
    rng("text_gap", "Space between text items", 0, 48, 2, 14, "px"),
]
banner_css = """
.{C} { position: relative; overflow: hidden; }
.{C} .ck-banner__media { position: absolute; inset: 0; }
.{C} .ck-banner__img { width: 100%; height: 100%; object-fit: cover; }
.{C} .ck-banner__img--mob { display: none; }
.{C} .ck-banner__inner { position: relative; display: flex; align-items: var(--ck-valign); min-height: var(--ck-min-h-m); }
.{C} .ck-banner__inner[data-pos="left"] { justify-content: flex-start; }
.{C} .ck-banner__inner[data-pos="center"] { justify-content: center; }
.{C} .ck-banner__inner[data-pos="right"] { justify-content: flex-end; }
.{C} .ck-banner__content { max-width: var(--ck-content-w); }
.{C} .ck-banner__text, .{C} .ck-banner__btn { margin-top: var(--ck-text-gap); }
@media screen and (max-width: 749px) {
  .{C} .ck-banner__img--mob { display: block; }
  .{C} .ck-banner__media:has(.ck-banner__img--mob) .ck-banner__img--desk { display: none; }
}
@media screen and (min-width: 750px) {
  .{C} .ck-banner__inner { min-height: var(--ck-min-h); }
}
"""
build("ck-promo-banner", "Clone: promo banner", banner_body, banner_vars, banner_settings, banner_css, None,
      d=dict(bg="#C4E9F2", pad_top=0, pad_bottom=0, pad_top_m=0, pad_bottom_m=0, width=1600, align="left", h_size=32, h_size_m=24))

# ================================================================ 4. CIRCLE CARDS
cards_body = """
<div class="ck-inner">
  {%- if section.settings.heading != blank -%}<h2 class="ck-heading ck-cards__heading">{{ section.settings.heading }}</h2>{%- endif -%}
  <div class="ck-cards__grid">
    {%- for block in section.blocks -%}
      <a class="ck-cards__card" href="{{ block.settings.link | default: routes.all_products_collection_url }}" style="{% if block.settings.ring_color != blank %}--ck-ring: {{ block.settings.ring_color }};{% endif %}" {{ block.shopify_attributes }}>
        <span class="ck-cards__media">
          {%- if block.settings.image != blank -%}
            """ + img_tag("block.settings.image", "ck-cards__img", "275, 400, 550, 800", "(min-width: 990px) 25vw, 50vw") + """
          {%- else -%}
            {%- assign ph_n = forloop.index0 | modulo: 6 | plus: 1 -%}
            {%- assign ph = 'collection-' | append: ph_n -%}
            {{ ph | placeholder_svg_tag: 'ck-cards__img' }}
          {%- endif -%}
        </span>
        <span class="ck-cards__label">{{ block.settings.label | escape }}</span>
      </a>
    {%- endfor -%}
  </div>
</div>
"""
cards_vars = """
    --ck-cols: {{ section.settings.columns_desktop }};
    --ck-cols-tablet: {{ section.settings.columns_tablet }};
    --ck-cols-mobile: {{ section.settings.columns_mobile }};
    --ck-gap: {{ section.settings.gap }}px;
    --ck-img-size: {{ section.settings.image_size }}%;
    --ck-label-size: {{ section.settings.label_size }}px;
    --ck-label-color: {{ section.settings.label_color }};
    --ck-heading-gap: {{ section.settings.heading_gap }}px;
    --ck-hover-scale: {{ section.settings.hover_zoom | divided_by: 100.0 | plus: 1 }};"""
cards_settings = [
    hdr("Cards"),
    {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "Build your routine"},
    rng("columns_desktop", "Columns (desktop)", 1, 6, 1, 4),
    rng("columns_tablet", "Columns (tablet)", 1, 4, 1, 2),
    rng("columns_mobile", "Columns (mobile)", 1, 4, 1, 2),
    rng("gap", "Gap", 0, 80, 2, 32, "px"),
    rng("image_size", "Circle size", 40, 100, 5, 90, "%"),
    rng("label_size", "Label size", 10, 28, 1, 15, "px"),
    color("label_color", "Label color", "#496CA4"),
    rng("heading_gap", "Space under heading", 0, 80, 2, 36, "px"),
    rng("hover_zoom", "Hover zoom", 0, 20, 1, 4, "%"),
]
cards_blocks = [{"type": "card", "name": "Card", "settings": [
    {"type": "image_picker", "id": "image", "label": "Image"},
    {"type": "text", "id": "label", "label": "Label", "default": "Category"},
    {"type": "url", "id": "link", "label": "Link"},
    {"type": "color", "id": "ring_color", "label": "Circle background (optional)"},
]}]
cards_css = """
.{C} .ck-cards__heading { margin-bottom: var(--ck-heading-gap); }
.{C} .ck-cards__grid { display: grid; gap: var(--ck-gap); grid-template-columns: repeat(var(--ck-cols-mobile), minmax(0, 1fr)); }
.{C} .ck-cards__card { display: flex; flex-direction: column; align-items: center; gap: var(--ck-gap); text-decoration: none; color: var(--ck-label-color); }
.{C} .ck-cards__media { display: block; width: var(--ck-img-size); aspect-ratio: 1; border-radius: 50%; overflow: hidden; background: var(--ck-ring, transparent); transition: transform var(--ck-anim-dur) ease; }
.{C} .ck-cards__card:hover .ck-cards__media { transform: scale(var(--ck-hover-scale)); }
.{C} .ck-cards__img { width: 100%; height: 100%; object-fit: cover; display: block; }
.{C} .ck-cards__label { font-size: var(--ck-label-size); }
@media screen and (min-width: 750px) { .{C} .ck-cards__grid { grid-template-columns: repeat(var(--ck-cols-tablet), minmax(0, 1fr)); } }
@media screen and (min-width: 990px) { .{C} .ck-cards__grid { grid-template-columns: repeat(var(--ck-cols), minmax(0, 1fr)); } }
"""
build("ck-circle-cards", "Clone: circle cards", cards_body, cards_vars, cards_settings, cards_css, None,
      blocks=cards_blocks, max_blocks=8,
      preset_blocks=[{"type": "card", "settings": {"label": t}} for t in ["Baby (0-4)", "Kids (5+)", "Parents", "Build a bundle"]],
      d=dict(pad_top=48, pad_bottom=56))

# ================================================================ 5. PRODUCT CAROUSEL
prod_body = """
<div class="ck-inner ck-prod__layout">
  <div class="ck-prod__intro">
    {%- if section.settings.heading != blank -%}<h2 class="ck-heading">{{ section.settings.heading }}</h2>{%- endif -%}
    {%- if section.settings.text != blank -%}<div class="ck-text ck-prod__text">{{ section.settings.text }}</div>{%- endif -%}
  </div>
  <ck-scroller class="ck-prod__scroller">
    {%- if section.settings.show_arrows -%}
      <button type="button" class="ck-prod__arrow ck-prod__arrow--prev" data-prev aria-label="{{ section.settings.previous_label | escape }}">""" + ARROW_L + """</button>
    {%- endif -%}
    <ul class="ck-prod__track" data-track role="list">
      {%- if section.settings.collection != blank -%}
        {%- for product in section.settings.collection.products limit: section.settings.products_to_show -%}
          <li class="ck-prod__card">
            <a class="ck-prod__media" href="{{ product.url }}">
              {%- if product.featured_media -%}
                """ + img_tag("product.featured_media", "ck-prod__img", "275, 400, 550, 800", "(min-width: 990px) 22vw, 70vw") + """
              {%- else -%}
                {{ 'product-1' | placeholder_svg_tag: 'ck-prod__img' }}
              {%- endif -%}
              {%- if section.settings.show_sale_badge and product.compare_at_price > product.price -%}
                <span class="ck-prod__badge">{{ section.settings.sale_badge_label | escape }}</span>
              {%- endif -%}
            </a>
            <a class="ck-prod__title" href="{{ product.url }}">{{ product.title | escape }}</a>
            {%- assign rating = product.metafields.reviews.rating.value -%}
            {%- if section.settings.show_rating and rating != blank -%}
              <span class="ck-prod__rating" style="--ck-rating: {{ rating.rating | divided_by: rating.scale_max | times: 100 }}%;">
                <span class="ck-prod__stars" aria-hidden="true"></span>
                <span class="ck-prod__count">({{ product.metafields.reviews.rating_count.value | default: 0 }})</span>
              </span>
            {%- endif -%}
            <span class="ck-prod__price">
              {%- if product.price_varies -%}{{ section.settings.from_label | escape }} {% endif -%}
              {{ product.price | money }}
              {%- if product.compare_at_price > product.price -%} <s class="ck-prod__compare">{{ product.compare_at_price | money }}</s>{%- endif -%}
            </span>
            {%- if section.settings.show_add_to_cart -%}
              {%- form 'product', product, class: 'ck-prod__form' -%}
                <input type="hidden" name="id" value="{{ product.selected_or_first_available_variant.id }}">
                <button type="submit" class="ck-btn ck-prod__atc"{% unless product.available %} disabled{% endunless %}>
                  {%- if product.available -%}{{ section.settings.add_to_cart_label | escape }}{%- else -%}{{ section.settings.sold_out_label | escape }}{%- endif -%}
                </button>
              {%- endform -%}
            {%- endif -%}
          </li>
        {%- endfor -%}
      {%- else -%}
        {%- for block in section.blocks -%}
          <li class="ck-prod__card" {{ block.shopify_attributes }}>
            <a class="ck-prod__media" href="{{ block.settings.link | default: routes.all_products_collection_url }}">
              {%- if block.settings.image != blank -%}
                {{ block.settings.image | image_url: width: 2400 | image_tag: widths: '275, 400, 550, 800', sizes: '(min-width: 990px) 22vw, 70vw', class: 'ck-prod__img', loading: lazy }}
              {%- else -%}
                {%- assign ph_n = forloop.index0 | modulo: 6 | plus: 1 -%}
                {%- assign ph = 'product-' | append: ph_n -%}
                {{ ph | placeholder_svg_tag: 'ck-prod__img' }}
              {%- endif -%}
              {%- if block.settings.badge != blank -%}<span class="ck-prod__badge">{{ block.settings.badge | escape }}</span>{%- endif -%}
            </a>
            <a class="ck-prod__title" href="{{ block.settings.link | default: routes.all_products_collection_url }}">{{ block.settings.title | escape }}</a>
            {%- if section.settings.show_rating and block.settings.rating > 0 -%}
              <span class="ck-prod__rating" style="--ck-rating: {{ block.settings.rating | times: 2 }}%;">
                <span class="ck-prod__stars" aria-hidden="true"></span>
                <span class="ck-prod__count">({{ block.settings.review_count | escape }})</span>
              </span>
            {%- endif -%}
            <span class="ck-prod__price">{{ block.settings.price | escape }}</span>
            {%- if section.settings.show_add_to_cart -%}
              <a class="ck-btn ck-prod__atc" href="{{ block.settings.link | default: routes.all_products_collection_url }}">{{ section.settings.add_to_cart_label | escape }}</a>
            {%- endif -%}
          </li>
        {%- endfor -%}
      {%- endif -%}
    </ul>
    {%- if section.settings.show_arrows -%}
      <button type="button" class="ck-prod__arrow ck-prod__arrow--next" data-next aria-label="{{ section.settings.next_label | escape }}">""" + ARROW_R + """</button>
    {%- endif -%}
  </ck-scroller>
</div>
"""
prod_vars = """
    --ck-per-view: {{ section.settings.slides_per_view_desktop }};
    --ck-per-view-tablet: {{ section.settings.slides_per_view_tablet }};
    --ck-per-view-mobile: {{ section.settings.slides_per_view_mobile }};
    --ck-gap: {{ section.settings.gap }}px;
    --ck-intro-w: {{ section.settings.intro_width }}%;
    --ck-card-bg: {{ section.settings.card_background }};
    --ck-card-size: {{ section.settings.card_text_size }}px;
    --ck-star-color: {{ section.settings.star_color }};
    --ck-star-size: {{ section.settings.star_size }}px;
    --ck-star-empty: {{ section.settings.star_empty_color }};
    --ck-badge-bg: {{ section.settings.badge_background }};
    --ck-badge-fg: {{ section.settings.badge_text }};
    --ck-arrow-color: {{ section.settings.arrow_color }};
    --ck-arrow-size: {{ section.settings.arrow_size }}px;"""
prod_settings = [
    hdr("Products"),
    {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "Meet the best sellers"},
    {"type": "richtext", "id": "text", "label": "Text"},
    {"type": "collection", "id": "collection", "label": "Collection"},
    rng("products_to_show", "Products to show", 2, 16, 1, 8),
    rng("intro_width", "Heading column width (desktop)", 15, 50, 1, 30, "%"),
    rng("slides_per_view_desktop", "Cards visible (desktop)", 1, 6, 1, 3),
    rng("slides_per_view_tablet", "Cards visible (tablet)", 1, 4, 1, 2),
    rng("slides_per_view_mobile", "Cards visible (mobile)", 1, 4, 1, 1),
    rng("gap", "Gap", 0, 60, 2, 12, "px"),
    color("card_background", "Image background", "#ffffff"),
    rng("card_text_size", "Card text size", 10, 22, 1, 14, "px"),
    chk("show_rating", "Show star rating (product reviews metafield)", True),
    color("star_color", "Star color", "#F4B400"),
    color("star_empty_color", "Empty star color", "#D9D9D9"),
    rng("star_size", "Star size", 8, 24, 1, 14, "px"),
    chk("show_sale_badge", "Show sale badge", True),
    {"type": "text", "id": "sale_badge_label", "label": "Sale badge text", "default": "Save more!"},
    color("badge_background", "Badge background", "#ffffff"),
    color("badge_text", "Badge text", "#000000"),
    {"type": "text", "id": "from_label", "label": "'From' price label", "default": "From"},
    chk("show_add_to_cart", "Show add to cart", True),
    {"type": "text", "id": "add_to_cart_label", "label": "Add to cart label", "default": "Add to cart +"},
    {"type": "text", "id": "sold_out_label", "label": "Sold out label", "default": "Sold out"},
    chk("show_arrows", "Show arrows", True),
    color("arrow_color", "Arrow color", "#000000"),
    rng("arrow_size", "Arrow size", 16, 56, 2, 28, "px"),
    {"type": "text", "id": "previous_label", "label": "Previous button label (screen readers)", "default": "Previous products"},
    {"type": "text", "id": "next_label", "label": "Next button label (screen readers)", "default": "Next products"},
]
prod_css = """
.{C} .ck-prod__layout { display: flex; flex-direction: column; gap: var(--ck-gap); align-items: stretch; }
.{C} .ck-prod__text { margin-top: var(--ck-gap); }
.{C} .ck-prod__scroller { position: relative; display: flex; align-items: center; gap: var(--ck-gap); min-width: 0; }
.{C} .ck-prod__track { list-style: none; margin: 0; padding: 0; display: flex; gap: var(--ck-gap); overflow-x: auto; scroll-snap-type: x mandatory; scroll-behavior: smooth; scrollbar-width: none; flex: 1; min-width: 0; }
.{C} .ck-prod__track::-webkit-scrollbar { display: none; }
.{C} .ck-prod__card { flex: 0 0 calc((100% - var(--ck-gap) * (var(--ck-per-view-mobile) - 1)) / var(--ck-per-view-mobile)); scroll-snap-align: start; display: flex; flex-direction: column; align-items: center; gap: var(--ck-gap); text-align: center; font-size: var(--ck-card-size); }
.{C} .ck-prod__media { position: relative; display: block; width: 100%; aspect-ratio: 1; background: var(--ck-card-bg); overflow: hidden; border-radius: var(--ck-radius); }
.{C} .ck-prod__img { width: 100%; height: 100%; object-fit: cover; display: block; }
.{C} .ck-prod__badge { position: absolute; top: var(--ck-gap); left: var(--ck-gap); background: var(--ck-badge-bg); color: var(--ck-badge-fg); font-weight: var(--ck-btn-weight); text-transform: uppercase; font-size: calc(var(--ck-card-size) * 0.75); padding: calc(var(--ck-gap) / 3) calc(var(--ck-gap) / 1.5); }
.{C} .ck-prod__title { color: inherit; text-decoration: none; font-weight: var(--ck-btn-weight); }
.{C} .ck-prod__rating { display: inline-flex; align-items: center; gap: calc(var(--ck-gap) / 2); }
.{C} .ck-prod__stars { display: inline-block; width: calc(var(--ck-star-size) * 5); height: var(--ck-star-size); background: linear-gradient(90deg, var(--ck-star-color) var(--ck-rating), var(--ck-star-empty) var(--ck-rating)); -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 2l3 7h7l-5.5 4.5 2 7.5-6.5-4.5-6.5 4.5 2-7.5L2 9h7z'/%3E%3C/svg%3E"); mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 2l3 7h7l-5.5 4.5 2 7.5-6.5-4.5-6.5 4.5 2-7.5L2 9h7z'/%3E%3C/svg%3E"); -webkit-mask-size: var(--ck-star-size) var(--ck-star-size); mask-size: var(--ck-star-size) var(--ck-star-size); -webkit-mask-repeat: repeat-x; mask-repeat: repeat-x; }
.{C} .ck-prod__compare { opacity: 0.6; }
.{C} .ck-prod__form { margin: 0; }
.{C} .ck-prod__atc[disabled] { opacity: 0.5; cursor: not-allowed; }
.{C} .ck-prod__arrow { flex: 0 0 auto; width: var(--ck-arrow-size); height: var(--ck-arrow-size); padding: 0; border: 0; background: none; color: var(--ck-arrow-color); cursor: pointer; }
.{C} .ck-prod__arrow[disabled] { opacity: 0.3; cursor: default; }
@media screen and (min-width: 750px) {
  .{C} .ck-prod__card { flex-basis: calc((100% - var(--ck-gap) * (var(--ck-per-view-tablet) - 1)) / var(--ck-per-view-tablet)); }
}
@media screen and (min-width: 990px) {
  .{C} .ck-prod__layout { flex-direction: row; align-items: center; }
  .{C} .ck-prod__intro { flex: 0 0 var(--ck-intro-w); }
  .{C} .ck-prod__scroller { flex: 1; }
  .{C} .ck-prod__card { flex-basis: calc((100% - var(--ck-gap) * (var(--ck-per-view) - 1)) / var(--ck-per-view)); }
}
"""
SCROLLER_JS = """
if (!customElements.get('ck-scroller')) {
  class CkScroller extends HTMLElement {
    connectedCallback() {
      this.track = this.querySelector('[data-track]');
      this.prev = this.querySelector('[data-prev]');
      this.next = this.querySelector('[data-next]');
      if (!this.track) return;
      this.onPrev = () => this.track.scrollBy({ left: -this.track.clientWidth, behavior: 'smooth' });
      this.onNext = () => this.track.scrollBy({ left: this.track.clientWidth, behavior: 'smooth' });
      this.onScroll = () => this.update();
      this.prev && this.prev.addEventListener('click', this.onPrev);
      this.next && this.next.addEventListener('click', this.onNext);
      this.track.addEventListener('scroll', this.onScroll, { passive: true });
      this.update();
    }
    disconnectedCallback() {
      if (!this.track) return;
      this.prev && this.prev.removeEventListener('click', this.onPrev);
      this.next && this.next.removeEventListener('click', this.onNext);
      this.track.removeEventListener('scroll', this.onScroll);
    }
    update() {
      const max = this.track.scrollWidth - this.track.clientWidth - 1;
      if (this.prev) this.prev.disabled = this.track.scrollLeft <= 0;
      if (this.next) this.next.disabled = this.track.scrollLeft >= max;
    }
  }
  customElements.define('ck-scroller', CkScroller);
}
document.addEventListener('shopify:section:load', () => {});
document.addEventListener('shopify:section:unload', () => {});
"""
prod_blocks = [{"type": "demo", "name": "Demo card (no collection)", "settings": [
    {"type": "image_picker", "id": "image", "label": "Image"},
    {"type": "text", "id": "title", "label": "Title", "default": "Product name"},
    {"type": "text", "id": "price", "label": "Price text", "default": "$20"},
    rng("rating", "Rating (out of 50, 50 = 5 stars)", 0, 50, 1, 48),
    {"type": "text", "id": "review_count", "label": "Review count", "default": "1,024"},
    {"type": "text", "id": "badge", "label": "Badge (optional)"},
    {"type": "url", "id": "link", "label": "Link"},
]}]
build("ck-product-carousel", "Clone: product carousel", prod_body, prod_vars, prod_settings, prod_css, SCROLLER_JS,
      blocks=prod_blocks, max_blocks=12, preset_blocks=[{"type": "demo"}, {"type": "demo"}, {"type": "demo"}, {"type": "demo"}],
      d=dict(bg="#C4E9F2", heading_color="#496CA4", h_size=48, h_size_m=32, pad_top=40, pad_bottom=40,
             align="center", width=1400, btn_size=12, btn_px=14, btn_py=8))

# ================================================================ 6. IMAGE + TEXT
it_body = """
<div class="ck-it__grid" data-media="{{ section.settings.media_position }}">
  <div class="ck-it__media">
    {%- if section.settings.image != blank -%}
      """ + img_tag("section.settings.image", "ck-it__img", "375, 550, 750, 1100, 1500", "(min-width: 750px) 50vw, 100vw") + """
    {%- else -%}
      {{ 'lifestyle-2' | placeholder_svg_tag: 'ck-it__img ck-it__ph' }}
    {%- endif -%}
  </div>
  <div class="ck-it__content">
    <div class="ck-it__box">
      {%- if section.settings.heading != blank -%}<h2 class="ck-heading">{{ section.settings.heading }}</h2>{%- endif -%}
      {%- if section.settings.text != blank -%}<div class="ck-text ck-it__text">{{ section.settings.text }}</div>{%- endif -%}
      {%- if section.settings.button_label != blank -%}<a class="ck-btn ck-it__btn" href="{{ section.settings.button_link | default: routes.all_products_collection_url }}">{{ section.settings.button_label | escape }}</a>{%- endif -%}
    </div>
  </div>
</div>
"""
it_vars = """
    --ck-media-w: {{ section.settings.media_width }}%;
    --ck-min-h: {{ section.settings.min_height_desktop }}px;
    --ck-min-h-m: {{ section.settings.min_height_mobile }}px;
    --ck-box-w: {{ section.settings.text_box_width }}px;
    --ck-text-gap: {{ section.settings.text_gap }}px;
    --ck-content-bg: {{ section.settings.content_background }};
    --ck-valign: {{ section.settings.vertical_alignment }};
    --ck-fit: {{ section.settings.image_fit }};"""
it_settings = [
    hdr("Image with text"),
    {"type": "image_picker", "id": "image", "label": "Image"},
    sel("image_fit", "Image fit", "cover", [("cover", "Fill"), ("contain", "Fit")]),
    sel("media_position", "Image position (desktop)", "left", [("left", "Left"), ("right", "Right")]),
    rng("media_width", "Image width (desktop)", 30, 70, 5, 50, "%"),
    rng("min_height_desktop", "Height (desktop)", 200, 1200, 20, 720, "px"),
    rng("min_height_mobile", "Image height (mobile)", 200, 800, 20, 360, "px"),
    color("content_background", "Text side background", "#FFEFAF"),
    sel("vertical_alignment", "Text vertical position", "center", [("flex-start", "Top"), ("center", "Middle"), ("flex-end", "Bottom")]),
    rng("text_box_width", "Text box width", 240, 800, 20, 480, "px"),
    rng("text_gap", "Space between text items", 0, 48, 2, 16, "px"),
    {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "Tell your product story here"},
    {"type": "richtext", "id": "text", "label": "Text", "default": "<p>Use this block to explain what makes your product different, in two or three short sentences.</p>"},
    {"type": "text", "id": "button_label", "label": "Button label", "default": "Learn more"},
    {"type": "url", "id": "button_link", "label": "Button link"},
]
it_css = """
.{C} .ck-it__grid { display: flex; flex-direction: column; }
.{C} .ck-it__media { position: relative; height: var(--ck-min-h-m); overflow: hidden; }
.{C} .ck-it__img { width: 100%; height: 100%; object-fit: var(--ck-fit); display: block; }
.{C} .ck-it__content { background: var(--ck-content-bg); display: flex; align-items: var(--ck-valign); justify-content: center; padding: var(--ck-pad-top-m) var(--ck-gutter) var(--ck-pad-bottom-m); }
.{C} .ck-it__box { max-width: var(--ck-box-w); }
.{C} .ck-it__text, .{C} .ck-it__btn { margin-top: var(--ck-text-gap); }
@media screen and (min-width: 750px) {
  .{C} .ck-it__grid { flex-direction: row; min-height: var(--ck-min-h); }
  .{C} .ck-it__grid[data-media="right"] { flex-direction: row-reverse; }
  .{C} .ck-it__media { flex: 0 0 var(--ck-media-w); height: auto; }
  .{C} .ck-it__content { flex: 1; padding: var(--ck-pad-top) var(--ck-gutter) var(--ck-pad-bottom); }
}
"""
build("ck-image-text", "Clone: image with text", it_body, it_vars, it_settings, it_css, None,
      d=dict(bg="#FFEFAF", fg="#000000", b_size=18, b_size_m=16, pad_top=48, pad_bottom=48, full=True, gutter=32,
             btn_bg="#ffffff", btn_fg="#000000", btn_hover="#f2f2f2", btn_border="#000000", btn_border_w=2))

# ================================================================ 7. LOGO STRIP
logo_body = """
<div class="ck-inner">
  {%- if section.settings.heading != blank -%}<h2 class="ck-heading ck-logos__heading">{{ section.settings.heading }}</h2>{%- endif -%}
  <ul class="ck-logos__list" role="list">
    {%- for block in section.blocks -%}
      <li class="ck-logos__item" {{ block.shopify_attributes }}>
        {%- if block.settings.link != blank -%}<a href="{{ block.settings.link }}" class="ck-logos__link">{%- endif -%}
        {%- if block.settings.image != blank -%}
          """ + img_tag("block.settings.image", "ck-logos__img", "150, 300, 450", "200px") + """
        {%- else -%}
          <span class="ck-logos__name">{{ block.settings.name | escape }}</span>
        {%- endif -%}
        {%- if block.settings.link != blank -%}</a>{%- endif -%}
      </li>
    {%- endfor -%}
  </ul>
</div>
"""
logo_vars = """
    --ck-gap: {{ section.settings.gap }}px;
    --ck-logo-h: {{ section.settings.logo_height }}px;
    --ck-logo-h-m: {{ section.settings.logo_height_mobile }}px;
    --ck-logo-opacity: {{ section.settings.logo_opacity | divided_by: 100.0 }};
    --ck-logo-filter: {% if section.settings.logos_white %}brightness(0) invert(1){% else %}none{% endif %};"""
logo_settings = [
    hdr("Logos"),
    {"type": "inline_richtext", "id": "heading", "label": "Heading (optional)"},
    rng("logo_height", "Logo height (desktop)", 16, 120, 2, 40, "px"),
    rng("logo_height_mobile", "Logo height (mobile)", 12, 80, 2, 26, "px"),
    rng("gap", "Gap", 8, 120, 4, 64, "px"),
    rng("logo_opacity", "Logo opacity", 20, 100, 5, 100, "%"),
    chk("logos_white", "Make logos white", True),
]
logo_blocks = [{"type": "logo", "name": "Logo", "settings": [
    {"type": "image_picker", "id": "image", "label": "Logo image"},
    {"type": "text", "id": "name", "label": "Name (shown when no image)", "default": "Press logo"},
    {"type": "url", "id": "link", "label": "Link"},
]}]
logo_css = """
.{C} .ck-logos__heading { margin-bottom: var(--ck-gap); }
.{C} .ck-logos__list { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: var(--ck-gap); }
.{C} .ck-logos__item { opacity: var(--ck-logo-opacity); }
.{C} .ck-logos__link { display: block; color: inherit; text-decoration: none; }
.{C} .ck-logos__img { height: var(--ck-logo-h-m); width: auto; display: block; filter: var(--ck-logo-filter); }
.{C} .ck-logos__name { font-family: var(--ck-heading-font); font-weight: var(--ck-h-weight); font-size: calc(var(--ck-logo-h-m) * 0.6); line-height: 1; }
@media screen and (min-width: 750px) {
  .{C} .ck-logos__img { height: var(--ck-logo-h); }
  .{C} .ck-logos__name { font-size: calc(var(--ck-logo-h) * 0.6); }
}
"""
build("ck-logo-strip", "Clone: logo strip", logo_body, logo_vars, logo_settings, logo_css, None,
      blocks=logo_blocks, max_blocks=10,
      preset_blocks=[{"type": "logo", "settings": {"name": f"Logo {i}"}} for i in range(1, 5)],
      d=dict(bg="#496CA4", fg="#ffffff", heading_color="#ffffff", pad_top=28, pad_bottom=28, pad_top_m=20, pad_bottom_m=20))

# ================================================================ 8. RICH TEXT + MEDIA
rm_body = """
<div class="ck-inner">
  {%- if section.settings.heading != blank -%}<h2 class="ck-heading ck-rm__heading">{{ section.settings.heading }}</h2>{%- endif -%}
  {%- if section.settings.text != blank -%}<div class="ck-text ck-rm__text">{{ section.settings.text }}</div>{%- endif -%}
  <div class="ck-rm__media">
    {%- if section.settings.video != blank -%}
      {{ section.settings.video | video_tag: image_size: '1100x', autoplay: section.settings.video_autoplay, loop: section.settings.video_autoplay, muted: section.settings.video_autoplay, controls: section.settings.video_controls, class: 'ck-rm__video' }}
    {%- elsif section.settings.image != blank -%}
      """ + img_tag("section.settings.image", "ck-rm__img", "375, 550, 750, 1100, 1500", "(min-width: 990px) 60vw, 100vw") + """
    {%- else -%}
      {{ 'lifestyle-2' | placeholder_svg_tag: 'ck-rm__img' }}
    {%- endif -%}
  </div>
  {%- if section.settings.link_label != blank -%}
    <a class="{% if section.settings.link_style == 'button' %}ck-btn{% else %}ck-rm__link{% endif %} ck-rm__cta" href="{{ section.settings.link | default: routes.root_url }}">{{ section.settings.link_label | escape }}</a>
  {%- endif -%}
</div>
"""
rm_vars = """
    --ck-media-max: {{ section.settings.media_width }}px;
    --ck-media-ratio: {{ section.settings.media_ratio }};
    --ck-text-gap: {{ section.settings.text_gap }}px;
    --ck-link-color: {{ section.settings.link_color }};
    --ck-link-size: {{ section.settings.link_size }}px;"""
rm_settings = [
    hdr("Media"),
    {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "We know you'll love these products as much as we do!"},
    {"type": "richtext", "id": "text", "label": "Text"},
    {"type": "video", "id": "video", "label": "Video (Shopify hosted)"},
    chk("video_autoplay", "Autoplay video (muted, looping)", False),
    chk("video_controls", "Show video controls", True),
    {"type": "image_picker", "id": "image", "label": "Image (used when no video)"},
    rng("media_width", "Media width", 240, 1400, 20, 820, "px"),
    sel("media_ratio", "Media shape", "16 / 9", [("16 / 9", "Wide"), ("4 / 3", "Landscape"), ("1 / 1", "Square"), ("auto", "Original")]),
    rng("text_gap", "Space between items", 0, 60, 2, 24, "px"),
    {"type": "text", "id": "link_label", "label": "Link label", "default": "Check out our guarantee"},
    {"type": "url", "id": "link", "label": "Link"},
    sel("link_style", "Link style", "link", [("link", "Text link"), ("button", "Button")]),
    color("link_color", "Text link color", "#427D8A"),
    rng("link_size", "Text link size", 10, 24, 1, 14, "px"),
]
rm_css = """
.{C} .ck-rm__text { margin-top: var(--ck-text-gap); }
.{C} .ck-rm__media { max-width: var(--ck-media-max); margin: var(--ck-text-gap) auto 0; aspect-ratio: var(--ck-media-ratio); overflow: hidden; border-radius: var(--ck-radius); }
.{C} .ck-rm__img, .{C} .ck-rm__video { width: 100%; height: 100%; object-fit: cover; display: block; }
.{C} .ck-rm__cta { display: inline-block; margin-top: var(--ck-text-gap); }
.{C} .ck-rm__link { color: var(--ck-link-color); font-size: var(--ck-link-size); font-weight: var(--ck-btn-weight); text-decoration: none; }
.{C} .ck-rm__link:hover { text-decoration: underline; }
"""
build("ck-rich-media", "Clone: text + media", rm_body, rm_vars, rm_settings, rm_css, None,
      d=dict(pad_top=48, pad_bottom=56, btn_bg="#ffffff", btn_fg="#000000", btn_hover="#f2f2f2", btn_border="#000000", btn_border_w=2))

# ================================================================ 9. TESTIMONIALS
tm_body = """
<div class="ck-inner">
  {%- if section.settings.icon != blank -%}
    <div class="ck-tm__icon">""" + img_tag("section.settings.icon", "ck-tm__icon-img", "100, 200, 300", "120px") + """</div>
  {%- endif -%}
  {%- if section.settings.heading != blank -%}<h2 class="ck-heading">{{ section.settings.heading }}</h2>{%- endif -%}
  <ck-slider class="ck-tm__slider" data-autoplay="{{ section.settings.autoplay }}" data-interval="{{ section.settings.autoplay_interval }}" data-loop="{{ section.settings.loop }}">
    {%- if section.settings.show_arrows and section.blocks.size > 1 -%}
      <button type="button" class="ck-tm__arrow ck-tm__arrow--prev" data-prev aria-label="{{ section.settings.previous_label | escape }}">""" + ARROW_L + """</button>
    {%- endif -%}
    <div class="ck-tm__track">
      {%- for block in section.blocks -%}
        <figure class="ck-tm__slide{% if forloop.first %} is-active{% endif %}" data-slide {{ block.shopify_attributes }}>
          <blockquote class="ck-tm__quote">{{ block.settings.quote }}</blockquote>
          <figcaption class="ck-tm__name">{{ block.settings.name | escape }}</figcaption>
        </figure>
      {%- endfor -%}
    </div>
    {%- if section.settings.show_arrows and section.blocks.size > 1 -%}
      <button type="button" class="ck-tm__arrow ck-tm__arrow--next" data-next aria-label="{{ section.settings.next_label | escape }}">""" + ARROW_R + """</button>
    {%- endif -%}
    {%- if section.settings.show_dots and section.blocks.size > 1 -%}
      <div class="ck-tm__dots">
        {%- for block in section.blocks -%}
          <button type="button" class="ck-tm__dot{% if forloop.first %} is-active{% endif %}" data-dot aria-label="{{ section.settings.next_label | escape }} {{ forloop.index }}"></button>
        {%- endfor -%}
      </div>
    {%- endif -%}
  </ck-slider>
</div>
"""
tm_vars = """
    --ck-icon-w: {{ section.settings.icon_width }}px;
    --ck-quote-size: {{ section.settings.quote_size }}px;
    --ck-name-size: {{ section.settings.name_size }}px;
    --ck-text-gap: {{ section.settings.text_gap }}px;
    --ck-speed: {{ section.settings.transition_speed }}ms;
    --ck-arrow-color: {{ section.settings.arrow_color }};
    --ck-arrow-size: {{ section.settings.arrow_size }}px;
    --ck-dot-color: {{ section.settings.dot_color }};
    --ck-dot-size: {{ section.settings.dot_size }}px;"""
tm_settings = [
    hdr("Reviews"),
    {"type": "image_picker", "id": "icon", "label": "Icon above heading"},
    rng("icon_width", "Icon width", 24, 200, 4, 80, "px"),
    {"type": "inline_richtext", "id": "heading", "label": "Heading", "default": "One of thousands of five-star reviews:"},
    rng("quote_size", "Quote size", 12, 40, 1, 18, "px"),
    rng("name_size", "Name size", 10, 24, 1, 13, "px"),
    rng("text_gap", "Space between items", 0, 48, 2, 16, "px"),
    chk("autoplay", "Autoplay", True),
    rng("autoplay_interval", "Autoplay interval", 2, 12, 1, 5, "s"),
    rng("transition_speed", "Transition speed", 100, 1500, 50, 400, "ms"),
    chk("loop", "Loop", True),
    chk("show_arrows", "Show arrows", True),
    chk("show_dots", "Show dots", True),
    color("arrow_color", "Arrow color", "#427D8A"),
    rng("arrow_size", "Arrow size", 16, 56, 2, 28, "px"),
    color("dot_color", "Dot color", "#427D8A"),
    rng("dot_size", "Dot size", 4, 16, 1, 6, "px"),
    {"type": "text", "id": "previous_label", "label": "Previous button label (screen readers)", "default": "Previous review"},
    {"type": "text", "id": "next_label", "label": "Next button label (screen readers)", "default": "Next review"},
]
tm_blocks = [{"type": "review", "name": "Review", "settings": [
    {"type": "richtext", "id": "quote", "label": "Quote", "default": "<p>“Write a short customer review here.”</p>"},
    {"type": "text", "id": "name", "label": "Name", "default": "Customer name"},
]}]
tm_css = """
.{C} .ck-tm__icon { width: var(--ck-icon-w); margin: 0 auto var(--ck-text-gap); }
.{C} .ck-tm__icon-img { width: 100%; height: auto; display: block; }
.{C} .ck-tm__slider { display: grid; grid-template-columns: var(--ck-arrow-size) 1fr var(--ck-arrow-size); align-items: center; gap: var(--ck-text-gap); margin-top: var(--ck-text-gap); }
.{C} .ck-tm__track { display: grid; grid-column: 2; }
.{C} .ck-tm__slide { grid-area: 1 / 1; margin: 0; opacity: 0; visibility: hidden; transition: opacity var(--ck-speed) ease, visibility var(--ck-speed) ease; }
.{C} .ck-tm__slide.is-active { opacity: 1; visibility: visible; }
.{C} .ck-tm__quote { margin: 0; padding: 0; border: 0; font-style: normal; font-size: var(--ck-quote-size); }
.{C} .ck-tm__quote::before, .{C} .ck-tm__quote::after { content: none; }
.{C} .ck-tm__quote p { margin: 0; }
.{C} .ck-tm__name { margin-top: calc(var(--ck-text-gap) / 2); font-size: var(--ck-name-size); }
.{C} .ck-tm__arrow { width: var(--ck-arrow-size); height: var(--ck-arrow-size); padding: 0; border: 0; background: none; color: var(--ck-arrow-color); cursor: pointer; }
.{C} .ck-tm__arrow--prev { grid-column: 1; grid-row: 1; }
.{C} .ck-tm__arrow--next { grid-column: 3; grid-row: 1; }
.{C} .ck-tm__dots { grid-column: 1 / -1; display: flex; justify-content: center; gap: var(--ck-dot-size); }
.{C} .ck-tm__dot { width: var(--ck-dot-size); height: var(--ck-dot-size); padding: 0; border: 0; border-radius: 50%; background: var(--ck-dot-color); opacity: 0.3; cursor: pointer; }
.{C} .ck-tm__dot.is-active { opacity: 1; }
"""
build("ck-testimonials", "Clone: review slider", tm_body, tm_vars, tm_settings, tm_css, SLIDER_JS,
      blocks=tm_blocks, max_blocks=12,
      preset_blocks=[{"type": "review"}, {"type": "review"}, {"type": "review"}],
      d=dict(heading_color="#427D8A", pad_top=40, pad_bottom=40, width=1600))

# ================================================================ 10. FOOTER
ft_body = """
<div class="ck-inner ck-ft__top">
  <div class="ck-ft__brand">
    <a href="{{ routes.root_url }}" class="ck-ft__logo">
      {%- if section.settings.logo != blank -%}
        """ + img_tag("section.settings.logo", "ck-ft__logo-img", "100, 200, 300", "120px") + """
      {%- else -%}
        <span class="ck-heading">{{ shop.name | escape }}</span>
      {%- endif -%}
    </a>
  </div>
  {%- for block in section.blocks -%}
    <nav class="ck-ft__col" {{ block.shopify_attributes }}>
      {%- if block.settings.title != blank -%}<p class="ck-ft__title">{{ block.settings.title | escape }}</p>{%- endif -%}
      {%- if block.settings.menu != blank -%}
        <ul class="ck-ft__links" role="list">
          {%- for link in block.settings.menu.links -%}
            <li><a href="{{ link.url }}">{{ link.title | escape }}</a></li>
          {%- endfor -%}
        </ul>
      {%- endif -%}
    </nav>
  {%- endfor -%}
  {%- if section.settings.show_newsletter -%}
    <div class="ck-ft__news">
      {%- if section.settings.newsletter_heading != blank -%}<p class="ck-ft__title">{{ section.settings.newsletter_heading | escape }}</p>{%- endif -%}
      {%- form 'customer', class: 'ck-ft__form' -%}
        <input type="hidden" name="contact[tags]" value="newsletter">
        <input class="ck-ft__input" type="email" name="contact[email]" required autocomplete="email" placeholder="{{ section.settings.email_placeholder | escape }}" aria-label="{{ section.settings.email_placeholder | escape }}">
        <button type="submit" class="ck-ft__submit" aria-label="{{ section.settings.submit_label | escape }}">""" + ARROW_R + """</button>
        {%- if form.posted_successfully? -%}<p class="ck-ft__ok">{{ section.settings.success_message | escape }}</p>{%- endif -%}
      {%- endform -%}
      {%- if section.settings.newsletter_note != blank -%}<div class="ck-ft__note">{{ section.settings.newsletter_note }}</div>{%- endif -%}
      {%- if section.settings.show_social -%}{% render 'social-icons', class: 'ck-ft__social' %}{%- endif -%}
    </div>
  {%- endif -%}
</div>
<div class="ck-inner ck-ft__bottom">
  <span>{{ section.settings.copyright_prefix | escape }} {{ 'now' | date: '%Y' }} {{ shop.name | escape }}</span>
  {%- if section.settings.show_policies -%}
    {%- for policy in shop.policies -%}<a href="{{ policy.url }}">{{ policy.title | escape }}</a>{%- endfor -%}
  {%- endif -%}
</div>
"""
ft_vars = """
    --ck-cols: {{ section.settings.columns_desktop }};
    --ck-cols-tablet: {{ section.settings.columns_tablet }};
    --ck-cols-mobile: {{ section.settings.columns_mobile }};
    --ck-gap: {{ section.settings.gap }}px;
    --ck-logo-w: {{ section.settings.logo_width }}px;
    --ck-title-size: {{ section.settings.title_size }}px;
    --ck-link-size: {{ section.settings.link_size }}px;
    --ck-link-gap: {{ section.settings.link_gap }}px;
    --ck-line: {{ section.settings.line_color }};
    --ck-small-size: {{ section.settings.small_size }}px;"""
ft_settings = [
    hdr("Footer"),
    {"type": "image_picker", "id": "logo", "label": "Logo"},
    rng("logo_width", "Logo width", 40, 300, 10, 100, "px"),
    rng("columns_desktop", "Columns (desktop)", 2, 6, 1, 5),
    rng("columns_tablet", "Columns (tablet)", 1, 4, 1, 3),
    rng("columns_mobile", "Columns (mobile)", 1, 4, 1, 2),
    rng("gap", "Gap", 8, 80, 4, 32, "px"),
    rng("title_size", "Column title size", 10, 24, 1, 14, "px"),
    rng("link_size", "Link size", 10, 20, 1, 13, "px"),
    rng("link_gap", "Space between links", 0, 20, 1, 6, "px"),
    rng("small_size", "Bottom text size", 9, 16, 1, 11, "px"),
    color("line_color", "Line color", "#000000"),
    chk("show_newsletter", "Show newsletter", True),
    {"type": "text", "id": "newsletter_heading", "label": "Newsletter heading", "default": "Our emails are (almost) as fun as we are."},
    {"type": "text", "id": "email_placeholder", "label": "Email placeholder", "default": "Email address"},
    {"type": "text", "id": "submit_label", "label": "Submit label (screen readers)", "default": "Subscribe"},
    {"type": "text", "id": "success_message", "label": "Success message", "default": "Thanks for subscribing!"},
    {"type": "richtext", "id": "newsletter_note", "label": "Small print under form"},
    chk("show_social", "Show social icons (set links in Theme settings)", True),
    {"type": "text", "id": "copyright_prefix", "label": "Copyright prefix", "default": "©"},
    chk("show_policies", "Show policy links", True),
]
ft_blocks = [{"type": "menu", "name": "Link column", "settings": [
    {"type": "text", "id": "title", "label": "Title", "default": "Shop"},
    {"type": "link_list", "id": "menu", "label": "Menu", "default": "footer"},
]}]
ft_css = """
.{C} { text-align: left; }
.{C} .ck-ft__top { display: grid; gap: var(--ck-gap); grid-template-columns: repeat(var(--ck-cols-mobile), minmax(0, 1fr)); }
.{C} .ck-ft__brand, .{C} .ck-ft__news { grid-column: 1 / -1; }
.{C} .ck-ft__logo { display: inline-block; color: inherit; text-decoration: none; }
.{C} .ck-ft__logo-img { width: var(--ck-logo-w); height: auto; display: block; }
.{C} .ck-ft__title { margin: 0 0 var(--ck-link-gap); font-size: var(--ck-title-size); font-weight: var(--ck-h-weight); }
.{C} .ck-ft__links { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--ck-link-gap); }
.{C} .ck-ft__links a, .{C} .ck-ft__bottom a { color: inherit; text-decoration: none; font-size: var(--ck-link-size); }
.{C} .ck-ft__links a:hover, .{C} .ck-ft__bottom a:hover { text-decoration: underline; }
.{C} .ck-ft__form { display: flex; align-items: center; border-bottom: 1px solid var(--ck-line); }
.{C} .ck-ft__input { flex: 1; border: 0; background: transparent; color: inherit; font: inherit; font-size: var(--ck-link-size); padding: var(--ck-link-gap) 0; outline-offset: 2px; }
.{C} .ck-ft__submit { width: var(--ck-title-size); height: var(--ck-title-size); border: 0; padding: 0; background: none; color: inherit; cursor: pointer; }
.{C} .ck-ft__ok, .{C} .ck-ft__note { font-size: var(--ck-small-size); margin-top: var(--ck-link-gap); }
.{C} .ck-ft__social { margin-top: var(--ck-link-gap); justify-content: flex-start; }
.{C} .ck-ft__bottom { display: flex; flex-wrap: wrap; gap: var(--ck-link-gap) var(--ck-gap); margin-top: var(--ck-gap); font-size: var(--ck-small-size); }
.{C} .ck-ft__bottom a { font-size: var(--ck-small-size); }
@media screen and (min-width: 750px) {
  .{C} .ck-ft__top { grid-template-columns: repeat(var(--ck-cols-tablet), minmax(0, 1fr)); }
}
@media screen and (min-width: 990px) {
  .{C} .ck-ft__top { grid-template-columns: repeat(var(--ck-cols), minmax(0, 1fr)); }
  .{C} .ck-ft__brand { grid-column: auto; }
  .{C} .ck-ft__news { grid-column: span 2; }
}
"""
build("ck-footer", "Clone: footer", ft_body, ft_vars, ft_settings, ft_css, None,
      blocks=ft_blocks, max_blocks=4,
      preset_blocks=[{"type": "menu", "settings": {"title": "Shop"}}, {"type": "menu", "settings": {"title": "Help"}}],
      d=dict(bg="#F9DE6E", fg="#000000", pad_top=40, pad_bottom=24, align="left", width=1400), tag="footer")
