# 北陸大学卓球部 インスタ素材メーカー

試合の結果やプレー動画を、インスタ用の画像・動画にすばやく仕上げるための道具です。

| ページ | ファイル | できること |
| --- | --- | --- |
| メニュー | `web/index.html` | 作りたいものを選ぶトップページ |
| ストーリーメーカー | `web/story.html` | オーダー用紙の写真から団体戦のオーダーを読み取り、ストーリー画像（1080×1920）を作る。スコアを選ぶだけで更新できる |
| 大会報告フィード | `web/feed.html` | 集合写真の上下に帯を付け、大会名・会場・日付を入れたフィード画像（3:4／4:5／正方形）を作る。色は桜・紅葉・雪・北陸グリーン・ホワイト |
| 得点入りゲーム動画 | `web/score.html` | 試合の動画を再生しながら、ラリーの間だけ「ラリー中」を押しっぱなし・点が決まったら得点ボタン。ラリーだけをつなぎ、得点（ゲームカウントも自動）と最初・最後の字幕が入った動画を1回で書き出す。縦長リールと横長を選べる |
| リールメーカー | `web/reel.html` | プレー動画に「選手 vs 選手」・見出し・チーム名の帯を付けて、リール用の縦長動画を書き出す |

どちらも北陸大学のロゴと、スクールカラーの緑・金が最初から入っています。相手チームの色だけ選べます。

## 公開のしかた（GitHub Pages）

1. リポジトリの Settings → Pages → Source を「GitHub Actions」にする
2. `main` に push すると `.github/workflows/pages.yml` が自動で公開する

公開後のアドレス:

- メニュー: https://0313akira.github.io/Takkyu-instagram/
- ストーリー: https://0313akira.github.io/Takkyu-instagram/story.html
- フィード: https://0313akira.github.io/Takkyu-instagram/feed.html
- 得点入り動画: https://0313akira.github.io/Takkyu-instagram/score.html
- リール: https://0313akira.github.io/Takkyu-instagram/reel.html

GitHub Pages 版はログイン不要で誰でも使えます。オーダー用紙の写真の読み取りは Claude で開いたときだけ使えるので、Pages 版では名前を手で入力します。

## ストーリーメーカーの使い方

1. オーダー用紙の写真を撮る・選ぶ（Claude 版のみ自動で読み取り）
2. 名前を確認し、試合が進んだらスコアを選ぶ
3. デザイン（グリーン・ホワイト・クラシック）と相手チームの色を選ぶ
4. 「画像を保存」→ インスタのストーリーで選ぶ

## 大会報告フィードの使い方

1. 集合写真を撮る・選ぶ（完成画像をドラッグすると位置、スライダーで大きさを調整）
2. 大会名（改行で2行）、会場、日付を入れる
3. 色（季節）と画像の形を選ぶ
4. 「画像を保存」→ インスタの投稿で選ぶ

## リールメーカーの使い方

1. プレー動画を選び、使う範囲（はじめ・おわり）とズームを決める
2. 選手名と見出しを入れる
3. 相手の選手名の色を選ぶ
4. 「動画を書き出す」→ インスタのリールで選ぶ

書き出しは再生しながら録画するため、動画の長さと同じだけ時間がかかります。途中で画面を閉じないでください。
パソコンの Chrome では iPhone の動画形式（HEVC）を読み込めないことがあります。そのときは iPhone で開いてください。

## パソコン用（Python）

```bash
pip install pillow
python make_story.py order.txt              # story.png ができる（北陸大学のロゴ入り）
python make_story.py order.txt -b none      # ロゴなし
```

`order.txt` は空行で区切ったまとまりが黒い枠 1 つになります。「○」は赤丸、「×」は青いバツで描かれます。

## インスタへの自動投稿（任意・未設定）

`publish_story.py` は Instagram Graph API でストーリーに投稿するスクリプトです。
部のアカウントをプロアカウントにし、Meta for Developers でアクセストークンを取得したうえで、画像を公開 URL に置く必要があります。

```bash
export IG_USER_ID=...
export IG_ACCESS_TOKEN=...
python publish_story.py https://example.com/story.png
```

アクセストークンは絶対にコミットしないでください。
