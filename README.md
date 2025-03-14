# gophish_2development

## 项目简介
**gophish_2development** 是基于 [Gophish](https://getgophish.com/) 为基础，新增部分自定义功能的钓鱼渗透测试平台，旨在增强 Gophish 的功能，使其更加适用于初学者和初级安全工程师。当然，该项目扩展了 Gophish 的功能，包括任务调度、数据可视化以及报告生（这里结合了[goreport](https://github.com/chrismaddalena/GoReport)项目）成等。

---
# 效果图

![图片出错了，请上传正确的图片！](./img/1.png "配置campaign，定时执行；显示campaign的执行情况；显示campaign的统计数据")

![图片出错了，请上传正确的图片！](./img/2.png "查看所有数据的图表")

## 功能介绍（开发中 🚀）
### ✅ 已实现功能：
1. **新增界面**
   - 配置 Campaign 任务，并支持定时执行。
   - 查看 Campaign 执行状态及统计数据。
   
2. **数据可视化**
   - 提供交互式数据可视化界面，展示所有数据的图表。
   
3. **报告生成**
   - 通过 Web 界面生成报告，目前支持 **Excel**、**Word** 以及 **Quick** 格式。
   - 计划增加 PDF 格式支持（开发中）。
   
---

## 安装与运行
### 1. 环境依赖
- Python 3.11+
- Flask
- MySQL
- Gophish
- 其他依赖可通过 `requirements.txt` 安装

### 2. 安装步骤
```bash
# 克隆项目
git clone https://github.com/your-repo/gophish_2development.git
cd gophish_2development

# 安装 Python 依赖
pip install -r requirements.txt

# 启动 Flask 服务器
python app.py
```

### 3. 配置 Gophish
确保你的 Gophish 服务已启动，并在 `gophish.config` 中正确配置 API Key 及服务器地址。

```json
{
  "gophish_url": "https://your-gophish-server:8891/",
  "api_key": "your-api-key"
}
```

### 4. 配置 app.py
请修改主程序中的域名+端口信息；
请修改API key，填写自己的key；

```python
# 配置 API 相关信息
API_KEY = "bd870f3e5dd55d951b0da09957d017ba"  # 你的 Gophish API 密钥
GOPHISH_URL = "https://122.21.95.27:3333/api/campaigns/"
```
---

## 可能遇到的问题及解决方案
### 1. **报告生成后无法下载**
- **原因**：文件路径可能不匹配。
- **解决方案**：
  1. 确保 `os.path.exists(report_file_name)` 正确。
  2. 使用 `ls -b` 确认文件名是否带有转义字符。
  3. 修改 `send_file` 代码，确保正确引用文件路径。

### 2. **Flask 服务器访问 500 错误**
- **原因**：缺少必要参数或 API Key 失效。
- **解决方案**：
  1. 确保请求参数完整。
  2. 检查 `gophish.config` 中的 API Key 是否正确。

---

## 未来计划
- [ ] **完善 UI 交互体验**
- [ ] **增加 PDF 格式报告支持**
- [ ] **增强数据可视化功能**
- [ ] **优化 Gophish API 交互方式**

---

## 贡献指南
欢迎任何形式的贡献，包括代码提交、Bug 反馈、功能建议等！

1. Fork 本项目。
2. 创建你的分支（`git checkout -b feature-xxx`）。
3. 提交你的修改（`git commit -m '添加新功能'`）。
4. 推送到远程分支（`git push origin feature-xxx`）。
5. 提交 Pull Request。

---

## 许可证
本项目基于 **Apache License** 许可证开源。

---

## 联系方式
- **wx**：tomorrow_me-

## 可作为毕业设计-基于Gophish的钓鱼渗透测试平台
