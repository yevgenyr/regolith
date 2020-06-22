import pytest

from regolith.tools import (
    filter_publications,
    fuzzy_retrieval,
    fragment_retrieval,
    number_suffix,
    latex_safe,
    update_schemas,
    merge_collections,
    group,
    is_fully_appointed,
    group_member_ids,
    month_and_year,
    awards_grants_honors,
    get_id_from_name,
    date_to_rfc822,
    key_value_pair_filter,
    collection_str,
    search_collection,
    collect_appts,
    search_collection,
    get_grant_amount,
    )


def test_author_publications():
    citations = [{"author": ["CJ", "SJLB"]}, {"editor": "SJLB"}]
    filter_publications(citations, {"SJLB"})


def test_fuzzy_retrieval():
    person = {
        "_id": "scopatz",
        "aka": [
            "Scopatz",
            "Scopatz, A",
            "Scopatz, A.",
            "Scopatz, A M",
            "Anthony Michael Scopatz",
        ],
        "name": "Anthony Scopatz",
    }
    assert fuzzy_retrieval([person], ["aka", "name", "_id"],
                           "scopatz") == person
    assert fuzzy_retrieval([person], ["aka", "name", "_id"],
                           "scopatz, a") is None
    assert (
            fuzzy_retrieval(
                [person], ["aka", "name", "_id"], "scopatz, a",
                case_sensitive=False,
            )
            == person
    )


@pytest.mark.parametrize(
    "input,expected",
    [
        (0, "th"),
        (1, "st"),
        (2, "nd"),
        (3, "rd"),
        (4, "th"),
        (10, "th"),
        (13, "th"),
        (33, "rd"),
        (None, ""),
        ("0", ""),
    ],
)
def test_number_suffix(input, expected):
    assert number_suffix(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (
                (
                        [
                            {
                                "_id": "proposal1",
                                "title": "European swallow",
                                "author": "king arthur",
                            }
                        ],
                        [{"_id": "grant1", "linked_to": "proposal1",
                          "amount": "100 mph"}],
                ),
                [
                    {
                        "_id": "grant1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "linked_to": "proposal1",
                        "amount": "100 mph",
                    }
                ],
        ),
        (
                (
                        [
                            {
                                "_id": "proposal1",
                                "title": "European swallow",
                                "author": "king arthur",
                            },
                            {
                                "_id": "proposal2",
                                "title": "African swallow",
                                "author": "king arthur",
                            },
                        ],
                        [{"_id": "grant1", "linked_to": "proposal1",
                          "amount": "100 mph"}],
                ),
                [
                    {
                        "_id": "grant1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "linked_to": "proposal1",
                        "amount": "100 mph",
                    }
                ],
        ),
        (
                (
                        [
                            {
                                "_id": "proposal1",
                                "title": "European swallow",
                                "author": "king arthur",
                                "amount": "50 mph",
                            },
                            {
                                "_id": "proposal2",
                                "title": "African swallow",
                                "author": "king arthur",
                            },
                        ],
                        [{"_id": "grant1", "linked_to": "proposal1",
                          "amount": "100 mph"}],
                ),
                [
                    {
                        "_id": "grant1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "linked_to": "proposal1",
                        "amount": "100 mph",
                    }
                ],
        ),
    ],
)
def test_merge_collections(input, expected):
    a = input[0]
    b = input[1]
    target_id = "linked_to"
    assert merge_collections(a, b, target_id) == expected


@pytest.mark.parametrize(
    "input,expected,kwargs",
    [
        ("$hi", r"\$hi", {}),
        (
                r"Website: https://github.com/CJ-Wright/"
                r"Masters_Thesis/raw/master/thesis.pdf hi",
                r"Website: \url{https://github.com/CJ-Wright/"
                r"Masters_Thesis/raw/master/thesis.pdf} hi",
                {},
        ),
        (
                r"Website: https://github.com/CJ-Wright/"
                r"Masters_Thesis/raw/master/thesis.pdf hi",
                r"Website: \href{https://github.com/CJ-Wright/"
                r"Masters_Thesis/raw/master/thesis.pdf} hi",
                {"wrapper": "href"},
        ),
        (
                r"Website: https://github.com/CJ-Wright/"
                r"Masters_Thesis/raw/master/thesis.pdf hi",
                r"Website: https://github.com/CJ-Wright/"
                r"Masters\_Thesis/raw/master/thesis.pdf hi",
                {"url_check": False},
        ),
    ],
)
def test_latex_safe(input, expected, kwargs):
    output = latex_safe(input, **kwargs)
    assert output == expected


DEFAULT_SCHEMA = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
    },
}

USER_SCHEMA0 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {"type": "dict",
                       "schema": {"day": {"required": False, }, }, },
        },
    },
}

EXPECTED_SCHEMA0 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": False,
                        "type": "integer",
                    },
                },
            },
        },
    },
}

USER_SCHEMA1 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {"type": "dict",
                       "schema": {"day": {"type": "string", }, }, },
        },
    },
}

EXPECTED_SCHEMA1 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "string",
                    },
                },
            },
        },
    },
}

USER_SCHEMA2 = {
    "expenses": {
        "begin_day": {
            "description": "The first day of expense",
            "required": True,
            "type": "string",
        }
    },
}

EXPECTED_SCHEMA2 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
        "begin_day": {
            "description": "The first day of expense",
            "required": True,
            "type": "string",
        },
    },
}

USER_SCHEMA3 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {"day": {"description": "The date on the receipt"}, },
            },
        },
    },
}

EXPECTED_SCHEMA3 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "The date on the receipt",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
    },
}

USER_SCHEMA4 = {
    "expenses": {
        "itemized_expenses": {
            "schema": {
                "schema": {
                    "prepaid_expense": {
                        "description": "Expense paid by the direct billing",
                        "required": True,
                        "type": "float",
                    },
                },
            },
        },
    },
}

EXPECTED_SCHEMA4 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                    "prepaid_expense": {
                        "description": "Expense paid by the direct billing",
                        "required": True,
                        "type": "float",
                    },
                },
            },
        },
    },
}

USER_SCHEMA5 = {}

EXPECTED_SCHEMA5 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
    },
}

USER_SCHEMA6 = {"expenses": {}}

EXPECTED_SCHEMA6 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
    },
}


@pytest.mark.parametrize(
    "default_schema, user_schema, expected_schema",
    [
        (DEFAULT_SCHEMA, USER_SCHEMA0, EXPECTED_SCHEMA0),
        (DEFAULT_SCHEMA, USER_SCHEMA1, EXPECTED_SCHEMA1),
        (DEFAULT_SCHEMA, USER_SCHEMA2, EXPECTED_SCHEMA2),
        (DEFAULT_SCHEMA, USER_SCHEMA3, EXPECTED_SCHEMA3),
        (DEFAULT_SCHEMA, USER_SCHEMA4, EXPECTED_SCHEMA4),
        (DEFAULT_SCHEMA, USER_SCHEMA5, EXPECTED_SCHEMA5),
        (DEFAULT_SCHEMA, USER_SCHEMA6, EXPECTED_SCHEMA6),
    ],
)
def test_update_schemas(default_schema, user_schema, expected_schema):
    updated_schema = update_schemas(default_schema, user_schema)
    assert updated_schema == expected_schema


def test_group():
    doc0 = {"k0": "v00", "k1": "v01"}
    doc1 = {"k0": "v10", "k1": "v11"}
    doc2 = {"k1": "v21"}
    doc3 = {"k0": "v00", "k1": "v31"}
    db = (doc for doc in (doc0, doc1, doc2, doc3))
    by = "k0"
    expect = {"v00": [doc0, doc3], "v10": [doc1]}
    assert group(db, by) == expect

ppl_coll = [
    {
        "_id": "m1",
        "name": "member1",
        "education": [{
            "group": "bg",
            "institution": "columbiau",
            "degree": "PhD",
            "department": "apam",
            "begin_year": 2016
        }],
        "employment": [{
            "begin_year": 2020,
            "begin_month": 1,
            "organization": "columbiau",
            "position": "Undergraduate Researcher",
            "advisor": "sbillinge",
            "status": "undergrad"
        }]
    },
    {
        "_id": "nm1",
        "name": "non-member1",
        "education": [{
            "institution": "columbiau",
            "degree": "PhD",
            "department": "apam",
            "begin_year": 2016
        }],
        "employment": [{
            "begin_year": 2020,
            "begin_month": 1,
            "organization": "columbiau",
            "position": "Undergraduate Researcher",
            "advisor": "sbillinge",
            "status": "undergrad"
        }]
    },
    {
        "_id": "m2",
        "name": "member2",
        "education": [{
            "institution": "columbiau",
            "degree": "PhD",
            "department": "apam",
            "begin_year": 2016
        }],
        "employment": [{
            "begin_year": 2020,
            "begin_month": 1,
            "group": "bg",
            "organization": "columbiau",
            "position": "Undergraduate Researcher",
            "advisor": "sbillinge",
            "status": "undergrad"
        }]
    },
]

@pytest.mark.parametrize(
    "input,expected",
    [
        (ppl_coll, set(["m1", "m2"])),
    ],
)
def test_group_member_ids(input, expected):
    actual = group_member_ids(input, "bg")
    assert actual == expected

p1 = {
    "_id": "scopatz",
    "aka": [
        "Scopatz",
        "Scopatz, A",
        "Scopatz, A.",
        "Scopatz, A M",
        "Anthony Michael Scopatz",
    ],
    "name": "Anthony Scopatz",
}
p2 = {
    "_id": "abc",
    "aka": [
        "A. BC",
        "BC, A",
        "Anthony BC",
    ],
    "name": "Anthony Bill Chris",
}

@pytest.mark.parametrize(
    "input, expected",
    [
        (([p1, p2], ["aka", "name", "_id"],
                           "Anth", False),[p1,p2]),
        (([p1, p2], ["aka", "name", "_id"],
                           "scopatz, a", True),[]),
        (([p1, p2], ["aka", "name", "_id"],
                           "scopatz, a", False),[p1]),
        (([p1, p2], ["aka", "name", "_id"],
                           "ill", False),[p2]),          
    ],
)
def test_fragment_retrieval(input, expected):
    assert(fragment_retrieval(input[0],input[1],input[2],case_sensitive = input[3]) == expected)

@pytest.mark.parametrize(
    "input, expected",
    [
        ((None, None), "present"),
        ((None, 2002), "2002"),
        ((5,2002), "May 2002"),        
    ],
)
def test_month_and_year(input,expected):
    assert(month_and_year(input[0],input[1]) == expected)

@pytest.mark.parametrize(
    "appts,start,end,expected",
    [
        ({"name": "Kurt Godel",
          "_id": "kgodel",
          "appointments": [
            {"begin_year": 2017,
             "begin_month": 6,
             "begin_day": 1,
             "end_year": 2017,
             "end_month": 6,
             "end_day": 30,
             "grant": "grant1",
             "loading": 1.0,
             "type": "pd",
            }]}, "2017-06-01", "2017-07-01", False),
        ({"name": "MC Escher",
          "_id": "mcescher",
          "appointments": [
            {"begin_date": '2017-06-01',
             "end_date": '2017-06-30',
             "grant": "grant1",
             "loading": 0.5,
             "type": "pd",
            },
           {"begin_date": '2017-06-01',
            "end_date": '2017-06-30',
            "grant": "grant2",
            "loading": 0.5,
            "type": "pd",
            }]} , "2017-06-01", "2017-06-30", True),
        ({"name": "Johann Sebastian Bach",
          "_id": "jsbach",
          "appointments":[
            {"begin_date": '2017-06-01',
             "end_date": '2017-06-30',
             "grant": "grant1",
             "loading": 0.5,
             "type": "pd",
            },
            {"begin_date": '2017-06-02',
             "end_date": '2017-06-29',
             "grant": "grant2",
             "loading": 0.5,
             "type": "pd",
            }]}, "2017-06-01", "2017-06-30", False),
        ({"name": "Evariste Galois",
          "_id": "egalois",
          "appointments": [
            {"begin_date": '2017-06-01',
             "end_date": '2017-06-15',
             "grant": "grant1",
             "loading": 1.0,
             "type": "pd",
            },
            {"begin_date": '2017-06-16',
             "end_date": '2017-06-30',
             "grant": "grant2",
             "loading": 1.0,
             "type": "pd",
            }]},"2017-06-01", "2017-06-30", True),
        ({"name": "Ludwig Wittgenstein",
          "_id": "lwittgenstein",
          "appointments": [
            {"begin_date": '2017-06-01',
             "end_date": '2017-06-15',
             "grant": "grant1",
             "loading": 1.0,
             "type": "pd",
            },
            {"begin_date": '2017-06-17',
             "end_date": '2017-06-30',
             "grant": "grant2",
             "loading": 1.0,
             "type": "pd",
            },
            {"begin_date": '2017-07-01',
             "end_date": '2017-07-30',
             "grant": "grant3",
             "loading": 1.0,
             "type": "pd",
            }]}, "2017-06-01", "2017-06-30", False),
        ({"name": "Buckminster Fuller",
          "_id": "bfuller",
          "appointments":[
            {"begin_date": '2017-06-01',
             "end_date": '2017-06-30',
             "grant": "grant1",
             "loading": 1.0,
             "type": "pd",
            },
            {"begin_date": '2017-06-17',
             "end_date": '2017-06-30',
             "grant": "grant2",
             "loading": 1.0,
             "type": "pd",
            }]}, "2017-06-01", "2017-06-30", False),
    ],
)
def test_is_fully_appointed(appts, start, end, expected):
    actual = is_fully_appointed(appts, start, end)
    assert actual == expected

@pytest.mark.parametrize(
    "input, expected",
    [
        ({'funding':[
            {"name": "Omega Laser User's Group Travel Award",
             "value": 1100,
             "year": 2013},
            {"name": "NIF User's Group Travel Award",
             "value": 1150,
             "year": 2013}]},
        [{'description': "Omega Laser User's Group Travel Award (\\$1,100)",
          'year': 2013,
          '_key': 2013.0},
         {'description':"NIF User's Group Travel Award (\\$1,150)",
          'year': 2013,
          '_key': 2013.0}]),
        ({'funding':[
            {"name": "Omega Laser User's Group Travel Award",
             "value": 1100,
             "year": 2013}],
             "service":[{"name": "International Steering Committee", "role": "chair",
                         "type": "profession", "year": 2020,
                         "month": 3, "notes": ["something"]}]},
         [{"description":"International Steering Committee",
           "year":2020,
           "_key":2020.03},
          {'description': "Omega Laser User's Group Travel Award (\\$1,100)",
           'year': 2013,
           '_key': 2013.0}]
        )
    ],
)
def test_get_id_from_name(input,expected):
    assert(awards_grants_honors(input) == expected)

@pytest.mark.parametrize(
    "input, expected",
    [
        (([{'_id':'afriend','aka':['AB Friend','Tony Friend'], 'name': 'Anthony B Friend'}], 'Simon'), None),
        (([{'_id':'afriend','aka':['AB Friend','Tony Friend'], 'name': 'Anthony B Friend'}], 'Anthony B Friend'),
         'afriend'),
        (([{'_id':'afriend','aka':['AB Friend','Tony Friend'], 'name': 'Anthony B Friend'},
           {'_id':'aeinstein','aka':['Einstein'], 'name': 'Albert Einstein'}],
         'Albert Einstein'),
         'aeinstein')
    ],
)
def test_get_id_from_name(input,expected):
    assert(get_id_from_name(input[0],input[1]) == expected)

@pytest.mark.parametrize(
    "input, expected",
    [
        ((2012, 'Jan', 18), 'Wed, 18 Jan 2012 00:00:00 -0000'),
        ((2020, 6, 22), 'Mon, 22 Jun 2020 00:00:00 -0000'),
    ],
)
def test_date_to_rfc822(input,expected):
    assert(date_to_rfc822(input[0], input[1], input[2]) == expected)

person1 = {
    "_id": "scopatz",
    "aka": [
        "Scopatz",
        "Scopatz, A",
        "Scopatz, A.",
        "Scopatz, A M",
        "Anthony Michael Scopatz",
    ],
    "name": "Anthony Scopatz",
    "position": "Professor"
}
person2 = {
    "_id": "abc",
    "aka": [
        "A. BC",
        "BC, A",
        "Anthony BC",
    ],
    "name": "Anthony Bill Chris",
    "position": "Professor"
}
person3 = {
    "_id": "jdoe",
    "aka": [
        "A. BC",
        "BC, A",
        "Anthony BC",
    ],
    "name": "John Doe",
}
people = [person1, person2, person3]
@pytest.mark.parametrize(
    "input, expected",
    [
        ((people, ['name', 'Doe']), [person3]),
        ((people, ['name', 'Jerry']), []),
        ((people, ['position', 'Prof']), [person1, person2]),
        ((people, ['position', 'Prof', 'name', 'Chris']), [person2]),
    ],
)
def test_key_value_pair_filter(input, expected):
    assert(key_value_pair_filter(input[0], input[1]) == expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (([person3], None), "jdoe    \n"),
        (([], None), ''),
        (([person1, person2], ['position']), "scopatz    position: Professor    \nabc    position: Professor    \n"),
        (([person2], ['position']), "abc    position: Professor    \n"),
    ],
)
def test_collection_str(input, expected):
    assert(collection_str(input[0], input[1]) == expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        ((people, ['name', 'Doe'], None), "jdoe    \n"),
        ((people, ['name', 'Jerry'], None), ""),
        ((people, ['position', 'Prof', 'name', 'Chris'], None), "abc    \n"),
        ((people, ['position', 'prof', 'name', 'Chris'], ['position']), "abc    position: Professor    \n"),
    ],
)
def test_search_collection(input, expected):
    assert(search_collection(input[0], input[1], input[2]) == expected)


appointed_people = [
    {'name': 'Kurt Godel', '_id': 'kgodel',
     'appointments':
     [{'_id': 'A', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.5, 'type': 'gra'},
      {'_id': 'B', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.25, 'type': 'gra'},
      {'_id': 'C', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.25, 'type': 'gra'}]
    },
    {'name': 'MC Escher', '_id': 'mcescher',
     'appointments':
     [{'_id': 'A', "begin_date": '2019-10-01', "end_date": '2019-10-31', 'grant': 'grant1', 'loading': 1.0, 'type': 'ss'},
      {'_id' :'B', "begin_date": '2019-11-01', "end_date": '2019-11-30', 'grant': 'grant2', 'loading': 0.5, 'type': 'ss'},
      {'_id': 'C', "begin_date": '2019-11-01', "end_date": '2019-11-30', 'grant': 'grant3', 'loading': 0.5, 'type': 'ss'},]
    },
    {'name': 'Johann Sebastian Bach', '_id': 'jsbach',
     'appointments':
     [{'_id': 'A', "begin_date": '2019-12-01', "end_date": '2020-12-15', 'grant': 'grant1', 'loading': 0.9, 'type': 'pd'},
      {'_id': 'B', "begin_date": '2019-12-16', "end_date": '2020-12-31', 'grant': 'grant2', 'loading': 0.9, 'type': 'pd'},
      {'_id': 'C', "begin_date": '2019-12-01', "end_date": '2020-12-31', 'grant': 'grant3', 'loading': 0.1, 'type': 'pd'}]
    },
    {'name': 'Ludwig Wittgenstein', '_id': 'lwittgenstein',
     'appointments':
     [{'_id': 'A', 'begin_date': '2019-12-10', 'end_date': '2019-12-20', 'grant': 'grant2', 'loading': 1.0, 'type': 'ss'}]
    },
    {'name': 'Karl Popper', '_id': 'kpopper',
     'appointments':
     [{'_id': 'A', 'begin_date': '2019-12-25', 'end_date': '2019-12-31', 'grant': 'grant2', 'loading': 1.0, 'type': 'ss'}]
     },
    {'name': 'GEM Anscombe', '_id': 'ganscombe', 'appointments': []},
    {'name': 'Sophie Germain', '_id': 'sgermain',
     'appointments':
         [{'_id': 'A', 'begin_date': '2019-09-02', 'end_date': '2019-09-06', 'grant': 'grant4', 'loading': 1.0,
           'type': 'ss'}]
     },
    ]

@pytest.mark.parametrize(
    "people,key,value,start,end,expected",
    [(appointed_people, 'grant', 'grant1', None, None,
      [{'person': 'kgodel', '_id': 'A', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.5, 'type': 'gra'},
       {'person': 'kgodel', '_id': 'B', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.25, 'type': 'gra'},
       {'person': 'kgodel', '_id': 'C', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.25, 'type': 'gra'},
       {'person': 'mcescher', '_id': 'A', "begin_date": '2019-10-01', "end_date": '2019-10-31', 'grant': 'grant1', 'loading': 1.0, 'type': 'ss'},
       {'person': 'jsbach', '_id': 'A', "begin_date": '2019-12-01', "end_date": '2020-12-15', 'grant': 'grant1', 'loading': 0.9, 'type': 'pd'},
      ]),
     (appointed_people, None, None, '2019-09-01', '2019-09-30',
      [{'person': 'kgodel', '_id': 'A', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.5, 'type': 'gra'},
       {'person': 'kgodel', '_id': 'B', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.25, 'type': 'gra'},
       {'person': 'kgodel', '_id': 'C', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.25, 'type': 'gra'},
       {'person': 'sgermain', '_id': 'A', 'begin_date': '2019-09-02', 'end_date': '2019-09-06', 'grant': 'grant4', 'loading': 1.0, 'type': 'ss'} ,
      ]),
     (appointed_people, ['loading', 'type'], [1.0, 'ss'], '2019-12-15', '2019-12-25',
      [{'person': 'lwittgenstein', '_id': 'A', 'begin_date': '2019-12-10', 'end_date': '2019-12-20', 'grant': 'grant2', 'loading': 1.0, 'type': 'ss'},
       {'person': 'kpopper', '_id': 'A', 'begin_date': '2019-12-25', 'end_date': '2019-12-31', 'grant': 'grant2', 'loading': 1.0, 'type': 'ss'}
       ]),
     (appointed_people, ['loading', 'type', 'grant'], [0.9, 'pd', 'grant3'], None, None, []),
     (appointed_people, None, None, None, None,
      [{'person': 'kgodel', '_id': 'A', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.5, 'type': 'gra'},
       {'person': 'kgodel', '_id': 'B', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.25, 'type': 'gra'},
       {'person': 'kgodel', '_id': 'C', "begin_date": '2019-09-01', "end_date": '2019-09-10', 'grant': 'grant1', 'loading': 0.25, 'type': 'gra'},
       {'person': 'mcescher', '_id': 'A', "begin_date": '2019-10-01', "end_date": '2019-10-31', 'grant': 'grant1', 'loading': 1.0, 'type': 'ss'},
       {'person': 'mcescher', '_id' :'B', "begin_date": '2019-11-01', "end_date": '2019-11-30', 'grant': 'grant2', 'loading': 0.5, 'type': 'ss'},
       {'person': 'mcescher', '_id': 'C', "begin_date": '2019-11-01', "end_date": '2019-11-30', 'grant': 'grant3', 'loading': 0.5, 'type': 'ss'},
       {'person': 'jsbach', '_id': 'A', "begin_date": '2019-12-01', "end_date": '2020-12-15', 'grant': 'grant1', 'loading': 0.9, 'type': 'pd'},
       {'person': 'jsbach', '_id': 'B', "begin_date": '2019-12-16', "end_date": '2020-12-31', 'grant': 'grant2', 'loading': 0.9, 'type': 'pd'},
       {'person': 'jsbach', '_id': 'C', "begin_date": '2019-12-01', "end_date": '2020-12-31', 'grant': 'grant3', 'loading': 0.1, 'type': 'pd'},
       {'person': 'lwittgenstein', '_id': 'A', 'begin_date': '2019-12-10', 'end_date': '2019-12-20', 'grant': 'grant2', 'loading': 1.0, 'type': 'ss'},
       {'person': 'kpopper', '_id': 'A', 'begin_date': '2019-12-25', 'end_date': '2019-12-31', 'grant': 'grant2', 'loading': 1.0, 'type': 'ss'},
       {'person': 'sgermain', '_id': 'A', 'begin_date': '2019-09-02', 'end_date': '2019-09-06', 'grant': 'grant4', 'loading': 1.0, 'type': 'ss'},
      ]),
     (appointed_people, 'type', 'ss', '2019-10-21', '2019-09-01', 'begin date is after end date'),
     (appointed_people, ['type', 'loading'], None, None, None, 'number of filter keys and filter values do not match'),
     (appointed_people, 'type', 'pd', '2019-12-10', None, 'please enter both begin date and end date or neither'),
    ]
)
def test_collect_appts(people, key, value, start, end, expected):
    try:
        actual = collect_appts(people, filter_key=key, filter_value=value, begin_date=start, end_date=end)
        assert actual == expected
    except ValueError:
        with pytest.raises(ValueError) as excinfo:
            actual = collect_appts(people, filter_key=key, filter_value=value, begin_date=start, end_date=end)
        assert str(excinfo.value) == expected
    except RuntimeError:
        with pytest.raises(RuntimeError) as excinfo:
            actual = collect_appts(people, filter_key=key, filter_value=value, begin_date=start, end_date=end)
        assert str(excinfo.value) == expected

appts1 = []
appts2 = []
appts3 = []
person1 = {}
person2 = {}
person3 = {}
people = []
grant1 = {}
grant2 = {}
grant3 = {}
grants = [grant1, grant2, grant3]
@pytest.mark.parametrize(
    "grant,people,start,end,expected",
    [

    ]
)
def test_get_grant_amount(grant, people, start, end, expected):
    actual = get_grant_amount(grant, people, begin_date=start, end_date=end)
    assert actual == expected
