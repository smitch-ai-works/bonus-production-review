#!/usr/bin/env python3
"""Build a standalone Japanese sales report using only the standard library."""

import argparse
import csv
import html
from pathlib import Path
import sys


FIELDS = ("date", "product", "quantity", "unit_price")


class ReportError(Exception):
    """An input error that can be displayed without exposing CSV values."""


def read_sales(path):
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        try:
            header = reader.fieldnames
            if header is None or len(header) != len(FIELDS) or set(header) != set(FIELDS):
                raise ReportError(
                    "CSV 1行目: ヘッダーには date, product, quantity, unit_price が必要です。"
                )
            while True:
                try:
                    row = next(reader)
                except StopIteration:
                    break
                line_number = reader.reader.line_num
                # DictReader skips empty physical lines. Also skip empty cells.
                if None not in row and all(
                    value is not None and not value.strip() for value in row.values()
                ):
                    continue
                if None in row or any(row.get(field) is None for field in FIELDS):
                    raise ReportError(
                        f"CSV {line_number}行目: 列数がヘッダーと一致しません。"
                    )
                values = {field: row[field].strip() for field in FIELDS}
                for field in FIELDS:
                    if not values[field]:
                        raise ReportError(
                            f"CSV {line_number}行目: {field} が空です。"
                        )
                for field in ("quantity", "unit_price"):
                    try:
                        values[field] = int(values[field])
                    except ValueError:
                        raise ReportError(
                            f"CSV {line_number}行目: {field} は整数で指定してください。"
                        ) from None
                values["revenue"] = values["quantity"] * values["unit_price"]
                rows.append(values)
        except csv.Error:
            line = max(reader.reader.line_num, 1)
            raise ReportError(f"CSV {line}行目付近: CSV の形式が不正です。") from None
        except UnicodeError:
            line = reader.reader.line_num + 1
            raise ReportError(
                f"CSV {line}行目付近: UTF-8 として読み込めません。"
            ) from None
    return rows


def yen(value):
    return f"¥{value:,}"


def build_html(rows, source_name):
    products = {}
    total_quantity = 0
    total_revenue = 0
    for row in rows:
        total_quantity += row["quantity"]
        total_revenue += row["revenue"]
        aggregate = products.setdefault(row["product"], {"quantity": 0, "revenue": 0})
        aggregate["quantity"] += row["quantity"]
        aggregate["revenue"] += row["revenue"]

    product_rows = []
    for name, totals in sorted(
        products.items(), key=lambda item: (-item[1]["revenue"], item[0])
    ):
        product_rows.append(
            f'<tr><th scope="row">{html.escape(name)}</th>'
            f'<td class="number">{totals["quantity"]:,}</td>'
            f'<td class="number">{yen(totals["revenue"])}</td></tr>'
        )

    detail_rows = []
    for row in rows:
        detail_rows.append(
            f'<tr><td>{html.escape(row["date"])}</td>'
            f'<th scope="row">{html.escape(row["product"])}</th>'
            f'<td class="number">{row["quantity"]:,}</td>'
            f'<td class="number">{yen(row["unit_price"])}</td>'
            f'<td class="number">{yen(row["revenue"])}</td></tr>'
        )

    if not product_rows:
        product_rows.append('<tr><td colspan="3">データがありません。</td></tr>')
        detail_rows.append('<tr><td colspan="5">データがありません。</td></tr>')

    return f'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>売上レポート</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: #183044; background: #f3f6fa;
      font-family: sans-serif; line-height: 1.6; overflow-wrap: anywhere; }}
    main {{ width: 100%; max-width: 960px; margin: 0 auto; padding: 28px 20px; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 0 0 14px; font-size: 20px; }}
    .source {{ margin: 0 0 24px; color: #526375; }}
    .summary {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px; margin: 0 0 24px; }}
    .summary div {{ min-width: 0; padding: 16px; background: #fff;
      border: 1px solid #d4deea; border-radius: 10px; }}
    dt {{ color: #526375; font-size: 14px; }}
    dd {{ margin: 4px 0 0; font-size: 24px; font-weight: bold; }}
    section, .detail-panel {{ min-width: 0; margin: 0 0 24px; padding: 20px;
      background: #fff; border: 1px solid #d4deea; border-radius: 10px; }}
    summary {{ cursor: pointer; font-weight: bold; }}
    summary:focus-visible {{ outline: 2px solid #183044; outline-offset: 4px; }}
    .detail-panel[open] summary {{ margin-bottom: 14px; }}
    table {{ width: 100%; table-layout: fixed; border-collapse: collapse; }}
    th, td {{ min-width: 0; padding: 10px 8px; border-bottom: 1px solid #d4deea;
      text-align: left; vertical-align: top; overflow-wrap: anywhere; white-space: normal; }}
    thead th {{ background: #edf3f8; font-weight: bold; }}
    tbody th {{ font-weight: normal; }}
    tfoot th, tfoot td {{ background: #edf3f8; font-weight: bold; }}
    .number {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .products col:first-child {{ width: 44%; }}
    .products col {{ width: 28%; }}
    .details .date {{ width: 22%; }}
    .details .product {{ width: 24%; }}
    .details .quantity {{ width: 12%; }}
    .details .money {{ width: 21%; }}
    @media (max-width: 480px) {{
      main {{ padding: 16px 12px; }}
      h1 {{ font-size: 24px; }}
      h2 {{ margin-bottom: 10px; }}
      .source {{ margin-bottom: 16px; font-size: 14px; }}
      .summary {{ gap: 6px; margin-bottom: 16px; }}
      .summary div {{ padding: 10px 6px; }}
      .summary dt {{ font-size: 11px; }}
      .summary dd {{ font-size: 20px; }}
      section, .detail-panel {{ margin-bottom: 16px; padding: 12px 8px; }}
      th, td {{ padding: 8px 3px; font-size: 12px; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>売上レポート</h1>
  <p class="source">元データ：{html.escape(source_name)}</p>
  <dl class="summary" aria-label="売上のまとめ">
    <div><dt>総売上</dt><dd>{yen(total_revenue)}</dd></div>
    <div><dt>総数量</dt><dd>{total_quantity:,}</dd></div>
    <div><dt>集計した行数</dt><dd>{len(rows):,}</dd></div>
  </dl>
  <section aria-labelledby="product-heading">
    <h2 id="product-heading">商品別売上</h2>
    <table class="products" aria-label="商品別の数量と売上">
      <colgroup><col><col><col></colgroup>
      <thead><tr><th scope="col">商品</th><th scope="col" class="number">数量</th><th scope="col" class="number">売上</th></tr></thead>
      <tbody>{''.join(product_rows)}</tbody>
      <tfoot><tr><th scope="row">合計</th><td class="number">{total_quantity:,}</td><td class="number">{yen(total_revenue)}</td></tr></tfoot>
    </table>
  </section>
  <details class="detail-panel">
    <summary>明細{len(rows):,}行を開く</summary>
    <table class="details" aria-label="すべての売上明細">
      <colgroup><col class="date"><col class="product"><col class="quantity"><col class="money"><col class="money"></colgroup>
      <thead><tr><th scope="col">日付</th><th scope="col">商品</th><th scope="col" class="number">数量</th><th scope="col" class="number">単価</th><th scope="col" class="number">小計</th></tr></thead>
      <tbody>{''.join(detail_rows)}</tbody>
    </table>
  </details>
</main>
</body>
</html>
'''


def main():
    # Keep Japanese messages and the yen sign readable on Windows pipes too.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="CSV から日本語の売上レポートを生成します。")
    parser.add_argument("--input", type=Path, default=directory / "sales.csv")
    parser.add_argument("--output", type=Path, default=directory / "report.html")
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        print("エラー: 入力ファイルと出力ファイルは別にしてください。", file=sys.stderr)
        return 1
    try:
        rows = read_sales(args.input)
        report = build_html(rows, args.input.name)
        args.output.write_text(report, encoding="utf-8")
    except ReportError as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1
    except OSError:
        print("エラー: ファイルを読み書きできません。入力と出力の指定を確認してください。", file=sys.stderr)
        return 1
    print("レポートを作成しました。")
    print(f"総売上: {yen(sum(row['revenue'] for row in rows))}")
    print(f"総数量: {sum(row['quantity'] for row in rows):,}")
    print(f"集計した行数: {len(rows):,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
