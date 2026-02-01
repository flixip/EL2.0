---
name: vue-element-plus
description: Provides guidance and documentation links for Element Plus components. Invoke when needing standard UI components like forms, checkboxes, or tables. Prioritize Element Plus over custom components.
---

# Vue Element Plus Component Guide

This skill guides the selection and implementation of Element Plus components. **Priority: Always check if Element Plus provides a component before building a custom one.**

## Usage Workflow

1.  **Identify Category**: Determine which category the required UI element belongs to (e.g., Form, Data, Feedback).
2.  **Check Experience**: **CRITICAL**: Before requesting the official website, check the `.trae/skills/vue-element-plus/experience/` directory for existing records of the component.
3.  **Locate Component**: If no record exists, use the [Component Index](#component-index) to find the official URL.
4.  **Consult Documentation**: Request/visit the URL to find available props, events, and slots.
5.  **Reference & Record**:
    *   Use the official example code as the primary reference.
    *   **SAVE** the reference code and usage notes into a new file in `.trae/skills/vue-element-plus/experience/<component-slug>.md`.
6.  **Implement**: Write the component code following Element Plus standards.

## Component Index

Base URL: `https://element-plus.org/en-US/component/`

### **Basic (基础组件)**
- [Button 按钮](button)
- [Border 边框](border)
- [Color 色彩](color)
- [Container 布局容器](container)
- [Icon 图标](icon)
- [Layout 布局](layout)
- [Link 链接](link)
- [Scrollbar 滚动条](scrollbar)
- [Space 间距](space)
- [Typography 字体](typography)

### **Configuration (配置组件)**
- [Config Provider 配置组件](config-provider)

### **Form (表单组件)**
- [Autocomplete 自动完成](autocomplete)
- [Cascader 级联选择器](cascader)
- [Checkbox 多选框](checkbox)
- [Color Picker 取色器](color-picker)
- [Date Picker 日期选择器](date-picker)
- [DateTime Picker 日期时间选择器](datetime-picker)
- [Form 表单](form)
- [Input 输入框](input)
- [Input Number 数字输入框](input-number)
- [Radio 单选框](radio)
- [Rate 评分](rate)
- [Select 选择器](select)
- [Select V2 虚拟列表选择器](select-v2)
- [Slider 滑块](slider)
- [Switch 开关](switch)
- [Time Picker 时间选择器](time-picker)
- [Time Select 时间选择](time-select)
- [Transfer 穿梭框](transfer)
- [Upload 上传](upload)
- [Segmented 分段控制器](segmented)

### **Data (数据展示)**
- [Avatar 头像](avatar)
- [Badge 徽章](badge)
- [Calendar 日历](calendar)
- [Card 卡片](card)
- [Carousel 走马灯](carousel)
- [Check Tag 复选标签](check-tag)
- [Collapse 折叠面板](collapse)
- [Descriptions 描述列表](descriptions)
- [Empty 空状态](empty)
- [Image 图片](image)
- [Infinite Scroll 无限滚动](infinite-scroll)
- [Pagination 分页](pagination)
- [Progress 进度条](progress)
- [Result 结果](result)
- [Skeleton 骨架屏](skeleton)
- [Table 表格](table)
- [Table V2 虚拟列表表格](table-v2)
- [Tag 标签](tag)
- [Timeline 时间线](timeline)
- [Tour 漫游导览](tour)
- [Tree 树形控件](tree)
- [Tree Select 树形选择](tree-select)
- [Tree V2 虚拟列表树](tree-v2)
- [Statistic 统计数值](statistic)

### **Navigation (导航组件)**
- [Affix 固钉](affix)
- [Backtop 回到顶部](backtop)
- [Breadcrumb 面包屑](breadcrumb)
- [Dropdown 下拉菜单](dropdown)
- [Menu 菜单](menu)
- [Page Header 页头](page-header)
- [Steps 步骤条](steps)
- [Tabs 标签页](tabs)
- [Anchor 锚点](anchor)

### **Feedback (反馈组件)**
- [Alert 提示](alert)
- [Dialog 对话框](dialog)
- [Drawer 抽屉](drawer)
- [Loading 加载](loading)
- [Message 消息提示](message)
- [Message Box 弹框](message-box)
- [Notification 通知](notification)
- [Popconfirm 气泡确认框](popconfirm)
- [Popover 气泡卡片](popover)
- [Tooltip 文字提示](tooltip)

### **Others (其他)**
- [Divider 分割线](divider)
- [Watermark 水印](watermark)

## Implementation Rules

- **Experience First**: Always check existing records in the `experience` folder to avoid redundant network requests.
- **Reference First**: If no record exists, fetch from the official "Show Code" examples and create a new experience record immediately.
- **Avoid Reinventing**: If the feature exists in Element Plus, use it instead of custom implementation.
- **Style Independence**: Use native E+ props and styles; do not force Tailwind CSS unless necessary for external layout.