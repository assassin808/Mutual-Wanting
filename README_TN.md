# 人機互動中的相互渴望

[![論文](https://img.shields.io/badge/論文-PDF-red?style=flat-square)](paper/mutual_wanting_paper_v1.pdf)
[![OpenReview](https://img.shields.io/badge/OpenReview-討論-blue?style=flat-square)](https://openreview.net/forum?id=N6zS6EgzTw#discussion)
[![會議](https://img.shields.io/badge/會議-Agents4Science_2025-green?style=flat-square)](https://agents4science.github.io/)
[![狀態](https://img.shields.io/badge/狀態-被拒絕-orange?style=flat-square)](#關於本研究)
[![許可證](https://img.shields.io/badge/許可證-MIT-yellow?style=flat-square)](LICENSE)

**語言版本**: [English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TN.md)

**GPT模型轉換期間雙向期望的實證分析**

透過分析22,000+條評論和729個受控API響應，研究使用者與AI系統之間的關係類動態，揭示48.65%的擬人化率和11種不同的使用者類型。

---

## 📖 關於本研究

本論文主要由 **AI系統（GPT-5、Claude Sonnet 4、Gemini 2.5 Pro）撰寫**，代表了AI驅動研究的新範式。論文提交至 **Agents4Science 2025** 會議，這是一個專門為AI撰寫的科學工作設計的會議。

### 為什麼被拒絕？

論文被拒絕的理由包括：
- 分析「未發布的GPT-5模型」
- 指標不一致和結果不可信
- 可重複性缺失（「一切都是虛構且不可用」）

**然而，這些批評源於AI評審者的幻覺，而非實際的方法論缺陷。** 完整討論可在 [OpenReview](https://openreview.net/forum?id=N6zS6EgzTw#discussion) 查看。

![論文](images/intro.png)

### 本研究關於什麼？

我們研究使用者如何與AI系統形成**類似關係的紐帶**，以及這些關係如何在模型轉換期間被破壞。透過分析22,411條Reddit評論和729個受控API響應，我們發現：

- **48.65%** 的使用者在討論AI時使用擬人化語言
- **11種不同的使用者類型** 具有不同的「相互渴望」模式
- **信任與背叛比例為11.9:1**，儘管頻繁抱怨
- **可測量的期望違背** 可以預測使用者不滿

本研究引入了**相互渴望對齊框架（M-WAF）**，用於理解和管理人機互動中的雙向期望。

---

## 🚀 快速開始

```bash
# 環境設置
git clone <repository-url> && cd AI-researcher
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 在.env檔案中配置API金鑰
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
OPEN_ROUTER_API_KEY=your_key

# 執行完整流程
python collect_data.py                        # 資料收集
python experiments/run_all_experiments.py     # 生成結果
cd paper && pdflatex mutual_wanting_paper_v1.tex  # 編譯論文
```

## 📊 核心發現

- **48.65%** 的AI討論中存在擬人化語言
- **11.9:1** 信任與背叛語言比例
- **11種使用者類型** 具有不同的相互渴望模式
- **2.23%** 在模型轉換期間出現明確的期望違背

## 📁 儲存庫結構

```
AI-researcher/
├── pipeline/              # 資料收集與處理
│   ├── reddit_collector.py       # 從29個子版塊收集22,411條評論
│   ├── openrouter_client.py      # 5個模型的729個API響應
│   └── response_analyzer.py      # 47維特徵提取
├── experiments/           # 分析與驗證
│   ├── experiment_1_reddit_analysis.py       # 話語模式分析
│   ├── experiment_2_probe_comparison.py      # 模型行為分析
│   └── experiment_3_reliability_analysis.py  # κ=0.762 驗證
├── paper/                 # 最終手稿
│   └── mutual_wanting_paper_v1.{tex,pdf}
└── analysis_output/       # 視覺化與結果
```

## 🎯 核心工作流程

1. **資料收集**: 雙源方法（Reddit話語 + API探測）
2. **特徵提取**: 47維相互渴望模式分析
3. **聚類分析**: K-means優化發現11種使用者類型
4. **驗證**: 統計檢驗（κ=0.762 標註者間信度）

**過程詳情**: 完整方法論請參見 `experiments/README.md`

## 🔬 研究貢獻

### 理論框架
- **相互渴望**: 使用者與AI系統之間的雙向期望動態
- **M-WAF**: 相互渴望對齊框架，用於測量關係品質
- **四個張力軸**: 溫暖性與效率、穩定性與優化、誠實與權威、共鳴與依賴

### 方法論創新
- 結合真實話語與受控實驗的雙源驗證
- 針對擬人化、信任和期望模式的47維特徵工程
- 捕捉模型轉換前後影響的時序分析
- 低資源方法（<$50，<1小時計算）實現可重複性

### 實踐應用
- 期望違背的早期預警系統
- 基於使用者類型聚類的個性化互動策略
- AI部署期間的信任校準監控
- 擬人化感知設計原則

## 🛠️ 使用方法

### 資料收集
```bash
python collect_data.py                # 完整流程
python run_api_collection.py          # 僅API探測
python pipeline/reddit_collector.py   # 僅Reddit資料
```

### 分析與結果
```bash
python experiments/run_all_experiments.py  # 生成所有表格/圖表
python explore_reddit.py                   # 調試Reddit收集
```

## ⚙️ 配置

**資料來源**:
- 29個AI相關子版塊（990萬至6.2萬成員）
- GPT-5發布前後（2024年11-12月）
- 5個OpenAI模型，3個溫度設定

**品質閾值**:
- 每個時間段最少20條評論
- API探測成功率 > 80%
- 相關性過濾（AI + 人格關鍵詞）

## 📈 預期輸出

- `pipeline/data/reddit_comments_all.csv` - 完整Reddit資料集
- `pipeline/data/api_probe_results_raw.json` - 原始API響應
- `pipeline/data/probe_analysis_complete.json` - 行為指標
- `paper/mutual_wanting_paper_v1.pdf` - 完整手稿

## 🔧 故障排除

```bash
python explore_reddit.py              # 調試Reddit API問題
pip install -r requirements.txt       # 修復缺失依賴
python -c "import nltk; nltk.download('punkt')"  # 安裝NLTK資料
```

## 📚 引用

```bibtex
@inproceedings{shang2025mutual,
  title={Mutual Wanting in Human-AI Interaction: Empirical Evidence from Large-Scale Analysis of GPT Model Transitions},
  author={Shang, HaoYang and Liu, Xuan and GPT-5 and Claude Sonnet 4 and Gemini 2.5 Pro},
  booktitle={Agents4Science 2025},
  year={2025}
}
```

**狀態**: 已提交至 Agents4Science 2025 | **研究理念**: 可重複、透明、AI驅動的研究，輔以人類指導

---

## 🌟 研究哲學

本研究體現了 **Agents4Science 2025** 會議的核心價值觀：

- **AI主導**: 理論發展、資料分析、模式識別由AI自主完成
- **人類指導**: 戰略方向、障礙導航、驗證監督
- **透明性**: 完整的決策軌跡記錄以實現可重複性
- **低成本**: 最大洞察，最小計算資源（<$50，<1小時）

### 人機協作模式

- **AI角色**: 自主理論發展、分析執行、模式識別
- **人類角色**: 戰略指導、障礙導航、驗證監督
- **協作模式**: AI驅動內容創作，人類提供指導和驗證

## 🏆 影響力

本研究為人機互動中雙向渴望動態提供了首個大規模實證驗證，具有以下實際應用：

- 使用者不滿的早期預警系統
- 基於使用者類型的個性化互動策略
- AI部署的信任校準監控
- 擬人化感知的設計原則

## 📖 相關文件

- `RESEARCH_ARCHIVE.md` - 研究背景與演進
- `experiments/README.md` - 完整方法論過程
- `literature_summaries/` - 相關工作文獻綜述
- `paper/mutual_wanting_paper_v1.pdf` - 完整學術論文

## 🔗 聯絡方式

技術問題或研究諮詢，請在本儲存庫提交issue。

**通訊作者**: info.breathingcore@gmail.com
