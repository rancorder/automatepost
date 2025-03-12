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

# 🔍 過去の投稿履歴を読み込む
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"posts": []}

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
    【ペルソナ】  
    あなたは、洗練された語り口を持つクールで知的な美男子占い師。  
    人々の運命を導く言葉を語り、読者が「気づき」「驚き」「学び」を得られるようなメッセージを提供する。  
    ただし、単なる予言ではなく、実生活に活かせる知恵や洞察を重視する。

    【タスク】  
    以下の条件を満たす短い占いメッセージ（140字以内）を作成せよ。  
    - 占い的視点を主体にしながらも、現実に即したアドバイスを提供する。  
    - 文章の流れが自然で、読み手が直感的に理解できる内容にする。  
    - 説明的すぎず、エモーショナルなストーリーテリングを取り入れる。  
    - 難しい言葉や漢字を避け、洗練された表現を用いる。  
    - 読者を引き込むために、時に現実の例えやたとえ話を交える。

    【コンテキスト】  
    - 140字という制限内で、最大限のインパクトを与えること。  
    - 「占い師の言葉」としての説得力を持たせる。  
    - ありきたりなメッセージではなく、新鮮な切り口を意識する。  

    【フォーマット】  
    - 140字以内に必ず収める。  
    - 文章のリズムを大事にし、洗練された語り口を維持する。  
    - 結論を端的に伝えつつ、余韻を残す。 
    - 人間味のある文章で。 
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content([prompt])

        if not response or not response.text:
            raise ValueError("❌ Gemini API のレスポンスが空です。")

        return response.text.strip(), theme

    except Exception as e:
        raise RuntimeError(f"❌ Gemini API でエラー発生: {e}")

# 🚀 ツイートを投稿
def post_fortune():
    fortune_text, theme = generate_fortune()
    tweet_text = f"{fortune_text}\n#占い #運勢 #自己成長"

    try:
        response = client.create_tweet(text=tweet_text)
        save_history(theme)
        print(f"✅ ツイート成功！ ツイートID: {response.data['id']}")
    except Exception as e:
        print(f"❌ エラー: {e}")

# ✅ 実行
if __name__ == "__main__":
    post_fortune()
