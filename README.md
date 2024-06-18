
# 概要
「想像と体験に関する研究」の実験装置およびアンケートシステム。<br>
 本研究は、人が想像力によって、どこまで体験を自ら作り出せるかを明らかにすることを目的とする。本システムでは、主に音声を使う様々な実験を提供し、被験者の知覚を変える能力を評価する。
 ブラウザーは、Chromeを利用すること。他のブラウザーの場合には、後述する対応が必要になる。
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
- URLパラメーターにidを渡すことにより、実験データにプロジェクトIDを書き込むことができる。idを指定しない場合は、0が設定される。
```
（フォーマット）
http://{ip}:{port}/[?id={id}]

（例）
http://192.168.10.1:8080/?id=1234
http://192.168.10.1:8080/
http://127.0.0.1/
```
- 実験を最後まで実施したら、下記動作確認用GSにアクセスし、正しくデータが書き込まれているか確認する。
    - 音声データが長いので、system.cfg の"display_skip_button = on"に設定することにより、SKIPボタンが表示し、音声データをスキップできるようになり、動作確認を1,2分で完了することができる。変更した場合には設定を反映させるために後述のシステム再起動処理を実施すること。
https://docs.google.com/spreadsheets/d/1FEAK4VtGf6CRZmUwzNu4tnenydN20Q8GDOzYlraqn7E/edit#gid=0
<br><br>


### 3-2. GS新規作成
- 自分のGoogleアカウントで、GSを新規作成する。ファイル名は任意で良いが、シート名は必ず「DATA」とすること。
- 新規に作成したGSのURLからGS IDをメモしておく。URLの"/d/"から次の"/"までの英数字がGS IDとなる。例として、前述の動作確認用GSのURLの場合には、**1FEAK4VtGf6CRZmUwzNu4tnenydN20Q8GDOzYlraqn7E**になる。
- このGS IDとシート名で、GSとGASを接続する。
<br><br>


### 3-3. GAS設定（GAS - GS間接続）
- GSメニュー > 拡張機能 > Apps Scriptを選択し、Apps Scriptエディタを起動する。
- ファイルの右側にあるプラスアイコンを押下し、"スクリプト"を選択し、ファイルを作成する。ファイル名は任意で構いません。
- そのファイルに、下記コードをコピーする。
- SpreadsheetApp.openById()の引数に、先ほどメモしたGS IDを設定する。
```javascript
function doPost(e) {
  var ss = SpreadsheetApp.openById('1FEAK4VtGf6CRZmUwzNu4tnenydN20Q8GDOzYlraqn7E');// 新規GS IDに書き換える。
  var sheet = ss.getSheetByName('DATA');
  
  var data = JSON.parse(e.postData.contents).data;
  var values = data.map(function(item) {
    return item[1]; 
  });
  
  sheet.appendRow(values);
  return ContentService.createTextOutput(JSON.stringify({"result": "success"}));
}
```
- 右上の[デプロイ]ボタンを押下して、自分のアカウント、公開先は"全員"になっていることを確認し、[デプロイ]ボタンを押下する
- その後、ダイアログが表示されるので、そこに記載されたGASのURLをコピーしておく。それを使いシステムとGASを接続する。
<br><br>


### 3-4. システム設定（システム - GAS間接続）
- 作業ディレクトリ直下にあるsystem.cfgをエディタで開く。
- 前述のGAS URLを下記のapp_script_urlにコピーする。
```javascript
app_script_url = https://script.google.com/a/macros/volocitee.com/s/AKfycbxF7S-m59UCCcPKGknU1sKUCouBdC5VfDtJARhKkRhEMfPDExBVtMjVpfpsUjwtR1w2/exec
```
<br><br>


## 4. システム再起動
- 変更内容を反映させるために（設定ファイルを読み込み直すために）、後述の再起動手順に従い、システムを再起動する。
<br><br><br><br>


# システムの使い方
## 1. デーモン版
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
sudo systemctl stop pcjp
sudo vim /etc/systemd/system/pcjp.service.d/env.conf
sudo sudo systemctl daemon-reload
sudo systemctl start pcjp
```
<br><br>

## 2. ローカル版 or ターミナル実行版
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

# Chrome以外を利用する場合
セキュリティ上、音声の自動再生ができないので、ブラウザ毎に対応が必要となる。
## Safari
1. 本システムをブラウザで開く。
2. 「Safari」＞「設定...」を選択する。
3. 「Webサイト」タグを選択し、左の設定一覧から「自動再生」を選択する。
4. 本システムのURLにあるドロップダウンメニューから「すべてのメディアを自動再生」を選択する。

## Firefox
1. 本システムをブラウザで開く。
2. アドレスバー内にある（URLの左側にある）設定アイコンをクリックする。
3. 自動再生設定のドロップダウンメニューから「音声と動画を許可」を選択する。
