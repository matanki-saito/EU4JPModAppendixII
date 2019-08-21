import json
import os
import pathlib
import re
from os.path import join as _

from special_escape import generate_printer, generate_encoder

encoder = generate_encoder("eu4", "txt")
printer = generate_printer("eu4", "txt")

# 万能ではないが、とりあえずこれで
force_mapping = {
    "Ibrahim": "イブラーヒーム"
}

# suffix_list = ['', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓', '⛎']
suffix_list = ['', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']


def load_map_from_file(reverse_map,
                       file_path,
                       mapping_db,
                       match_key_pattern=None):
    """
    ＼＼٩( 'ω' )و ／／
    :param reverse_map: [A]^-1
    :param file_path: 対象のファイル
    :param mapping_db: マッピング。破壊的
    :param match_key_pattern: マッチさせるキーのパターン
    :return:
    """
    match_key_compiled_pattern = None
    if match_key_pattern is not None:
        match_key_compiled_pattern = re.compile(match_key_pattern)

    with open(file_path, 'r', encoding='utf-8') as f:
        for entry in json.load(f):
            key = entry["key"]
            original = entry["original"]
            translation = entry["translation"]

            # 訳が空の場合はスキップ
            if translation is "":
                translation = original

            # n:1をチェックする
            if translation in reverse_map:
                if original not in reverse_map[translation]:
                    reverse_map[translation].append(original)
            else:
                reverse_map[translation] = [original]

            suffix_index = reverse_map[translation].index(original)

            # キーのパターンチェック
            if match_key_compiled_pattern is not None and match_key_compiled_pattern.search(key) is None:
                continue

            nx_translation = '{}{}'.format(translation, suffix_list[suffix_index])

            # すでに訳が登録されており、それがさらに別の訳である場合、問題となる(1:n)
            if original in mapping_db:
                if nx_translation not in mapping_db[original]:
                    mapping_db[original].append(nx_translation)

            # 訳が存在する場合は登録する
            else:
                mapping_db[original] = [0, nx_translation]


def gen_map(target_dir_path,
            match_key_pattern=None):
    tmp_reverse_map = {}
    result = {}

    # Map生成
    for file in os.listdir(path=target_dir_path):
        load_map_from_file(
            reverse_map=tmp_reverse_map,
            file_path=os.path.join(target_dir_path, file),
            mapping_db=result,
            match_key_pattern=match_key_pattern
        )

    print("---------")

    for key, value in tmp_reverse_map.items():
        if len(value) > 1:
            print("n:1 / {}:{}".format(value, key))

    return result


debuga = {}


def replace_text(name,
                 src_text,
                 match_pattern,
                 translation_map,
                 file_path):
    """
    対象のテキストを読み込んで、マッチする部分を変更する
    :param name: ラベル
    :param src_text:　対象のテキスト
    :param match_pattern: マッチパターン、(x)(target)(x)である必要がある
    :param translation_map: 翻訳マッピングオブジェクト key:[text1,text2,...]
    :param file_path: ファイルパス
    :return: 置換えされたテキストと個数のタプル
    """

    def repl(x):
        """
        置き換え関数
        :param x: グルーピングされたマッチオブジェクト
        :return: 置き換え後の文字列
        """

        groups = x.groups()
        # "でテキストがwrapされていない
        if len(groups) >= 8 and groups[6] is not None and groups[7] is not None:
            pre = groups[6]
            text = groups[7]
        # "でテキストがwrapされている
        elif len(groups) >= 6 and groups[2] is not None and groups[4] is not None:
            pre = groups[2]
            text = groups[4]
        else:
            raise

        if text in force_mapping:
            mapping_text = force_mapping[text]
        elif text in translation_map:
            lis = translation_map.get(text)
            if len(lis) > 2:
                lis[0] += 1

            mapping_text = lis[1]
        else:
            mapping_text = None

        key = '{}:{}:{}'.format(name, text, '' if mapping_text is None else mapping_text)
        if key not in debuga:
            debuga[key] = set()
        debuga[key].add(file_path)

        if mapping_text is None or text == mapping_text:
            return groups[0]
        else:
            return '{}"{}"'.format(pre, mapping_text)

    return re.sub(match_pattern, repl, src_text)


def u_write(file_path, text):
    """
    拡張子を変更して保存する
    :param file_path: ファイルパス
    :param text: 書き込み対象のテキスト
    :return: なし
    """

    if os.path.exists(file_path):
        return

    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    printer(src_array=encoder(src_array=map(ord, text)), out_file_path=file_path)


def scan_files(src_path,
               dst_path,
               target_list):
    """
    :param src_path:  ソースのパス
    :param dst_path:　成果物のパス
    :param target_list: ターゲット
    :return: なし
    """

    if not os.path.exists(src_path):
        raise Exception('srcがおかしい')

    if not os.path.exists(dst_path):
        raise Exception('dstがおかしい')

    for file_path in pathlib.Path(src_path).glob('**/*.txt'):
        # events/Tenguri.txtなどはコメントにUTF-8で書き込んでいるようで、テキストにCP1252には存在しない
        # 0x81などが発生してしまうのでignoreしている
        with open(str(file_path), 'r', encoding='windows-1252', errors='ignore') as f:
            src_text = dst_text = f.read()
            for target in target_list:
                dst_text = replace_text(name=target.name,
                                        src_text=dst_text,
                                        match_pattern=target.match_pattern,
                                        translation_map=target.map,
                                        file_path=file_path)

            # 変更があったもののみを保存
            if dst_text != src_text:
                a = str(file_path).replace(src_path + "\\", "")
                u_write(os.path.join(dst_path, a),
                        dst_text)

    print("---------")
    for target in target_list:
        for key, value in target.map.items():
            if len(value) > 2:
                print(("★" if value[0] > 0 else "☆") + " 1:n / {}:{}".format(key, value[1:]))


class Target(object):
    def __init__(self, name, ignore_list, match_pattern, mapper):
        self.name = name
        self.ignore_list = ignore_list
        self.match_pattern = match_pattern
        self.map = mapper


def replace_items(paratranz_unziped_folder_path,
                  output_folder_path,
                  resource_dir_path):
    """
    :param paratranz_unziped_folder_path: paratranzのフォルダパス
    :param output_folder_path: 出力フォルダパス
    :param resource_dir_path:
    :return:
    """

    target_list = [
        Target(name="monarch",
               ignore_list="TBD",
               match_pattern=r'(((\shas_ruler\s*=\s*)("([^"]+)"))|((\shas_ruler\s*=\s*)([^"\s]+)))',
               mapper=gen_map(
                   target_dir_path=_(paratranz_unziped_folder_path, "raw\\history\\countries"),
                   match_key_pattern=r"monarch\|name"
               )),
        Target(name="heir",
               ignore_list="TBD",
               match_pattern=r'(((\shas_heir\s*=\s*)("([^"]+)"))|((\shas_heir\s*=\s*)([^"\s]+)))',
               mapper=gen_map(
                   target_dir_path=_(paratranz_unziped_folder_path, "raw\\history\\countries"),
                   match_key_pattern=r"heir\|name"
               )),
        Target(name="leader",
               ignore_list="TBD",
               match_pattern=r'(((\shas_leader\s*=\s*)("([^"]+)"))|((\shas_leader\s*=\s*)([^"\s]+)))',
               mapper=gen_map(
                   target_dir_path=_(paratranz_unziped_folder_path, "raw\\history\\countries"),
                   match_key_pattern=r"leader\|name"
               )),
        Target(name="dynasty",
               ignore_list="TBD",
               match_pattern=r'(((\sdynasty\s*=\s*)("([^"]+)"))|((\sdynasty\s*=\s*)([^"\s]+)))',
               mapper=gen_map(
                   target_dir_path=_(paratranz_unziped_folder_path, "raw\\history\\countries"),
                   match_key_pattern=r"(monarch|queen|heir)\|dynasty"
               ))
    ]

    scan_files(target_list=target_list,
               src_path=resource_dir_path,
               dst_path=output_folder_path)

    with open(_('tmp', "keys.txt"), 'w', encoding="utf-8") as fw:
        for key in debuga:
            fw.write("{}:\n{}\n\n".format(key, ','.join(map(os.path.basename, debuga[key]))))
