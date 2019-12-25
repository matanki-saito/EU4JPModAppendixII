import glob
import json
import re
from os.path import join as _

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
            if translation == "":
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

            # otiginalと同じである場合はスキップ
            if original != nx_translation:
                # すでに訳が登録されており、それがさらに別の訳である場合、問題となる(1:n)
                if original in mapping_db:
                    if nx_translation not in mapping_db[original]:
                        mapping_db[original].append(nx_translation)

                # 訳が存在する場合は登録する
                else:
                    mapping_db[original] = [0, nx_translation]


def generate_name_map_from_cultures(paratranz_unzipped_folder_path,
                                    tmp_reverse_map,
                                    result,
                                    match_key_pattern):
    tmp_reverse_map = {}
    result = {}

    # Map生成
    countries_raw_jsons = _(paratranz_unzipped_folder_path, "raw", "history", "countries", "*.json")

    for json_file in glob.glob(countries_raw_jsons):
        load_map_from_file(
            reverse_map=tmp_reverse_map,
            file_path=json_file,
            mapping_db=result,
            match_key_pattern=match_key_pattern
        )
    return tmp_reverse_map, result


def generate_first_name_mapping(paratranz_unzipped_folder_path,
                                debug=False):
    """
    commonとhistoryからfirst名のマッピングを生成する。
    :param paratranz_unzipped_folder_path: sourceとなる展開したフォルダのパス
    :param debug: trueにすると1:nとn:1の問題があるものをprintする
    :return: 英日マッピング、日英マッピング
    """

    reverse_map = {}
    normal_map = {}

    reverse_map, normal_map = generate_name_map_from_cultures(
        paratranz_unzipped_folder_path,
        reverse_map,
        normal_map,
        match_key_pattern=r"(monarch|queen|heir|leader)\|name")

    # Map生成
    cultures_raw_json_file = _(paratranz_unzipped_folder_path,
                               "raw", "common", "cultures", "00_cultures.txt.json")

    load_map_from_file(
        reverse_map=reverse_map,
        file_path=cultures_raw_json_file,
        mapping_db=normal_map,
        match_key_pattern=r"female_names|male_names")

    if debug:
        for key, value in reverse_map.items():
            if len(value) > 1:
                print("n:1 / {}:{}".format(value, key))

        for key, value in normal_map.items():
            if len(value) > 2:
                print("1:n / {}:{}".format(key, value[1:]))

    return reverse_map, normal_map


def generate_dynasty_name_mapping(paratranz_unzipped_folder_path,
                                  debug=False):
    """
    commonとhistoryからdynasty名のマッピングを生成する。
    :param paratranz_unzipped_folder_path: sourceとなる展開したフォルダのパス
    :param debug: trueにするとprintする
    :return: 英日マッピング、日英マッピング
    """

    reverse_map = {}
    normal_map = {}

    reverse_map, normal_map = generate_name_map_from_cultures(
        paratranz_unzipped_folder_path,
        reverse_map,
        normal_map,
        match_key_pattern=r"(monarch|queen|heir|leader)\|dynasty")

    # Map生成
    cultures_raw_json_file = _(paratranz_unzipped_folder_path,
                               "raw", "common", "cultures", "00_cultures.txt.json")

    load_map_from_file(
        reverse_map=reverse_map,
        file_path=cultures_raw_json_file,
        mapping_db=normal_map,
        match_key_pattern=r"dynasty_names")

    if debug:
        for key, value in reverse_map.items():
            if len(value) > 1:
                print("n:1 / {}:{}".format(value, key))

        for key, value in normal_map.items():
            if len(value) > 2:
                print("1:n / {}:{}".format(key, value[1:]))

    return reverse_map, normal_map


if __name__ == "__main__":
    path = _("./", "2019_12_20_23_04_11")
    # generate_dynasty_name_mapping(paratranz_unzipped_folder_path=path)
    generate_first_name_mapping(paratranz_unzipped_folder_path=path, debug=True)
