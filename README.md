
# 概要
「想像と体験に関する研究」の実験装置およびアンケートシステム。<br>
本研究は、人が想像力によって、どこまで体験を自ら作り出せるかを明らかにすることを目的とする。本システムでは、主に音声を使う様々な実験を提供し、被験者の知覚を変える能力を評価する。<br>
**ブラウザーは、Chromeを利用すること。他のブラウザーの場合には、後述する対応が必要になる。**
<br><br><br><br>

# 目次
- [インストール](#インストール)
- [システムの使い方](#システムの使い方)
- [アンインストール](#アンインストール)
- [Chrome以外を利用する場合](#Chrome以外を利用する場合)
<br><br><br><br>

# インストール
## 1. システムのインストール
- システムのインストールには下記のソフトウェアが事前にインストールされている必要がある。
    - Python 3
    - pip (Python 3.4以上であればプリインストールされている)
    - git
<br><br>

- 下記プロンプトを実行して、システムをインストールする。
```sh
# リポジトリをクローン
git clone https://github.com/ksk-S/PhenoControl-JP.git

# 作業ディレクトリに移動
cd PhenoControl-JP

# インストールスクリプトを実行
./install.sh
```
<br><br>


## 2. システムのデーモン化
- インストールの作業ディレクトリのまま、下記プロンプトを実行して、デーモン化する。
- ローカル環境で一時的に実行する場合には本作業は不要。
```sh
# デーモン化スクリプトの実行
./setup_pcjp_service.sh
```
<br><br>


## 3. データ書き込み先設定
- 本システムは、アンケート結果をGoogle Spreadsheet（以下、GS）に保存する。
- 本システム - Google Apps Script（以下、GAS） - GSという順番でデータが流れていくので、下記手順でそれぞれを接続していく。

### 3-1. 動作確認

- 動作確認用のGSが事前に組み込まれているので、システムが正常にインストールされているか動作確認する。下記例に基づき、それぞれの環境に応じて、ブラウザ経由でシステムにアクセスし動作確認する。
- URLパラメーターは2つある:
  - `project_id`: 書き込み先 Spreadsheet を選択する（`system.cfg` の `[projects]` でルックアップ）。未指定または未登録の場合は `[google] app_script_url` のデフォルト GS にフォールバック。
  - `session_id`: 旧「プロジェクトID」。CONSENT_CHECK シートの説明文を選択する。未指定の場合は0が設定される。動作確認用 GS では現状 0 と 112 のみが有効。
```
（フォーマット）
http://{ip}:{port}/[?project_id={project_id}&session_id={session_id}]

（例）
http://192.168.10.1:8080/?project_id=alpha&session_id=112
http://192.168.10.1:8080/?session_id=1234
http://192.168.10.1:8080/
http://127.0.0.1/
```
- 実験を最後まで実施したら、下記GSの「DATA」シートにアクセスし、正しくデータが書き込まれているか確認する。
    - 音声データの再生時間が長いので、system.cfg の"display_skip_button = on"に設定することにより、SKIPボタンが表示し、音声データをスキップできるようになり、動作確認を1,2分で完了することができる。変更した場合には設定を反映させるためにシステムを再起動すること。
https://docs.google.com/spreadsheets/d/1FEAK4VtGf6CRZmUwzNu4tnenydN20Q8GDOzYlraqn7E/edit#gid=0
<br><br>


### 3-2. GS新規作成
1. 動作確認用の下記GSを「ファイル」＞「コピーを作成」でコピーする。GS自体のアクセス権限は運用に応じて設定する。全公開する必要はない。
https://docs.google.com/spreadsheets/d/1FEAK4VtGf6CRZmUwzNu4tnenydN20Q8GDOzYlraqn7E/edit#gid=0
2. 新規に作成したGSのURLからGS IDをメモしておく。URLの"/d/"から次の"/"までの英数字がGS IDとなる。例として、前述の動作確認用GSのURLの場合には、**1FEAK4VtGf6CRZmUwzNu4tnenydN20Q8GDOzYlraqn7E**になる。
3. このGS IDとシート名で、GSとGASを接続する。
<br><br>


### 3-3. GAS設定（GAS - GS間接続）
1. GS内メニューで、「拡張機能」＞「Apps Script」を選択し、Apps Scriptエディタを起動する。
2. gsID変数に先ほどメモしたGS IDをコピーする。
3. 右上の[デプロイ]ボタンを押下して、自分のアカウント、公開先は"全員"になっていることを確認し、[デプロイ]ボタンを押下する
4. その後、ダイアログが表示されるので、そこに記載されたGASのURLをコピーしておく。それを使いシステムとGASを接続する。
<br><br>


### 3-4. システム設定（システム - GAS間接続）
1. 作業ディレクトリ直下にあるsystem.cfgをエディタで開く。
2. 前述のGAS URLを下記のapp_script_urlにコピーする。これがデフォルトの書き込み先になる（URL に `project_id` がない、または `[project.*]` に未登録の場合に使われる）。
```ini
[google]
app_script_url = https://script.google.com/a/macros/volocitee.com/s/AKfycbxF7S-m59UCCcPKGknU1sKUCouBdC5VfDtJARhKkRhEMfPDExBVtMjVpfpsUjwtR1w2/exec
```
3. **プロジェクトごとに別の Spreadsheet を使う場合**、プロジェクトごとに `[project.<任意名>]` セクションを追加する。各セクションには `project_id` / `project_name` / `app_script_url` の 3 つを必ず指定する。各プロジェクト用に GS をコピー → GAS をデプロイ → URL をここに登録、を繰り返す。
```ini
[project.alpha]
project_id = alpha
project_name = アルファ実験
app_script_url = https://script.google.com/macros/s/AKfycbx.../exec

[project.beta]
project_id = beta
project_name = ベータ実験
app_script_url = https://script.google.com/macros/s/AKfycbx.../exec
```
- アクセス時の URL: `http://{ip}:{port}/?project_id=alpha&session_id=112`
- ルックアップは `project_id` フィールドの値で行われる（セクション名 `[project.alpha]` は任意のラベル扱い、ただし `project_id` と揃えると分かりやすい）。
- `project_id` が未指定 / 未登録 → `[google] app_script_url` のデフォルトにフォールバック（`project_name` は空文字として GS に書かれる）。
<br><br>


### 3-5. GAS スクリプト側の対応（変数名のリネーム）
- 本システムは Apps Script に対して `session_id` というクエリパラメータ名でリクエストを送るように変更されている（旧 `id` からのリネーム）。**コピー元の動作確認用 GS の Apps Script (Code.gs)** で受け側を `session_id` に修正する必要がある。サンプルは作業ディレクトリ直下の [gascode.txt](gascode.txt) を参照。
- 例（`doGet` の冒頭）:
```javascript
function doGet(e) {
  var sessionId = e.parameter.session_id;   // 旧: e.parameter.id
  // CONSENT_CHECK シートを sessionId で引いて同意 HTML を返す
  ...
}
```
- POST 側 (`doPost`) は変更不要（行データはそのまま追記）。
- **CONSENT_CHECK シートの A 列ヘッダも「プロジェクトID」→「セッションID」に変更**しておくと整合が取れる。GAS は `data[i][0]` で値を引いているだけなので、ヘッダ文字列の変更は動作に影響しない。
<br><br>


### 3-6. DATA シートの列レイアウト
- 本システムが GAS に送信するデータの列順は以下の通り（26 列）:

| 列 | 内容 | 列 | 内容 |
|---|---|---|---|
| A | project_id   | N | Q2 |
| B | project_name | O | Q3 |
| C | session_id   | P | Q4a |
| D | start_time   | Q | Q4b |
| E | end_time     | R | Q5 |
| F | duration     | S | Q6 |
| G | user         | T | Q7 |
| H | age          | U | Q8 |
| I | gender       | V | Q9 |
| J | ball_color   | W | Q10a |
| K | comments1    | X | Q10b |
| L | comments2    | Y | Q11 |
| M | Q1           | Z | Q12 |
| | | **AA** | **（スコア式の貼り付け先）** |

- 1 行目には対応するヘッダ（`project_id`, `project_name`, `session_id`, ... , `Q12`）を手動で入力しておく。
- **既存 GS でデータがある場合**: A 列に「project_id」、B 列に「project_name」のヘッダを挿入し、既存行の値を埋める（不明なら空欄でも可）。データ列が 2 つ右にずれる形になる。
<br><br>


### 3-7. スコア列の追加
- GS の DATA シートでアンケート回答（M〜X 列の Q1〜Q10b）からスコアを自動計算したい場合は、**AA1 セル**（Q12 の次列）に以下の数式を貼り付ける。ARRAYFORMULA で全行に自動展開される。
```
=ARRAYFORMULA(IF(ROW(M:M)=1, "score", IF(M:M="", "", (M:M + N:N + O:O + (P:P+Q:Q)/2 + R:R + S:S + T:T + U:U + V:V + SQRT(W:W*X:X)) / 9)))
```
- 元の式 `=AVERAGE(K2, L2, M2, AVERAGE(N2,O2), P2, Q2, R2, S2, T2, SQRT(U2*V2))` を `project_id` / `project_name` 列追加に伴い K〜V → M〜X にシフトさせたもの（9 項目の平均）。Q11, Q12 (Y, Z 列) はスコアには含まれない。
<br><br>


## 4. システム再起動
- 変更内容を反映させるために（設定ファイルを読み込み直すために）、後述の再起動手順に従い、システムを再起動する。
<br><br>


## ５． セッションIDの設定
- GSの「CONSENT_CHECK」シートで、セッションID（旧プロジェクトID）とそれに対応する同意文をHTMLで書き込む。同一プロジェクト（同一 GS）内でも複数の説明 HTML を使い分けられる。
  - ここに記載のないセッションIDが、ユーザーから入力された場合にはシステムエラーが表示される。
- システムの再起動は不要。
<br><br><br><br>


# システムの使い方
## 1. デーモン版の操作方法
### 1-1. 起動
- 前述のデーモン化を実施済みであれば、すでに起動されていて、またサーバー起動時にも自動起動されるようになっているので、基本的には本作業は不要。
```sh
sudo systemctl start pcjp
```
<br><br>

### 1-2. 停止
```sh
sudo systemctl stop pcjp
```
<br><br>

### 1-3. 再起動
```sh
sudo systemctl restart pcjp
```
<br><br>

### 1-4. ポート番号変更
- デフォルトの8080以外を指定する場合には、env.conf内でポート番号を設定する。
```sh
sudo vim /etc/systemd/system/pcjp.service.d/env.conf 
sudo systemctl stop pcjp
sudo sudo systemctl daemon-reload
sudo systemctl start pcjp
```
<br><br>

### 1-5. 設定ファイル変更
- system.cfgの値を変更する場合はデーモンを再起動してください。
```sh
sudo vim system.cfg
sudo systemctl restart pcjp
```
<br><br>

## 2. ローカル版 or ターミナル実行版の操作方法
- Macなどのローカル環境で実行する場合には、作業ディレクトリ直下にあるスクリプトで直接操作する。
### 2-1. 起動
```sh
./run.sh
```
<br><br>

### 2-2. 停止
```sh
./stop.sh
```
<br><br>

### 2-3. 再起動
```sh
./stop.sh;./run.sh
```
<br><br>

### 2-4. ポート番号変更
- デフォルトの8080以外を指定する場合には、run.shに引数で渡す。
```sh
sudo ./stop.sh
sudo ./run.sh 5757
```
<br><br><br><br>


# アンインストール
## 1. デーモン化解除
- もしデーモン化している場合には、下記作業でデーモン化の解除を行う。
```sh
sudo systemctl stop pcjp
sudo systemctl disable pcjp
sudo rm /etc/systemd/system/pcjp
sudo rm -r /etc/systemd/system/pcjp.service.d
```
<br><br>

## 2. システムアンインストール
- 作業ディレクトリを丸ごと削除する。
```sh
rm -rf PhenoControl-JP
```
<br><br><br><br>


# Chrome以外を利用する場合
セキュリティ上、音声の自動再生ができないので、ブラウザ毎に対応が必要となる。
## Safari
1. 本システムをブラウザで開く。
2. 「Safari」＞「設定...」を選択する。
3. 「Webサイト」タグを選択し、左の設定一覧から「自動再生」を選択する。
4. 本システムのURLにあるドロップダウンメニューから「すべてのメディアを自動再生」を選択する。
<br><br>


## Firefox
1. 本システムをブラウザで開く。
2. アドレスバー内にある（URLの左側にある）鍵アイコン（http接続の場合には赤色の斜線が入っている）をクリックする。
3. 「安全な接続」（http接続の場合には「安全でない接続」と表記される）＞「詳細を表示」を選択する。
4. 「サイト別設定」を選択し、ページ下部にある自動設定項目にある「標準設定を使用する」のチェックボックスを解除する。
5. 「音声と動画を許可」を選択する。

