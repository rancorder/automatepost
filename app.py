import os
import tweepy
import google.generativeai as genai
from datetime import datetime, timezone, timedelta

# ✅ 環境変数から API キーを取得
# X API
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_secret = os.getenv("ACCESS_SECRET")

# Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")

# 🔍 環境変数の確認
if not all([api_key, api_secret, access_token, access_secret, gemini_api_key]):
    raise ValueError("❌ 環境変数が不足しています。GitHub Secrets を確認してください。")

# ✅ X API 接続（OAuth 1.0a）
try:
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )
except Exception as e:
    raise RuntimeError(f"❌ X API 接続エラー: {e}")

# ✅ Gemini API 接続
try:
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    raise RuntimeError(f"❌ Gemini API 接続エラー: {e}")

# 📅 日本時間（JST）での今日の曜日を取得
jst_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9)))
today_date = jst_now.strftime("%Y年%m月%d日")
today_weekday = jst_now.strftime("%A")  # 'Monday', 'Tuesday' など

# 🔮 曜日ごとのテーマ
topics = {
    "Monday": "週のスタート時に運気を上げる方法",
    "Tuesday": "ナイトルーティンと開運の関係",
    "Wednesday": "夢占いの歴史と直感力の関係",
    "Thursday": "拡散されやすい運勢診断の統計的根拠",
    "Friday": "選択式占いと心理学の関連性",
    "Saturday": "週末のリフレッシュが運勢に与える影響",
    "Sunday": "週間占いの根拠と歴史"
}

# 🔮 Geminiでツイートを生成（140字以内）
def generate_fortune():
    topic = topics.get(today_weekday, "占いの歴史")  # 曜日に対応するテーマを取得

    prompt = f"""
    {today_date} の {today_weekday} の占いツイートです。
    テーマ: {topic}
    140文字以内のTwitter投稿として適切な形式で文章を作成してください。
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content([prompt])

        # 🔍 レスポンスがない場合の対策
        if not response or not response.text:
            raise ValueError("❌ Gemini API のレスポンスが空です。")

        # 📝 テキストを取得し、140文字以内にカット
        fortune_text = response.text.strip()
        max_length = 140 - len("\n#AI占い #今日の運勢 #未来の羅針盤")

        if len(fortune_text) > max_length:
            fortune_text = fortune_text[:max_length].rsplit(" ", 1)[0]  # 単語が途中で切れないように調整

        return fortune_text

    except Exception as e:
        return f"⚠️ Gemini API エラー: {e}"

# 🚀 ツイートを投稿
def post_fortune():
    fortune_text = generate_fortune()
    tweet_text = f"🔮 {today_date} ({today_weekday}) の運勢 🔮\n{fortune_text}\n#AI占い #今日の運勢 #未来の羅針盤"

    try:
        response = client.create_tweet(text=tweet_text)
        print(f"✅ 占いツイート成功！ ツイートID: {response.data['id']}")
    except tweepy.errors.TweepyException as e:
        print(f"❌ X API エラー: {e}")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")

# ✅ 実行（毎日の運勢をツイート）
if __name__ == "__main__":
    post_fortune()
