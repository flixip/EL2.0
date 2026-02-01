import { ref, watch } from 'vue';
import { ndviData } from '@/data/sampleData';

/**
 * CSV 数据项接口
 */
export interface CSVDataItem {
  id: string;
  name: string;
  rawText: string;
  headers: string[];
  rows: string[][];
  mapping: {
    nameField: string;
    valueFields: string[];
  };
}

/**
 * TableManager 数据管理器
 * 负责 CSV 解析、列表维护及数据映射逻辑
 */
export default class TableManager {
  private static instance: TableManager | null = null;

  // 已导入的 CSV 列表
  public importedCSVList = ref<CSVDataItem[]>([]);

  // 聚合后的数据 Map<区域名称, 数值数组>
  public dataState = ref<Map<string, number[]>>(new Map());

  // 时间配置范围（由 CSV 数据决定）
  public yearRange = ref(0);

  private constructor() {
    // 监听列表变化，自动更新聚合数据状态
    watch(this.importedCSVList, () => {
      this.aggregateData();
    }, { deep: true });
  }

  public static getInstance(): TableManager {
    if (!TableManager.instance) {
      TableManager.instance = new TableManager();
    }
    return TableManager.instance;
  }

  /**
   * 解析 CSV 文本
   */
  public parseCSV(text: string): { headers: string[]; rows: string[][] } {
    const lines = text.split('\n').filter(l => l.trim());
    if (lines.length === 0) return { headers: [], rows: [] };
    
    const headers = lines[0].split(',').map(h => h.trim());
    const rows = lines.slice(1).map(line => line.split(',').map(v => v.trim()));
    
    return { headers, rows };
  }

  /**
   * 添加 CSV 数据
   */
  public addCSV(name: string, rawText: string): string {
    const { headers, rows } = this.parseCSV(rawText);
    const id = `csv_${Date.now()}`;
    
    this.importedCSVList.value.push({
      id,
      name,
      rawText,
      headers,
      rows,
      mapping: { nameField: '', valueFields: [] }
    });
    
    return id;
  }

  /**
   * 更新 CSV 数据（用于编辑保存）
   */
  public updateCSV(id: string, newText: string): void {
    const index = this.importedCSVList.value.findIndex(item => item.id === id);
    if (index !== -1) {
      const { headers, rows } = this.parseCSV(newText);
      const item = this.importedCSVList.value[index];
      
      this.importedCSVList.value[index] = {
        ...item,
        rawText: newText,
        headers,
        rows
      };
    }
  }

  /**
   * 删除 CSV 数据
   */
  public removeCSV(id: string): void {
    this.importedCSVList.value = this.importedCSVList.value.filter(item => item.id !== id);
  }

  /**
   * 应用映射关系
   */
  public applyMapping(id: string, nameField: string, valueFields: string[]): void {
    const item = this.importedCSVList.value.find(i => i.id === id);
    if (item) {
      item.mapping = { nameField, valueFields };
      this.aggregateData();
    }
  }

  /**
   * 聚合所有已映射的数据
   */
  private aggregateData(): void {
    const newData = new Map<string, number[]>();
    let maxRange = 0;

    this.importedCSVList.value.forEach(item => {
      const { nameField, valueFields } = item.mapping;
      if (!nameField || valueFields.length === 0) return;

      const nameIdx = item.headers.indexOf(nameField);
      const valIdxs = valueFields.map(f => item.headers.indexOf(f));

      item.rows.forEach(row => {
        const name = row[nameIdx];
        const vals = valIdxs.map(idx => parseFloat(row[idx]) || 0);
        
        if (name) {
          newData.set(name, vals);
        }
      });

      maxRange = Math.max(maxRange, valueFields.length);
    });

    this.dataState.value = newData;
    this.yearRange.value = maxRange;
  }

  /**
   * 获取模板数据的原始文本
   */
  public getTemplateCSVText(): string {
    const header = "District,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010";
    const body = ndviData.map(item => `${item.district},${item.data.join(',')}`).join('\n');
    return `${header}\n${body}`;
  }

  /**
   * 加载示例模板
   */
  public loadTemplateData(): string {
    const rawText = this.getTemplateCSVText();
    const id = this.addCSV('示例 NDVI 数据.csv', rawText);
    
    // 自动应用映射
    const valueFields = ["2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010"];
    this.applyMapping(id, "District", valueFields);
    
    return id;
  }
}
