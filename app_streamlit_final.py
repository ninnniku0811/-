import os
import re
import html
import json

from fugashi import Tagger
from kanjize import number2kanji

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

        if length == 2:
            target = 1
        elif length >= 3:
            target = 2
        else:
            target = 1

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

    body_html = "\n".join(body_parts)
    copy_json = json.dumps(copy_text, ensure_ascii=False)

    box_html = f"""
    <div class="result-box">
        <button class="copy-btn" onclick='navigator.clipboard.writeText({copy_json}); this.innerText="コピー済み"; setTimeout(() => this.innerText="コピー", 1200);'>コピー</button>
        <div class="result-body">
            {body_html}
        </div>
    </div>
    <style>
        .result-box {{
            position: relative;
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: 2.4rem 1rem 1rem 1rem;
            background: rgb(250, 250, 250);
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            white-space: pre-wrap;
            line-height: 1.9;
            font-size: 0.95rem;
        }}
        .copy-btn {{
            position: absolute;
            top: 0.45rem;
            right: 0.45rem;
            border: 1px solid rgba(49, 51, 63, 0.25);
            border-radius: 0.35rem;
            background: white;
            padding: 0.25rem 0.6rem;
            cursor: pointer;
            font-size: 0.8rem;
        }}
        .copy-btn:hover {{
            background: rgb(240, 242, 246);
        }}
        .tag {{
            color: #7CFC00;
            font-weight: 700;
        }}
        .word {{
            color: #111;
        }}
        .blank {{
            height: 0.8rem;
        }}
    </style>
    """

    height = max(180, min(900, 80 + len(display_items) * 30))
    components.html(box_html, height=height, scrolling=True)

# ===========================
# GUI
# ===========================

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="母音検索システム", layout="wide")

st.title("母音検索システム")

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
        "⑫を適用する",
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
            sch_md == "単語で検索"
            and rl >= 2
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
