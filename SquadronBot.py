import discord
from discord import app_commands
from discord.ext import commands
import datetime
import locale
import re,os,sys

ver = "1.4.3"
try:
  with open("/home/py/DiscordBot_Server/SquadronBot.token") as f:
    TOKEN = f.read()
  with open("/home/py/DiscordBot_Server/dev_id") as f:
    dev_id_file = f.read().strip()
except Exception as e:
  print(e)

try:
  import requestBR
  import GetCurrentBR
except ImportError:
  print("ImportError!!")
  requestBR = "[ERROR] Import_Error"
  CurrentBR = "[ERROR] Import_Error"
except Exception as e:
  print(e)
  requestBR = f"[ERROR] {e}."
  CurrentBR = f"[ERROR] {e}."

async def get_cache_br():
  #キャッシュされたBRデータがないか確認
  #キャッシュ期限がまだあるならそのまま返す、期限切れorデータがない場合は更新/作成する
  now = datetime.datetime.now()
  use_cache = False
  cached_lines = []
  if os.path.exists("/home/py/DiscordBot_Server/br_cache"):
    try:
      with open("/home/py/DiscordBot_Server/br_cache") as f:
        cached_lines = f.readlines()
      if cached_lines:
        last_line = cached_lines[-1] # 最終行を取得
        pattern = r"\d{2}/\d{2} \~ (\d{2}/\d{2})" #r"~\s*(\d{1,2}/\d{1,2})"
        match = re.search(pattern, last_line) #正規表現で日付を抽出 ("12/26 ~ 12/31 BR 4.7" から "12/31" を取る)
        #print(f"last_line:{last_line},\nmatch:{match},\nmatch.group(1):{match.group(1)}") #DEBUG
      if match:
        end_date_str = match.group(1) # "12/31"
        year=now.year
        end_date_str= f"{end_date_str}/{year}"
        end_date = datetime.datetime.strptime(end_date_str, "%m/%d/%Y")

        #年跨ぎの補正
        if now.month == 1 and end_date.month == 12:
          end_date = end_date.replace(year=now.year - 1)
        end_date = end_date + datetime.timedelta(days=1, hours=23, minutes=59, seconds=59) #期限日の翌日正午まで
        #end_date = end_date.replace(hour=23, minute=59, second=59)
        if now <= end_date: #現在時刻が期限内ならキャッシュを使う
          use_cache = True
      #
    except Exception as e:
      print(f"キャッシュ読み込みエラー: {e}")
  if use_cache and cached_lines: #キャッシュを使用
    print(f"/br_list: キャッシュを使用します [有効期限/現在:{end_date}/{now}]")
    return cached_lines, use_cache
  if requestBR is None: #インポートエラー時
    return "❌ エラー: requestBR モジュールが見つかりませんでした。\n可能であれば開発者へ連絡してください", use_cache
  print("/br_list: データを新規取得/更新します")
  new_data = requestBR.main()
  if new_data: #ファイルへ保存
    try:
      with open("/home/py/DiscordBot_Server/br_cache", "w", encoding="utf-8") as f:
        f.write("\n".join(new_data))
    except Exception as e:
      print(f"キャッシュ保存エラー: {e}")
  return new_data, use_cache

# ロケールを日本語に設定（曜日などを日本語表記にするため）
try:
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, '') # システムのデフォルト
    except:
        pass # 設定できない場合は無視

# Botの設定
MY_GUILD = discord.Object(id=1441810392790728788) # テストするサーバーID（同期を早くするため）
LOG_CHANNEL_ID = 1443851237220024341  # ログを送信するチャンネルID

def is_target_channel(ctx):
    return ctx.channel.id == LOG_CHANNEL_ID

class MyClient(commands.Bot): #discord.Client→commands.Bot
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        #コマンドをテストサーバーに即時反映
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
intents.message_content = True
mentions = discord.AllowedMentions(everyone=True, users=False, roles=True)

client = MyClient(intents=intents,allowed_mentions=mentions, command_prefix='!')

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    if LOG_CHANNEL_ID is None:
        print("警告: LOG_CHANNEL_ID が設定されていません。ログメッセージは送信されません。")
    else:
        log_msg = f"[INFO] Botが起動しました。バージョン: {ver}"
        await send_log_message(log_msg)
# BRリスト
BR_CHOICES = [
    "4.7", "5.0", "5.3", "5.7", "6.0", "6.3", "6.7","7.0", "7.3",
    "7.7", "8.0", "8.3", "8.7", "9.0", "9.3", "9.7","10.0", "10.3",
    "10.7", "11.0", "11.3", "11.7", "12.0", "12.3","12.7", "13.0",
    "13.3", "13.7", "14.0", "14.3", "14.7", "15.0","15.3", "15.7",
    "16.0", "16.3", "16.7", "17.0", "17.3", "17.7", "18.0"
]

#オートコンプリート補助関数
async def br_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """BRの選択肢を返すオートコンプリート"""
    return [
        app_commands.Choice(name=br, value=br)
        for br in BR_CHOICES if current in br
    ][:25] #25件まで表示

#オートコンプリート補助関数
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
        # 例 "11/23 (土)"
        label = date_obj.strftime("%m/%d (%a)")

        # 値として渡すテキスト: パースしやすい形式 "YYYY-MM-DD"
        value_str = date_obj.strftime("%Y-%m-%d")

        choices.append(app_commands.Choice(name=label, value=value_str))

    return choices

# --- コマンド定義 ---
@client.tree.command(name="squadron", description="クラン戦募集用テンプレート")
@app_commands.describe(
    schedule1="日程1を選択してください",
    br1="BR1を選択してください",
    schedule2="日程2(任意)",
    br2="BR2(日程2がある場合は必須)"
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
        log_msg = f"[ERROR] {interaction.user.display_name} さんが /squadron コマンドを使用しましたが、日程2に対してBR2が未設定でした。"
        #await send_log_message(log_msg)
        await interaction.response.send_message(
            "❌ **エラー**: 日程2を設定する場合は、BR2も選択してください。", 
            ephemeral=True
        )
        return

    # --- タイムスタンプ生成ロジック ---
    def create_timestamp_str(date_str):
        # 文字列 YYYY-MM-DD を datetime型に変換
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        dt = dt.replace(hour=23, minute=0, second=0) #23時で固定

        # UNIXタイムスタンプに変換
        timestamp = int(dt.timestamp())

        # Discord形式の文字列を返す
        # <t:TIMESTAMP:F> = 年月日 時間 曜日
        # <t:TIMESTAMP:R> = 相対時間 (あと〇時間)
        return f"<t:{timestamp}:F> (<t:{timestamp}:R>)"

    # --- メッセージ作成 ---
    # 日程1
    role = interaction.guild.get_role(1446054426849706056)
    if role:
        msg = f"{role.mention} クラン戦募集、参加できる日程にリアクションをつけてください\n"
        log_msg = f"[INFO] {interaction.user.display_name} さん /squadron コマンドを使用して、ロールメンションに成功"
    else:
        msg = "@here クラン戦募集、参加できる日程にリアクションをつけてください\n"
        log_msg = f"[ERROR] {interaction.user.display_name} さん /squadron コマンドを使用しましたが、ロールが見つからないためhereメンションを使用します"
    ts1_str = create_timestamp_str(schedule1)
    msg += f":one: {ts1_str} **BR {br1}**\n"

    # 日程2 (もしあれば)
    if schedule2:
        ts2_str = create_timestamp_str(schedule2)
        msg += f":two: {ts2_str} **BR {br2}**"

    # 送信
    await send_log_message(log_msg)
    await interaction.response.send_message(msg)

@client.tree.command(name="br_list", description="現在のBRローテーション表を表示します")
async def br_list(interaction: discord.Interaction):
    log_msg = f"[INFO] {interaction.user.display_name} さんが /br_list コマンドを使用しました。"
    await interaction.response.defer()

    if requestBR is None:
        log_msg = f"[FATAL] {interaction.user.display_name} さんが /br_list コマンドを使用しましたが、requestBR モジュールが見つかりませんでした。"
        await interaction.followup.send("❌ エラー: requestBR モジュールが見つかりませんでした。\n可能であれば開発者へ連絡してください", ephemeral=True)
        return

    try:
        # requestBRからリストを取得
        br_data_list, is_cached = await get_cache_br() #requestBR.main()

        if not br_data_list:
            log_msg = f"{interaction.user.display_name} さんが /br_list コマンドを使用しましたが、データ取得に失敗しました。\nJSONデータが取得できません。"
            await interaction.followup.send("データ取得に失敗:BR情報が取得できませんでした", ephemeral=True)
            return

        # リストを改行で結合して表示
        br_data_list = [s.rstrip() for s in br_data_list]
        formatted_text = "\n".join(br_data_list)
        await interaction.followup.send(f"```{formatted_text}```")
        await send_log_message(f"{log_msg}、キャッシュ有効：{is_cached}")
    except Exception as e:
        log_msg = f"[FATAL] {interaction.user.display_name} さんが /br_list コマンドを使用しましたが、エラーが発生しました:\n{e}"
        await send_log_message(log_msg)
        await interaction.followup.send(f"エラーが発生しました:\n{e}", ephemeral=True)

@client.tree.command(name="br_now", description="本日のBRを表示します")
async def br_now(interaction: discord.Interaction):
  try:
    CurrentBR = GetCurrentBR.get_current_br()
  except GetCurrentBR.BROutOfRange as e:
      log_msg = f"[FATAL] /br_nowを実行しましたが、キャッシュが期限切れです\nエラー内容:{e}"
      await send_log_message(log_msg)
      await interaction.response.send_message("最新の情報が取得できません、最低1時間ほど待って再試行してください", ephemeral=True)
  if GetCurrentBR is None:
      log_msg = f"[FATAL] {interaction.user.display_name} さんが /br_now コマンドを使用しましたが、GetCurrentBR モジュールが見つかりませんでした。"
      await send_log_message(log_msg)
      await interaction.response.send_message("❌ エラー: GetCurrentBR モジュールが見つかりませんでした。\n可能であれば開発者へ連絡してください", ephemeral=True)
      return None
  if "BR " not in CurrentBR:
     log_msg = f"[FATAL] {interaction.user.display_name} さんが /br_now コマンドを使用しましたが、取得したBRの形式が不正でした: {CurrentBR}"
     await send_log_message(log_msg)
     await interaction.response.send_message(f"❌ エラー: 取得したBRの形式が不正でした:\n{CurrentBR}", ephemeral=True)
     return None
  else:
    CurrentBR = CurrentBR.replace("BR ","")
    if CurrentBR in BR_CHOICES:
        log_msg = f"[INFO] {interaction.user.display_name} さんが /br_now コマンドを使用しました。"
        await interaction.response.send_message(f"本日のクラン戦BRは **{CurrentBR}** です。") 
    else:
        log_msg = f"[FATAL] {interaction.user.display_name} さんが /br_now コマンドを使用しましたが、取得したBRの形式が不正でした: {CurrentBR}"
        await interaction.response.send_message(f"❌ エラー: 取得したBRの形式が不正でした:\n{CurrentBR}", ephemeral=True)
    await send_log_message(log_msg)


def is_owner_check():
    async def predicate(interaction: discord.Interaction):
        DEV_ID = int(dev_id_file)
        return interaction.user.id == DEV_ID
    return app_commands.check(predicate)

@client.tree.command(name="sync", description="開発者用: コマンドツリーの同期")
@is_owner_check() #開発者かチェック
async def sync(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    # 1. テストサーバーに同期 (即時反映)
    client.tree.copy_global_to(guild=MY_GUILD)
    synced_guild = await client.tree.sync(guild=MY_GUILD)
    # 2. グローバル同期 (全サーバーに反映し、古いコマンドを削除)
    # これが setup_hook にあった「await self.tree.sync()」に相当します
    synced_global = await client.tree.sync()

    log_msg = f"[INFO] {interaction.user.display_name} さんが /sync コマンドを実行し、コマンドを同期しました。"
    response_msg = (
        "✅ コマンドの同期が完了しました。\n"
        f"・**テストギルド（{MY_GUILD.id})**: {len(synced_guild)} 個のコマンドを同期\n"
        f"・**グローバル**: {len(synced_global)} 個のコマンドを同期 (反映には時間がかかります)"
    )

    await interaction.followup.send(response_msg, ephemeral=True)
    await send_log_message(log_msg)

@sync.error


async def sync_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    # チェックに失敗した場合(CheckFailure)
    if isinstance(error, app_commands.CheckFailure):
        log_msg = f"[ERROR] {interaction.user.display_name} さんが /sync コマンドを実行しようとしましたが、権限がありません。"
        await interaction.response.send_message(
            "❌ **権限がありません**\nこのコマンドはBot開発者のみ実行可能です。",
            ephemeral=True
        )
        await send_log_message(log_msg)
    else:
        # その他の予期せぬエラー
        print(error) # コンソールに表示

async def send_log_message(message: str):
    """指定されたチャンネルにログメッセージを送信するヘルパー関数"""
    channel = client.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        print(f"ログチャンネルが見つかりません: ID {LOG_CHANNEL_ID}")



@client.command() #ログチャンネル限定で使えるコマンド Bot再起動
@commands.check(is_target_channel)
async def restart_bot(ctx):
    await ctx.send("🔄 **Botを再起動します...**")
    log_msg = f"[INFO] {ctx.author.display_name} さんが restart_bot コマンドを使用し、Botを再起動しました。"
    await send_log_message(log_msg)
    try:
       python = sys.executable
       script = os.path.abspath(__file__)
       print("BOTを再起動しています")
       os.execl(python, python, script)
    except Exception as e:
       await ctx.send(f"❌ **再起動に失敗しました:** {e}")   
@restart_bot.error
async def restart_bot_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f'❌このコマンドは専用チャンネルでのみ実行可能です！', ephemeral=True)

@client.command() #ログチャンネル限定で使えるコマンド Bot停止
@commands.check(is_target_channel)
async def stop_bot(ctx):
    await ctx.send("Botを停止します...")
    log_msg = f"[INFO] {ctx.author.display_name} さんが stop_bot コマンドを使用し、Botを停止しました。"
    await send_log_message(log_msg)
    await client.close()
@stop_bot.error
async def stop_bot_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f'❌このコマンドは専用チャンネルでのみ実行可能です！', ephemeral=True)

# Bot起動
client.run(TOKEN)
