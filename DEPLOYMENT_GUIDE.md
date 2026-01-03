# 🚀 Noon 3C 监控系统 - 指纹浏览器部署指南

> **版本**: 2.0 (Stealth Enhanced)  
> **更新日期**: 2026-01-03  
> **目标**: 绕过 Cloudflare 反爬，实现稳定数据采集

---

## 📋 目录

1. [快速开始](#快速开始)
2. [指纹浏览器配置](#指纹浏览器配置)
3. [代理设置](#代理设置)
4. [常见问题](#常见问题)
5. [生产部署](#生产部署)

---

## 🎯 快速开始

### 方案A：直接使用指纹浏览器版本（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/adasn9979-creator/noon-3c-monitor.git
cd noon-3c-monitor

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装指纹浏览器增强包
pip install undetected-chromedriver==3.5.5
pip install fake-useragent==1.4.0

# 4. 下载 scraper_stealth.py（从项目根目录）
# 文件已包含完整的反检测代码

# 5. 运行测试
python scraper_stealth.py
```

### 方案B：手动改造现有代码

编辑 `scraper.py`，将 `init_driver()` 函数替换为：

```python
import undetected_chromedriver as uc
from fake_useragent import UserAgent

def init_stealth_driver():
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    ua = UserAgent()
    options.add_argument(f'user-agent={ua.random}')
    
    driver = uc.Chrome(options=options, headless=False)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        '''
    })
    
    return driver
```

---

## 🎭 指纹浏览器配置详解

### 核心技术栈

| 组件 | 作用 | 绕过能力 |
|------|------|----------|
| **undetected-chromedriver** | 自动patch WebDriver | 绕过 `navigator.webdriver` 检测 |
| **fake-useragent** | 随机UA生成 | 避免UA黑名单 |
| **CDP命令注入** | JavaScript特征覆盖 | 隐藏自动化标志 |
| **窗口大小随机化** | 设备指纹模拟 | 模拟真实用户 |

### 关键参数说明

```python
# 1. 禁用自动化特征
options.add_argument('--disable-blink-features=AutomationControlled')

# 2. 随机窗口大小（每次运行不同）
window_sizes = [(1920, 1080), (1366, 768), (1440, 900)]
width, height = random.choice(window_sizes)
options.add_argument(f'--window-size={width},{height}')

# 3. 模拟阿联酋地区用户
options.add_argument('--lang=en-US,en;q=0.9,ar;q=0.8')

# 4. WebDriver特征覆盖
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': '''
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
    '''
})
```

---

## 🌐 代理设置

### 何时需要代理？

- ✅ 被 Cloudflare 长期拦截
- ✅ IP 被 Noon 封禁
- ✅ 需要模拟阿联酋本地访问
- ❌ 首次测试可以不用

### 推荐代理服务

#### 1. Bright Data（专业级）

```python
PROXY_SERVER = "http://username:password@brd.superproxy.io:22225"
```

- 价格: $500/月起（企业版）
- 优点: IP池最大，成功率>99%
- 适合: 大规模抓取

#### 2. SmartProxy（性价比）

```python
PROXY_SERVER = "http://user:pass@gate.smartproxy.com:7000"
```

- 价格: $75/月起
- 优点: 住宅IP，中东地区覆盖好
- 适合: 中小规模监控

#### 3. ProxyScrape（免费测试）

```python
PROXY_SERVER = "http://free-proxy.proxyscrape.com:8080"
```

- 价格: 免费（每天100次）
- 优点: 快速测试
- 缺点: 不稳定，仅用于验证

### 代理配置方法

在 `scraper_stealth.py` 中修改：

```python
# 第22行：启用代理
PROXY_ENABLED = True

# 第23行：填入代理地址
PROXY_SERVER = "http://username:password@proxy-server:port"
```

---

## ❓ 常见问题

### Q1: 运行后仍然显示 Access Denied

**解决方案**:

1. 检查 Chrome 版本（必须>= 120）
   ```bash
   google-chrome --version
   ```

2. 清理旧的 ChromeDriver
   ```bash
   rm -rf ~/.wdm/  # Linux/Mac
   ```

3. 尝试非无头模式（观察浏览器行为）
   ```python
   driver = uc.Chrome(options=options, headless=False)  # 改为 False
   ```

### Q2: 安装 undetected-chromedriver 失败

**错误**: `ERROR: Could not find a version that satisfies the requirement`

**解决**: 升级 pip
```bash
pip install --upgrade pip
pip install undetected-chromedriver==3.5.5
```

### Q3: 数据抓取成功但都是空值

**原因**: Noon 网站结构更新，CSS选择器失效

**调试步骤**:

1. 检查保存的 `debug_*.html` 文件
2. 在Chrome开发者工具中查看最新的 `data-qa` 属性
3. 更新 `scraper_stealth.py` 中的选择器

### Q4: 销量数据还是假的怎么办？

**当前限制**: Noon 前端不显示精确销量

**改进方案**:

**方法1**: 抓取 Best Sellers 排名
```python
url = 'https://www.noon.com/uae-en/mobiles/?sort=popularity'
# 通过排名推算销量区间
```

**方法2**: 监控评论数变化
```python
reviews_count = card.find('[data-qa="product-reviews"]').text
# 公式: 估算销量 ≈ 评论数 × 50
```

**方法3**: 接入 Noon Partner API（需卖家账号）

---

## 🏭 生产部署

### 1. 定时任务（Linux）

```bash
# 编辑 crontab
crontab -e

# 每天早9点和下午3点运行
0 9,15 * * * cd /path/to/noon-3c-monitor && python scraper_stealth.py >> logs/cron.log 2>&1
```

### 2. 后台运行（nohup）

```bash
nohup python scraper_stealth.py > output.log 2>&1 &
```

### 3. Docker 部署

```dockerfile
FROM python:3.10-slim

# 安装 Chrome
RUN apt-get update && apt-get install -y \
    wget gnupg2 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install undetected-chromedriver fake-useragent

COPY . .
CMD ["python", "scraper_stealth.py"]
```

构建运行:
```bash
docker build -t noon-monitor .
docker run -v $(pwd)/data:/app/data noon-monitor
```

### 4. 云服务器推荐

| 服务商 | 配置 | 价格 | 适用场景 |
|--------|------|------|----------|
| **阿里云** | 2核4G | ¥80/月 | 国内访问，需配代理 |
| **AWS EC2** | t3.medium | $30/月 | 全球节点，灵活 |
| **Vultr** | 2核4G (迪拜) | $18/月 | 距离UAE近，延迟低 |

---

## 📊 性能优化建议

### 1. 并发抓取（谨慎使用）

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(scrape_noon_category, driver, name, url) 
               for name, url in NOON_CATEGORIES.items()]
```

⚠️ **风险**: 并发过高容易触发封禁

### 2. 数据库存储（推荐）

```python
import sqlite3

conn = sqlite3.connect('noon_monitor.db')
df.to_sql('products', conn, if_exists='append', index=False)
```

### 3. 增量抓取

只抓取价格/库存变化的商品，减少请求量

---

## 🛡️ 法律与道德声明

1. **遵守 robots.txt**: 本工具仅用于公开数据采集
2. **合理频率**: 默认延迟3-6秒，避免对服务器造成压力
3. **商业使用**: 建议联系Noon官方获取API授权
4. **数据隐私**: 不抓取用户个人信息

---

## 📞 技术支持

遇到问题？

1. 查看 [Issues](https://github.com/adasn9979-creator/noon-3c-monitor/issues)
2. 提交详细的错误日志和 `debug_*.html` 文件
3. 说明你的运行环境（OS、Python版本、Chrome版本）

---

**最后更新**: 2026-01-03 | **维护者**: @adasn9979-creator
