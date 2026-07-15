# ================================
# YouTube Data API Search API Sample
# Google Colab 用（main関数あり）
# ================================

import requests
import json

API_KEY = "AIzaSyAkwY8_VH-AznYEQAM7jciYon3UonIs770"  # ←自分のAPIキーを入れる
SEARCH_QUERY = "ClaudeCode"  # ←検索キーワード
OUTPUT_JSONL = "youtube_results.jsonl"  # ←出力先ファイル名


def youtube_search(query, max_results=5):
    """YouTube Search API を叩いて結果を返す"""
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None

    return response.json()


def save_as_jsonl(items, output_path):
    """検索結果を1件1行のJSONL形式で保存する"""
    with open(output_path, "w", encoding="utf-8") as f:
        for item in items:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            record = {
                "video_id": video_id,
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "published_at": snippet["publishedAt"],
                "description": snippet["description"],
                "url": "https://www.youtube.com/watch?v=" + video_id,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    """メイン処理"""
    print(f"検索キーワード: {SEARCH_QUERY}")
    result = youtube_search(SEARCH_QUERY)

    if not result:
        print("検索結果なし")
        return

    items = result.get("items", [])

    print("\n=== 検索結果 ===")
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
