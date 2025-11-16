from flask import Flask, render_template, request  # ★ 追加：request を使う
from dotenv import load_dotenv                    # ★ 追加：環境変数を読む
from openai import OpenAI                         # ★ 追加：ChatGPT API クライアント
import os                                         # ★ 追加：os.getenv でキーを読む

# .env から環境変数を読み込む（OPENAI_API_KEY など）
load_dotenv(override=True)

app = Flask(__name__)

# OpenAIクライアントを作成（環境変数 OPENAI_API_KEY を利用）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    """
    メイン画面。
    - GET: フォームだけ表示
    - POST: メモを受け取り、ChatGPT で整理して表示
    """

    organized_text = None  # 整理後の文章（結果）
    memo_text = ""         # フォームに表示するメモ（再表示用）

    if request.method == "POST":
        # フォームから memo を取得（未入力時 None 防止のため or "" を付ける）
        memo_text = (request.form.get("memo") or "").strip()

        if memo_text:
            # --- ChatGPT に渡すプロンプトを作成（仕事メモ用フォーマット） ---
            prompt = f"""
以下は、仕事中に先輩や上司から教わった内容などをメモしたものです。
このメモを、業務学習ノートとして整理してください。

出力は必ず、次の構成で日本語で書いてください。

■ 今日学んだことのまとめ
（1〜3行程度で要約）

■ 手順 / やり方
・ 箇条書きで具体的な手順を書く

■ なぜそうするのか（理由・背景）
・ 箇条書きで理由・背景を書く

■ 注意点 / ハマりポイント
・ 箇条書きで注意点や失敗しやすい点を書く

■ 次にやること（TODO）
・ 箇条書きで、今後やるべきことを書く

メモの内容は変えずに、分かりにくいところは補足してもかまいません。
箇条書きの先頭には「・」を付けてください。

【メモ】
{memo_text}
"""

            try:
                # ChatGPT API を呼び出して、メモを整理してもらう
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "あなたは、日本語の業務メモを整理するアシスタントです。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.2,  # ぶれを小さく（安定した出力にする）
                )

                # 返ってきた整理結果のテキストを取り出す
                organized_text = (res.choices[0].message.content or "").strip()

            except Exception as e:
                # エラーが起きたときは、その旨を画面に表示する
                organized_text = f"（メモの整理に失敗しました: {e}）"
        else:
            # メモが空だったときのメッセージ
            organized_text = "（メモが空です。内容を入力してください）"

    # GET のとき or POST 後の描画
    # - memo_text: フォームの textarea に再表示するため
    # - organized_text: 結果表示用（最初は None）
    return render_template(
        "index.html",
        memo_text=memo_text,
        organized_text=organized_text,
    )


if __name__ == "__main__":
    app.run(debug=True)
