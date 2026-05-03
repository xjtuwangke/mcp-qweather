# Weather MCP Server

基于 [FastMCP](https://gofastmcp.com) 框架开发的天气预报MCP服务，集成和风天气API。

## 特性

- **18个工具** - 天气、地理、空气质量、天文等数据查询
- **JWT认证** - Ed25519签名保障安全
- **Docker部署** - 支持IP:Port远程访问(HTTP模式)

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入凭据
```

### 2. 本地运行 (Stdio模式)

```bash
uv sync
uv run python server.py
```

### 3. Docker部署 (HTTP模式)

```bash
# 配置环境变量
export QWEATHER_API_HOST="https://xxx.qweatherapi.com"
export QWEATHER_KEY_ID="your-key-id"
export QWEATHER_PROJECT_ID="your-project-id"

# 运行容器
./docker-run.sh --detach
```

或使用docker-compose:

```bash
cp .env.example .env
# 编辑 .env 填入凭据
docker-compose up -d
```

---

## 工具列表

### Geo Tools (地理查询)

| 工具 | 功能 |
|------|------|
| `city_lookup` | 城市搜索 (名称/坐标/LocationID) |
| `poi_lookup` | POI搜索 (景点/车站/机场) |
| `poi_range` | 周边POI搜索 (指定半径) |

### Weather Tools (天气预报)

| 工具 | 功能 |
|------|------|
| `weather_now` | 实时天气 |
| `weather_daily` | 每日预报 (3d/7d/10d/15d/30d) |
| `weather_hourly` | 逐小时预报 (24h/72h/168h) |
| `grid_weather_now` | 格点实时天气 (3-5km分辨率) |
| `grid_weather_daily` | 格点每日预报 (3d/7d) |
| `grid_weather_hourly` | 格点逐小时预报 (24h/72h) |

### Minutely/Air/Astronomy Tools

| 工具 | 功能 |
|------|------|
| `minutely_precipitation` | 分钟级降水 (未来2小时, 仅中国) |
| `indices_forecast` | 生活指数 (穿衣/洗车/紫外线等16项) |
| `air_now` | 实时空气质量 (按坐标) |
| `air_hourly` | 24小时空气质量预报 |
| `air_daily` | 3天空气质量预报 |
| `air_station` | 监测站空气质量数据 |
| `astronomy_sun` | 日出日落 |
| `astronomy_moon` | 月相月升月落 |
| `solar_elevation_angle` | 太阳高度角/方位角 |

### indices_forecast 指数类型

| ID | 类型 | ID | 类型 |
|----|------|----|------|
| 1 | 运动指数 | 9 | 空调开启指数 |
| 2 | 洗车指数 | 10 | 过敏指数 |
| 3 | 穿衣指数 | 11 | 太阳镜指数 |
| 4 | 感冒指数 | 12 | 化妆指数 |
| 5 | 晨练指数 | 13 | 晾晒指数 |
| 6 | 旅游指数 | 14 | 交通指数 |
| 7 | 紫外线指数 | 15 | 钓鱼指数 |
| 8 | 空气污染扩散指数 | 16 | 防晒指数 |

---

## MCP客户端连接

### 方式1: Stdio本地进程

适用于同一主机上的客户端:

```python
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

async def main():
    transport = PythonStdioTransport("server.py", cwd="/path/to/mcp-weather")
    async with Client(transport) as client:
        result = await client.call_tool("weather_now", {"location": "101010100"})
        print(result.data)

        result = await client.call_tool("city_lookup", {"location": "Beijing", "number": 3})
        print(result.data)

asyncio.run(main())
```

### 方式2: HTTP远程访问

容器默认使用HTTP模式运行，客户端连接:

```python
from fastmcp import Client

async def main():
    client = Client("http://localhost:8000/mcp")
    async with client as c:
        tools = await c.list_tools()
        result = await c.call_tool("weather_now", {"location": "101010100"})
        print(result.data)

asyncio.run(main())
```

> **注意**: 如果使用 `docker-compose.yaml` 部署，主机端口为 **28001**，连接地址应为 `http://localhost:28001/mcp`。

---

## Docker部署详解

### 文件说明

| 文件 | 说明 |
|------|------|
| `Dockerfile` | 容器镜像构建 |
| `docker-compose.yaml` | Compose编排 (主机端口28001) |
| `docker-run.sh` | 快速启动脚本 (主机端口8000) |
| `.dockerignore` | 镜像构建排除 |

### 密钥注入方式

#### 方式1: 文件挂载 (推荐)

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/keys/ed25519-private.pem:/run/secrets/private_key.pem:ro \
  -e QWEATHER_API_HOST=https://xxx.qweatherapi.com \
  -e QWEATHER_KEY_ID=your-key-id \
  -e QWEATHER_PROJECT_ID=your-project-id \
  -e PRIVATE_KEY_PATH=/run/secrets/private_key.pem \
  mcp-weather:latest
```

#### 方式2: docker-compose

```bash
cp .env.example .env
# 编辑 .env 填入凭据
docker-compose up -d
```

### 验证部署

```bash
# 检查容器状态
docker ps | grep mcp-weather

# 查看日志
docker logs -f mcp-weather

# 测试连接 (主机端口8000, docker-compose则用28001)
uv run python -c "
import asyncio
from fastmcp import Client
async def test():
    async with Client('http://localhost:8000/mcp') as c:
        tools = await c.list_tools()
        print(f'Tools: {len(tools)}')
asyncio.run(test())
"
```

---

## 认证方式

使用JWT (Ed25519) 进行身份认证:

1. **生成Ed25519密钥对** (已生成):
   ```bash
   openssl genpkey -algorithm ED25519 -out keys/ed25519-private.pem
   openssl pkey -pubout -in keys/ed25519-private.pem > keys/ed25519-public.pem
   ```

2. **上传公钥** 到[和风天气控制台](https://console.qweather.com/project)创建JWT凭据

3. **配置环境变量**:
   ```
   QWEATHER_API_HOST=https://你的APIHost.qweatherapi.com
   QWEATHER_KEY_ID=你的凭据ID
   QWEATHER_PROJECT_ID=你的项目ID
   PRIVATE_KEY_PATH=./keys/ed25519-private.pem
   ```

---

## 项目结构

```
mcp-weather/
├── apis/
│   ├── __init__.py       # 包导出 (GeoAPI, WeatherAPI, MinutelyAPI)
│   ├── base.py           # QWeatherAPI基类, JWT认证, 输入验证器
│   ├── geo.py            # GeoAPI (城市/POI搜索)
│   ├── weather.py        # WeatherAPI (天气预报)
│   ├── minutely.py       # 分钟级降水/空气质量/天文API
│   └── schemas.py        # Pydantic模型预留
├── keys/
│   ├── ed25519-private.pem   # 私钥 (gitignored)
│   └── ed25519-public.pem    # 公钥
├── tests/
│   └── test_api.py       # 完整测试套件 (~61测试)
├── server.py             # MCP服务器入口 (18个工具)
├── config.py             # pydantic-settings配置管理
├── test_client.py        # 简单MCP客户端示例
├── pyproject.toml        # uv项目配置
├── uv.lock               # 依赖锁文件
├── Dockerfile            # Docker镜像 (HTTP模式)
├── docker-compose.yaml   # Compose编排 (主机端口28001)
├── docker-run.sh         # 快速启动脚本 (主机端口8000)
├── .dockerignore         # 镜像构建排除
├── .env.example          # 环境变量模板
├── .gitignore            # Git忽略规则
├── LICENSE               # MIT开源许可证
├── AGENTS.md             # Agent开发指南
└── README.md             # 项目文档
```

---

## 测试

```bash
uv run python tests/test_api.py
```

---

## 下游API文档

- [GeoAPI](https://dev.qweather.com/docs/api/geoapi/)
- [WeatherAPI](https://dev.qweather.com/docs/api/weather/)
- [Minutely API](https://dev.qweather.com/docs/api/minutely/)
- [Air Quality API](https://dev.qweather.com/docs/api/air-quality/)
- [Astronomy API](https://dev.qweather.com/docs/api/astronomy/)
- [认证文档](https://dev.qweather.com/docs/configuration/authentication/)
