import os
import tweepy
import google.generativeai as genai
from datetime import datetime, timezone, timedelta
import random
import json

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

# 📅 日本時間（JST）での今日の日付を取得
jst_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9)))
today = jst_now.strftime("%Y年%m月%d日")

# 📌 ポスト履歴を管理するファイル
HISTORY_FILE = "tweet_history.json"

# 🔍 過去の投稿履歴を読み込む（IndentationError 修正済み）
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"posts": []}  # 正しくインデントを修正

# 💾 新しい投稿を履歴に追加
def save_history(post_text):
    history = load_history()
    history["posts"].append(post_text)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=2)

# 🔮 テーマリスト（重複を避けながらランダム選択）
THEMES = [
    "意外性があるネタ（驚き＆エンタメ要素）",
    "共感しやすいネタ（恋愛・性格・相性）",
    "実用性のあるネタ（運気UP・開運法）",
    "SNSでバズるネタ（リプライ・シェアしたくなる）",
    "面白い組み合わせの占い（エンタメ系）",
    "ビジネス：成功する人・しない人の違い",
    "お金：貯まる人・貯まらない人の習慣",
    "人間関係：良い縁を引き寄せる人の特徴",
    "決断力：「迷う人」と「即決できる人」の違い",
    "仕事運：「チャンスを掴む人」と「逃す人」の違い",
    "メンタル：「ネガティブ思考の人」と「ポジティブ思考の人」",
    "運気を上げる習慣：毎日の小さな開運行動",
    "未来を変える行動：今日からできる運命の変え方"
]

# 📌 直近の投稿と被らないテーマを選択
def select_theme():
    history = load_history()
    past_posts = history["posts"][-5:]  # 直近5件の履歴を確認
    available_themes = [theme for theme in THEMES if theme not in past_posts]

    return random.choice(available_themes) if available_themes else random.choice(THEMES)

# 🔮 Geminiで占いメッセージを生成（140字以内）
def generate_fortune():
    theme = select_theme()

    prompt = f"""
    あなたはクールで知的な美男子占い師だ。
    140文字ギリギリまで使い、占い的視点を主体にしながら現実に即したアドバイスを提供せよ。
    読者が「気づき」「驚き」「学び」を得られるような内容にし、
    説明的すぎず、スマートかつ洗練された語り口で伝えること。

    【条件】
    - 今日のテーマは「{theme}」
    - 読者が直感的に理解できるよう、時に現実の例えを交えること。
    - ストーリーテリングを意識し、長めの文章で引き込む。
    - 難しい言葉や漢字は極力避け、洗練された表現を使う。
    - クールな美男子占い師の語り口を維持する。
    - 140字以内に必ず収める。

    【出力例】
    「成功する人は迷わない。運は動く者に味方する。準備ばかりしている者にチャンスは来ない。今この瞬間、君が選ぶ未来が運命を変える。」
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content([prompt])

        # 🔍 レスポンスがない場合の対策
        if not response or not response.text:
            raise ValueError("❌ Gemini API のレスポンスが空です。")

        # 📝 テキストを取得し、140文字以内にカット
        fortune_text = response.text.strip()
        max_length = 140 - len("\n#占い #運勢 #自己成長")

        if len(fortune_text) > max_length:
            fortune_text = fortune_text[:max_length].rsplit(" ", 1)[0]  # 単語が途中で切れないように調整

        return fortune_text, theme

    except Exception as e:
        raise RuntimeError(f"❌ Gemini API でエラー発生: {e}")

# 🚀 ツイートを投稿
def post_fortune():
    fortune_text, theme = generate_fortune()
    tweet_text = f"\n{fortune_text}\n#占い #運勢 #自己成長"

    try:
        response = client.create_tweet(text=tweet_text)
        save_history(theme)  # 投稿履歴を記録
        print(f"✅ ツイート成功！ ツイートID: {response.data['id']}")
    except tweepy.errors.TweepyException as e:
        print(f"❌ X API エラー: {e}")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")

# ✅ 実行（毎日7時、12時、20時にツイート）
if __name__ == "__main__":
    post_fortune()
