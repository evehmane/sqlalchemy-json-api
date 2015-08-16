import pytest


@pytest.mark.usefixtures('table_creator', 'dataset')
class TestQueryBuilderSelectWithInclude(object):
    @pytest.mark.parametrize(
        ('fields', 'include', 'result'),
        (
            (
                {'users': []},
                ['all_friends'],
                {
                    'data': [
                        {'type': 'users', 'id': '1'},
                        {'type': 'users', 'id': '2'}
                    ],
                    'included': [
                        {'type': 'users', 'id': '3'},
                        {'type': 'users', 'id': '4'}
                    ]
                }
            ),
        )
    )
    def test_with_many_root_entities(
        self,
        query_builder,
        session,
        user_cls,
        fields,
        include,
        result
    ):
        query = query_builder.select(
            user_cls,
            fields=fields,
            include=include,
            from_obj=session.query(user_cls).filter(user_cls.id.in_([1, 2]))
        )
        import sqlalchemy as sa
        print(query.compile(dialect=sa.dialects.postgresql.dialect()))
        assert session.execute(query).scalar() == result

    @pytest.mark.parametrize(
        ('fields', 'include', 'result'),
        (
            (
                {'articles': ['name', 'content', 'category']},
                ['category'],
                {
                    'data': [{
                        'type': 'articles',
                        'id': '1',
                        'attributes': {
                            'name': 'Some article',
                            'content': None
                        },
                        'relationships': {
                            'category': {
                                'data': {'type': 'categories', 'id': '1'}
                            }
                        }
                    }],
                    'included': [{
                        'type': 'categories',
                        'id': '1',
                        'attributes': {
                            'created_at': None,
                            'name': 'Some category'
                        },
                        'relationships': {
                            'articles': {
                                'data': [{'type': 'articles', 'id': '1'}]
                            },
                            'subcategories': {
                                'data': [
                                    {'type': 'categories', 'id': '2'},
                                    {'type': 'categories', 'id': '4'}
                                ]
                            },
                            'parent': {'data': None}
                        }
                    }]
                }
            ),
            (
                {'articles': [], 'categories': ['name']},
                ['category'],
                {
                    'data': [{
                        'type': 'articles',
                        'id': '1',
                    }],
                    'included': [{
                        'type': 'categories',
                        'id': '1',
                        'attributes': {
                            'name': 'Some category'
                        }
                    }]
                }
            ),
            (
                {'articles': ['category'], 'categories': ['name']},
                ['category'],
                {
                    'data': [{
                        'type': 'articles',
                        'id': '1',
                        'relationships': {
                            'category': {
                                'data': {'type': 'categories', 'id': '1'}
                            }
                        }
                    }],
                    'included': [{
                        'type': 'categories',
                        'id': '1',
                        'attributes': {
                            'name': 'Some category'
                        }
                    }]
                }
            ),
            (
                {
                    'articles': ['name', 'content', 'category'],
                    'categories': ['name']
                },
                ['category'],
                {
                    'data': [{
                        'type': 'articles',
                        'id': '1',
                        'attributes': {
                            'name': 'Some article',
                            'content': None
                        },
                        'relationships': {
                            'category': {
                                'data': {'type': 'categories', 'id': '1'}
                            }
                        }
                    }],
                    'included': [{
                        'type': 'categories',
                        'id': '1',
                        'attributes': {
                            'name': 'Some category'
                        }
                    }]
                }
            ),
            (
                {
                    'articles': ['name', 'content', 'category', 'comments'],
                    'categories': ['name'],
                    'comments': ['content']
                },
                ['category', 'comments'],
                {
                    'data': [{
                        'type': 'articles',
                        'id': '1',
                        'attributes': {
                            'name': 'Some article',
                            'content': None
                        },
                        'relationships': {
                            'category': {
                                'data': {'type': 'categories', 'id': '1'}
                            },
                            'comments': {
                                'data': [{'type': 'comments', 'id': '1'}]
                            }
                        }
                    }],
                    'included': [
                        {
                            'type': 'categories',
                            'id': '1',
                            'attributes': {'name': 'Some category'}
                        },
                        {
                            'type': 'comments',
                            'id': '1',
                            'attributes': {'content': 'Some comment'}
                        },
                    ]
                }
            ),
        )
    )
    def test_include_parameter(
        self,
        query_builder,
        session,
        article_cls,
        fields,
        include,
        result
    ):
        query = query_builder.select(
            article_cls,
            fields=fields,
            include=include
        )
        assert session.execute(query).scalar() == result

    @pytest.mark.parametrize(
        ('fields', 'include', 'result'),
        (
            (
                {
                    'articles': ['name', 'content', 'category'],
                    'categories': ['name', 'subcategories'],
                },
                ['category.subcategories'],
                {
                    'data': [{
                        'type': 'articles',
                        'id': '1',
                        'attributes': {
                            'name': 'Some article',
                            'content': None
                        },
                        'relationships': {
                            'category': {
                                'data': {'type': 'categories', 'id': '1'}
                            }
                        }
                    }],
                    'included': [
                        {
                            'type': 'categories',
                            'id': '1',
                            'attributes': {'name': 'Some category'},
                            'relationships': {
                                'subcategories': {
                                    'data': [
                                        {'type': 'categories', 'id': '2'},
                                        {'type': 'categories', 'id': '4'}
                                    ]
                                }
                            }
                        },
                        {
                            'type': 'categories',
                            'id': '2',
                            'attributes': {'name': 'Subcategory 1'},
                            'relationships': {
                                'subcategories': {
                                    'data': [{'type': 'categories', 'id': '3'}]
                                }
                            }
                        },
                        {
                            'type': 'categories',
                            'id': '4',
                            'attributes': {'name': 'Subcategory 2'},
                            'relationships': {
                                'subcategories': {
                                    'data': []
                                }
                            }
                        },
                    ]
                }
            ),
            (
                {
                    'articles': ['name', 'content', 'category'],
                    'categories': ['name', 'subcategories'],
                },
                ['category.subcategories.subcategories'],
                {
                    'data': [{
                        'type': 'articles',
                        'id': '1',
                        'attributes': {
                            'name': 'Some article',
                            'content': None
                        },
                        'relationships': {
                            'category': {
                                'data': {'type': 'categories', 'id': '1'}
                            }
                        }
                    }],
                    'included': [
                        {
                            'type': 'categories',
                            'id': '1',
                            'attributes': {'name': 'Some category'},
                            'relationships': {
                                'subcategories': {
                                    'data': [
                                        {'type': 'categories', 'id': '2'},
                                        {'type': 'categories', 'id': '4'}
                                    ]
                                }
                            }
                        },
                        {
                            'type': 'categories',
                            'id': '2',
                            'attributes': {'name': 'Subcategory 1'},
                            'relationships': {
                                'subcategories': {
                                    'data': [{'type': 'categories', 'id': '3'}]
                                }
                            }
                        },
                        {
                            'type': 'categories',
                            'id': '3',
                            'attributes': {'name': 'Subsubcategory 1'},
                            'relationships': {
                                'subcategories': {
                                    'data': [
                                        {'type': 'categories', 'id': '5'},
                                        {'type': 'categories', 'id': '6'}
                                    ]
                                }
                            }
                        },
                        {
                            'type': 'categories',
                            'id': '4',
                            'attributes': {'name': 'Subcategory 2'},
                            'relationships': {
                                'subcategories': {
                                    'data': []
                                }
                            }
                        },
                    ]
                }
            ),
        )
    )
    def test_deep_relationships(
        self,
        query_builder,
        session,
        article_cls,
        fields,
        include,
        result
    ):
        query = query_builder.select(
            article_cls,
            fields=fields,
            include=include
        )
        assert session.execute(query).scalar() == result

    @pytest.mark.parametrize(
        ('fields', 'include', 'result'),
        (
            (
                {
                    'users': ['name', 'all_friends'],
                },
                ['all_friends'],
                {
                    'data': [{
                        'type': 'users',
                        'id': '1',
                        'attributes': {
                            'name': 'User 1',
                        },
                        'relationships': {
                            'all_friends': {
                                'data': [
                                    {'type': 'users', 'id': '2'}
                                ]
                            }
                        }
                    }],
                    'included': [
                        {
                            'type': 'users',
                            'id': '2',
                            'attributes': {'name': 'User 2'},
                            'relationships': {
                                'all_friends': {
                                    'data': [
                                        {'type': 'users', 'id': '1'},
                                        {'type': 'users', 'id': '3'},
                                        {'type': 'users', 'id': '4'}
                                    ]
                                }
                            }
                        },
                    ]
                }
            ),
            (
                {
                    'users': ['name', 'all_friends'],
                },
                ['all_friends.all_friends'],
                {
                    'data': [{
                        'type': 'users',
                        'id': '1',
                        'attributes': {
                            'name': 'User 1',
                        },
                        'relationships': {
                            'all_friends': {
                                'data': [
                                    {'type': 'users', 'id': '2'}
                                ]
                            }
                        }
                    }],
                    'included': [
                        {
                            'type': 'users',
                            'id': '2',
                            'attributes': {'name': 'User 2'},
                            'relationships': {
                                'all_friends': {
                                    'data': [
                                        {'type': 'users', 'id': '1'},
                                        {'type': 'users', 'id': '3'},
                                        {'type': 'users', 'id': '4'}
                                    ]
                                }
                            }
                        },
                        {
                            'type': 'users',
                            'id': '3',
                            'attributes': {'name': 'User 3'},
                            'relationships': {
                                'all_friends': {
                                    'data': [
                                        {'type': 'users', 'id': '2'},
                                        {'type': 'users', 'id': '5'}
                                    ]
                                }
                            }
                        },
                        {
                            'type': 'users',
                            'id': '4',
                            'attributes': {'name': 'User 4'},
                            'relationships': {
                                'all_friends': {
                                    'data': [
                                        {'type': 'users', 'id': '2'}
                                    ]
                                }
                            }
                        },
                    ]
                }
            ),
            (
                {
                    'users': ['name', 'all_friends'],
                },
                ['all_friends.all_friends.all_friends'],
                {
                    'data': [{
                        'type': 'users',
                        'id': '1',
                        'attributes': {
                            'name': 'User 1',
                        },
                        'relationships': {
                            'all_friends': {
                                'data': [
                                    {'type': 'users', 'id': '2'}
                                ]
                            }
                        }
                    }],
                    'included': [
                        {
                            'type': 'users',
                            'id': '2',
                            'attributes': {'name': 'User 2'},
                            'relationships': {
                                'all_friends': {
                                    'data': [
                                        {'type': 'users', 'id': '1'},
                                        {'type': 'users', 'id': '3'},
                                        {'type': 'users', 'id': '4'}
                                    ]
                                }
                            }
                        },
                        {
                            'type': 'users',
                            'id': '3',
                            'attributes': {'name': 'User 3'},
                            'relationships': {
                                'all_friends': {
                                    'data': [
                                        {'type': 'users', 'id': '2'},
                                        {'type': 'users', 'id': '5'}
                                    ]
                                }
                            }
                        },
                        {
                            'type': 'users',
                            'id': '4',
                            'attributes': {'name': 'User 4'},
                            'relationships': {
                                'all_friends': {
                                    'data': [
                                        {'type': 'users', 'id': '2'}
                                    ]
                                }
                            }
                        },
                        {
                            'type': 'users',
                            'id': '5',
                            'attributes': {'name': 'User 5'},
                            'relationships': {
                                'all_friends': {
                                    'data': [
                                        {'type': 'users', 'id': '3'}
                                    ]
                                }
                            }
                        },
                    ]
                }
            ),
        )
    )
    def test_self_referencing_m2m(
        self,
        query_builder,
        session,
        user_cls,
        fields,
        include,
        result
    ):
        query = query_builder.select(
            user_cls,
            fields=fields,
            include=include,
            from_obj=session.query(user_cls).filter(
                user_cls.id == 1
            )
        )
        assert session.execute(query).scalar() == result

    @pytest.mark.parametrize(
        ('fields', 'include', 'result'),
        (
            (
                {
                    'users': ['groups'],
                },
                ['groups'],
                {
                    'data': [{
                        'type': 'users',
                        'id': '5',
                        'relationships': {
                            'groups': {
                                'data': []
                            }
                        }
                    }],
                    'included': []
                }
            ),
        )
    )
    def test_included_as_empty(
        self,
        query_builder,
        session,
        user_cls,
        fields,
        include,
        result
    ):
        query = query_builder.select(
            user_cls,
            fields=fields,
            include=include,
            from_obj=session.query(user_cls).filter(
                user_cls.id == 5
            )
        )
        assert session.execute(query).scalar() == result
