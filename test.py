from pyparsing import *

test = """
Geso = {
    key = 1
}
"""


def hoge(x):
    return x[0][1]


def main():
    group = Forward()
    container = Forward()

    key = Regex(r'[\.\-A-zÀ-ÿœšŸŠŒŽž\'0-9_]*')

    begin_container = Word("{")
    end_container = Word("}")

    begin_array = Word("{")
    end_array = Word("}")
    false = Word("false").setParseAction(lambda x: False)
    null = Word("null").setParseAction(lambda x: None)
    true = Word("true").setParseAction(lambda x: True)

    identify = Regex(r'[\.\-A-zÀ-ÿœšŸŠŒŽž’\'0-9_]+')

    operator = Word("=") | Word("<") | Word(">") | Word("=>") | Word("<=")

    value = container | group
    value.setParseAction(lambda x: x[0])

    head = group("head")
    tail = Group(ZeroOrMore(group("m")))

    sentences = Group(Optional(head + tail))

    primitive = false | null | true | identify | Word(nums) | Word("no") | Word("yes")

    # { xxxx }
    container <<= Group(begin_container + sentences + end_container)
    container.setParseAction(hoge)

    # Key = xxx もしくは 1など
    group <<= Group(key("key") + operator("operator") + value("value")) | primitive

    start = Group(ZeroOrMore(group))

    print(start.parseString(test).dump(include_list=False))


if __name__ == "__main__":
    main()
