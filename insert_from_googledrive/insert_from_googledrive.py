from __future__ import print_function
import os.path
import io
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from notion_client import Client
from tqdm import tqdm
from common.common import Common as Com

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_NAME = 'Documents'
MAX_PAGE_SIZE = 1000


def main():
    # 認証情報を生成 or 取得
    creds = get_credential()

    try:
        # GoogleDriveインスタンスの生成
        service = build('drive', 'v3', credentials=creds)

        # GoogleDriveのフォルダリストを取得
        folders = get_folder_list(service=service)

        # GoogleDriveのファイルリストを取得
        files = get_file_list(service=service, folders=folders)

        # 設定ファイルを取得
        settings = Com.get_setting_json()

        # 設定ファイルの情報を抽出
        NOTION_API_KEY = settings['notion_api_key']  # アクセストークン
        ID_DB_MAIN = settings['id']['db']['main']['prod']  # 書き込み先DBのID
        UUID_DOCUMENT_GOOGLE_DRIVE = settings['uuid']['db']['category']['google_drive']  # 書き込むTAG(リレーション)

        # Notionインスタンスの作成
        notion = Client(auth=NOTION_API_KEY)

        # 書き込み先DBのタイトルリストを取得
        title_list = get_title_list(notion=notion, db_id=ID_DB_MAIN)

        # DBにリンクを投稿
        exist_list = []
        not_exist_list = []
        for file in tqdm(files):
            # リレーション設定
            relations = [{'id': UUID_DOCUMENT_GOOGLE_DRIVE}]
            # DB登録がないものだけ投稿
            if file['name'] not in title_list:
                Com.add_post_by_googledrive(
                    notion=notion
                    , db_id=ID_DB_MAIN
                    , post_title=file['name']
                    , relations=relations
                    , url=file['webViewLink']
                )
                exist_list.append(file['name'])
            else:
                not_exist_list.append(file['name'])
        if 0 < len(not_exist_list):
            print('以下のファイルを登録しました:\n' + str(exist_list))
            # print('以下のファイルをスキップしました:\n' + str(not_exist_list))

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


def get_credential():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_folder_list(service):
    results = service.files().list(
        pageSize=MAX_PAGE_SIZE
        , fields='nextPageToken, files(id, name)'
        , q='name="' + FOLDER_NAME + '" and mimeType="application/vnd.google-apps.folder"'
    ).execute()
    folders = results.get('files', [])

    if not folders:
        print('No folders found.')
        sys.exit(1)
    return folders


def get_file_list(service, folders):
    query = ''

    for folder in folders:
        if query != '':
            query += ' or '
        query += '"' + folder['id'] + '" in parents'
    query = '(' + query + ')'
    query += ' and (name contains ".jpg" or name contains ".png" or name contains ".pdf" or name contains ".xls")'

    results = service.files().list(
        pageSize=MAX_PAGE_SIZE
        , fields='nextPageToken, files(id, name, webContentLink, webViewLink)'
        , q=query
    ).execute()
    files = results.get('files', [])
    files = sorted(files, key=lambda x: x['name'])

    if not files:
        print('No files found.')
        sys.exit(1)
    return files


def get_file_image(service, file):
    request = service.files().get_media(fileId=file['id'])
    save_path = os.path.join('temp_img', file['name'])
    fh = io.FileIO(save_path, mode='wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        stats, done = downloader.next_chunk()


def get_title_list(notion, db_id):
    # 処理結果
    result_list = []
    # リクエストする内容
    payload = {
        'database_id': db_id,
        'page_size': 100
    }
    # ループフラグ
    has_more = True
    # ページングしながら処理
    while has_more:
        # 1ページ単位で取得
        results = Com.custom_search(notion=notion, payload=payload)
        # タイトルリストを取得
        list = results['results']
        list = [rec.get('properties') for rec in list]
        list = [rec.get('Name') for rec in list]
        list = [rec.get('title') for rec in list]
        list = [rec[0].get('text') for rec in list]
        list = [rec.get('content') for rec in list]
        # 返却結果に結合
        result_list += list
        # 次ページの存在判定
        has_more = results['has_more']
        # ページング設定
        if has_more:
            payload['start_cursor'] = results['next_cursor']
    # 処理結果を返却
    return result_list


if __name__ == '__main__':
    main()
