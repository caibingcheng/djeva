# DJEVA — Agent Context

## 项目介绍
DJEVA 是蛋卷基金（Danjuan）指数估值数据的自动备份工具。

- **数据来源**: https://danjuanapp.com/djmodule/value-center
- **更新频率**: 每周一至周五 20:00（北京时间）
- **数据内容**: 多个指数的估值指标（PE、PB、ROE、股息率、预测 PEG 等）

## 数据来源
- API 地址: `https://danjuanapp.com/djapi/index_eva/dj`
- 用户代理: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53`

## 项目结构

```
djeva/
├── main.py              # 数据抓取脚本（入口）
├── requirements.txt     # Python 依赖（pandas, requests）
├── index.html           # 前端数据浏览页面
├── djeva.js             # 自动生成的日期索引（由 main.py 生成）
├── lib/                 # GridManager 前端表格库
│   ├── gridmanager.css
│   └── gridmanager.js
├── source/              # 原始 API 响应数据（JSON）
├── json/                # 提取的 items 列表（JSON）
└── csv/                 # 提取的 items 列表（CSV）
```

## 关键文件说明

- **`main.py`**: 主抓取脚本，执行后：
  1. 从蛋卷 API 获取当日估值数据
  2. 在 `source/` 保存原始响应（`YYYY-MM-DD.json`）
  3. 在 `json/` 保存提取的 items 列表（`YYYY-MM-DD.json`）
  4. 在 `csv/` 保存提取的 items 列表（`YYYY-MM-DD.csv`）
  5. 更新 `djeva.js` 日期索引文件

- **`index.html`**: 前端页面，功能：
  - 年/月/日选择器浏览历史数据
  - GridManager 表格展示估值数据
  - 支持按 PE/PB/ROE 等列排序
  - 指数代码链接到蛋卷详情页

- **`djeva.js`**: 自动生成的 JS 文件，包含所有可用日期的索引，用于前端选择器

## 运行方式

```bash
# 安装依赖
pip install -r requirements.txt

# 手动执行数据抓取
python main.py
```

## CI/CD

- 文件: `.github/workflows/fetch.yml`
- 触发: 每周一至周五 14:00 UTC（北京时间 20:00）
- 行为:
  1. 安装依赖
  2. 运行 `python main.py`
  3. 如有新数据，自动 commit 并 push

## 开发注意事项

1. **不要手动修改 `djeva.js`**: 该文件由 `main.py` 自动生成
2. **数据文件命名**: 所有数据文件使用 `YYYY-MM-DD` 格式
3. **前端无构建工具**: 纯 HTML/CSS/JS，无需 npm/webpack
4. **依赖简单**: 仅需 pandas + requests
5. **数据完整性**: source/ 目录保存了完整的 API 响应，json/ 和 csv/ 仅保存 items 列表

## 技术栈

- **后端**: Python 3, pandas, requests
- **前端**: 原生 HTML/CSS/JavaScript, GridManager.js
- **部署**: GitHub Pages（静态页面）
