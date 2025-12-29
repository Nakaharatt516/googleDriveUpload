import os
import tkinter as tk
from tkinter import filedialog, messagebox

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 権限のスコープ（ファイルの読み書き権限）
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_authenticated_service():
    """OAuth 2.0認証を行い、Drive APIサービスを構築する"""
    creds = None
    # すでにトークンがある場合はロード
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # トークンがない、または有効期限切れの場合はログイン画面を表示
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.json が必要です
            if not os.path.exists('credentials.json'):
                messagebox.showerror("エラー", "credentials.json が見つかりません。\nGoogle Cloud ConsoleからOAuthクライアントIDのJSONをダウンロードして配置してください。")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 次回のためにトークンを保存
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def select_file():
    """ファイル選択ダイアログを表示"""
    root = tk.Tk()
    root.withdraw() # メインウィンドウを隠す
    file_path = filedialog.askopenfilename(title="アップロードするファイルを選択してください")
    root.destroy()
    return file_path

def main():
    # 1. ファイルを選択
    file_path = select_file()
    if not file_path:
        print("ファイルが選択されませんでした。")
        return

    # 2. 認証とサービス構築
    print("認証を確認中...")
    service = get_authenticated_service()
    if not service:
        return

    # 3. アップロード処理
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name}
    
    # MIMEタイプ自動判定でアップロード
    media = MediaFileUpload(file_path, resumable=True)

    try:
        print(f"アップロード中: {file_name} ...")
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"完了しました！ File ID: {file.get('id')}")
        
        # 完了メッセージボックス（不要なら削除可）
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("成功", f"アップロードが完了したんご！！！\nファイル名: {file_name}")
        root.destroy()

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("エラー", f"アップロード中にエラーが発生しました:\n{e}")
        root.destroy()

if __name__ == '__main__':
    main()