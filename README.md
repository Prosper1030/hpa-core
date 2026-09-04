# hpa-core

人力飛機雙梁結構分析核心（trusted computational kernel）。

這個 repo 只放**成熟到不應該再被實驗性開發隨手修改**的計算核心。它的外部依賴
只有 NumPy 與 SciPy，不讀 config、不讀檔案、不認識飛機定義；呼叫端必須自己
準備好一個 `DualBeamMainlineModel` 再交進來。

## 邊界

```text
application / builder  →  prepared DualBeamMainlineModel  →  hpa-core kernel
```

模型的建構（config、材料資料庫、氣動載荷、幾何組裝）屬於上游 application
層，**不在這個 repo 裡**。即使某個 helper 本身是純 NumPy，只要它屬於 model
construction，就留在 application 側，不為了測試方便而擴張 core 邊界。

## 內容

| 模組 | 用途 |
|---|---|
| `hpa_core.constants` | `G_STANDARD` |
| `hpa_core.fem.elements` | Timoshenko 梁勁度、旋轉矩陣、12x12 轉換、complex-step 範數 |
| `hpa_core.dual_beam_mainline.types` | kernel 的資料型別與分析模式定義 |
| `hpa_core.dual_beam_mainline.rib_link` | 主梁/後梁連結列的組裝 |
| `hpa_core.dual_beam_mainline.constraints` | 約束組裝（根部、鋼索、連結） |
| `hpa_core.dual_beam_mainline.load_split` | 載荷分配與扭矩參考轉換 |
| `hpa_core.dual_beam_mainline.solver` | 雙梁狀態求解 |
| `hpa_core.dual_beam_mainline.recovery` | 反力與結構響應回復 |
| `hpa_core.dual_beam_mainline.smooth` | 平滑聚合 |
| `hpa_core.dual_beam_mainline.optimizer_view` | 最佳化器面向的指標與可行性摘要 |
| `hpa_core.dual_beam_mainline.kernel` | 公開入口 `run_dual_beam_mainline_kernel()` |
| `hpa_core.dual_beam_mainline.serialization` | 模型的無損 JSON 序列化 |

## 安裝與測試

```bash
uv venv --python 3.10.18 .venv
uv pip install --python .venv/bin/python numpy scipy pytest
uv pip install --python .venv/bin/python --no-deps --editable .
.venv/bin/python -m pytest
```

測試套件不需要任何 application 層套件，也不需要外部 solver。它讀
`tests/fixtures/dual_beam_mainline/track_s_rerun_snapshot_model.json` ——
一份由上游 application repo 產生並逐位元驗證過的模型快照。

## 修改紀律

- 不做 formatting、rename、或「順手修正」。搬進來時保留的既有 lint 訊息是
  刻意留下的，不要清。
- `fem/elements.py` 裡的 `+1e-30`、`np.result_type`、`_cs_norm` 看起來像冗餘
  防禦，實際上是 **complex-step 微分的必要條件**。動它們會無聲破壞
  `check_partials`。
- 任何數值方程式、容差、安全係數的修改都不屬於這個 repo 的日常維護範圍。
