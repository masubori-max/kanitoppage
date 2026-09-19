from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MAPPING = {
    "kani-zuwai": ["かに本舗"],
    "kani-kegani": ["かにまみれ"],
    "kani-taraba": ["かに本舗"],
    "kani-nabe": [],
}
EXPECTED_IMAGES = {
    "kani-top-header-new.png",
    "type-zuwai.webp",
    "type-kegani.webp",
    "type-taraba.webp",
    "type-kani-nabe.webp",
    "purpose-family.webp",
    "purpose-gift.webp",
    "purpose-easy.webp",
    "purpose-volume.webp",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.images = []
        self.stores = {key: [] for key in EXPECTED_MAPPING}
        self.affiliate_links = []
        self.section_stack = []
        self.script_count = 0
        self.disclosure_count = 0
        self._capture_disclosure = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id")
        if element_id:
            self.ids.add(element_id)
        if tag == "section":
            self.section_stack.append(element_id)
        if tag == "img":
            self.images.append(attrs)
        if tag == "a" and attrs.get("data-affiliate-store"):
            section_id = next(
                (item for item in reversed(self.section_stack) if item in EXPECTED_MAPPING),
                None,
            )
            if section_id:
                self.stores[section_id].append(attrs["data-affiliate-store"])
            self.affiliate_links.append(attrs)
        if tag == "script":
            self.script_count += 1
        if tag == "p" and "kani-disclosure" in attrs.get("class", "").split():
            self._capture_disclosure = True

    def handle_endtag(self, tag):
        if tag == "section" and self.section_stack:
            self.section_stack.pop()
        if tag == "p" and self._capture_disclosure:
            self._capture_disclosure = False

    def handle_data(self, data):
        if self._capture_disclosure and "アフィリエイト広告" in data:
            self.disclosure_count += 1


def validate(path: Path, wordpress: bool = False):
    parser = PageParser()
    text = path.read_text(encoding="utf-8")
    parser.feed(text)
    errors = []
    warnings = []

    missing_ids = set(EXPECTED_MAPPING) - parser.ids
    if missing_ids:
        errors.append(f"必須IDがありません: {sorted(missing_ids)}")

    for section_id, expected in EXPECTED_MAPPING.items():
        if parser.stores[section_id] != expected:
            errors.append(
                f"{section_id} の通販対応が違います: "
                f"expected={expected}, actual={parser.stores[section_id]}"
            )

    if parser.disclosure_count < 1:
        errors.append("ファーストビュー付近の広告表記がありません")
    if parser.script_count:
        errors.append("初期版ではJavaScriptを使用しません")

    for attrs in parser.affiliate_links:
        store = attrs["data-affiliate-store"]
        href = attrs.get("href", "")
        if attrs.get("target") != "_blank":
            errors.append(f"{store}: target=_blank がありません")
        if "noopener" not in attrs.get("rel", "").split():
            errors.append(f"{store}: rel=noopener がありません")
        if attrs.get("data-affiliate-status") == "replacement-required":
            warnings.append(f"{store}: 公開前に有効な広告URLへ差し替えが必要です")
        elif "sponsored" not in attrs.get("rel", "").split():
            errors.append(f"{store}: rel=sponsored がありません")
        if urlparse(href).scheme not in {"http", "https"}:
            errors.append(f"{store}: 外部リンクURLが不正です")

    non_decorative = [
        attrs for attrs in parser.images
        if "kani-recommendation__thumb" not in attrs.get("class", "").split()
    ]
    for attrs in non_decorative:
        if not attrs.get("alt", "").strip():
            errors.append(f"説明用画像のaltが空です: {attrs.get('src')}")

    if wordpress:
        if "assets/images/" in text:
            errors.append("WordPress版にローカル画像パスが残っています")
        if "/wp-content/uploads/" not in text:
            errors.append("WordPressメディアURLがありません")
    else:
        used = {
            Path(attrs.get("src", "")).name
            for attrs in parser.images
            if attrs.get("src", "").startswith("assets/images/")
        }
        if used != EXPECTED_IMAGES:
            errors.append(
                f"使用画像が9点構成と一致しません: "
                f"missing={sorted(EXPECTED_IMAGES - used)}, extra={sorted(used - EXPECTED_IMAGES)}"
            )
        for name in EXPECTED_IMAGES:
            if not (ROOT / "assets" / "images" / name).is_file():
                errors.append(f"画像ファイルがありません: {name}")

    return errors, warnings


def main():
    all_errors = []
    all_warnings = []
    for filename, wordpress in (
        ("index.html", False),
        ("wordpress-fixed-page.html", True),
    ):
        errors, warnings = validate(ROOT / filename, wordpress=wordpress)
        all_errors.extend(f"{filename}: {item}" for item in errors)
        all_warnings.extend(f"{filename}: {item}" for item in warnings)

    for warning in all_warnings:
        print(f"WARNING: {warning}")
    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("OK: HTML、通販対応、広告属性、画像構成を検証しました")


if __name__ == "__main__":
    main()
