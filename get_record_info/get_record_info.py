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
    POST_TITLE = 'あったわ'  # 投稿タイトル

    # Notionインスタンスの作成
    notion = Client(auth=NOTION_API_KEY)

    # 投稿タイトルの検索
    results = Com.search_post_title(notion=notion, db_id=ID_DB_MAIN, post_title=POST_TITLE)

    # 取得できた場合
    if 0 < len(results):
        # 結果をクリップボードにコピー
        pyperclip.copy(json.dumps(results))
        # 結果をコンソールに表示
        pprint(results)

