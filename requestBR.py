import requests,re
from bs4 import BeautifulSoup

url = "https://forum.warthunder.com/t/season-schedule-for-squadron-battles/4446/1"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def Get_web_response():
 try:
    # 1. ウェブページを取得
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    # 2. Beautiful Soupで解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # 3. 本文要素をCSSセレクタで特定
    # 優先度1: 通常のDiscourse投稿本文 (.cooked) を検索
    post_content = soup.select_one('article[data-post-number="1"] .cooked')

    # post_content が None の場合、優先度3: .topic-body を検索
    if not post_content:
        post_content = soup.select_one('.topic-body')
        if post_content:
            #print("selector '.topic-body'")
            pass

    if post_content:
        # 4. 要素からテキストを抽出、整形
        full_text = post_content.get_text(separator='\n', strip=True)

        # 5. 抽出されたテキストから、目的のスケジュールブロックを切り出す
        start_marker = "High available BRs in the beginning and lower BRs by the end of the season. Stepping down of BR will happen as follows once a week:"
        end_marker_fragment = "Until the end of season, мах"

        start_index = full_text.find(start_marker)
        end_index_fragment = full_text.find(end_marker_fragment)

        if start_index != -1 and end_index_fragment != -1:
            # 終了行の末尾を特定
            next_newline_after_fragment = full_text.find('\n', end_index_fragment)
            block_end = next_newline_after_fragment if next_newline_after_fragment != -1 else len(full_text)

            # スケジュールブロックを抽出
            extracted_block = full_text[start_index:block_end].strip()

            # 結果を出力
            return extracted_block
    else:
      return None #if not post content
 except requests.exceptions.RequestException as e:
    return (f"Request Error: {e}")


def Align(extracted_block: str) -> list[str]:
    """
    抽出されたブロックから週ごとのスケジュール行を抽出し、
    "MM/DD ~ MM/DD BR X.X" 形式に整形します。

    Args:
        extracted_block: Beautiful Soupで抽出されたテキストブロック。

    Returns:
        整形されたスケジュール文字列のリスト。
    """
    
    # 抽出結果を改行で分割し、処理対象の行（"week"が含まれる行）のみをフィルタリング
    lines = extracted_block.split('\n')
    
    # スケジュールデータを含む行のみをフィルタリング
    schedule_lines = [line.strip() for line in lines if "week" in line or "Until the end of season" in line]

    formatted_schedules = []
    
    # 正規表現パターン:
    # (BRの数値) (\d{2}\.\d{2}) — (\d{2}\.\d{2})
    # 1. BRの数値 (X.X または X.XX)
    # 2. 開始日付 (MM.DD)
    # 3. 終了日付 (MM.DD)
    # 終了日付の後の括弧と文字列末尾までをマッチさせています
    pattern = re.compile(r'BR\s+(\d+\.\d+)\s+\((\d{2})\.(\d{2})\s+—\s+(\d{2})\.(\d{2})\)')
    
    for line in schedule_lines:
        match = pattern.search(line)
        
        if match:
            # 正規表現でキャプチャしたグループを取得
            br_value = match.group(1)
            start_day = match.group(2)
            start_month = match.group(3)
            end_day = match.group(4)
            end_month = match.group(5)
            
            # ご要望の形式 "MM/DD ~ MM/DD BR X.X" に整形
            # 注意: 元のデータは MM.DD 形式（例: 01.11）のため、そのまま MM/DD に変換します。
            formatted_line = (
                f"{start_month}/{start_day} ~ {end_month}/{end_day} BR {br_value}"
            )
            formatted_schedules.append(formatted_line)
        
        elif "Until the end of season" in line:
            # 最終行のパターンは少し異なるため、個別に処理
            # 例: Until the end of season, мах BR 4.7 (26.12 — 31.12)
            final_match = re.search(r'BR\s+(\d+\.\d+)\s+\((\d{2})\.(\d{2})\s+—\s+(\d{2})\.(\d{2})\)', line)
            if final_match:
                br_value = final_match.group(1)
                start_day = final_match.group(2)
                start_month = final_match.group(3)
                end_day = final_match.group(4)
                end_month = final_match.group(5)
                
                # 最終行も同じ形式に整形
                formatted_line = (
                    f"{start_month}/{start_day} ~ {end_month}/{end_day} BR {br_value}"
                )
                formatted_schedules.append(formatted_line)

    return formatted_schedules
   
def main():
  extracted_block = Get_web_response()
  aligned_data = Align(extracted_block)
  return aligned_data
def debug():
   extracted_block,aligned_data=main()
   print(f"extracted_block:{extracted_block}")
   print(f"aligned_data:{aligned_data}")


if __name__ == "__main__":
    print(main())
    #debug()
