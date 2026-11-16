"""Write templates/index.json for the أساس demo homepage (copy: 2-الكاتب/06-website-copy.md).
Usage: python build_index.py <theme_dir>
No invented reviews, numbers or guarantees: every claim the brand must prove shows a placeholder chip.
"""
import json, os, sys

THEME = sys.argv[1]
P = lambda *ps: "".join(f"<p>{x}</p>" for x in ps)
NOTE = "سعر تجريبي"
sections, order = {}, []


def add(key, type_, settings, blocks=None):
    sec = {"type": type_, "settings": settings}
    if blocks:
        sec["blocks"] = {f"{key}_{i}": b for i, b in enumerate(blocks, 1)}
        sec["block_order"] = list(sec["blocks"])
    sections[key] = sec
    order.append(key)


def blk(type_, **s):
    return {"type": type_, "settings": s}


# 1. Hero
add("hero", "ck-ec-hero", {
    "heading": "ريحتك تدخل قبلك… وتقعد بعد ما تطلع.",
    "text": P("عطور ودهن عود وبخور مبنية من القاعدة: نبدأ بالعود الحقيقي، وبعدين كل شي ثاني. ونكتب لك على كل عطر كم ساعة يقعد."),
    "button_label": "اكتشف عطرك", "button_link": "shopify://collections/all",
    "link2_label": "جرّب قبل لا تشتري ←",
    "image_alt": "صورة الواجهة",
})

# 0. Marquee (claims the brand must confirm keep a visible marker)
add("marquee", "ck-ec-marquee", {"heading_size": 32, "heading_size_mobile": 18, "speed": 70}, [
    blk("item", text="جرّب قبل القنينة: مجموعة التجربة ينخصم سعرها من طلبك الجاي [يحتاج إثبات]"),
    blk("item", text="ما ثبت معك الساعات المكتوبة؟ رجّعه [يحتاج إثبات]"),
    blk("item", text="يرد عليك إنسان بالواتساب خلال ___ دقيقة"),
    blk("item", text="توصيل داخل الكويت خلال ___ ساعة، مغلّف ضد الحر"),
])

# 2. سمعناها منكم
add("quotes", "ck-ec-quotes", {
    "heading": "إذا قلت وحدة من هذي… مو بروحك.",
    "background_color": "#FFFFFF", "card_background": "#FFE3D7",
    "footer_text": P("المشكلة مو بجلدك. ومو لازم ترش أكثر. المشكلة بطريقة بناء العطر نفسه."),
    "padding_top": 70,
}, [blk("quote", text=t) for t in [
    "«الريحة حلوة… والثبات صفر.»", "«رشّيته الصبح، وقبل الظهر اختفى.»",
    "«دفعت فلوس عطر… وطلع كأنه ماي.»", "«نفس الريحة بالضبط… بس ما يقعد.»"]])

# 3. ليش عطرك يطير؟
add("why", "ck-ec-split", {
    "badge_text": "ليش عطرك يطير؟", "heading": "لأنه مبني من فوق.",
    "text": P("أي عطر له ثلاث طبقات.",
              "<strong>الطبقة الأولى:</strong> أول ريحة تشمها. حلوة، وتطير بعد دقايق.",
              "<strong>الطبقة الوسطى:</strong> تقعد ساعة أو ساعتين.",
              "<strong>القاعدة:</strong> هي اللي تقعد على جلدك وعلى ثوبك لين آخر اليوم.",
              "الريحة الأولى سهلة. أي أحد يقلدها، وأي أحد يحطها بقنينة حلوة. القاعدة هي الغالية. العود الحقيقي، والراتنج، والمسك. وهذي أول شي ينقص بالعطر الرخيص والمقلد.",
              "جذي تشم العطر بالمحل وتقول «يجنن»… وبعد ساعة ما تلاقي منه شي."),
    "button_label": "", "image_asset": "ec-ins-1.png", "image_alt": "",
    "media_position": "start", "panel_alignment": "start", "panel_background": "#FFE3D7", "padding_top": 50,
}, [
    blk("timeline", is_header=True, label="", stage_1="٠ دقيقة", stage_2="ساعة", stage_3="٦ ساعات"),
    blk("timeline", label="عطر مبني من فوق", stage_1="قوي", stage_2="خفيف", stage_3="ما في شي", row_color="#E5E5E5"),
    blk("timeline", label="عطر مبني من القاعدة", stage_1="قوي", stage_2="ثابت", stage_3="لين الحين موجود", row_color="#E5E5E5"),
    blk("note", text=P("رقم الـ ٦ ساعات لعطرنا"), show_proof=True, proof_note="رقم اختبار حقيقي"),
    blk("note", style="big", text=P("الريحة الأولى ديكور… الثبات أساس. وبيت بلا أساس، حتى لو صبغته ذهب، يطيح.")),
])

# 4. الطريقة القديمة
old = [("تدفع على الاسم", "فوق ٢٠٠ دينار… والسؤال نفسه: يثبت؟ الاسم ما يثبّت عطر. القاعدة تثبّته.", "#FFE3D7"),
       ("تاخذ البديل الرخيص", "ينسخ أول ريحة بس. القاعدة اللي تقعد؟ ما تنسخ.", "#F5F5DC"),
       ("تستر من مزاد أو لايف", "«أصلي بس بدون كرتون». لا تعرف شنو بداخله، ولا متى انفتح، ولا وين انحفظ.", "#E6E6FA"),
       ("ترش أكثر", "عشر رشات من عطر بلا قاعدة… تطير بنفس السرعة. بس تزعج اللي جنبك.", "#FFF5E5")]
add("old_way", "ck-ec-cards", {
    "heading": "جربت كل شي؟ هذا ليش ما نفع.", "background_color": "#FFFFFF",
    "columns_desktop": 4, "columns_tablet": 2, "columns_mobile": 1,
    "card_padding": 30, "card_alignment": "start",
    "footer_text": P("<strong>المشكلة وحدة بالأربع: محد يبدأ من القاعدة.</strong>"),
    "padding_top": 70,
}, [blk("card", number=str(i), title=t, text=P(x), card_background=c) for i, (t, x, c) in enumerate(old, 1)])

# 5. مبني من القاعدة (reference: 3 benefit cards)
add("base_intro", "ck-ec-split", {
    "badge_text": "مبني من القاعدة", "heading": "إحنا نبدأ من تحت.",
    "text": P("كل عطر عندنا يبدأ بقاعدته: عود حقيقي، وراتنج، ومسك.",
              "بعدين نبني فوقها الوسط، وآخر شي الريحة الأولى.",
              "يعني الريحة اللي تحبها بأول دقيقة… هي نفسها اللي تلاقيها آخر الليل، بس أهدى."),
    "button_label": "شوف كيف نختبر الثبات ←", "image_alt": "",
    "image_asset": "ec-ins-3.png", "media_position": "start", "panel_background": "#FFF5E5", "padding_top": 50,
}, [blk("note", text=P("مواد القاعدة لكل عطر"), show_proof=True, proof_note="مواد القاعدة لكل عطر")])

add("base", "ck-ec-cards", {
    "heading": "", "padding_top": 60, "padding_bottom": 60,
}, [
    blk("card", image_asset="ec-ft-1.png", title="القاعدة مكتوبة أول شي.",
        text=P("على كل عطر تشوف شنو قاعدته قبل لا تشوف ريحته الأولى.")),
    blk("card", image_asset="ec-ft-2.png", title="الثبات بالساعات، مو بالكلام.",
        text=P("نكتب لك كم ساعة يقعد على الجلد، وعلى الدشداشة، وعلى العباية."),
        show_proof=True, proof_note="ساعات الاختبار + الطريقة"),
    blk("card", image_asset="ec-ft-3.png", title="فوحان واضح.",
        text=P("نقول لك إذا هو عطر «يدخل المكان قبلك» أو عطر «قريب منك»، عشان تختار على مكانك: دوام، ديوانية، عزيمة.")),
])

# 6. تسوّق حسب القسم
cats = [("عطور رجالي", "تقعد على الدشداشة لين آخر الديوانية.", "ec-cat-1.png"),
        ("عطور نسائي", "تمسك بالعباية والشيلة، مو بس بالرشة الأولى.", "ec-cat-2.png"),
        ("للجنسين", "قاعدة عود ومسك تناسب الكل.", "ec-cat-3.png"),
        ("دهن العود", "نقطة وحدة تكفي، إذا كان صدق.", "ec-cat-4.png"),
        ("عود وبخور ومعمول", "للبيت، للدوام، وللعزايم.", "ec-ins-4.png"),
        ("مباخر", "حرارة صح، ريحة صح.", "ec-ins-2.png"),
        ("هدايا", "جاهزة ومغلّفة، على ميزانيتك.", "ec-ins-3.png")]
add("categories", "ck-ec-categories", {"heading": "كل قسم… نفس القاعدة.", "padding_top": 70, "arrows_desktop": True},
    [blk("category", title=t, text=x, image_asset=a, link="shopify://collections/all") for t, x, a in cats])

# 7. الأكثر طلب
perf = [("ec-p-1.jpg", "عود + عنبر + مسك", "قوي", "شتوي", "٢٤ د.ك"),
        ("ec-p-5.jpg", "عود + راتنج + مسك", "متوسط", "طول السنة", "٢٢ د.ك"),
        ("ec-p-4.jpg", "عنبر + مسك", "قريب", "صيفي", "١٨ د.ك"),
        ("ec-p-2.jpg", "عود + مسك", "قوي", "شتوي", "٢٨ د.ك"),
        ("ec-p-10.jpg", "مسك + عنبر", "متوسط", "طول السنة", "٢٠ د.ك"),
        ("ec-p-3.jpg", "عود + عنبر", "قريب", "صيفي", "٢٦ د.ك")]
# Card stays as short as the reference card (brand, name, price); base / ثبات / فوحان / موسم in two short lines.
add("bestsellers", "ck-ec-products", {
    "heading": "الأكثر طلب", "price_note": NOTE, "padding_top": 70,
}, [blk("product", image_asset=img, vendor="أساس", title=f"اسم العطر {n}",
        details=P(f"القاعدة: {base} (مثال) · الثبات: ___ ساعة",
                  f"الفوحان: {f} · الموسم: {season}"),
        price=price, show_proof=True, proof_note="القاعدة والساعات")
    for n, (img, base, f, season, price) in zip("١٢٣٤٥٦", perf)])

# 8. العود الصدق - short like the reference promo panel; the full oud argument is oud_detail below
add("oud", "ck-ec-split", {
    "badge_text": "العود", "heading": "العود الصدق… داخله مثل برّا.",
    "text": P("مثل الذهب. المطلي يلمع من برّا. الصافي ذهب لين داخله."),
    "button_label": "تسوّق العود والبخور", "button_link": "shopify://collections/all", "image_alt": "",
    "image_asset": "ec-promo.png", "panel_background": "#F5F5DC", "padding_top": 50,
})
add("oud_detail", "ck-ec-split", {
    "badge_text": "العود الصدق", "heading": "جرّبها بنفسك",
    "text": P("العود الحقيقي يتكوّن داخل الشجرة على سنين. وقليل من الشجر يطلع منه أصلاً.",
              "عشان جذي السوق امتلى خشب مدهون، وخشب مصبوغ، وريحة «عود» مسوية بالمختبر.",
              "الدهن اللي على السطح يفوح قوي أول دقايق… وبعدين يطير، أو تطلع منه ريحة خشب محروق.",
              "العود الصدق غير. الدهن داخل الخشب نفسه، فالريحة تطلع طبقة ورى طبقة، وتقعد."),
    "button_label": "تسوّق العود والبخور", "button_link": "shopify://collections/all", "image_alt": "",
    "image_asset": "ec-cat-4.png", "media_position": "start", "panel_alignment": "start",
    "panel_background": "#F5F5DC", "badge_background": "#B9AC8A", "padding_top": 50,
}, [
    blk("step", number="١", title="اكسرها:", text=P("إذا لون العودة من داخل مثل برّا، هذي إشارة إنها مو مصبوغة.")),
    blk("step", number="٢", title="بخّرها على حرارة هادية:", text=P("الصدق يطلع طبقات، ويتغيّر ويحلى. المدهون يفوح دفعة وحدة وينطفي.")),
    blk("step", number="٣", title="شم ثوبك بعد ساعة:", text=P("الريحة اللي تقعد… هي اللي كانت داخل.")),
    blk("note", style="box", text=P("وما نسميها «سوبر» و«دبل سوبر». نقول لك وش تناسب: <strong>يومي · دوام · ديوانية · مناسبات</strong>، وسعر كل وحدة واضح وثابت.")),
    blk("note", text=P("شهادة / تحليل لكل دفعة"), show_proof=True, proof_note="شهادة أو تحليل"),
])

# 9. ريحة البيت (reference: featured product row)
add("home_scent", "ck-ec-featured", {
    "tag": "ريحة البيت", "title": "طقم «ريحة البيت»",
    "text": P("معمول يومي + عود للعزايم + مبخرة"),
    "price": "___ د.ك", "price_note": NOTE, "button_label": "خذ طقم ريحة البيت",
    "button_link": "shopify://collections/all",
    "show_proof": True, "proof_note": "مواصفات المبخرة وضمانها",
    "image_alt": "", "side_image_alt": "",
})

add("home_detail", "ck-ec-split", {
    "badge_text": "ريحة البيت", "heading": "بيت ريحته عزايم… حتى بيوم عادي.",
    "text": P("تبي الريحة تمسك بالستاير والكنب، والضيف أول ما يدخل يسأل «وش البخور حقك؟»",
              "السر مو بس بالبخور. السر بالحرارة.",
              "نفس البخور، إذا انحط على جمرة حارة، يطلع دفعة قوية وبعدين ريحة خشب محروق.",
              "وإذا انحط على حرارة هادية، يطلع ناعم وطبقات ويقعد.",
              "<strong>عشان جذي:</strong> كل علبة بخور معها كرت «كيف تبخّر صح»."),
    "button_label": "خذ طقم ريحة البيت", "button_link": "shopify://collections/all", "image_alt": "",
    "image_asset": "ec-hand.png", "panel_background": "#E6E6FA", "media_background": "#E5DCCB", "padding_top": 50,
})

# 10. هدايا
gifts = [("تحت ١٥ د.ك", "للزميل، للجار، للضيف", "ec-p-6.jpg", False, ""),
         ("من ٢٥ لـ ٣٥ د.ك", "للأهل والمناسبات", "ec-p-8.jpg", False, ""),
         ("بوكس على ذوقك", "اختار القطع، ونحط اسمه عليه", "ec-p-7.jpg", True, "البوكس والاسم")]
add("gifts", "ck-ec-products", {
    "heading": "هدية تبيّض الوجه.",
    "subheading": P("العطر هدية ما تنرد. اختار على ميزانيتك، وإحنا نغلّفها ونوصلها على الوقت."),
    "columns_desktop": 4, "price_note": NOTE, "show_vendor": False,
    "footer_text": P("كيس هدية لكل قطعة. وموعد توصيل نقوله لك قبل لا تدفع. [يحتاج إثبات من البراند]"),
    "padding_top": 70,
}, [blk("product", image_asset=img, title=t, details=P(x), price="", show_proof=sp, proof_note=pn)
    for t, x, img, sp, pn in gifts])

# 11. Proof (slots only, never invented reviews)
add("proof", "ck-ec-cards", {
    "heading": "لا تصدقنا… صدّق ثوبك.", "background_color": "#FFFFFF",
    "columns_desktop": 4, "columns_tablet": 2, "card_padding": 30,
    "footer_text": P("«من ٢٠٠٢ صار في ‹عود› يتسوّى بالمختبر» · «قليل من شجر العود يطلع منه راتنج أصلاً»"),
    "padding_top": 70,
}, [blk("card", dashed=True, title="تقييم زبون حقيقي",
        text=P("مكان لتقييم حقيقي من زبائن البراند. ما نكتب تقييمات من عندنا."),
        show_proof=True, proof_note="تقييم حقيقي") for _ in range(3)] + [
    blk("card", dashed=True, title="كيف نختبر الثبات", text=P("الطريقة، والأرقام، وصور."),
        show_proof=True, proof_note="طريقة الاختبار والأرقام")])

# 12. Offer + guarantee
offer = [("مجموعة التجربة:", "عينات من عطورنا. سعرها ينخصم من أول قنينة كاملة تشتريها. (سعر تجريبي: ٦–٩ د.ك)", "محتوى المجموعة والسعر"),
         ("ضمان الثبات:", "إذا ما قعد معك العطر الساعات المكتوبة عليه، رجّعه.", "شروط الضمان"),
         ("ما تدفع على شي مو موجود:", "اللي تشوفه بالموقع موجود عندنا. وإذا صار شي، فلوسك ترجع فوراً.", "سياسة الاسترجاع"),
         ("إنسان يرد عليك:", "بالواتساب، خلال ___ دقيقة بأوقات الدوام.", "وقت الرد")]
add("offer", "ck-ec-cards", {
    "heading": "جرّب أول. ادفع بعدين على اللي حبيته.", "background_color": "#FFECE1",
    "columns_desktop": 4, "columns_tablet": 2, "card_padding": 30, "card_alignment": "start",
    "card_background": "#FFFFFF", "button_label": "اطلب مجموعة التجربة",
    "button_link": "shopify://collections/all", "padding_top": 60, "padding_bottom": 60,
}, [blk("card", number=str(i), title=t, text=P(x), show_proof=True, proof_note=pn)
    for i, (t, x, pn) in enumerate(offer, 1)])

# 13. FAQ
faq = [("كل المحلات تقول ثبات عالي. شنو الفرق عندكم؟", "إحنا نكتب الرقم: كم ساعة على الجلد وكم على الثوب، وكيف اختبرناه. وإذا ما قعد، رجّعه.", True),
       ("أخاف يكون مقلد أو معاد تعبئة.", "عطورنا تركيبتنا إحنا، مو نسخة من ماركة. وتوصلك من عندنا مباشرة، مختومة.", True),
       ("ما أقدر أشم أونلاين. شلون أختار؟", "ابدأ بمجموعة التجربة. وسعرها ينخصم من القنينة الكبيرة.", False),
       ("ليش أدفع ٢٠ دينار وأنا ألقى عطر بـ ٥؟", "اللي بـ ٥ غالباً ينسخ أول ريحة بس. تدفع على القاعدة اللي تقعد، مو على قنينة.", False),
       ("دهن العود ريحته غريبة أول ما حطيته. يعني مغشوش؟", "لا، بالعكس. الدهن الصدق يفتح قوي، وبعدين يهدأ ويقعد قريب من الجلد. نقطة أو نقطتين تكفي، وعطه وقت.", False),
       ("البخور عندي يطلع ريحة خشب محروق. ليش؟", "غالباً الحرارة عالية. حط كسرة صغيرة على حرارة هادية. الكرت اللي مع العلبة يشرح لك.", False),
       ("شلون أعرف إن العود مو مدهون؟", "اكسره وشوف داخله، وبخّره على حرارة هادية وشوف إذا يطلع طبقات. ومع كل دفعة نعطيك ___", True),
       ("العطر يوصل حار من الشمس؟", "نغلّفه ضد الحر ونوصله خلال ___ ساعة.", True),
       ("أبي هدية وما أعرف شنو آخذ.", "اختار ميزانيتك من قسم الهدايا، أو كلّمنا بالواتساب ونختار معك.", False),
       ("إذا خلص المنتج بعد ما دفعت؟", "ما نعرض إلا الموجود. وإذا صار خطأ، فلوسك ترجع فوراً.", True)]
add("faq", "ck-ec-faq", {"heading": "الأسئلة الشائعة", "padding_top": 70},
    [blk("qa", question=q, answer=P(a), show_proof=sp) for q, a, sp in faq])

# 14. Final CTA
add("final_cta", "ck-ec-split", {
    "heading": "خل الناس تسألك «وش عطرك؟»… مو «متى حطيته؟»",
    "text": P("ابدأ من القاعدة. جرّب عيناتك اليوم، وخذ القنينة اللي تقعد معك."),
    "button_label": "اطلب مجموعة التجربة", "button_link": "shopify://collections/all",
    "link2_label": "أو تسوّق كل العطور ←", "link2_link": "shopify://collections/all",
    "image_asset": "ec-ins-5.png", "image_alt": "", "panel_background": "#F5F5DC",
    "padding_top": 50, "padding_bottom": 50,
})

# 15. Instagram + newsletter
add("gram", "ck-ec-gallery", {
    "heading": "شوفوا الثبات بعيون زبائنا (@___)",
    "subheading": P("[يحتاج إثبات من البراند: حساب إنستقرام وصور زبائن حقيقيين]"),
    "padding_top": 70, "padding_bottom": 100,
}, [blk("photo", image_asset=f"ec-ins-{i}.png") for i in range(1, 6)])
add("newsletter", "ck-ec-newsletter", {
    "kicker": "", "heading": "تعلّم تختار ريحتك",
    "text": P("نرسل لك مرة بالأسبوع: كيف تختار عطر يثبت، كيف تبخّر صح، وأول من يعرف بالدفعات الجديدة."),
    "placeholder": "إيميلك", "button_label": "اشترك", "success_message": "تم الاشتراك، شكراً!",
    "image_alt": "", "heading_size": 56,
})

# Reference sections first, in the reference order (hero..benefits), then the copy-only sections, then gram + newsletter.
# Same section order as reference 6481 (hero, marquee, categories, new arrivals, promo, featured,
# today's picks, benefits, gram, newsletter). Copy-only sections sit between picks and benefits
# and after benefits, so the reference's skeleton stays intact top and bottom.
REF_ORDER = ["hero", "marquee", "categories", "bestsellers", "oud", "home_scent", "gifts", "base",
             "quotes", "why", "old_way", "base_intro", "oud_detail", "home_detail",
             "proof", "offer", "faq", "final_cta", "gram", "newsletter"]
assert sorted(REF_ORDER) == sorted(order)
order = REF_ORDER
out = {"sections": sections, "order": order}
path = os.path.join(THEME, "templates", "index.json")
with open(path, "w", encoding="utf-8", newline="\n") as f:  # no BOM: Shopify rejects it
    json.dump(out, f, ensure_ascii=False, indent=2)
print("wrote", path, len(order), "sections")
