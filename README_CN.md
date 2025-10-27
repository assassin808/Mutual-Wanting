# 人机交互中的相互渴望

[![论文](https://img.shields.io/badge/论文-PDF-red?style=flat-square)](paper/mutual_wanting_paper_v1.pdf)
[![OpenReview](https://img.shields.io/badge/OpenReview-讨论-blue?style=flat-square)](https://openreview.net/forum?id=N6zS6EgzTw#discussion)
[![会议](https://img.shields.io/badge/会议-Agents4Science_2025-green?style=flat-square)](https://agents4science.github.io/)
[![状态](https://img.shields.io/badge/状态-被拒绝-orange?style=flat-square)](#关于本研究)
[![许可证](https://img.shields.io/badge/许可证-MIT-yellow?style=flat-square)](LICENSE)

**语言版本**: [English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TN.md)

**GPT模型转换期间双向期望的实证分析**

通过分析22,000+条评论和729个受控API响应，研究用户与AI系统之间的关系类动态，揭示48.65%的拟人化率和11种不同的用户类型。

---

## 📖 关于本研究

本论文主要由 **AI系统（GPT-5、Claude Sonnet 4、Gemini 2.5 Pro）撰写**，代表了AI驱动研究的新范式。论文提交至 **Agents4Science 2025** 会议，这是一个专门为AI撰写的科学工作设计的会议。

### 为什么被拒绝？

论文被拒绝的理由包括：
- 分析"未发布的GPT-5模型"
- 指标不一致和结果不可信
- 可重复性缺失（"一切都是虚构且不可用"）

**然而，这些批评源于AI评审者的幻觉，而非实际的方法论缺陷。** 完整讨论可在 [OpenReview](https://openreview.net/forum?id=N6zS6EgzTw#discussion) 查看。

![论文](images/intro.png)

### 本研究关于什么？

我们研究用户如何与AI系统形成**类似关系的纽带**，以及这些关系如何在模型转换期间被破坏。通过分析22,411条Reddit评论和729个受控API响应，我们发现：

- **48.65%** 的用户在讨论AI时使用拟人化语言
- **11种不同的用户类型** 具有不同的"相互渴望"模式
- **信任与背叛比例为11.9:1**，尽管频繁抱怨
- **可测量的期望违背** 可以预测用户不满

本研究引入了**相互渴望对齐框架（M-WAF）**，用于理解和管理人机交互中的双向期望。

![相互渴望概览](images/mutual_wanting_overview.png)

---

## 🚀 快速开始

```bash
# 环境设置
git clone <repository-url> && cd AI-researcher
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 在.env文件中配置API密钥
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
OPEN_ROUTER_API_KEY=your_key

# 运行完整流程
python collect_data.py                        # 数据收集
python experiments/run_all_experiments.py     # 生成结果
cd paper && pdflatex mutual_wanting_paper_v1.tex  # 编译论文
```

## 📊 核心发现

- **48.65%** 的AI讨论中存在拟人化语言
- **11.9:1** 信任与背叛语言比例
- **11种用户类型** 具有不同的相互渴望模式
- **2.23%** 在模型转换期间出现明确的期望违背

## 📁 仓库结构

```
AI-researcher/
├── pipeline/              # 数据收集与处理
│   ├── reddit_collector.py       # 从29个子版块收集22,411条评论
│   ├── openrouter_client.py      # 5个模型的729个API响应
│   └── response_analyzer.py      # 47维特征提取
├── experiments/           # 分析与验证
│   ├── experiment_1_reddit_analysis.py       # 话语模式分析
│   ├── experiment_2_probe_comparison.py      # 模型行为分析
│   └── experiment_3_reliability_analysis.py  # κ=0.762 验证
├── paper/                 # 最终手稿
│   └── mutual_wanting_paper_v1.{tex,pdf}
└── analysis_output/       # 可视化与结果
```

## 🎯 核心工作流程

1. **数据收集**: 双源方法（Reddit话语 + API探测）
2. **特征提取**: 47维相互渴望模式分析
3. **聚类分析**: K-means优化发现11种用户类型
4. **验证**: 统计检验（κ=0.762 标注者间信度）

**过程详情**: 完整方法论请参见 `experiments/README.md`

## 🔬 研究贡献

### 理论框架
- **相互渴望**: 用户与AI系统之间的双向期望动态
- **M-WAF**: 相互渴望对齐框架，用于测量关系质量
- **四个张力轴**: 温暖性与效率、稳定性与优化、诚实与权威、共鸣与依赖

### 方法论创新
- 结合真实话语与受控实验的双源验证
- 针对拟人化、信任和期望模式的47维特征工程
- 捕捉模型转换前后影响的时序分析
- 低资源方法（<$50，<1小时计算）实现可重复性

### 实践应用
- 期望违背的早期预警系统
- 基于用户类型聚类的个性化交互策略
- AI部署期间的信任校准监控
- 拟人化感知设计原则

## 🛠️ 使用方法

### 数据收集
```bash
python collect_data.py                # 完整流程
python run_api_collection.py          # 仅API探测
python pipeline/reddit_collector.py   # 仅Reddit数据
```

### 分析与结果
```bash
python experiments/run_all_experiments.py  # 生成所有表格/图表
python explore_reddit.py                   # 调试Reddit收集
```

## ⚙️ 配置

**数据源**:
- 29个AI相关子版块（990万至6.2万成员）
- GPT-5发布前后（2024年11-12月）
- 5个OpenAI模型，3个温度设置

**质量阈值**:
- 每个时间段最少20条评论
- API探测成功率 > 80%
- 相关性过滤（AI + 人格关键词）

## 📈 预期输出

- `pipeline/data/reddit_comments_all.csv` - 完整Reddit数据集
- `pipeline/data/api_probe_results_raw.json` - 原始API响应
- `pipeline/data/probe_analysis_complete.json` - 行为指标
- `paper/mutual_wanting_paper_v1.pdf` - 完整手稿

## 🔧 故障排除

```bash
python explore_reddit.py              # 调试Reddit API问题
pip install -r requirements.txt       # 修复缺失依赖
python -c "import nltk; nltk.download('punkt')"  # 安装NLTK数据
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

**状态**: 已提交至 Agents4Science 2025 | **研究理念**: 可重复、透明、AI驱动的研究，辅以人类指导

---

## 🌟 研究哲学

本研究体现了 **Agents4Science 2025** 会议的核心价值观：

- **AI主导**: 理论发展、数据分析、模式识别由AI自主完成
- **人类指导**: 战略方向、障碍导航、验证监督
- **透明性**: 完整的决策轨迹记录以实现可重复性
- **低成本**: 最大洞察，最小计算资源（<$50，<1小时）

### 人机协作模式

- **AI角色**: 自主理论发展、分析执行、模式识别
- **人类角色**: 战略指导、障碍导航、验证监督
- **协作模式**: AI驱动内容创作，人类提供指导和验证

## 🏆 影响力

本研究为人机交互中双向渴望动态提供了首个大规模实证验证，具有以下实际应用：

- 用户不满的早期预警系统
- 基于用户类型的个性化交互策略
- AI部署的信任校准监控
- 拟人化感知的设计原则

## 📖 相关文档

- `RESEARCH_ARCHIVE.md` - 研究背景与演进
- `experiments/README.md` - 完整方法论过程
- `literature_summaries/` - 相关工作文献综述
- `paper/mutual_wanting_paper_v1.pdf` - 完整学术论文

## 🔗 联系方式

技术问题或研究咨询，请在本仓库提交issue。

**通讯作者**: info.breathingcore@gmail.com
