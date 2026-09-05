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

## Quick Start

```bash
uv venv --python 3.10.18 .venv
uv pip install --python .venv/bin/python numpy scipy pytest
uv pip install --python .venv/bin/python --no-deps --editable .

# 直接跑內建的模型快照
.venv/bin/python examples/run_snapshot.py

# 或用 CLI
.venv/bin/hpa-core inspect tests/fixtures/dual_beam_mainline/track_s_rerun_snapshot_model.json
.venv/bin/hpa-core run     tests/fixtures/dual_beam_mainline/track_s_rerun_snapshot_model.json
.venv/bin/hpa-core run     <model.json> --mode dual_beam_robustness --json
```

`examples/run_snapshot.py` 是最短的端到端用法，刻意寫成自足、可直接複製修改。
CLI 做的事完全一樣，只是包裝：**serialization → kernel → presentation**。

輸出範例（內建快照）：

```text
tip deflection main          2195.656 mm
max von Mises main            360.122 MPa
failure index               -0.639878   (<= 0 passes)
spar tube mass full           19.2400 kg
max wire tension              3479.58 N  (utilisation 0.759)
analysis succeeded       True
overall hard feasible    False
hard failures            ['moment_closure']
```

> 內建快照是一個**真實的中間設計狀態**，不是「通過」的設計。
> `overall hard feasible False` 是那份快照的實際狀態，不是程式錯誤。

## 測試

```bash
.venv/bin/python -m pytest        # 27 passed
```

測試套件不需要任何 application 層套件，也不需要外部 solver。它讀
`tests/fixtures/dual_beam_mainline/track_s_rerun_snapshot_model.json` ——
一份由上游 application repo 產生並逐位元驗證過的模型快照。

## 什麼可以進 hpa-core

```text
Core Candidate = Mature ∩ Still Needed ∩ Current/Future Mainline ∩ Worth Stabilizing
```

四個條件必須**同時**成立：

| 條件 | 意思 |
|---|---|
| **Mature** | 已經穩定，不預期隨實驗改動 |
| **Still Needed** | 現在真的有人在用，不是歷史遺留 |
| **Current/Future Mainline** | 在目前或未來的主線上，不是已退役的路線 |
| **Worth Stabilizing** | 值得付出凍結它的代價 |

> **「可重用 / 通用 / 純函式」不足以成為進 hpa-core 的理由。**

外加兩個硬性技術條件：只依賴 NumPy 與 SciPy；不讀 config、不讀檔案、
不認識飛機——呼叫端交進來的是已經建好的資料結構。

### 不在 hpa-core 裡（也不要加進來）

| 東西 | 為什麼在外面 |
|---|---|
| model construction / `builder.py` | 屬於 seam 的 application 側。即使某個 helper 是純 NumPy（例如把安裝預張力換算成未拉伸長度）也一樣 |
| OpenMDAO 與任何最佳化驅動器 | 工作流語意，不是 kernel |
| `HPAConfig` / 任何 config 綱要 | kernel 不讀 config |
| 氣動載荷生成、載荷對應 | 上游 application |
| 材料資料庫 / `MaterialDB` / `data/*.yaml` | 上游 application |
| ANSYS / CalculiX / APDL 驗證與匯出 | 獨立驗證路徑 |
| CFD / meshing（gmsh、SU2、OpenFOAM） | 屬於 `hpa-meshing` |
| aircraft workflow / orchestration | 屬於 `hpa-next` |

核心 seam：

```text
application / builder  →  prepared DualBeamMainlineModel  →  hpa-core kernel
```

## 修改紀律

- 不做 formatting、rename、或「順手修正」。搬進來時保留的既有 lint 訊息是
  刻意留下的，不要清。
- `fem/elements.py` 裡的 `+1e-30`、`np.result_type`、`_cs_norm` 看起來像冗餘
  防禦，實際上是 **complex-step 微分的必要條件**。動它們會無聲破壞
  `check_partials`。
- 任何數值方程式、容差、安全係數的修改都不屬於這個 repo 的日常維護範圍。
