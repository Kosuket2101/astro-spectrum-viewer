# filters/

このディレクトリに filter response curve を置いてください。

## 推奨フォーマット

```csv
# name: My Filter
# wavelength_unit: nm
# color: #2f80ed
wavelength,throughput
400,0.00
410,0.12
420,0.45
...
```

- 2列: `wavelength`, `throughput`
- カンマ、空白、セミコロン区切りに対応
- コメント行は `#` で開始
- `wavelength_unit` は `nm`, `angstrom`, `um` に対応
- `color` は任意。GUIのカラーピッカーからも変更可能
- throughput は通常 0〜1 を推奨
- `.csv`, `.txt`, `.dat` を読み込み対象にします

ファイルを追加して `main` に push すると GitHub Actions が
`filters/index.json` を生成して GitHub Pages に公開します。
