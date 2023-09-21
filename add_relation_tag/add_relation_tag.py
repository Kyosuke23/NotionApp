import pyperclip
import json
from pprint import pprint
from notion_client import Client
from common.common import Common as Com

if __name__ == '__main__':
    # 設定ファイルを取得
    settings = Com.get_setting_json()

    # 設定ファイルの情報を抽出
    NOTION_API_KEY = settings['notion_api_key']  # アクセストークン
    ID_DB_MAIN = settings['id']['db']['main']['prod']  # 取得先DBのID
    POST_TITLE = 'add_test'  # 投稿タイトル

    # Notionインスタンスの作成
    notion = Client(auth=NOTION_API_KEY)

    # 投稿タイトルの検索
    # results = Com.search_post_title(notion=notion, db_id=ID_DB_MAIN, post_title=POST_TITLE)
    # results = Com.search_all_post(notion=notion, db_id=ID_DB_MAIN)
    #
    # # 取得できた場合
    # if 0 < len(results):
    #     for result in results['results']:
    #         page_id = result['id']

    page_id = 'dd432188-ce75-4ba2-81de-979078a3c1b4'
    categories = [
        {'id': "7b198601-381b-4809-b4c5-a74d42ecf29d"}
        , {'id': "e41c311f-ed13-42de-b55a-c63a39e5695f"}
    ]
    r = Com.update_relation_tag(notion=notion, page_id=page_id, categories=categories)
    pprint(r)
