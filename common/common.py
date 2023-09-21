import json
from pathlib import Path


class Common:
    @classmethod
    def get_setting_json(cls):
        # 設定ファイルの読み込み
        parent = Path(__file__).resolve().parent
        with open(parent.parent.joinpath('settings/settings.json')) as f:
            settings = json.load(f)
        return settings

    @classmethod
    def search_all_post(cls, notion, db_id):
        return notion.databases.query(
            **{
                'database_id': db_id,
            }
        )

    @classmethod
    def search_post_title(cls, notion, db_id, post_title=None):
        """
        実行日の投稿数を取得
        :param notion: Notionインスタンス
        :return: 取得数
        """
        return notion.databases.query(
            **{
                'database_id': db_id,
                'filter': {
                    'and': [
                        {
                            'property': 'Name',
                            'title': {
                                'equals': post_title
                            }
                        },
                    ]
                }
            }
        )

    @classmethod
    def add_post(cls, notion, db_id, post_title, tag_id, content):
        """
        新規投稿を作成
        :param notion: Notionインスタンス
        """
        notion.pages.create(
            **{
                'parent': {
                    'database_id': db_id
                },
                'properties': {
                    'Name': {
                        'title': [
                            {
                                'text': {
                                    'content': post_title
                                }
                            }
                        ]
                    },
                    'Tag': {
                        'relation': [
                            {
                                'id': tag_id
                            }
                        ]
                    }
                },
                'children': [
                    {
                        'object': 'block',
                        'type': 'paragraph',
                        'paragraph': {
                            'rich_text': [
                                {
                                    'text': {
                                        'content': content
                                    }
                                }
                            ],
                        }
                    },
                ],
            }
        )

    @classmethod
    def add_post_by_googledrive(cls, notion, db_id, post_title, tag_id, url):
        """
        新規投稿を作成
        :param notion: Notionインスタンス
        """
        notion.pages.create(
            **{
                'parent': {
                    'database_id': db_id
                },
                'properties': {
                    'Name': {
                        'title': [
                            {
                                'text': {
                                    'content': post_title
                                }
                            }
                        ]
                    },
                    'Tag': {
                        'relation': [
                            {
                                'id': tag_id
                            }
                        ]
                    },
                    'URL': {
                        'url': url
                    }
                },
            }
        )

    @classmethod
    def add_block(cls, notion, page_id, content):
        """
        同日の投稿にブロックを追加
        :param notion: Notionインスタンス
        :param page_id: ブロックID
        """
        notion.blocks.children.append(
            **{
                'block_id': page_id,
                'children': [
                    {
                        'object': 'block',
                        'type': 'paragraph',
                        'paragraph': {
                            'rich_text': [
                                {
                                    'text': {
                                        'content': content
                                    }
                                }
                            ],
                        }
                    },
                ],
            }
        )