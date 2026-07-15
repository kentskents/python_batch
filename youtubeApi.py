# ================================
# YouTube Data API Search API Sample
# Google Colab 用（main関数あり）
# ================================

import requests
import json
from datetime import datetime, timedelta, timezone

API_KEY = "AIzaSyAkwY8_VH-AznYEQAM7jciYon3UonIs770"  # ←自分のAPIキーを入れる
SEARCH_QUERY = "ClaudeCode"  # ←検索キーワード
OUTPUT_JSONL = "youtube_results.jsonl"  # ←出力先ファイル名


def youtube_search(query, max_results=10):
    """YouTube Search API を叩いて結果を返す（過去1年〜現在の期間で絞り込み）"""
    url = "https://www.googleapis.com/youtube/v3/search"

    # datetime.now(timezone.utc) で「現在時刻」をUTC(協定世界時)で取得する。
    # YouTube APIはUTC基準の日時を要求するため、タイムゾーンを明示している。
    now = datetime.now(timezone.utc)
    # timedelta(days=365) は「365日分の時間の長さ」を表すオブジェクト。
    # now から引き算することで「1年前の日時」を計算できる。
    one_year_ago = now - timedelta(days=365)

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        # strftime(...) で datetime オブジェクトを指定フォーマットの文字列に変換する。
        # "%Y-%m-%dT%H:%M:%SZ" は YouTube APIが要求するRFC3339形式
        # （例: 2025-07-15T09:30:00Z）に合わせたもの。
        "publishedAfter": one_year_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),   # この日時以降に投稿された動画
        "publishedBefore": now.strftime("%Y-%m-%dT%H:%M:%SZ"),          # この日時より前に投稿された動画
        # order="date" は投稿日時で並び替える指定。ただしYouTube APIは「新しい順」固定で、
        # 「古い順」は用意されていないため、取得後にPython側で並び替え直す。
        "order": "date",
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None

    return response.json()


def save_as_jsonl(items, output_path):
    """検索結果を1件1行のJSONL形式で保存する

    JSONLとは「JSON Lines」の略で、1行に1つのJSONオブジェクトを書き出すファイル形式。
    通常のJSON（配列で全件を1つのファイルにまとめる形式）と違い、
    1行ずつ独立したデータとして扱えるため、大量データの追記や1行単位の読み込みがしやすい。
    """
    # "a" は追記モード（ファイルが無ければ新規作成、あれば末尾に追加）。
    # encoding="utf-8" を指定しないと、日本語タイトルなどが環境によって文字化けすることがある。
    with open(output_path, "a", encoding="utf-8") as f:
        for item in items:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            # 1件分のデータをPythonの辞書(dict)にまとめる。
            record = {
                "video_id": video_id,
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "published_at": snippet["publishedAt"],
                "description": snippet["description"],
                "url": "https://www.youtube.com/watch?v=" + video_id,
            }
            # json.dumps() は辞書をJSON形式の文字列に変換する関数。
            # ensure_ascii=False にしないと、日本語が \uXXXX のような形式に
            # エスケープされてしまい人間が読みづらくなるため指定している。
            # 最後に "\n" を付けて改行することで、次の1件を次の行に書き込む
            # （これがJSONLの「1行1レコード」というルールを守るポイント）。
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    """メイン処理"""
    print(f"検索キーワード: {SEARCH_QUERY}")
    result = youtube_search(SEARCH_QUERY)

    if not result:
        print("検索結果なし")
        return

    items = result.get("items", [])

    # order="date" 指定によりAPI側から既に新しい順で返ってくるが、
    # 念のためPython側でも publishedAt を基準に降順（新しい順）で並び替えておく。
    # reverse=True にすると降順＝新しい順になる。
    items = sorted(items, key=lambda item: item["snippet"]["publishedAt"], reverse=True)

    print("\n=== 検索結果（投稿日が新しい順） ===")
    for item in items:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]

        print("タイトル:", title)
        print("チャンネル:", channel)
        print("URL: https://www.youtube.com/watch?v=" + video_id)
        print("-" * 40)

    save_as_jsonl(items, OUTPUT_JSONL)
    print(f"\nJSONLに出力しました: {OUTPUT_JSONL}")


# 実行
if __name__ == "__main__":
    main()
