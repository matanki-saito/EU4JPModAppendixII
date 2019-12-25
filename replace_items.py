import os
import pathlib
import re
from os.path import join as _

from generate_map import generate_dynasty_name_mapping, generate_first_name_mapping
from special_escape import generate_printer, generate_encoder

encoder = generate_encoder("eu4", "txt")
printer = generate_printer("eu4", "txt")

# 万能ではないが、とりあえずこれで
force_mapping = {
    "Ibrahim": "イブラーヒーム"
}

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

    if match_pattern is None:
        match_pattern = r'((\s+)("?)(' + '|'.join(map(re.escape, translation_map.keys())) + r')("?)(\s+))'
        match_pattern = re.compile(match_pattern)

    def repl(x):
        """
        置き換え関数
        :param x: グルーピングされたマッチオブジェクト
        :return: 置き換え後の文字列
        """

        groups = x.groups()
        # "でテキストがwrapされていない
        if len(groups) >= 5 and groups[3] is not None:
            pre = groups[1]
            text = groups[3]
            post = groups[5]
        # "でテキストがwrapされている
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
            return '{}"{}"{}'.format(pre, mapping_text, post)

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

    #    printer(src_array=encoder(src_array=map(ord, text)), out_file_path=file_path)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


def scan_files(src_path,
               dst_path,
               target_list,
               translated_utf8_path):
    """
    :param src_path:  ソースのパス
    :param dst_path:　成果物のパス
    :param target_list: ターゲット
    :param translated_utf8_path: UTF8 source path
    :return: なし
    """

    if not os.path.exists(src_path):
        raise Exception('srcがおかしい')

    if not os.path.exists(dst_path):
        raise Exception('dstがおかしい')

    for file_path in pathlib.Path(src_path).glob('**/*.txt'):
        base_path = str(file_path).replace(src_path + "\\", "")

        # resource folderにあるものを見る
        # events/Tenguri.txtなどはコメントにUTF-8で書き込んでいるようで、テキストにCP1252には存在しない
        # 0x81などが発生してしまうのでignoreしている
        with open(str(file_path), 'r', encoding='windows-1252', errors='ignore') as f:
            dst_text = resource_text = f.read()

        # utf8 sourceを見る
        t_path = _(translated_utf8_path, base_path)
        if os.path.exists(t_path) and not base_path.startswith("history\\countries\\") \
                and not base_path.startswith("common\\culutres\\00_cultures.txt"):
            with open(str(t_path), 'r', encoding='utf-8') as f:
                dst_text = f.read()

        for target in target_list:
            dst_text = replace_text(name=target.name,
                                    src_text=dst_text,
                                    match_pattern=target.match_pattern,
                                    translation_map=target.map,
                                    file_path=file_path)

            # 変更があったもののみを保存
            if dst_text != resource_text:
                u_write(os.path.join(dst_path, base_path), dst_text)

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

    revert_map1, normal_map1 = generate_dynasty_name_mapping(
        paratranz_unzipped_folder_path=paratranz_unziped_folder_path)

    revert_map2, normal_map2 = generate_first_name_mapping(
        paratranz_unzipped_folder_path=paratranz_unziped_folder_path)

    normal_map1 = dict(normal_map1, **normal_map2)

    target_list = [
        Target(name="dynasty",
               ignore_list="TBD",
               match_pattern=None,
               mapper=normal_map1)
    ]

    scan_files(target_list=target_list,
               src_path=resource_dir_path,
               dst_path=output_folder_path,
               translated_utf8_path=_(paratranz_unziped_folder_path, "utf8"))

    with open(_('tmp', "keys.txt"), 'w', encoding="utf-8") as fw:
        for key in debuga:
            fw.write("{}:\n{}\n\n".format(key, ','.join(map(os.path.basename, debuga[key]))))
