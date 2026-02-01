# 插件引入策略 (Plugin Strategies)

Leaflet 插件种类繁多，根据其打包方式，推荐以下两种引入策略。

## 策略 A: 本地 ES Module 导入 (推荐)
适用于现代、有 NPM 包维护的插件。

```typescript
// 1. 安装：npm install leaflet-draw
// 2. 引入逻辑：
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';
```

## 策略 B: 动态脚本加载 (Legacy/CDN)
适用于无 NPM 包的老旧插件，或需要根据业务逻辑按需远程加载的场景。

```typescript
/**
 * 动态加载远程 Leaflet 插件
 * @param url js文件地址
 * @param cssUrl css文件地址 (可选)
 */
const loadExtension = (url: string, cssUrl?: string): Promise<boolean> => {
  return new Promise((resolve, reject) => {
    // 加载 CSS
    if (cssUrl) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = cssUrl;
      document.head.appendChild(link);
    }
    
    // 加载 JS
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
    script.onload = () => resolve(true);
    script.onerror = () => reject(new Error(`Load failed: ${url}`));
    document.body.appendChild(script);
  });
};
```
