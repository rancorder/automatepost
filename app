import os
import tweepy
import google.generativeai as genai
import datetime
import time
import random

# ✅ 必要なライブラリを確実にインストール
try:
    import tweepy
except ModuleNotFoundError:
    import subprocess
    subprocess.run(["pip", "install", "tweepy", "google-generativeai"])
    import tweepy

# 🔑 GitHub Secrets から API キーを取得
# X API
bearer_token = os.getenv("BEARER_TOKEN")
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_secret = os.getenv("ACCESS_SECRET")

# Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ✅ X API接続（OAuth 1.0a）
client = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_secret
)

# ✅ Gemini API接続（v1を使用）
genai.configure(api_key=gemini_api_key)

# 📌 今日の日付を取得
today = datetime.datetime.now().strftime("%Y年%m月%d日")

# 🔮 今日の運勢TOP5の生まれ月を選定
def get_top5_birth_months():
    months = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    return random.sample(months, 5)  # ランダムに5つ選択

# 🔮 Geminiで占いメッセージを生成（140字以内）
def generate_fortune():
    top5_months = get_top5_birth_months()
    month_str = "・".join(top5_months)

    prompt = f"""
    {today}の運勢ランキングTOP5🎉
    今日特に運勢が良い生まれ月は {month_str} 生まれのあなた！🌟
    運気を活かすヒントも添えて、140文字以内でまとめてください。
    """

    model = genai.GenerativeModel("gemini-1.5-pro-latest")  # 最新モデルを使用
    response = model.generate_content([prompt])  # 修正: 引数をリスト形式に変更

    # 出力されたテキストを取得し、140文字以内にカット
    fortune_text = response.text.strip()
    max_length = 140 - len("\n#AI占い #今日の運勢 #未来の羅針盤")

    if len(fortune_text) > max_length:
        fortune_text = fortune_text[:max_length]

    return fortune_text

# 🚀 ツイートを投稿
def post_fortune():
    fortune_text = generate_fortune()
    tweet_text = f"🔮 {today}の運勢 🔮\n{fortune_text}\n#AI占い #今日の運勢 #未来の羅針盤"

    try:
        response = client.create_tweet(text=tweet_text)
        print(f"✅ 占いツイート成功！ ツイートID: {response.data['id']}")
    except tweepy.errors.TweepyException as e:
        print(f"❌ エラー: {e}")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")

# ✅ 実行（毎日の運勢をツイート）
if __name__ == "__main__":
    post_fortune()
