import os
import re
import html
import json
import random

from fugashi import Tagger
from kanjize import number2kanji

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="母音検索システム", layout="wide")

tagger = Tagger()

def cv_num(text):

    def repl(m):
        try:
            return number2kanji(int(m.group()))
        except:
            return m.group()

    return re.sub(r"\d+", repl, text)

ALP = {
    "A":"エー","B":"ビー","C":"シー","D":"ディー","E":"イー",
    "F":"エフ","G":"ジー","H":"エイチ","I":"アイ","J":"ジェー",
    "K":"ケー","L":"エル","M":"エム","N":"エヌ","O":"オー",
    "P":"ピー","Q":"キュー","R":"アール","S":"エス","T":"ティー",
    "U":"ユー","V":"ブイ","W":"ダブリュー","X":"エックス",
    "Y":"ワイ","Z":"ゼット",
    "a":"エー","b":"ビー","c":"シー","d":"ディー","e":"イー",
    "f":"エフ","g":"ジー","h":"エイチ","i":"アイ","j":"ジェー",
    "k":"ケー","l":"エル","m":"エム","n":"エヌ","o":"オー",
    "p":"ピー","q":"キュー","r":"アール","s":"エス","t":"ティー",
    "u":"ユー","v":"ブイ","w":"ダブリュー","x":"エックス",
    "y":"ワイ","z":"ゼット",
}

def replace_alp(text):
    return "".join(ALP.get(ch, ch) for ch in text)

def knf(text):

    text = cv_num(text)

    text = text.replace("&", "アンド")
    text = text.replace("＆", "アンド")

    result = []

    for word in tagger(text):

        kana = None

        try:
            kana = word.feature.kana
        except:
            pass

        if not kana:
            try:
                kana = word.feature.kanaBase
            except:
                pass

        if kana:
            result.append(kana)
        else:
            result.append(word.surface)

    return "".join(result)


# ===========================
# Step0
# お段+う、え段+い を短縮
# ===========================

def st0(word):

    word = word.replace("っ", "")
    word = word.replace("ッ", "")

    word = word.replace("ょう", "ょ")
    word = word.replace("ョウ", "ョ")

    # お段 + う
    for kana in [
        'こ', 'そ', 'と', 'の', 'ほ', 'も',
        'よ', 'ろ', 'を', 'ご', 'ぼ', 'ぽ',
        'ど', 'お', 'ぞ'
    ]:
        word = word.replace(kana + "う", kana + "ー")

    for kana in [
        'コ', 'ソ', 'ト', 'ノ', 'ホ', 'モ',
        'ヨ', 'ロ', 'ヲ', 'ゴ', 'ボ', 'ポ',
        'ド', 'オ', 'ゾ'
    ]:
        word = word.replace(kana + "ウ", kana + "ー")

    # え段 + い
    for kana in [
        'え',
        'け', 'せ', 'て', 'ね', 'へ', 'め', 'れ',
        'げ', 'ぜ', 'で', 'べ', 'ぺ'
    ]:
        word = word.replace(kana + "い", kana + "ー")

    for kana in [
        'エ',
        'ケ', 'セ', 'テ', 'ネ', 'ヘ', 'メ', 'レ',
        'ゲ', 'ゼ', 'デ', 'ベ', 'ペ'
    ]:
        word = word.replace(kana + "イ", kana + "ー")

    return word


# ===========================
# Step1 母音化
# ===========================

vw_mp = {
    'あ':'あ','い':'い','う':'う','え':'え','お':'お',

    'か':'あ','き':'い','く':'う','け':'え','こ':'お',
    'さ':'あ','し':'い','す':'う','せ':'え','そ':'お',
    'た':'あ','ち':'い','つ':'う','て':'え','と':'お',
    'な':'あ','に':'い','ぬ':'う','ね':'え','の':'お',
    'は':'あ','ひ':'い','ふ':'う','へ':'え','ほ':'お',
    'ま':'あ','み':'い','む':'う','め':'え','も':'お',

    'や':'あ','ゆ':'う','よ':'お',

    'ら':'あ','り':'い','る':'う','れ':'え','ろ':'お',

    'わ':'あ','を':'お',

    'が':'あ','ぎ':'い','ぐ':'う','げ':'え','ご':'お',
    'ざ':'あ','じ':'い','ず':'う','ぜ':'え','ぞ':'お',
    'だ':'あ','ぢ':'い','づ':'う','で':'え','ど':'お',
    'ば':'あ','び':'い','ぶ':'う','べ':'え','ぼ':'お',
    'ぱ':'あ','ぴ':'い','ぷ':'う','ぺ':'え','ぽ':'お',

    'ん':'ん',

    'ヴ':'う',
    'ゔ':'う',

    'ア':'あ','イ':'い','ウ':'う','エ':'え','オ':'お',

    'カ':'あ','キ':'い','ク':'う','ケ':'え','コ':'お',
    'サ':'あ','シ':'い','ス':'う','セ':'え','ソ':'お',
    'タ':'あ','チ':'い','ツ':'う','テ':'え','ト':'お',
    'ナ':'あ','ニ':'い','ヌ':'う','ネ':'え','ノ':'お',
    'ハ':'あ','ヒ':'い','フ':'う','ヘ':'え','ホ':'お',
    'マ':'あ','ミ':'い','ム':'う','メ':'え','モ':'お',

    'ヤ':'あ','ユ':'う','ヨ':'お',

    'ラ':'あ','リ':'い','ル':'う','レ':'え','ロ':'お',

    'ワ':'あ','ヲ':'お',

    'ガ':'あ','ギ':'い','グ':'う','ゲ':'え','ゴ':'お',
    'ザ':'あ','ジ':'い','ズ':'う','ゼ':'え','ゾ':'お',
    'ダ':'あ','ヂ':'い','ヅ':'う','デ':'え','ド':'お',
    'バ':'あ','ビ':'い','ブ':'う','ベ':'え','ボ':'お',
    'パ':'あ','ピ':'い','プ':'う','ペ':'え','ポ':'お'
}

sm_mp = {
    'ゃ':'あ',
    'ゅ':'う',
    'ょ':'お',

    'ャ':'あ',
    'ュ':'う',
    'ョ':'お',

    'ぁ':'あ',
    'ぃ':'い',
    'ぅ':'う',
    'ぇ':'え',
    'ぉ':'お',

    'ァ':'あ',
    'ィ':'い',
    'ゥ':'う',
    'ェ':'え',
    'ォ':'お'
}


def st1(word):

    vowels = []

    i = 0

    while i < len(word):

        if i + 1 < len(word) and word[i + 1] in sm_mp:
            vowels.append(sm_mp[word[i + 1]])
            i += 2

        else:
            vowels.append(vw_mp.get(word[i], word[i]))
            i += 1

    return vowels


# ===========================
# Step3
# ふつう：途中の「う」を消す
# やわめ：途中の「う」「い」を消す
# ===========================


# ===========================
# 新仕様用関数
# ===========================

def rem_dup(seq):

    while True:

        cgd = False

        i = 0

        while i < len(seq) - 1:

            if seq[i] == seq[i + 1]:

                cdd = seq[:i + 1] + seq[i + 2:]

                if len(cdd) < 4:
                    return seq, True

                seq = cdd
                cgd = True
                break

            i += 1

        if not cgd:
            return seq, False


def rem_no_vw(seq):
    return [x for x in seq if x in ["あ","い","う","え","お"]]


def rem_mid_vw(vowels, target):
    while True:
        rmd = False
        for i in range(1, len(vowels)-1):
            if vowels[i] == target:
                cdd = vowels[:i] + vowels[i+1:]
                if len(cdd) < 4:
                    return vowels, True
                vowels = cdd
                rmd = True
                break
        if not rmd:
            return vowels, False


def cmp_p_rep(vowels):

    i = 0
    while i < len(vowels) - 3:

        found = False

        for size in range(2, (len(vowels) - i)//2 + 1):

            bl = vowels[i:i+size]
            repeat = 1

            while vowels[i+repeat*size:i+(repeat+1)*size] == bl:
                repeat += 1

            if repeat >= 2:

                keep = 1 if repeat == 2 else 2

                cdd = (
                    vowels[:i]
                    + bl * keep
                    + vowels[i + repeat*size:]
                )

                if len(cdd) < 4:
                    return vowels, True

                vowels = cdd
                found = True
                break

        if not found:
            i += 1

    return vowels, False


# ===========================
# 母音抽出（新仕様）
# ===========================

def prp_wd(word):

    word = replace_alp(word)
    red = knf(word)

    return red

def cmp_dup_vw(seq):

    # 連続区間解析
    runs = []

    i = 0

    while i < len(seq):

        j = i + 1

        while (
            j < len(seq)
            and seq[j] == seq[i]
        ):
            j += 1

        length = j - i

        # ばりかた用：同一母音が3文字以上連なっている場合だけ、
        # 2文字になるまで先頭側から削る。2連続はそのまま残す。
        if length >= 3:
            target = 2
        else:
            target = length

        runs.append([
            seq[i],
            length,
            target,
        ])

        i = j

    # 先頭側から1文字ずつ削る
    while True:

        cgd = False

        for run in runs:

            char, length, target = run

            if length > target:

                cdd_len = (
                    sum(r[1] for r in runs)
                    - 1
                )

                if cdd_len < 4:
                    return (
                        list(
                            "".join(
                                c * l
                                for c, l, _ in runs
                            )
                        ),
                        True
                    )

                run[1] -= 1
                cgd = True
                break

        if not cgd:
            break

    result = []

    for char, length, _ in runs:
        result.extend([char] * length)

    return result, False

def ext_f_red(
    red,
    rl=2,
    us12=True
):

    word = st0(red)

    seq = st1(word)

    if rl == 0:

        seq, stop = cmp_dup_vw(seq)

    else:

        seq, stop = rem_dup(seq)
    if stop:
        return "".join(rem_no_vw(seq))

    vowels = rem_no_vw(seq)

    if rl != 0:

        vowels, stop = (
            rem_dup(
                vowels
            )
        )

        if stop:
            return "".join(vowels)

    if rl >= 2:
        vowels, stop = rem_mid_vw(vowels, "う")
        if stop:
            return "".join(vowels)

    if rl >= 3:
        vowels, stop = rem_mid_vw(vowels, "い")
        if stop:
            return "".join(vowels)

    if rl != 0:

        vowels, stop = (
            rem_dup(
                vowels
            )
        )

        if stop:
            return "".join(vowels)

    if rl != 0 and us12:

        vowels, stop = cmp_p_rep(vowels)

    return "".join(vowels)

def ext(
    word,
    rl=2,
    us12=True
):

    red = prp_wd(word)

    return ext_f_red(
        red,
        rl,
        us12
    )

# ===========================
# 母音検索用
# ④→⑥のみ
# ===========================

def ext_vw_sch(word):

    word = prp_wd(word)

    seq = st1(word)

    vowels = rem_no_vw(seq)

    return "".join(vowels)


# ===========================
# words.txt
# ===========================

fd = os.path.dirname(os.path.abspath(__file__))
wd_fl = os.path.join(fd, "words.txt")

def bud_dic(rl, us12):

    new_dict = {}
    used = set()
    new_ct = 0

    with open(wd_fl, encoding="utf-8") as f:

        for line in f:

            word = line.strip()

            if not word:
                continue

            if word.startswith("#"):
                continue

            if word in used:
                continue

            used.add(word)

            red = prp_wd(word)

            red_len = len(red)

            vowel = ext_f_red(
                red,
                rl,
                us12
            )

            if vowel not in new_dict:
                new_dict[vowel] = []

            hard_vowel = ext_f_red(
                red,
                1,
                us12
            )

            new_dict[vowel].append(
                (word, red_len, hard_vowel)
            )

            new_ct += 1

    for key in new_dict:
        new_dict[key].sort(key=lambda x: x[1])

    return new_dict, new_ct



# ===========================
# 表示用
# ===========================

def has_same_hard_group(entries):

    counts = {}

    for item in entries:
        if len(item) >= 3:
            hard_key = item[2]
        else:
            hard_key = ""

        counts[hard_key] = counts.get(hard_key, 0) + 1

    return any(v >= 2 for v in counts.values())


def make_grouped_lines(entries):

    groups = []
    index = {}

    for item in entries:

        word = item[0]
        hard_key = item[2] if len(item) >= 3 else ""

        if hard_key not in index:
            index[hard_key] = len(groups)
            groups.append({
                "hard_key": hard_key,
                "words": []
            })

        groups[index[hard_key]]["words"].append(word)

    display_items = []
    copy_words = []
    other_words = []

    # 2語以上ある分類だけ先に表示
    for group in groups:

        hard_key = group["hard_key"]
        words = group["words"]

        if len(words) >= 2:
            display_items.append({
                "type": "tag",
                "text": f"ー{hard_key}ー"
            })

            for word in words:
                display_items.append({
                    "type": "word",
                    "text": word
                })
                copy_words.append(word)

            # グループ間だけ空ける
            display_items.append({
                "type": "blank",
                "text": ""
            })

        else:
            other_words.extend(words)

    # 1語だけの分類は最後に「その他」としてまとめる
    if other_words:
        display_items.append({
            "type": "tag",
            "text": "ーその他ー"
        })

        for word in other_words:
            display_items.append({
                "type": "word",
                "text": word
            })
            copy_words.append(word)

    if display_items and display_items[-1]["type"] == "blank":
        display_items.pop()

    return display_items, "\n".join(copy_words)

def render_grouped_result(entries):

    display_items, copy_text = make_grouped_lines(entries)

    body_parts = []

    for item in display_items:

        text = html.escape(item["text"])

        if item["type"] == "tag":
            body_parts.append(f'<div class="tag">{text}</div>')
        elif item["type"] == "blank":
            body_parts.append('<div class="blank"></div>')
        else:
            body_parts.append(f'<div class="word">{text}</div>')

    # 余計なインデントや改行が表示に混ざらないように、HTMLは詰めて作る
    body_html = "".join(body_parts)
    copy_json = json.dumps(copy_text, ensure_ascii=False)

    box_html = (
        '<div class="result-box">'
        f'<button class="copy-btn" onclick=\'navigator.clipboard.writeText({copy_json}); this.innerText="コピー済み"; setTimeout(() => this.innerText="コピー", 1200);\'>コピー</button>'
        f'<div class="result-body">{body_html}</div>'
        '</div>'
        '<style>'
        '.result-box{'
        'position:relative;'
        'border:1px solid rgba(49,51,63,.2);'
        'border-radius:.5rem;'
        'padding:.55rem 1rem .8rem 1rem;'
        'background:rgb(250,250,250);'
        'font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;'
        'font-size:.95rem;'
        'line-height:1.25;'
        'white-space:normal;'
        '}'
        '.copy-btn{'
        'position:absolute;'
        'top:.35rem;'
        'right:.45rem;'
        'border:1px solid rgba(49,51,63,.25);'
        'border-radius:.35rem;'
        'background:white;'
        'padding:.2rem .55rem;'
        'cursor:pointer;'
        'font-size:.8rem;'
        'line-height:1.2;'
        '}'
        '.copy-btn:hover{background:rgb(240,242,246);}'
        '.result-body{margin:0;padding:0;}'
        '.tag{color:#7CFC00;font-weight:700;margin:0;padding:0;line-height:1.35;}'
        '.word{color:#111;margin:0;padding:0;line-height:1.35;}'
        '.blank{height:.75rem;margin:0;padding:0;}'
        '</style>'
    )

    height = max(120, min(900, 40 + len(display_items) * 22))
    components.html(box_html, height=height, scrolling=False)


# ===========================
# 背景アニメーション用
# ===========================

@st.cache_data
def ld_bg_words():
    words = []
    try:
        with open(wd_fl, encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word and not word.startswith("#"):
                    words.append(word)
    except Exception:
        words = []

    if not words:
        words = ["あいうえお", "母音", "フラッシュカード"]

    short_words = [w for w in words if len(w) <= 14]
    return short_words or words


def render_flying_words_background():
    words = ld_bg_words()

    directions = [
        ("120vw", "0vh"),
        ("-120vw", "0vh"),
        ("0vw", "120vh"),
        ("0vw", "-120vh"),
        ("90vw", "90vh"),
        ("-90vw", "90vh"),
        ("90vw", "-90vh"),
        ("-90vw", "-90vh"),
    ]

    spans = []
    css_parts = []

    # 2秒ごとに1つ出続けるよう、40秒周期に対して20個をずらして回す
    # 以前は12個だけだったため、最後の単語が出たあと次の周期まで空白時間ができていた。
    for i in range(20):
        word = html.escape(random.choice(words))
        x = random.randint(0, 92)
        y = random.randint(8, 88)
        dx, dy = random.choice(directions)
        start_rot = random.randint(-35, 35)
        end_rot = start_rot + random.choice([-1, 1]) * random.randint(220, 520)
        size = random.uniform(1.4, 3.2)
        delay = i * 2

        spans.append(f'<span class="fly-word fly-word-{i}">{word}</span>')
        css_parts.append(
            f'.fly-word-{i}{{left:{x}vw;top:{y}vh;font-size:clamp(1.1rem,{size:.2f}vw,3.2rem);animation-delay:{delay}s;--dx:{dx};--dy:{dy};--start-rot:{start_rot}deg;--end-rot:{end_rot}deg;}}'
        )

    # st.markdown だと環境によって <style> 内の @keyframes が本文として表示されることがあるため、
    # CSS/HTML 注入専用の st.html を使う。
    bg_html = (
        '<div class="flying-words-bg" aria-hidden="true">'
        + ''.join(spans)
        + '</div>'
        + '<style>'
        + '.flying-words-bg{position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;overflow:hidden;z-index:0;}'
        + '.stApp header,.stApp [data-testid="stToolbar"],.stApp [data-testid="stDecoration"],.stApp [data-testid="stStatusWidget"],.stApp [data-testid="stAppViewContainer"]{position:relative;z-index:1;}'
        + '.stApp [data-testid="stAppViewContainer"]{background:transparent;}'
        + '.stApp .block-container{position:relative;z-index:2;}'
        + '.fly-word{position:absolute;display:inline-block;color:rgba(20,120,80,.30);font-weight:900;letter-spacing:.05em;white-space:nowrap;text-shadow:0 1px 10px rgba(0,0,0,.14);user-select:none;opacity:0;transform:translate(0,0) rotate(var(--start-rot));animation:flyWord 40s linear infinite;will-change:transform,opacity;}'
        + ''.join(css_parts)
        + '@keyframes flyWord{0%{opacity:0;transform:translate(0,0) rotate(var(--start-rot));}2%{opacity:.34;}8%{opacity:.28;}15%{opacity:0;transform:translate(var(--dx),var(--dy)) rotate(var(--end-rot));}100%{opacity:0;transform:translate(var(--dx),var(--dy)) rotate(var(--end-rot));}}'
        + '@media (max-width:640px){.fly-word{color:rgba(20,120,80,.24);max-width:90vw;}}'
        + '</style>'
    )

    if hasattr(st, "html"):
        st.html(bg_html)
    else:
        st.markdown(bg_html, unsafe_allow_html=True)

# ===========================
# 母音フラッシュカード用
# ===========================

def len_match_key(key, len_label):

    if len_label == "4":
        return len(key) == 4
    if len_label == "5":
        return len(key) == 5
    if len_label == "6":
        return len(key) == 6
    return len(key) >= 7

@st.cache_data
def ld_flash_dic(
    rl,
    us12
):
    return bud_dic(
        rl,
        us12
    )

def get_flash_candidates(vowel_dict, len_label):

    candidates = []

    for key, entries in vowel_dict.items():

        if not len_match_key(key, len_label):
            continue

        if len(entries) < 2:
            continue

        candidates.append(key)

    candidates.sort()

    return candidates


def make_flash_answer_html(entries, output_mode, answer_key):

    display_items, copy_text = make_grouped_lines(entries)

    body_parts = []

    if output_mode == "単語で出力" and answer_key:
        body_parts.append(
            f'<div class="flash-answer-key">母音：{html.escape(answer_key)}</div>'
        )

    for item in display_items:

        text = html.escape(item["text"])

        if item["type"] == "tag":
            body_parts.append(f'<div class="flash-tag">{text}</div>')
        elif item["type"] == "blank":
            body_parts.append('<div class="flash-blank"></div>')
        else:
            body_parts.append(f'<div class="flash-word">{text}</div>')

    body_html = "".join(body_parts)
    copy_json = json.dumps(copy_text, ensure_ascii=False)

    return (
        '<div class="flash-answer-box">'
        f'<button class="flash-copy-btn" onclick=\'navigator.clipboard.writeText({copy_json}); this.innerText="コピー済み"; setTimeout(() => this.innerText="コピー", 1200);\'>コピー</button>'
        f'<div class="flash-answer-body">{body_html}</div>'
        '</div>'
    )


def render_flash_html(
    display_text,
    output_mode,
    previous_text="",
    answer_entries=None,
    answer_key="",
    show_answer=False,
    animate=True,
    slide_dir="right",
):

    display_text = html.escape(display_text or "")
    previous_text = html.escape(previous_text or "")
    answer_key_raw = answer_key or ""
    answer_entries = answer_entries or []

    prev_html = ""
    if previous_text and animate:
        old_class = "flash-card-old-left" if slide_dir == "left" else "flash-card-old-right"
        prev_html = (
            f'<div class="flash-card {old_class}">'
            f'{previous_text}'
            '</div>'
        )

    if output_mode == "単語で出力":
        card_border = "#ffb000"
    else:
        card_border = "#20c878"

    answer_html = ""
    if show_answer:
        answer_html = make_flash_answer_html(
            answer_entries,
            output_mode,
            answer_key_raw,
        )

    current_class = "flash-card-current" if animate else "flash-card-current-noanim"

    block = f"""
    <div class="flash-wrap">
        {prev_html}
        <div class="flash-card {current_class}" style="border-color:{card_border};">
            {display_text}
        </div>
        {answer_html}
    </div>
    <style>
    .flash-wrap{{
        position:relative;
        overflow:hidden;
        margin:1rem 0 .8rem 0;
        width:100%;
        max-width:100%;
        box-sizing:border-box;
    }}
    .flash-card{{
        padding:1.15rem 1rem;
        border:5px solid #20c878;
        border-radius:12px;
        text-align:center;
        font-size:clamp(1.55rem, 6vw, 2.2rem);
        font-weight:800;
        color:white;
        background:rgba(0,0,0,.28);
        line-height:1.25;
        min-height:92px;
        display:flex;
        align-items:center;
        justify-content:center;
        box-sizing:border-box;
        overflow-wrap:anywhere;
        word-break:break-word;
    }}
    .flash-card-current{{
        animation:slideIn .18s ease-out both;
    }}
    .flash-card-current-noanim{{
        animation:none;
    }}
    .flash-card-old-right, .flash-card-old-left{{
        position:absolute;
        left:0;
        right:0;
        top:0;
        z-index:2;
    }}
    .flash-card-old-right{{
        animation:slideOutRight .26s ease-in both;
    }}
    .flash-card-old-left{{
        animation:slideOutLeft .26s ease-in both;
    }}
    .flash-answer-box{{
        position:relative;
        margin-top:.8rem;
        padding:.75rem 1rem .85rem 1rem;
        border:3px solid #ff315f;
        border-radius:10px;
        background:rgba(255,255,255,.94);
        font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;
        font-size:clamp(.9rem, 3.6vw, 1rem);
        line-height:1.35;
        white-space:normal;
        color:#111;
        box-sizing:border-box;
    }}
    .flash-copy-btn{{
        position:absolute;
        top:.35rem;
        right:.45rem;
        border:1px solid rgba(49,51,63,.25);
        border-radius:.35rem;
        background:white;
        padding:.2rem .55rem;
        cursor:pointer;
        font-size:.8rem;
        line-height:1.2;
        z-index:3;
    }}
    .flash-copy-btn:hover{{background:rgb(240,242,246);}}
    .flash-answer-body{{margin:0;padding:0;}}
    .flash-answer-key{{
        font-weight:800;
        margin:0 0 .4rem 0;
        padding-right:4.2rem;
        color:#ff315f;
        line-height:1.35;
    }}
    .flash-tag{{color:#7CFC00;font-weight:800;margin:0;padding:0;line-height:1.35;}}
    .flash-word{{color:#111;margin:0;padding:0;line-height:1.35;}}
    .flash-blank{{height:.75rem;margin:0;padding:0;}}
    @keyframes slideOutRight{{
        from{{transform:translateX(0);opacity:1;}}
        to{{transform:translateX(115%);opacity:.05;}}
    }}
    @keyframes slideOutLeft{{
        from{{transform:translateX(0);opacity:1;}}
        to{{transform:translateX(-115%);opacity:.05;}}
    }}
    @keyframes slideIn{{
        from{{transform:translateX(-4%);opacity:.65;}}
        to{{transform:translateX(0);opacity:1;}}
    }}
    @media (max-width: 640px){{
        .flash-wrap{{margin:.75rem 0 .6rem 0;}}
        .flash-card{{min-height:78px;padding:.9rem .65rem;border-width:4px;}}
        .flash-answer-box{{padding:.7rem .7rem .8rem .7rem;border-width:2.5px;}}
        .flash-copy-btn{{font-size:.75rem;padding:.16rem .45rem;}}
    }}
    </style>
    """
    display_count = len(make_grouped_lines(answer_entries)[0]) if show_answer and answer_entries else 0
    base_height = 150
    if show_answer:
        base_height += 85 + display_count * 22
        if output_mode == "単語で出力":
            base_height += 28
    components.html(block, height=max(150, min(1800, base_height)), scrolling=False)


def make_history_item(display, key, entries, output_mode):

    words = [item[0] for item in entries]

    return {
        "display": display,
        "key": key,
        "words": words,
        "output_mode": output_mode,
    }


def render_flash_history(history):

    if not history:
        st.caption("履歴はまだありません。")
        return

    st.markdown("**履歴（最新5件）**")

    for idx, item in enumerate(history, start=1):
        display = html.escape(item.get("display", ""))
        key = html.escape(item.get("key", ""))
        words = item.get("words", [])
        output_mode = item.get("output_mode", "")

        word_lines = "".join(
            f'<div class="hist-word">{html.escape(word)}</div>'
            for word in words
        )

        if output_mode == "単語で出力":
            answer_head = f"母音：{key}"
        else:
            answer_head = "答え"

        hist_html = f"""
        <div class="hist-card">
            <div class="hist-no">{idx}</div>
            <div class="hist-label">お題</div>
            <div class="hist-title">{display}</div>
            <details>
                <summary>{html.escape(answer_head)}（{len(words)}語）</summary>
                <div class="hist-words">{word_lines}</div>
            </details>
        </div>
        """
        st.markdown(hist_html, unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .hist-card{
            position:relative;
            border:1px solid rgba(49,51,63,.22);
            border-radius:10px;
            background:rgba(255,255,255,.86);
            padding:.55rem .65rem .6rem 2.25rem;
            margin:0 0 .55rem 0;
            box-sizing:border-box;
        }
        .hist-no{
            position:absolute;
            top:.52rem;
            left:.55rem;
            width:1.25rem;
            height:1.25rem;
            border-radius:999px;
            background:#20c878;
            color:white;
            font-size:.78rem;
            font-weight:800;
            display:flex;
            align-items:center;
            justify-content:center;
        }
        .hist-label{font-size:.72rem;opacity:.68;line-height:1.1;}
        .hist-title{font-size:1rem;font-weight:800;line-height:1.25;overflow-wrap:anywhere;word-break:break-word;}
        .hist-card details{margin-top:.25rem;font-size:.86rem;line-height:1.3;}
        .hist-card summary{cursor:pointer;color:#ff315f;font-weight:800;}
        .hist-words{margin-top:.25rem;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;}
        .hist-word{margin:0;padding:0;line-height:1.25;}
        @media (max-width: 640px){
            .hist-card{padding:.5rem .55rem .55rem 2.05rem;margin-bottom:.45rem;}
            .hist-title{font-size:.95rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_answer_button_card():
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] button[kind="secondary"]{
            min-height:82px;
            border:5px solid #ff315f;
            border-radius:12px;
            background:rgba(0,0,0,.20);
            color:white;
            font-size:clamp(1.35rem, 5vw, 2rem);
            font-weight:800;
            white-space:normal;
            line-height:1.15;
        }
        div[data-testid="stButton"] button[kind="secondary"]:hover{
            border-color:#ff315f;
            color:white;
            background:rgba(0,0,0,.30);
        }
        @media (max-width: 640px){
            div[data-testid="stButton"] button[kind="secondary"]{
                min-height:68px;
                border-width:4px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_flashcard_section():

    st.markdown("---")
    st.subheader("母音フラッシュカード")

    with st.container(border=True):

        flash_rl_nm = {
            "ばりかた": 0,
            "かため": 1,
            "ふつう": 2,
            "やわめ": 3,
        }

        flash_rl_lb = st.radio(
            "フラッシュカードの変換ルール",
            list(flash_rl_nm.keys()),
            horizontal=True,
            index=2,
            key="flash_rule"
        )

        flash_rl = flash_rl_nm[flash_rl_lb]

        if flash_rl == 0:
            flash_us12 = False
        else:
            flash_us12 = st.checkbox(
                "羅列を消す",
                value=True,
                key="flash_us12"
            )

        output_mode = st.radio(
            "出力方法",
            ["母音で出力", "単語で出力"],
            horizontal=True,
            index=0,
            key="flash_output_mode"
        )

        st.markdown("**文字数を指定**")
        len_label = st.radio(
            "文字数を指定",
            ["4", "5", "6", "7以上"],
            horizontal=True,
            index=0,
            key="flash_len",
            label_visibility="collapsed"
        )

        flash_dic, flash_ct = ld_flash_dic(
            flash_rl,
            flash_us12
        )

        candidates = get_flash_candidates(
            flash_dic,
            len_label
        )

        st.caption(
            f"対象母音数: {len(candidates):,} / 登録単語数: {flash_ct:,}"
        )

        init_values = {
            "flash_card_key": "",
            "flash_card_words": [],
            "flash_card_entries": [],
            "flash_card_answer": False,
            "flash_card_rule": flash_rl_lb,
            "flash_card_len": len_label,
            "flash_card_us12": flash_us12,
            "flash_card_output_mode": output_mode,
            "flash_card_display": "",
            "flash_card_previous_display": "",
            "flash_card_anim": False,
            "flash_card_slide_dir": "right",
            "flash_card_history": [],
        }

        for k, v in init_values.items():
            if k not in st.session_state:
                st.session_state[k] = v

        changed_cond = (
            st.session_state.flash_card_rule != flash_rl_lb
            or st.session_state.flash_card_len != len_label
            or st.session_state.flash_card_us12 != flash_us12
            or st.session_state.flash_card_output_mode != output_mode
        )

        if changed_cond:
            st.session_state.flash_card_key = ""
            st.session_state.flash_card_words = []
            st.session_state.flash_card_entries = []
            st.session_state.flash_card_answer = False
            st.session_state.flash_card_rule = flash_rl_lb
            st.session_state.flash_card_len = len_label
            st.session_state.flash_card_us12 = flash_us12
            st.session_state.flash_card_output_mode = output_mode
            st.session_state.flash_card_display = ""
            st.session_state.flash_card_previous_display = ""
            st.session_state.flash_card_anim = False
            st.session_state.flash_card_slide_dir = "right"

        left_col, hist_col = st.columns([3.1, 1.25], gap="large")

        with left_col:

            if st.button("めくる", key="flash_flip"):

                if candidates:
                    selected_key = random.choice(candidates)
                    selected_entries = flash_dic[selected_key]
                    selected_words = [item[0] for item in selected_entries]

                    st.session_state.flash_card_previous_display = st.session_state.flash_card_display
                    st.session_state.flash_card_anim = bool(st.session_state.flash_card_display)
                    st.session_state.flash_card_slide_dir = random.choice(["left", "right"])
                    st.session_state.flash_card_key = selected_key
                    st.session_state.flash_card_words = selected_words
                    st.session_state.flash_card_entries = selected_entries
                    st.session_state.flash_card_answer = False

                    if output_mode == "単語で出力":
                        st.session_state.flash_card_display = random.choice(selected_words)
                    else:
                        st.session_state.flash_card_display = selected_key

                    new_hist = make_history_item(
                        st.session_state.flash_card_display,
                        selected_key,
                        selected_entries,
                        output_mode,
                    )
                    st.session_state.flash_card_history = (
                        [new_hist] + st.session_state.flash_card_history
                    )[:5]

                else:
                    st.session_state.flash_card_previous_display = st.session_state.flash_card_display
                    st.session_state.flash_card_anim = bool(st.session_state.flash_card_display)
                    st.session_state.flash_card_slide_dir = random.choice(["left", "right"])
                    st.session_state.flash_card_key = ""
                    st.session_state.flash_card_words = []
                    st.session_state.flash_card_entries = []
                    st.session_state.flash_card_answer = False
                    st.session_state.flash_card_display = ""

            if candidates:

                if st.session_state.flash_card_key:

                    render_flash_html(
                        st.session_state.flash_card_display,
                        output_mode,
                        previous_text=st.session_state.flash_card_previous_display,
                        answer_entries=st.session_state.flash_card_entries,
                        answer_key=st.session_state.flash_card_key,
                        show_answer=st.session_state.flash_card_answer,
                        animate=st.session_state.flash_card_anim and not st.session_state.flash_card_answer,
                        slide_dir=st.session_state.flash_card_slide_dir,
                    )

                    if not st.session_state.flash_card_answer:
                        render_answer_button_card()
                        if st.button(
                            "答えを出す",
                            key="flash_show_answer_big",
                            use_container_width=True,
                        ):
                            st.session_state.flash_card_answer = True
                            st.session_state.flash_card_anim = False
                            st.session_state.flash_card_previous_display = ""
                            st.rerun()

                else:
                    st.info("めくるボタンを押してください。")

            else:
                st.warning("この条件に合う、2語以上ある母音がありません。")

        with hist_col:
            render_flash_history(st.session_state.flash_card_history)

# ===========================
# GUI
# ===========================


st.title("母音検索システム")
render_flying_words_background()

rl_nm = {
    "ばりかた": 0,
    "かため": 1,
    "ふつう": 2,
    "やわめ": 3,
}

rl_lb = st.radio(
    "変換ルール",
    list(rl_nm.keys()),
    horizontal=True,
    index=1
)

rl = rl_nm[rl_lb]

if rl == 0:
    us12 = False
else:
    us12 = st.checkbox(
        "羅列を消す",
        value=True
    )

rl = rl_nm[rl_lb]
sch_md = st.radio(
    "検索方法",
    ["単語で検索", "母音で検索"],
    horizontal=True,
)

@st.cache_data
def ld_dic(
    rl,
    us12
):
    return bud_dic(
        rl,
        us12
    )

vw_dic, ct = ld_dic(
    rl,
    us12
)

st.caption(f"登録単語数: {ct:,}")

qu = st.text_input("検索語")

if qu:

    if sch_md == "単語で検索":
        key = ext(
            qu,
            rl,
            us12
        )
    else:
        key = ext_vw_sch(qu)

    res = vw_dic.get(key, [])

    st.write("検索キー:", key)
    st.write("一致件数:", len(res))

    if res:

        use_grouped_view = (
            rl >= 2
            and has_same_hard_group(res)
        )

        if use_grouped_view:
            render_grouped_result(res)
        else:
            res_tx = "\n".join(
                item[0] for item in res
            )

            st.code(
                res_tx,
                language=None
            )

    else:
        st.info("一致する単語はありません。")

with st.expander("変換テスト"):
    t = st.text_input("テスト文字列", key="test")
    if t:
        st.write("かな:", knf(t))
        st.write(
            "単語検索キー:",
            ext(
                t,
                rl,
                us12
            )
        )
        st.write("母音検索キー:", ext_vw_sch(t))


render_flashcard_section()
