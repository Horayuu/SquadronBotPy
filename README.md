# Squadron Scheduler Bot
このBotはWarThunderにおけるクラン戦を想定した高機能Botです
**※このコードは私個人用として公開しておりソースコードの使用、再配布は許可していません。**
This repository is published for personal use.
Unauthorized use, or redistribution of the source code is prohibited.

# 主な機能
**クラン戦招集**:     /squadronで招集を作成可能、  
　　　　　　必須引数"schedule1"と"br1"、任意で引数"schedule2"と"br2"を選択できます  

**BR表をリクエスト**: /br_listでBR表を表示できます、引数はありません  


### ChangeLog
Ver 1.1.0 初期バージョン 大枠の実装とGitHubPush  
Ver 1.1.1 初リリース 機能は/squadronの招集機能のみ  
Ver 1.1.2 hereメンションを実装  
Ver 1.2.0 BR表の表示を可能に /br_listコマンド実装。  
Ver 1.2.1 細かい修正をリリース gitignoreを調整しただけ  
Ver 1.2.2 開発者用 /syncコマンドの実装(Botコマンドを同期する)  
Ver 1.2.3 開発者以外が/syncを使用する際にメッセージを返すように変更、コメントアウトいじり  
Ver 1.2.4 一部のエラーメッセージを修正しました  
Ver 1.3.0 /br_listが保存済みのキャッシュを使用するように変更しました(アクセス制限対策)  
Ver 1.3.1 各コマンドを実行した際ログを送信するようにしました  
Ver 1.4.0 /br_nowによって当日のBRを取得できるようにしました  
Ver 1.4.1 /squadronコマンドでメンションが機能していない不具合を修正  
Ver 1.4.2 /br_nowの内部時刻が更新されない不具合を修正  