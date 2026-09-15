# カニ通販サイト型トップページ

「安全なカニ通販.com」の新しい固定ページ用ローカル実装です。公開中のトップページやWordPressには、まだ変更を加えていません。

## ファイル

- `index.html` — ローカル確認用の完成ページ
- `wordpress-fixed-page.html` — WordPress本文へ貼り付けるHTML断片
- `wordpress-additional.css` — `.kani-top` 配下だけに効く追加CSS
- `assets/images/` — 生成・最適化済みWebP画像9点
- `tests/validate_html.py` — カテゴリ、通販会社、広告属性、画像を検証
- `IMAGE-PROMPTS.md` — 画像生成に使用した最終プロンプト

JavaScriptは使用していません。ページ内移動と購入導線はHTML/CSSだけで機能します。

## ローカル確認

```bash
python3 -m http.server 8000
```

ブラウザで `http://localhost:8000/` を開きます。`file://` ではなくlocalhostで確認してください。

## WordPressへ移すとき

1. `assets/images/` の9画像をWordPressメディアへアップロードします。
2. `wordpress-fixed-page.html` 内の `{{MEDIA_BASE_URL}}` をアップロード先URLに置換します。
3. HTMLを新規固定ページのコードエディターへ貼り付けます。
4. `wordpress-additional.css` を追加CSSへ貼り付けます。
5. 下書きプレビューでPC・スマホ表示とリンクを再確認します。
6. 承認後にだけ固定ページを公開し、ホームページ設定を切り替えます。

テーマのPHP、既存トップページ、投稿、プラグインは変更対象外です。

## 通販会社の固定対応

| 種類 | 通販会社 |
|---|---|
| ズワイガニ | かに本舗／かにまみれ／ますよね |
| 毛ガニ | かにまみれ／北釧水産 |
| タラバガニ | かに本舗／かにまみれ |
| カニ鍋 | 北釧水産／かに本舗 |

## 広告リンクの状態

2026年9月15日に、現在の公開サイトで使われているURLから遷移を確認しました。

- かに本舗：A8広告リンクの遷移を確認済み
- ますよね：A8広告リンクの遷移を確認済み
- かにまみれ：A8広告リンクの遷移を確認済み
- 北釧水産：公開サイトに残っているA8広告リンクは掲載終了または配信停止で無効

北釧水産の2ボタンは、リンク切れを避けるため公式サイトへの通常リンクにしています。HTML内では `data-affiliate-status="replacement-required"` を付けています。公開前にASPで新しい提携URLを取得し、`href` と `rel="sponsored noopener"` を設定してください。

価格、送料、在庫、配送条件は変動するため、トップページ本文には固定表示していません。

## 検証

```bash
python3 tests/validate_html.py
```

北釧水産の広告URLが未設定の間は、検証結果に警告が2件表示されます。これは既知の公開前作業です。
