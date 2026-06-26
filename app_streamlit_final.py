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

def attr_text(text):
    return html.escape(text or "", quote=True)

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

def st0(word, remove_sokuon=True):

    if remove_sokuon:
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

# 旧版で使っていた「母音以外を直前母音にする」処理は廃止。
# 現在のばりかたでは rem_no_vw() で母音以外を削除する。

def cmp_dup_vw(seq):

    # 現在のばりかた用：同一母音が4文字以上連なっている場合だけ、
    # 3文字になるまで先頭側から1文字ずつ削る。
    # 2連続・3連続はそのまま残す。
    while True:

        changed = False
        i = 0

        while i < len(seq):

            j = i + 1

            while j < len(seq) and seq[j] == seq[i]:
                j += 1

            run_len = j - i

            if run_len >= 4:

                candidate = seq[:i] + seq[i + 1:]

                if len(candidate) < 4:
                    return seq, True

                seq = candidate
                changed = True
                break

            i = j

        if not changed:
            return seq, False


def cmp_dup_vw_old_barikata(seq):

    # 旧ばりかた用：
    # 同一母音2連続は1文字まで、3連続以上は2文字まで残す。
    # 削除すると全体が4文字未満になる場合は、その削除を行わず終了する。
    runs = []

    i = 0

    while i < len(seq):

        j = i + 1

        while j < len(seq) and seq[j] == seq[i]:
            j += 1

        length = j - i

        if length == 2:
            target = 1
        elif length >= 3:
            target = 2
        else:
            target = 1

        runs.append([seq[i], length, target])
        i = j

    while True:

        changed = False

        for run in runs:

            if run[1] > run[2]:

                candidate_len = sum(r[1] for r in runs) - 1

                if candidate_len < 4:
                    result = []
                    for char, length, _ in runs:
                        result.extend([char] * length)
                    return result, True

                run[1] -= 1
                changed = True
                break

        if not changed:
            break

    result = []

    for char, length, _ in runs:
        result.extend([char] * length)

    return result, False



def othello_non_vowels_between_same_vowels(seq):

    # かため用：母音以外が「同じ母音」に挟まれている場合、
    # その母音に変換する。
    # 例：おーお → おおお / あんあ → あああ
    # 違う母音に挟まれているもの、片側しか母音がないものは後で削除する。
    vowels = {"あ", "い", "う", "え", "お"}
    seq = list(seq)
    n = len(seq)
    i = 0

    while i < n:

        if seq[i] in vowels:
            i += 1
            continue

        start = i

        while i < n and seq[i] not in vowels:
            i += 1

        end = i

        left = seq[start - 1] if start - 1 >= 0 else None
        right = seq[end] if end < n else None

        if left in vowels and right in vowels and left == right:
            for j in range(start, end):
                seq[j] = left

    return seq

def ext_old_barikata_f_red(red):

    # 「かため」用：旧ばりかたをベースにしつつ、
    # 母音以外が同じ母音に挟まれた場合はオセロ方式でその母音に変える。
    # それ以外の母音以外は削除する。
    word = st0(red, remove_sokuon=False)
    seq = st1(word)

    seq = othello_non_vowels_between_same_vowels(seq)
    seq = rem_no_vw(seq)

    seq, stop = cmp_dup_vw_old_barikata(seq)

    return "".join(seq)


def ext_old_katame_group_f_red(red, us12=True):

    # ふつう・やわめの分類タグを変えないため、
    # タグ計算だけは従来の「かため」ルールを使う。
    word = st0(red, remove_sokuon=True)
    seq = st1(word)

    seq, stop = rem_dup(seq)
    if stop:
        return "".join(rem_no_vw(seq))

    vowels = rem_no_vw(seq)

    vowels, stop = rem_dup(vowels)
    if stop:
        return "".join(vowels)

    if us12:
        vowels, stop = cmp_p_rep(vowels)

    return "".join(vowels)


def ext_group_key_f_red(red, rl=2):

    # 分類タグ・長い形での検索用キー。
    # 最終的に検索辞書へ登録するキーとは分ける。
    #
    # 重要：ここでは「羅列削除」だけでなく、
    # ふつう/やわめの中間「う」「い」削除も行わない。
    # そのため、
    #   あおあおあう
    #   あおあおあいう
    #   あおうあおあう
    # のようなものは、ルール適用後に近い形になっても、
    # それぞれ別の分類タグとして残る。

    if rl == 0:
        return ext_f_red(red, 0, True)

    if rl == 1:
        return ext_f_red(red, 1, True)

    word = st0(red, remove_sokuon=True)
    seq = st1(word)

    seq, stop = rem_dup(seq)
    if stop:
        return "".join(rem_no_vw(seq))

    vowels = rem_no_vw(seq)

    vowels, stop = rem_dup(vowels)
    if stop:
        return "".join(vowels)

    # ここで止める。
    # 中間う/い削除、最後の重複削除、羅列削除はしない。
    return "".join(vowels)


def ext_pre_rep_f_red(red, rl=2):

    # 検索フィルタ用キー。
    # 最終キーの直前、つまり「羅列削除」だけを行う前の状態を返す。
    # ふつう/やわめの中間「う」「い」削除など、羅列削除以外のルールは通常どおり行う。
    # 例：
    #   おあおあえお       → おあおあえお → 羅列削除後は おあえお
    #   おあおあいえうお   → おあおあえお → 羅列削除後は おあえお
    #   おあいえお         → おあえお     → 羅列削除後も おあえお
    # そのため、長い羅列形で検索した場合は、同じ pre_rep を持つものだけ拾える。

    if rl == 0:
        return ext_f_red(red, 0, True)

    if rl == 1:
        return ext_f_red(red, 1, True)

    word = st0(red, remove_sokuon=True)

    seq = st1(word)

    seq, stop = rem_dup(seq)
    if stop:
        return "".join(rem_no_vw(seq))

    vowels = rem_no_vw(seq)

    vowels, stop = rem_dup(vowels)
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

    vowels, stop = rem_dup(vowels)
    if stop:
        return "".join(vowels)

    # ここで止める。羅列削除 cmp_p_rep は行わない。
    return "".join(vowels)


def ext_pre_rep(word, rl=2):

    red = prp_wd(word)

    return ext_pre_rep_f_red(
        red,
        rl,
    )

def ext_vw_rule_f_red(red, rl=2, us12=True):

    # 母音検索用：お段+う、え段+いの短縮（st0）は行わない。
    # それ以外の選択ルールは単語検索側と同じ流れで適用する。

    seq = st1(red)

    if rl == 0:
        vowels = rem_no_vw(seq)
        vowels, stop = cmp_dup_vw(vowels)
        return "".join(vowels)

    if rl == 1:
        seq = othello_non_vowels_between_same_vowels(seq)
        vowels = rem_no_vw(seq)
        vowels, stop = cmp_dup_vw_old_barikata(vowels)
        return "".join(vowels)

    seq, stop = rem_dup(seq)
    if stop:
        return "".join(rem_no_vw(seq))

    vowels = rem_no_vw(seq)

    vowels, stop = rem_dup(vowels)
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

    vowels, stop = rem_dup(vowels)
    if stop:
        return "".join(vowels)

    if us12:
        vowels, stop = cmp_p_rep(vowels)

    return "".join(vowels)


def ext_vw_pre_rep_f_red(red, rl=2):

    # 母音検索用の羅列削除前キー。
    # st0は使わず、お段+う / え段+い は消さない。
    # 羅列削除だけを行う前の状態を返す。

    seq = st1(red)

    if rl == 0:
        vowels = rem_no_vw(seq)
        vowels, stop = cmp_dup_vw(vowels)
        return "".join(vowels)

    if rl == 1:
        seq = othello_non_vowels_between_same_vowels(seq)
        vowels = rem_no_vw(seq)
        vowels, stop = cmp_dup_vw_old_barikata(vowels)
        return "".join(vowels)

    seq, stop = rem_dup(seq)
    if stop:
        return "".join(rem_no_vw(seq))

    vowels = rem_no_vw(seq)

    vowels, stop = rem_dup(vowels)
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

    vowels, stop = rem_dup(vowels)
    if stop:
        return "".join(vowels)

    return "".join(vowels)


def ext_vw_rule(word, rl=2, us12=True):

    red = prp_wd(word)

    return ext_vw_rule_f_red(
        red,
        rl,
        us12,
    )


def ext_vw_pre_rep(word, rl=2):

    red = prp_wd(word)

    return ext_vw_pre_rep_f_red(
        red,
        rl,
    )


def ext_f_red(
    red,
    rl=2,
    us12=True
):

    if rl == 0:

        # 現在のばりかた：母音以外は削除。
        # 同一母音が4個以上連続している場合だけ、3個になるまで削る。
        word = st0(red, remove_sokuon=False)
        seq = st1(word)
        seq = rem_no_vw(seq)
        seq, stop = cmp_dup_vw(seq)

        return "".join(seq)

    if rl == 1:

        # かためは「旧ばりかた」ベース。
        # 同じ母音に挟まれた母音以外は、その母音に変える。
        return ext_old_barikata_f_red(red)

    word = st0(red, remove_sokuon=True)

    seq = st1(word)

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

            # 辞書側は「羅列を消す」を常時ONにした最終キーで登録する。
            vowel = ext_f_red(
                red,
                rl,
                us12
            )

            if vowel not in new_dict:
                new_dict[vowel] = []

            # 分類タグ・長い形での検索用キー。
            # 検索辞書側の最終キーは羅列削除まで行うが、
            # 分類タグは「中間う/い削除」と「羅列削除」の前の形で保持する。
            # これにより、い/うを消した結果として同じ形になる単語は、
            # 無理に同じ分類タグへ入らず、別タグとして残る。
            hard_vowel = ext_group_key_f_red(
                red,
                rl
            )

            pre_rep_vowel = ext_pre_rep_f_red(
                red,
                rl
            )

            new_dict[vowel].append(
                (word, red_len, hard_vowel, pre_rep_vowel)
            )

            new_ct += 1

    for key in new_dict:
        new_dict[key].sort(key=lambda x: x[1])

    return new_dict, new_ct



def collect_search_results(vowel_dict, key, query_pre_rep=None):

    # 検索キーに一致するものを返す。
    # 基本は「最終キー」が検索キーに一致するものを拾う。
    # ただし検索語自体が羅列削除で短くなる場合は、
    # 「羅列削除前キー（pre_rep）」が検索語側の pre_rep と一致するものだけに絞る。
    #
    # 例：やわめで「おあおあえお」を単語検索
    #   検索語 pre_rep = おあおあえお
    #   検索語 final   = おあえお
    #   ーおあいえおー         は pre_rep が おあえお なので出ない
    #   ーおあおあいえうおー   は pre_rep が おあおあえお なので出る

    restrict_by_pre_rep = (
        query_pre_rep is not None
        and query_pre_rep != key
    )

    results = []
    seen_words = set()

    for item in vowel_dict.get(key, []):
        word = item[0]
        item_pre_rep = item[3] if len(item) >= 4 else ""

        if restrict_by_pre_rep and item_pre_rep != query_pre_rep:
            continue

        if word not in seen_words:
            results.append(item)
            seen_words.add(word)

    # 検索語が羅列削除で短くならない場合だけ、分類タグそのものに一致する語も補助的に拾う。
    # 羅列形で検索したときに、検索ルールを変えて別タグを混ぜないため。
    if not restrict_by_pre_rep:
        for entries in vowel_dict.values():
            for item in entries:
                word = item[0]
                hard_key = item[2] if len(item) >= 3 else ""
                if hard_key == key and word not in seen_words:
                    results.append(item)
                    seen_words.add(word)

    results.sort(key=lambda x: x[1])

    return results


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


def middle_u_remove_distance(source_key, target_key, max_remove=2):

    if not source_key or not target_key:
        return None

    if source_key == target_key:
        return 0

    best = None

    def dfs(chars, removed):
        nonlocal best

        current = "".join(chars)

        if current == target_key:
            if best is None or removed < best:
                best = removed
            return

        if removed >= max_remove:
            return

        if best is not None and removed >= best:
            return

        # targetより短くなったら成立しない
        if len(chars) <= len(target_key):
            return

        for i, ch in enumerate(chars):
            # 「中間のう」だけ削除候補にする
            if ch != "う":
                continue
            if i == 0 or i == len(chars) - 1:
                continue

            nxt = chars[:i] + chars[i + 1:]
            dfs(nxt, removed + 1)

    dfs(list(source_key), 0)

    if best in (1, 2):
        return best

    return None


def make_grouped_lines(entries):

    groups = []
    index = {}

    for item in entries:

        word = item[0]
        red_len = item[1] if len(item) >= 2 else 0
        hard_key = item[2] if len(item) >= 3 else ""

        if hard_key not in index:
            index[hard_key] = len(groups)
            groups.append({
                "hard_key": hard_key,
                "items": []
            })

        groups[index[hard_key]]["items"].append({
            "word": word,
            "red_len": red_len,
            "kind": "normal",
            "source_key": hard_key,
        })

    display_items = []
    copy_words_base = []
    copy_words_all = []
    other_groups = []

    main_groups = [g for g in groups if len(g["items"]) >= 2]

    for group in groups:
        if len(group["items"]) < 2:
            other_groups.append({
                "hard_key": group["hard_key"],
                "items": group["items"],
                "attached_to": None,
                "color_type": None,
            })

    # 「その他」候補のうち、主要分類に対して中間の「う」を1つ消すと一致するものは赤、
    # 2つ消すと一致するものは紫として、その分類内に入れる。
    # ただし表示位置は分類の最後にまとめず、通常単語と同じ並びの中に混ぜる。
    attachments = {g["hard_key"]: [] for g in main_groups}
    remaining_other_items = []

    for other in other_groups:

        src_key = other["hard_key"]
        best_target = None
        best_dist = None

        for main in main_groups:
            dist = middle_u_remove_distance(src_key, main["hard_key"], 2)
            if dist is None:
                continue
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_target = main["hard_key"]

        if best_target is not None:
            color_type = "red" if best_dist == 1 else "purple"
            for item in other["items"]:
                attachments[best_target].append({
                    "word": item["word"],
                    "red_len": item.get("red_len", 0),
                    "source_key": src_key,
                    "kind": color_type,
                })
        else:
            remaining_other_items.extend(other["items"])

    # 2語以上ある分類だけ先に表示
    for group in groups:

        hard_key = group["hard_key"]
        items = group["items"]

        if len(items) >= 2:

            attached = attachments.get(hard_key, [])
            combined = []
            for item in items:
                combined.append({
                    "word": item["word"],
                    "red_len": item.get("red_len", 0),
                    "kind": "normal",
                    "source_key": hard_key,
                })
            combined.extend(attached)

            # 普通の結果一覧に自然に混ざるよう、読み長さ順で並べる。
            # 同じ長さなら通常→赤→紫の順にして、元の見え方をなるべく保つ。
            kind_order = {"normal": 0, "red": 1, "purple": 2}
            combined.sort(key=lambda x: (x.get("red_len", 0), kind_order.get(x.get("kind"), 9), x.get("word", "")))

            base_words = [x["word"] for x in combined if x.get("kind") == "normal"]
            all_words = [x["word"] for x in combined]

            display_items.append({
                "type": "tag",
                "text": f"ー{hard_key}ー",
                "copy_text_base": "\n".join(base_words),
                "copy_text_all": "\n".join(all_words),
            })

            for item in combined:
                if item.get("kind") == "red":
                    item_type = "word_red"
                elif item.get("kind") == "purple":
                    item_type = "word_purple"
                else:
                    item_type = "word"

                display_items.append({
                    "type": item_type,
                    "text": item["word"],
                    "source_key": item.get("source_key", ""),
                })

                if item.get("kind") == "normal":
                    copy_words_base.append(item["word"])
                copy_words_all.append(item["word"])

            # グループ間だけ空ける
            display_items.append({
                "type": "blank",
                "text": ""
            })

    # 残った1語だけの分類は最後に「その他」としてまとめる
    if remaining_other_items:
        remaining_other_items.sort(key=lambda x: (x.get("red_len", 0), x.get("word", "")))
        remaining_other_words = [x["word"] for x in remaining_other_items]

        display_items.append({
            "type": "tag",
            "text": "ーその他ー",
            "copy_text_base": "\n".join(remaining_other_words),
            "copy_text_all": "\n".join(remaining_other_words),
        })

        for word in remaining_other_words:
            display_items.append({
                "type": "word",
                "text": word
            })
            copy_words_base.append(word)
            copy_words_all.append(word)

    if display_items and display_items[-1]["type"] == "blank":
        display_items.pop()

    return display_items, "\n".join(copy_words_base), "\n".join(copy_words_all)

def render_grouped_result(entries):

    display_items, copy_text_base, copy_text_all = make_grouped_lines(entries)

    body_parts = []

    for item in display_items:

        text = html.escape(item["text"])

        if item["type"] == "tag":
            tag_copy_base_attr = attr_text(item.get("copy_text_base", ""))
            tag_copy_all_attr = attr_text(item.get("copy_text_all", ""))
            body_parts.append(
                f'<div class="tag-row"><span class="tag">{text}</span>'
                f'''<button class="tag-copy-btn" data-base="{tag_copy_base_attr}" data-all="{tag_copy_all_attr}" onclick="const b=this.closest(\'.result-box\'); const inc=b.querySelector(\'.include-colored\')?.checked; navigator.clipboard.writeText(inc ? this.dataset.all : this.dataset.base); this.innerText=\'コピー済み\'; setTimeout(() => this.innerText=\'コピー\', 1200);">コピー</button>'''
                f'</div>'
            )
        elif item["type"] == "blank":
            body_parts.append('<div class="blank"></div>')
        elif item["type"] == "word_red":
            title = html.escape(item.get("source_key", ""))
            body_parts.append(f'<div class="word word-red" title="{title}">{text}</div>')
        elif item["type"] == "word_purple":
            title = html.escape(item.get("source_key", ""))
            body_parts.append(f'<div class="word word-purple" title="{title}">{text}</div>')
        else:
            body_parts.append(f'<div class="word">{text}</div>')

    # 余計なインデントや改行が表示に混ざらないように、HTMLは詰めて作る
    body_html = "".join(body_parts)
    copy_base_attr = attr_text(copy_text_base)
    copy_all_attr = attr_text(copy_text_all)

    box_html = (
        '<div class="result-box">'
        '<label class="copy-option"><input type="checkbox" class="include-colored"> 赤・紫もコピー</label>'
        f'''<button class="copy-btn" data-base="{copy_base_attr}" data-all="{copy_all_attr}" onclick="const b=this.closest(\'.result-box\'); const inc=b.querySelector(\'.include-colored\')?.checked; navigator.clipboard.writeText(inc ? this.dataset.all : this.dataset.base); this.innerText=\'コピー済み\'; setTimeout(() => this.innerText=\'コピー\', 1200);">コピー</button>'''
        f'<div class="result-body">{body_html}</div>'
        '</div>'
        '<style>'
        '.result-box{'
        'position:relative;'
        'border:1px solid rgba(49,51,63,.2);'
        'border-radius:.5rem;'
        'padding:2rem 1rem .8rem 1rem;'
        'background:rgb(250,250,250);'
        'font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;'
        'font-size:.95rem;'
        'line-height:1.25;'
        'white-space:normal;'
        '}'
        '.copy-option{position:absolute;top:.38rem;left:.55rem;font-size:.78rem;line-height:1.2;color:#444;display:flex;align-items:center;gap:.25rem;}'
        '.copy-option input{margin:0;}'
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
        '.tag-row{display:flex;align-items:center;gap:.45rem;margin:0;padding:0;line-height:1.35;}'
        '.tag{color:#7CFC00;font-weight:700;margin:0;padding:0;line-height:1.35;}'
        '.tag-copy-btn{border:1px solid rgba(49,51,63,.25);border-radius:.32rem;background:white;padding:.08rem .42rem;cursor:pointer;font-size:.72rem;line-height:1.15;}'
        '.tag-copy-btn:hover{background:rgb(240,242,246);}'
        '.word{color:#111;margin:0;padding:0;line-height:1.35;}'
        '.word-red{color:#d90000;font-weight:700;}'
        '.word-purple{color:#8a2be2;font-weight:700;}'
        '.blank{height:.75rem;margin:0;padding:0;}'
        '</style>'
    )

    height = max(120, min(10000, 65 + len(display_items) * 22))
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

    spans = []
    css_parts = []

    # 1秒ごとに1つ出続けるよう、40秒周期に対して40個をずらして回す。
    # 出現位置は画面端に固定し、そこからランダムな一方向へ飛ばす。
    for i in range(40):
        word = html.escape(random.choice(words))
        side = random.choice(["left", "right", "top", "bottom"])

        if side == "left":
            x = -12
            y = random.randint(4, 92)
            dx = random.randint(105, 145)
            dy = random.randint(-35, 35)
        elif side == "right":
            x = 105
            y = random.randint(4, 92)
            dx = -random.randint(105, 145)
            dy = random.randint(-35, 35)
        elif side == "top":
            x = random.randint(0, 92)
            y = -10
            dx = random.randint(-35, 35)
            dy = random.randint(105, 145)
        else:
            x = random.randint(0, 92)
            y = 105
            dx = random.randint(-35, 35)
            dy = -random.randint(105, 145)

        start_rot = random.randint(-35, 35)
        end_rot = start_rot + random.choice([-1, 1]) * random.randint(220, 520)
        size = random.uniform(1.4, 3.2)
        delay = i

        spans.append(f'<span class="fly-word fly-word-{i}">{word}</span>')
        css_parts.append(
            f'.fly-word-{i}{{left:{x}vw;top:{y}vh;font-size:clamp(1.1rem,{size:.2f}vw,3.2rem);animation-delay:{delay}s;--dx:{dx}vw;--dy:{dy}vh;--start-rot:{start_rot}deg;--end-rot:{end_rot}deg;}}'
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
        + '.fly-word{position:absolute;display:inline-block;color:rgba(80,80,80,.30);font-weight:900;letter-spacing:.05em;white-space:nowrap;text-shadow:0 1px 10px rgba(0,0,0,.12);user-select:none;opacity:0;transform:translate(0,0) rotate(var(--start-rot));animation:flyWord 40s linear infinite;will-change:transform,opacity;}'
        + ''.join(css_parts)
        + '@keyframes flyWord{0%{opacity:0;transform:translate(0,0) rotate(var(--start-rot));}2%{opacity:.36;}10%{opacity:.28;}18%{opacity:0;transform:translate(var(--dx),var(--dy)) rotate(var(--end-rot));}100%{opacity:0;transform:translate(var(--dx),var(--dy)) rotate(var(--end-rot));}}'
        + '@media (max-width:640px){.fly-word{color:rgba(80,80,80,.25);max-width:90vw;}}'
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

    display_items, copy_text_base, copy_text_all = make_grouped_lines(entries)

    body_parts = []

    if output_mode == "単語で出力" and answer_key:
        body_parts.append(
            f'<div class="flash-answer-key">母音：{html.escape(answer_key)}</div>'
        )

    for item in display_items:

        text = html.escape(item["text"])

        if item["type"] == "tag":
            tag_copy_base_attr = attr_text(item.get("copy_text_base", ""))
            tag_copy_all_attr = attr_text(item.get("copy_text_all", ""))
            body_parts.append(
                f'<div class="flash-tag-row"><span class="flash-tag">{text}</span>'
                f'''<button class="flash-tag-copy-btn" data-base="{tag_copy_base_attr}" data-all="{tag_copy_all_attr}" onclick="const b=this.closest(\'.flash-answer-box\'); const inc=b.querySelector(\'.flash-include-colored\')?.checked; navigator.clipboard.writeText(inc ? this.dataset.all : this.dataset.base); this.innerText=\'コピー済み\'; setTimeout(() => this.innerText=\'コピー\', 1200);">コピー</button>'''
                f'</div>'
            )
        elif item["type"] == "blank":
            body_parts.append('<div class="flash-blank"></div>')
        elif item["type"] == "word_red":
            title = html.escape(item.get("source_key", ""))
            body_parts.append(f'<div class="flash-word flash-word-red" title="{title}">{text}</div>')
        elif item["type"] == "word_purple":
            title = html.escape(item.get("source_key", ""))
            body_parts.append(f'<div class="flash-word flash-word-purple" title="{title}">{text}</div>')
        else:
            body_parts.append(f'<div class="flash-word">{text}</div>')

    body_html = "".join(body_parts)
    copy_base_attr = attr_text(copy_text_base)
    copy_all_attr = attr_text(copy_text_all)

    return (
        '<div class="flash-answer-box">'
        '<label class="flash-copy-option"><input type="checkbox" class="flash-include-colored"> 赤・紫もコピー</label>'
        f'''<button class="flash-copy-btn" data-base="{copy_base_attr}" data-all="{copy_all_attr}" onclick="const b=this.closest(\'.flash-answer-box\'); const inc=b.querySelector(\'.flash-include-colored\')?.checked; navigator.clipboard.writeText(inc ? this.dataset.all : this.dataset.base); this.innerText=\'コピー済み\'; setTimeout(() => this.innerText=\'コピー\', 1200);">コピー</button>'''
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
        padding:2rem 1rem .85rem 1rem;
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
    .flash-copy-option{{
        position:absolute;
        top:.38rem;
        left:.55rem;
        font-size:.78rem;
        line-height:1.2;
        color:#444;
        display:flex;
        align-items:center;
        gap:.25rem;
    }}
    .flash-copy-option input{{margin:0;}}
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
    .flash-tag-row{{display:flex;align-items:center;gap:.45rem;margin:0;padding:0;line-height:1.35;}}
    .flash-tag{{color:#7CFC00;font-weight:800;margin:0;padding:0;line-height:1.35;}}
    .flash-tag-copy-btn{{border:1px solid rgba(49,51,63,.25);border-radius:.32rem;background:white;padding:.08rem .42rem;cursor:pointer;font-size:.72rem;line-height:1.15;}}
    .flash-tag-copy-btn:hover{{background:rgb(240,242,246);}}
    .flash-word{{color:#111;margin:0;padding:0;line-height:1.35;}}
    .flash-word-red{{color:#d90000;font-weight:800;}}
    .flash-word-purple{{color:#8a2be2;font-weight:800;}}
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
    components.html(block, height=max(150, min(12000, base_height)), scrolling=False)


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

        # 羅列削除はシステムとして常時ON。
        # 画面上のチェックボックスは表示しない。
        flash_us12 = True

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
# 単語神経衰弱
# ===========================

def build_memory_cards(rl, us12=True, pair_count=6):

    mem_dic, mem_ct = ld_dic(rl, us12)

    candidates = []

    for key, entries in mem_dic.items():
        words = []
        seen = set()
        for item in entries:
            word = item[0]
            if word not in seen:
                words.append(item)
                seen.add(word)
        if len(words) >= 2:
            candidates.append((key, words))

    if len(candidates) < pair_count:
        return [], len(candidates), mem_ct

    selected_groups = random.sample(candidates, pair_count)

    cards = []
    card_id = 0

    for key, entries in selected_groups:
        pair_items = random.sample(entries, 2)
        for item in pair_items:
            cards.append({
                "id": card_id,
                "word": item[0],
                "key": key,
            })
            card_id += 1

    random.shuffle(cards)

    # shuffle後もインデックスで扱えるように id を振り直す
    for i, card in enumerate(cards):
        card["id"] = i

    return cards, len(candidates), mem_ct


def start_memory_game(rl_lb, rl, us12=True):

    cards, candidate_count, mem_ct = build_memory_cards(
        rl,
        us12,
        pair_count=6,
    )

    st.session_state.memory_cards = cards
    st.session_state.memory_matched = [False] * len(cards)
    st.session_state.memory_selected = []
    st.session_state.memory_moves = 0
    st.session_state.memory_found = 0
    st.session_state.memory_rule = rl_lb
    st.session_state.memory_candidate_count = candidate_count
    st.session_state.memory_word_count = mem_ct
    st.session_state.memory_message = ""


def handle_memory_click(idx):

    cards = st.session_state.get("memory_cards", [])
    matched = st.session_state.get("memory_matched", [])
    selected = st.session_state.get("memory_selected", [])

    if not cards or idx >= len(cards):
        return

    # 前回2枚開いて外れていた場合は、次のクリックで閉じる
    if len(selected) >= 2:
        selected = []

    if matched[idx]:
        st.session_state.memory_selected = selected
        return

    if idx in selected:
        st.session_state.memory_selected = selected
        return

    selected.append(idx)

    if len(selected) == 2:
        st.session_state.memory_moves = st.session_state.get("memory_moves", 0) + 1
        a, b = selected
        if cards[a]["key"] == cards[b]["key"]:
            matched[a] = True
            matched[b] = True
            st.session_state.memory_found = st.session_state.get("memory_found", 0) + 1
            st.session_state.memory_message = f"正解！検索キー：{cards[a]['key']}"
            selected = []
        else:
            st.session_state.memory_message = "ちがいます。次のカードを押すと閉じます。"

    st.session_state.memory_matched = matched
    st.session_state.memory_selected = selected


def render_memory_card_button(card, idx):

    matched = st.session_state.get("memory_matched", [])
    selected = st.session_state.get("memory_selected", [])

    is_open = (
        idx < len(matched)
        and (
            matched[idx]
            or idx in selected
        )
    )

    if is_open:
        label = card["word"]
    else:
        label = "？"

    if idx < len(matched) and matched[idx]:
        label = "✓ " + label

    st.button(
        label,
        key=f"memory_card_{idx}_{card.get('id', idx)}",
        use_container_width=True,
        on_click=handle_memory_click,
        args=(idx,),
        disabled=(idx < len(matched) and matched[idx]),
    )


def render_memory_game_section():

    st.markdown("---")
    st.subheader("単語神経衰弱")

    with st.container(border=True):

        st.caption("同じ検索キーになる単語ペアを6組見つけるゲームです。")

        mem_rl_nm = {
            "ばりかた": 0,
            "かため": 1,
            "ふつう": 2,
            "やわめ": 3,
        }

        mem_rl_lb = st.radio(
            "神経衰弱の変換ルール",
            list(mem_rl_nm.keys()),
            horizontal=True,
            index=2,
            key="memory_rule_select",
        )

        mem_rl = mem_rl_nm[mem_rl_lb]
        mem_us12 = True

        if "memory_cards" not in st.session_state:
            start_memory_game(mem_rl_lb, mem_rl, mem_us12)

        if st.session_state.get("memory_rule") != mem_rl_lb:
            start_memory_game(mem_rl_lb, mem_rl, mem_us12)

        top_cols = st.columns([1, 1, 1], gap="small")
        with top_cols[0]:
            if st.button("新しいゲーム", key="memory_new", use_container_width=True):
                start_memory_game(mem_rl_lb, mem_rl, mem_us12)
                st.rerun()
        with top_cols[1]:
            st.metric("見つけたペア", f"{st.session_state.get('memory_found', 0)} / 6")
        with top_cols[2]:
            st.metric("めくった回数", st.session_state.get("memory_moves", 0))

        candidate_count = st.session_state.get("memory_candidate_count", 0)
        mem_word_count = st.session_state.get("memory_word_count", 0)
        st.caption(f"対象検索キー数: {candidate_count:,} / 登録単語数: {mem_word_count:,}")

        cards = st.session_state.get("memory_cards", [])

        if not cards:
            st.warning("この条件では、ペアを6組作れる検索キーが足りません。")
            return

        msg = st.session_state.get("memory_message", "")
        if msg:
            if msg.startswith("正解"):
                st.success(msg)
            else:
                st.info(msg)

        st.markdown(
            """
            <style>
            div[data-testid="stButton"] button[kind="secondary"]{
                min-height:3.4rem;
                white-space:normal;
                word-break:break-word;
                line-height:1.15;
                font-weight:800;
            }
            @media (max-width:640px){
                div[data-testid="stButton"] button[kind="secondary"]{
                    min-height:3rem;
                    font-size:.9rem;
                    padding:.35rem .25rem;
                }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # 12枚を3列×4段で表示。スマホでも比較的崩れにくい幅にする。
        for row_start in range(0, len(cards), 3):
            cols = st.columns(3, gap="small")
            for offset, col in enumerate(cols):
                idx = row_start + offset
                if idx < len(cards):
                    with col:
                        render_memory_card_button(cards[idx], idx)

        if st.session_state.get("memory_found", 0) >= 6:
            st.balloons()
            st.success("クリア！6ペアすべて見つけました。")

        with st.expander("答えを見る"):
            answer_groups = {}
            for card in cards:
                answer_groups.setdefault(card["key"], []).append(card["word"])

            for key, words in answer_groups.items():
                st.markdown(f"**{key}**")
                st.write(" / ".join(words))

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

# 羅列削除はシステムとして常時ON。
# 画面上のチェックボックスは表示しない。
us12 = True

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

    query_pre_rep = None

    if sch_md == "単語で検索":
        # 検索語側も通常ルールどおりに処理する。
        # ただし、検索語が羅列削除で短くなる場合は、
        # 羅列削除前の形が同じものだけを検索結果に残す。
        key = ext(
            qu,
            rl,
            us12
        )
        query_pre_rep = ext_pre_rep(
            qu,
            rl
        )
    else:
        # 母音検索では st0（お段+う、え段+いの短縮）は行わない。
        # ただし、羅列削除前キーによる絞り込みは単語検索と同じように行う。
        key = ext_vw_rule(
            qu,
            rl,
            us12
        )
        query_pre_rep = ext_vw_pre_rep(
            qu,
            rl
        )

    res = collect_search_results(vw_dic, key, query_pre_rep)

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
        st.write("羅列削除前キー:", ext_pre_rep(t, rl))
        st.write("母音検索キー:", ext_vw_rule(t, rl, us12))
        st.write("母音検索・羅列削除前キー:", ext_vw_pre_rep(t, rl))


render_flashcard_section()
render_memory_game_section()

with st.expander("未読漢字チェック"):

    if "kanji_problems" not in st.session_state:
        st.session_state.kanji_problems = []

    if st.button("チェック開始"):

        import re

        kanji_re = re.compile(
            r'[\u3400-\u4DBF\u4E00-\u9FFF]'
        )

        problems = []

        checked = set()

        for words in vw_dic.values():

            for word, *_ in words:

                if word in checked:
                    continue

                checked.add(word)

                reading = knf(word)

                remain = "".join(
                    kanji_re.findall(reading)
                )

                if remain:

                    problems.append(
                        (
                            word,
                            reading,
                            remain
                        )
                    )

        st.session_state.kanji_problems = problems

    problems = st.session_state.kanji_problems

    st.write(f"件数: {len(problems)}")

    if problems:

        text = "\n".join(
            f"{w} → {r} [{k}]"
            for w, r, k in problems
        )

        st.code(text)

        problem_words = {
            w for w, _, _ in problems
        }

        with open(wd_fl, encoding="utf-8") as f:
            original_lines = f.readlines()

        filtered_lines = []

        for line in original_lines:

            word = line.strip()

            if (
                word
                and not word.startswith("#")
                and word in problem_words
            ):
                continue

            filtered_lines.append(line)

        filtered_text = "".join(filtered_lines)

        st.text_area(
            "未読漢字除外版 words.txt",
            filtered_text,
            height=400
        )

        st.download_button(
            "除外版をダウンロード",
            filtered_text,
            file_name="words_filtered.txt",
            mime="text/plain"
        )

with st.expander("同一かなチェック"):

    if st.button("チェック開始", key="same_kana_check"):

        from collections import defaultdict

        # ------------------
        # 同一かなグループ作成
        # ------------------

        kana_groups = defaultdict(list)

        checked = set()

        for words in vw_dic.values():

            for word, *_ in words:

                if word in checked:
                    continue

                checked.add(word)

                kana = knf(word)

                kana_groups[kana].append(word)

        # 2語以上だけ残す
        kana_groups = {
            k: v
            for k, v in kana_groups.items()
            if len(v) >= 2
        }

        st.session_state.same_kana_groups = kana_groups

    kana_groups = st.session_state.get(
        "same_kana_groups",
        {}
    )

    if kana_groups:

        st.write(
            f"同一かなグループ数: {len(kana_groups)}"
        )

        selected_words = set()

        for idx, (kana, words) in enumerate(
            sorted(
                kana_groups.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )
        ):

            st.markdown(
                f"### {kana} （{len(words)}語）"
            )

            selected = st.radio(
                "残す単語",
                words,
                key=f"samekana_{idx}",
                label_visibility="collapsed"
            )

            selected_words.add(selected)

        # ------------------
        # words.txt生成
        # ------------------

        all_words = []

        with open(wd_fl, encoding="utf-8") as f:

            for line in f:

                word = line.strip()

                if not word:
                    continue

                if word.startswith("#"):
                    continue

                all_words.append(word)

        duplicate_words = set()

        for words in kana_groups.values():

            duplicate_words.update(words)

        filtered_words = []

        for word in all_words:

            if word in duplicate_words:

                if word in selected_words:
                    filtered_words.append(word)

            else:
                filtered_words.append(word)

        filtered_text = "\n".join(
            filtered_words
        )

        st.text_area(
            "同一かな除外版 words.txt",
            filtered_text,
            height=400
        )

        st.download_button(
            "除外版をダウンロード",
            filtered_text,
            file_name="words_samekana_filtered.txt",
            mime="text/plain"
        )
