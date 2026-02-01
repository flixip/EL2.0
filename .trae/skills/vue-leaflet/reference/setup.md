# 环境搭建与基础引入 (Setup & Basic Import)

## 1. 依赖安装
推荐使用 PNPM 进行依赖管理。

```bash
# 安装核心库
pnpm install leaflet
# 如果使用 TypeScript，需安装类型声明
pnpm install @types/leaflet -D
```

## 2. 基础引入
在 Vue 组件中必须引入 Leaflet 的核心 CSS，否则地图瓦片显示会错位。

```typescript
import L from 'leaflet';
import 'leaflet/dist/leaflet.css'; // 必须引入 CSS
```

## 3. 注意事项
- 确保 `leaflet.css` 在全局或组件级被正确加载。
- 如果使用 Vite，确保 `leaflet` 已被正确识别。
