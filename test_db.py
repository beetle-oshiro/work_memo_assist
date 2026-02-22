# psycopg2 ライブラリを読み込む
# PostgreSQL に接続するための標準的なライブラリだよ
import psycopg2
import os
from dotenv import load_dotenv

# .env ファイルの内容を読み込む
# これをしないと os.getenv() が読み取れない
load_dotenv()

# .env に書いた DATABASE_URL を取得
# Render の External Database URL を使ってOK
db_url = os.getenv("DATABASE_URL")

try:
    # PostgreSQL に接続を試みる
    # db_url に接続情報（host, password など全部）が入っている
    conn = psycopg2.connect(db_url)

    # カーソルを作る（SQLを実行するためのもの）
    cur = conn.cursor()

    # 簡単なテストクエリ
    cur.execute("SELECT NOW();")

    # 結果を1行だけ取得
    result = cur.fetchone()

    # 結果の表示
    print("DB 接続成功！ 現在時刻:", result)

    # 接続を閉じる（忘れやすいので注意）
    cur.close()
    conn.close()

except Exception as e:
    # エラーが起きた時は内容を表示
    print("DB 接続エラー:", e)
