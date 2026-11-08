"""作った画像をインスタのストーリーに投稿する（Instagram Graph API を使用）。

必要なもの:
    - インスタのアカウントが「プロアカウント（ビジネス or クリエイター）」であること
    - Meta for Developers で作ったアプリのアクセストークン（instagram_content_publish 権限）
    - 画像がインターネット上の公開 URL に置いてあること（API は URL からしか画像を受け取らない）

使い方:
    export IG_USER_ID=1784xxxxxxxxxxxx
    export IG_ACCESS_TOKEN=EAAB....
    python publish_story.py https://example.com/story.png
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://graph.facebook.com/v21.0"


def call(method, path, **params):
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    data = urllib.parse.urlencode(params)
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data}")
    else:
        req = urllib.request.Request(url, data=data.encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"API エラー: {e.read().decode()}")


def publish_story(image_url):
    user_id = os.environ["IG_USER_ID"]
    # 1. ストーリー用のコンテナを作る
    container = call("POST", f"{user_id}/media", image_url=image_url, media_type="STORIES")["id"]
    # 2. インスタ側で画像の処理が終わるまで待つ
    for _ in range(30):
        status = call("GET", container, fields="status_code")["status_code"]
        if status == "FINISHED":
            break
        if status == "ERROR":
            sys.exit("インスタ側で画像の処理に失敗しました。")
        time.sleep(2)
    # 3. 公開する
    media = call("POST", f"{user_id}/media_publish", creation_id=container)
    print(f"ストーリーに投稿しました（media id: {media['id']}）")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("使い方: python publish_story.py <画像の公開URL>")
    for key in ("IG_USER_ID", "IG_ACCESS_TOKEN"):
        if key not in os.environ:
            sys.exit(f"環境変数 {key} を設定してください。")
    publish_story(sys.argv[1])
