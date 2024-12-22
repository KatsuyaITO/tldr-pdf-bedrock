import streamlit as st
import os
import random
import string
from PyPDF2 import PdfReader, PdfWriter

# ================================
# AWS Bedrock の設定
# ================================
import boto3
import json
import base64
from botocore.exceptions import ClientError

REGION = "REGION"
AWS_ACCESS="AWS_ACCESS"
AWS_SECRET="AWS_SECRET"

client = boto3.client(
    "bedrock-runtime",
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS,
    aws_secret_access_key=AWS_SECRET,
)

# ================================
# ユーティリティ関数（フォルダ名のランダム生成など）
# ================================
def generate_random_folder_name(length=8):
    """ランダムな英数字で構成されるフォルダ名を生成"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ================================
# Mistral用の単純な呼び出しラッパ関数
# ================================
def get_model_response_old(
    prompt: str,
    model_id: str = 'mistral.mistral-large-2402-v1:0',
    max_tokens: int = 1500,
    top_p: float = 0.7,
    temperature: float = 0.7,
    top_k: int = 50,
    client=client,
    only_text: bool = True
):
    """
    Bedrock(Mistral)モデルに対してプロンプトを投げ、レスポンスを取得する関数。
    `converse` メソッドを利用し、一括で推論結果を取得する。
    """
    # Mistral用の <s>[INST] ... [/INST] の形に整形
    if prompt.find("<s>") == -1:
        prompt = f"<s>[INST]{prompt}[/INST]"

    conversation = [
        {
            "role": "user",
            "content": [
                {"text": prompt}
            ],
        }
    ]

    inference_config = {
        "maxTokens": max_tokens,
        "topP": top_p,
        "temperature": temperature,
    }

    try:
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig=inference_config,
        )
    except (ClientError, Exception) as e:
        return f"ERROR: Can't invoke '{model_id}'. Reason: {e}"

    # 最終的なテキストを抽出
    if only_text:
        return response.get("output").get("message").get("content")[0]["text"]
    else:
        return response

# ================================
# 英語→日本語LaTeXスライド生成関数（Beamer形式）
# ================================
def generate_japanese_slides_bedrock(
    english_text: str,
    model_id: str = 'mistral.mistral-large-2402-v1:0',
    max_tokens: int = 1500,
    top_p: float = 0.7,
    temperature: float = 0.7,
    top_k: int = 50
) -> str:
    """
    英語の文章を日本語のBeamerスライド(LaTeX)に変換する関数。
    """
    
    prompt = f"""
以下の英語の文章を説明するわかりやすい日本語の1ページのスライドを作成してください。

## 原文

{english_text}


## スライドのフォーマット

\\begin{{frame}}{{このページで言いたいことや重要な概念}}
  \\textbf{{その重要な概念の説明・キーメッセージ。繰り返し登場する単語は英語2〜3文字の略称(例：BTC,JPY等)にする。}}
  \\begin{{block}}{{具体的な説明など・このページのわかりやすい要約}}
    \\begin{{itemize}}
      \\item 3行程度の完結な説明をitemizeで作る。完結な文章を心がける。
      \\item 各行は40文字以内にする。体言止めなどをつかう。
      \\item itemizeは3行までにする。
    \\end{{itemize}}
  \\end{{block}}
\\end{{frame}}

## Output (1ページのスライドの内容のみをLaTeX・Beamerフォーマットで日本語で出力する）:
"""

    slides_text = get_model_response_old(
        prompt,
        model_id=model_id,
        max_tokens=max_tokens,
        top_p=top_p,
        temperature=temperature,
        top_k=top_k,
        client=client,
        only_text=True
    )
    return slides_text

# ================================
# 生成されたスライドを Output.tex に追記で書き込む関数
# ================================
def append_slides_to_tex_file(slides_text: str, tex_file_path: str):
    """
    slides_text 内に \begin{frame} が含まれている場合は、
    その部分（\begin{frame} 以降）を取り出して追記保存します。
    含まれていない場合は、slides_text 全体を追記します。
    また、スライドの文法が途中で終了している場合は、itemize, block, frame の順番で終了タグを追加します。
    """
    import re

    def is_slide_complete(text):
        """
        スライドがLaTeX文法的に完結しているかを確認。
        \begin{frame}, \begin{block}, \begin{itemize} とそれぞれ対応する終了タグが存在するかチェック。
        """
        begin_frame_count = len(re.findall(r"\\begin{frame}", text))
        end_frame_count = len(re.findall(r"\\end{frame}", text))
        begin_block_count = len(re.findall(r"\\begin{block}", text))
        end_block_count = len(re.findall(r"\\end{block}", text))
        begin_itemize_count = len(re.findall(r"\\begin{itemize}", text))
        end_itemize_count = len(re.findall(r"\\end{itemize}", text))
        
        return (
            begin_frame_count == end_frame_count and
            begin_block_count == end_block_count and
            begin_itemize_count == end_itemize_count
        )

    def complete_slide(text):
        """
        スライドの文法を補完する関数。
        itemize, block, frame の順番で終了タグを補完。
        """
        if text.count(r"\\begin{itemize}") > text.count(r"\\end{itemize}"):
            text += "\n\\end{itemize}"
        if text.count(r"\\begin{block}") > text.count(r"\\end{block}"):
            text += "\n\\end{block}"
        if text.count(r"\\begin{frame}") > text.count(r"\\end{frame}"):
            text += "\n\\end{frame}"
        return text

    # スライドの開始部分を抽出（\begin{frame} から）
    start_index = slides_text.find(r"\begin{frame}")
    if start_index != -1:
        slides_text = slides_text[start_index:]

    # 文法チェックと補完
    if not is_slide_complete(slides_text):
        slides_text = complete_slide(slides_text)

    # スライドをファイルに追記
    with open(tex_file_path, "a", encoding="utf-8") as f:
        f.write(slides_text)
        f.write("\n\n")  # 区切りの改行

# ================================
# Streamlitメイン関数
# ================================
def main():
    st.title("PDF 分割 + テキスト変換 + Beamer スライド生成")
    st.write("アップロードした PDF を 2ページ単位で分割し、テキストを抽出して、それぞれ Beamer スライド化してみます。")

    uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])

    # 一時的な保存フォルダを作る
    UPLOAD_FOLDER = "uploads"
    OUTPUT_FOLDER = "output"
    PAGES = 4
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.pdf'):
            # "実行"ボタン
            if st.button("ファイルを処理する"):
                # ファイルを保存
                file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # PDFを読み込む
                reader = PdfReader(file_path)
                num_pages = len(reader.pages)
                if num_pages < 2:
                    st.error("PDF は2ページ以上必要です。")
                    return

                # ランダムなフォルダ名を作成
                folder_name = generate_random_folder_name()
                folder_path = os.path.join(OUTPUT_FOLDER, folder_name)
                os.makedirs(folder_path, exist_ok=True)

                st.write(f"全ページ数: {num_pages}ページ")
                st.write(f"分割されたPDFとテキストは `{folder_path}` フォルダに保存されます。")

                group_num = 1
                slides_results = []  # 各グループのスライドを保持

                # Output.tex ファイルを作成（上書き防止のため、最初に空で生成しておく）
                tex_file_path = os.path.join(folder_path, "Output.tex")
                with open(tex_file_path, "w", encoding="utf-8") as f:
                    f.write("% このファイルにBeamerスライドが追記されます\n\n")

                for i in range(0, num_pages, PAGES):
                    writer = PdfWriter()
                    for j in range(PAGES):
                        if i + j < num_pages:
                            writer.add_page(reader.pages[i + j])

                    output_pdf_path = os.path.join(folder_path, f'group_{group_num}.pdf')
                    with open(output_pdf_path, 'wb') as out_pdf:
                        writer.write(out_pdf)

                    # テキスト抽出
                    extracted_text = ""
                    for page_index in range(i, min(i + PAGES, num_pages)):
                        extracted_text += reader.pages[page_index].extract_text() + "\n"

                    output_txt_path = os.path.join(folder_path, f'group_{group_num}.txt')
                    with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(extracted_text)

                    # Beamer用のスライドを生成 (英語テキスト→日本語Beamer と想定)
                    st.write(f"### group_{group_num} のテキスト")
                    st.text(extracted_text)

                    with st.spinner(f"group_{group_num} のテキストを Bedrock に問い合わせ中..."):
                        slides_text = generate_japanese_slides_bedrock(extracted_text)
                        slides_results.append(slides_text)

                    st.write(f"#### group_{group_num} の LaTeX Beamer 出力")
                    st.code(slides_text, language="latex")

                    # 生成したスライドを Output.tex に追記
                    append_slides_to_tex_file(slides_text, tex_file_path)

                    group_num += 1

                st.success("すべての処理が完了しました。Output.tex にスライドが追記されています。")

        else:
            st.error("無効なファイルタイプです。PDFファイルのみアップロードしてください。")

if __name__ == "__main__":
    main()

