# db.py
# メモシステム用の「データベース接続」と「INSERT処理」をまとめたファイル

import os
import psycopg2
from dotenv import load_dotenv


# .env ファイルの内容を読み込む
load_dotenv()


def get_connection():
    """
    PostgreSQL に接続して、接続オブジェクト（conn）を返す関数。
    .env に書かれた DATABASE_URL を使う。
    Render の PostgreSQL でも接続できるように sslmode=require を補う。
    """
    # .env に書いた DATABASE_URL を取得
    db_url = os.getenv("DATABASE_URL")

    # DATABASE_URL が設定されていない場合はエラーにする
    if not db_url:
        raise ValueError("DATABASE_URL が設定されていません。.env を確認してください。")

    # DATABASE_URL に sslmode が無い場合は追加する
    if "sslmode=" not in db_url:
        if "?" in db_url:
            db_url = db_url + "&sslmode=require"
        else:
            db_url = db_url + "?sslmode=require"

    # psycopg2.connect() に URL を渡して接続する
    conn = psycopg2.connect(db_url)
    return conn


def insert_memo(memo_text: str, organized_text: str) -> None:
    """
    memos テーブルに 1 件のメモを保存する関数。
    - memo_text: 元のメモ（フォームに入力した内容）
    - organized_text: ChatGPT で整理された文章
    """
    # データベースに接続する
    conn = get_connection()
    cur = conn.cursor()

    try:
        # INSERT 文を実行して、memos テーブルにデータを追加する
        cur.execute(
            """
            INSERT INTO memos (memo_text, organized_text)
            VALUES (%s, %s);
            """,
            (memo_text, organized_text)
        )

        # 変更を確定する
        conn.commit()

    except Exception as e:
        print("memos への INSERT に失敗しました:", e)
        conn.rollback()
        raise

    finally:
        # カーソルと接続を必ず閉じる
        cur.close()
        conn.close()


def get_all_memos():
    """
    memos テーブルに保存されているデータを
    新しい順（created_at の降順）で全部取り出す関数。
    返り値は「辞書のリスト」にしておく。
    """
    # まずは DB に接続
    conn = get_connection()
    cur = conn.cursor()

    try:
        # memos テーブルからデータをすべて取得
        cur.execute(
            """
            SELECT id, memo_text, organized_text, created_at
            FROM memos
            ORDER BY created_at DESC, id DESC;
            """
        )

        rows = cur.fetchall()

        memos = []
        for row in rows:
            memos.append(
                {
                    "id": row[0],
                    "memo_text": row[1],
                    "organized_text": row[2],
                    "created_at": row[3],
                }
            )

        return memos

    except Exception as e:
        print("memos の取得に失敗しました:", e)
        return []

    finally:
        # 必ずカーソルと接続を閉じる
        cur.close()
        conn.close()