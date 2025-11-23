import discord
from discord import app_commands
from discord.ext import commands
import datetime
import locale

ver = "1.0.1"

with open "SquadronBot.token" as f:
  f.read()
token = tokenfile

# ロケールを日本語に設定（曜日などを日本語表記にするため）
try:
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, '') # システムのデフォルト
    except:
        pass # 設定できない場合は無視

# Botの設定
TOKEN = token
MY_GUILD = discord.Object(id=1441810392790728788) # テストするサーバーID（同期を早くするため推奨）

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # 1. 現在のコマンド(squadronなど)をテストサーバーに即時反映
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

        # 2. グローバルコマンドとしても同期（反映に最大1時間かかる）
        #'''API制限にかからないように、一度実行したらコメントアウトしてください！！'''
        #await self.tree.sync()

intents = discord.Intents.default()
client = MyClient(intents=intents)

# --- 補助関数: BRのリスト ---
# 必要に応じてリストを修正
BR_CHOICES = [
    "4.7", "5.0", "5.3", "5.7", "6.0", "6.3", "6.7","7.0", "7.3",
    "7.7", "8.0", "8.3", "8.7", "9.0", "9.3", "9.7","10.0", "10.3",
    "10.7", "11.0", "11.3", "11.7", "12.0", "12.3","12.7", "13.0",
    "13.3", "13.7", "14.0", "14.3", "14.7", "15.0","15.3", "15.7",
    "16.0", "16.3", "16.7", "17.0", "17.3", "17.7", "18.0"
]

async def br_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """BRの選択肢を返すオートコンプリート"""
    return [
        app_commands.Choice(name=br, value=br)
        for br in BR_CHOICES if current in br
    ][:25] # Discordの制限で最大25件まで

# --- 補助関数: 日付のリスト ---
async def date_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """現在から7日分の日付を選択肢として返すオートコンプリート"""
    choices = []
    now = datetime.datetime.now()
    
    for i in range(7):
        # 日付をずらす
        date_obj = now + datetime.timedelta(days=i)
        # 表示用テキスト: 例 "11/23 (土)"
        label = date_obj.strftime("%m/%d (%a)")
        
        # 値として渡すテキスト: パースしやすい形式 "YYYY-MM-DD"
        # 実際の募集時間は、一旦「21:00」固定として処理する例にします
        # (必要ならオートコンプリートの選択肢自体を "11/23 21:00", "11/23 22:00" と増やすことも可能)
        value_str = date_obj.strftime("%Y-%m-%d")
        
        choices.append(app_commands.Choice(name=label, value=value_str))
    
    return choices

# --- コマンド定義 ---
@client.tree.command(name="squadron", description="クラン戦募集用テンプレート")
@app_commands.describe(
    schedule1="日程1を選択してください",
    br1="BR1を選択してください",
    schedule2="日程2（任意）",
    br2="BR2（日程2がある場合は必須）"
)
@app_commands.autocomplete(
    schedule1=date_autocomplete,
    br1=br_autocomplete,
    schedule2=date_autocomplete,
    br2=br_autocomplete
)
async def squadron(
    interaction: discord.Interaction, 
    schedule1: str, 
    br1: str, 
    schedule2: str = None, 
    br2: str = None
):
    # --- バリデーション (条件付き必須チェック) ---
    if schedule2 is not None and br2 is None:
        await interaction.response.send_message(
            "❌ **エラー**: 日程2を設定する場合は、BR2も選択してください。", 
            ephemeral=True
        )
        return

    # --- タイムスタンプ生成ロジック ---
    def create_timestamp_str(date_str):
        # 文字列 YYYY-MM-DD を datetime型に変換
        # 時間は便宜上 21:00 (JST) と仮定してセットします
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        dt = dt.replace(hour=23, minute=0, second=0)
        
        # UNIXタイムスタンプに変換
        timestamp = int(dt.timestamp())
        
        # Discord形式の文字列を返す
        # <t:TIMESTAMP:f> = 年月日 時間
        # <t:TIMESTAMP:R> = 相対時間 (あと〇時間)
        return f"<t:{timestamp}:f> (<t:{timestamp}:R>)"

    # --- メッセージ作成 ---
    # 日程1
    msg = f"クラン戦募集、参加できる日程にリアクションをつけてください\n"
    ts1_str = create_timestamp_str(schedule1)
    msg += f":one: {ts1_str} **BR {br1}**\n"

    # 日程2 (もしあれば)
    if schedule2:
        ts2_str = create_timestamp_str(schedule2)
        msg += f":two: {ts2_str} **BR {br2}**"

    # 送信
    await interaction.response.send_message(msg)

# Bot起動
client.run(TOKEN)
