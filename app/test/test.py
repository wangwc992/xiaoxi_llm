from app.data.dictionaries import school_abbreviations

q = "墨大留学"


def query_rewrite(query):
    # 遍历school_abbreviation
    for index, school_abbreviation in enumerate(school_abbreviations):
        # 从第二个元素开始，遍历school_abbreviation
        for school in school_abbreviation[1:]:
            if school in query:
                query = query.replace(school, f'''{school}({school_abbreviation[0]})''')
                return query
    return query


if __name__ == '__main__':
    print(query_rewrite(q))
