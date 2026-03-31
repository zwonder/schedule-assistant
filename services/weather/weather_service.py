"""
天气预报微服务
- 使用 Open-Meteo (免费/无Key) + Nominatim 地理编码
- 查询当前及未来天气
- 根据天气给出穿衣建议
- 提醒是否携带雨具
"""
import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.base_service import BaseService
from core.config_loader import config


# WMO 天气码 → 中文描述 & 图标
WMO_CODE_MAP = {
    0:  ("晴天",       "☀️"),
    1:  ("基本晴朗",   "🌤️"),
    2:  ("局部多云",   "⛅"),
    3:  ("阴天",       "☁️"),
    45: ("有雾",       "🌫️"),
    48: ("冻雾",       "🌫️"),
    51: ("轻度毛毛雨", "🌦️"),
    53: ("中度毛毛雨", "🌦️"),
    55: ("重度毛毛雨", "🌧️"),
    61: ("小雨",       "🌧️"),
    63: ("中雨",       "🌧️"),
    65: ("大雨",       "🌧️"),
    71: ("小雪",       "❄️"),
    73: ("中雪",       "🌨️"),
    75: ("大雪",       "🌨️"),
    77: ("雪粒",       "❄️"),
    80: ("阵雨",       "🌦️"),
    81: ("中度阵雨",   "🌧️"),
    82: ("强阵雨",     "⛈️"),
    85: ("阵雪",       "🌨️"),
    86: ("强阵雪",     "❄️"),
    95: ("雷暴",       "⛈️"),
    96: ("雷暴伴小冰雹","⛈️"),
    99: ("雷暴伴大冰雹","⛈️"),
}


def wmo_desc(code: int) -> Tuple[str, str]:
    """返回 (中文描述, 图标)"""
    return WMO_CODE_MAP.get(code, ("未知天气", "🌡️"))


class WeatherService(BaseService):
    """天气预报服务（Open-Meteo + Nominatim，完全免费无需注册）"""

    GEO_API  = "https://geocoding-api.open-meteo.com/v1/search"
    WEA_API  = "https://api.open-meteo.com/v1/forecast"
    HEADERS  = {"User-Agent": "curl/7.68.0"}

    def __init__(self):
        super().__init__(name="weather", version="2.0.0")
        self.city: str = config.get("weather.city", "Beijing")
        self._geo_cache: Optional[Dict] = None   # 缓存地理信息
        self._last_data: Optional[Dict] = None

    def start(self) -> bool:
        self._running = True
        print(f"[WeatherService] 天气服务已启动，城市: {self.city}")
        return True

    def stop(self) -> bool:
        self._running = False
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "running": self._running,
            "city": self.city,
            "last_query": self._last_data is not None,
        }

    # ------------------------------------------------------------------ #
    #  城市设置
    # ------------------------------------------------------------------ #
    def set_city(self, city: str) -> None:
        self.city = city
        self._geo_cache = None   # 清空地理缓存，强制重新查找
        config.set("weather.city", city)
        print(f"[WeatherService] 城市已更新为: {city}")

    # ------------------------------------------------------------------ #
    #  地理编码：城市名 → 经纬度
    # ------------------------------------------------------------------ #
    def _geocode(self, city: str) -> Optional[Dict]:
        """使用 Open-Meteo Geocoding API 将城市名转为经纬度"""
        if self._geo_cache and self._geo_cache.get("query") == city:
            return self._geo_cache
        params = urllib.parse.urlencode({
            "name": city, "count": 1, "language": "zh", "format": "json"
        })
        url = f"{self.GEO_API}?{params}"
        try:
            req = urllib.request.Request(url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                if not results:
                    print(f"[WeatherService] 未找到城市: {city}")
                    return None
                r = results[0]
                geo = {
                    "query":     city,
                    "name":      r.get("name", city),
                    "country":   r.get("country", ""),
                    "admin1":    r.get("admin1", ""),
                    "latitude":  r["latitude"],
                    "longitude": r["longitude"],
                    "timezone":  r.get("timezone", "Asia/Shanghai"),
                }
                self._geo_cache = geo
                return geo
        except Exception as e:
            print(f"[WeatherService] 地理编码失败: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  获取天气
    # ------------------------------------------------------------------ #
    def fetch_weather(self) -> Optional[Dict]:
        """获取天气数据，返回结构化 dict"""
        geo = self._geocode(self.city)
        if not geo:
            return None

        params = urllib.parse.urlencode({
            "latitude":   geo["latitude"],
            "longitude":  geo["longitude"],
            "timezone":   geo["timezone"],
            "forecast_days": 3,
            "current": ",".join([
                "temperature_2m", "relative_humidity_2m",
                "apparent_temperature", "weather_code",
                "wind_speed_10m", "uv_index", "visibility",
            ]),
            "daily": ",".join([
                "temperature_2m_max", "temperature_2m_min",
                "apparent_temperature_max", "apparent_temperature_min",
                "precipitation_probability_max", "weather_code",
                "wind_speed_10m_max",
            ]),
        })
        url = f"{self.WEA_API}?{params}"
        try:
            req = urllib.request.Request(url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
                result = self._parse_response(raw, geo)
                self._last_data = result
                return result
        except Exception as e:
            print(f"[WeatherService] 天气请求失败: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  解析 Open-Meteo 响应
    # ------------------------------------------------------------------ #
    def _parse_response(self, raw: Dict, geo: Dict) -> Dict:
        cur_raw = raw.get("current", {})
        daily   = raw.get("daily", {})

        # 当前天气
        wcode = cur_raw.get("weather_code", 0)
        desc, icon = wmo_desc(wcode)
        current = {
            "temp":        round(cur_raw.get("temperature_2m", 0), 1),
            "feels_like":  round(cur_raw.get("apparent_temperature", 0), 1),
            "humidity":    cur_raw.get("relative_humidity_2m", 0),
            "wind_speed":  round(cur_raw.get("wind_speed_10m", 0), 1),
            "uv_index":    cur_raw.get("uv_index", 0),
            "visibility":  cur_raw.get("visibility", 0),
            "weather_code": wcode,
            "desc":        desc,
            "icon":        icon,
        }

        # 逐日预报
        times    = daily.get("time", [])
        max_t    = daily.get("temperature_2m_max", [])
        min_t    = daily.get("temperature_2m_min", [])
        feels_max= daily.get("apparent_temperature_max", [])
        feels_min= daily.get("apparent_temperature_min", [])
        rain_pct = daily.get("precipitation_probability_max", [])
        wcodes   = daily.get("weather_code", [])
        wind_max = daily.get("wind_speed_10m_max", [])

        forecasts = []
        day_labels = ["今天", "明天", "后天"]
        for i in range(min(3, len(times))):
            wc = wcodes[i] if i < len(wcodes) else 0
            d_desc, d_icon = wmo_desc(wc)
            day = {
                "label":       day_labels[i] if i < len(day_labels) else f"第{i+1}天",
                "date":        times[i],
                "max_temp":    round(max_t[i], 1) if i < len(max_t) else 0,
                "min_temp":    round(min_t[i], 1) if i < len(min_t) else 0,
                "feels_max":   round(feels_max[i], 1) if i < len(feels_max) else 0,
                "feels_min":   round(feels_min[i], 1) if i < len(feels_min) else 0,
                "rain_chance": rain_pct[i] if i < len(rain_pct) else 0,
                "wind_speed":  round(wind_max[i], 1) if i < len(wind_max) else 0,
                "weather_code": wc,
                "desc":        d_desc,
                "icon":        d_icon,
            }
            day["clothing_advice"] = self._clothing_advice(day)
            day["umbrella_advice"] = self._umbrella_advice(day)
            forecasts.append(day)

        return {
            "geo":        geo,
            "area":       geo["name"],
            "country":    geo["country"],
            "city":       self.city,
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "current":    current,
            "forecasts":  forecasts,
        }

    # ------------------------------------------------------------------ #
    #  穿衣 & 雨具建议
    # ------------------------------------------------------------------ #
    @staticmethod
    def _clothing_advice(day: Dict) -> List[str]:
        advice = []
        feels_min = day["feels_min"]
        feels_max = day["feels_max"]
        wind      = day["wind_speed"]

        if feels_min < 0:
            advice.append("❄️ 体感气温零度以下，请穿厚羽绒服、保暖内衣，注意防冻")
        elif feels_min < 5:
            advice.append("🧥 体感较寒冷，建议穿羽绒服或厚外套，做好保暖")
        elif feels_min < 10:
            advice.append("🧣 早晚偏凉，建议穿毛衣+外套，可备围巾手套")
        elif feels_min < 15:
            advice.append("🧤 天气凉爽，建议穿薄外套或夹克")
        elif feels_max < 25:
            advice.append("👕 气温舒适，穿长袖或薄外套即可")
        elif feels_max < 30:
            advice.append("👗 天气温暖，穿短袖或轻薄衣物")
        else:
            advice.append("🌞 天气炎热，建议穿透气短袖，注意防晒补水")

        if (feels_max - feels_min) >= 10:
            advice.append("🌡️ 今日温差较大，建议带一件外套备用")
        if wind >= 40:
            advice.append("💨 风力较大，外出注意防风，避免骑行")
        elif wind >= 20:
            advice.append("🌬️ 有风，建议穿防风外套")
        return advice

    @staticmethod
    def _umbrella_advice(day: Dict) -> Optional[str]:
        rain = day.get("rain_chance", 0)
        code = day.get("weather_code", 0)
        # 雪
        if code in (71, 73, 75, 77, 85, 86):
            return f"❄️ 预计有降雪，建议携带雨伞，穿防滑鞋"
        if rain >= 70:
            return f"☔ 降雨概率 {rain}%，强烈建议携带雨伞"
        elif rain >= 40:
            return f"🌂 降雨概率 {rain}%，建议携带折叠伞"
        elif rain >= 20:
            return f"⛅ 有小雨可能（{rain}%），可备一把折叠伞"
        return None

    # ------------------------------------------------------------------ #
    #  公开报告接口（兼容旧 main.py 调用）
    # ------------------------------------------------------------------ #
    def get_tomorrow_brief(self) -> str:
        data = self.fetch_weather()
        if not data or len(data.get("forecasts", [])) < 2:
            return "天气数据获取失败"
        day = data["forecasts"][1]
        parts = [f"明日气温 {day['min_temp']}~{day['max_temp']}°C，{day['desc']}"]
        clothing = day.get("clothing_advice", [])
        if clothing:
            parts.append(clothing[0])
        umbrella = day.get("umbrella_advice")
        if umbrella:
            parts.append(umbrella)
        return "；".join(parts)
