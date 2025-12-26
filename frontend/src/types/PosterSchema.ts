// frontend/src/types/PosterSchema.ts

// 1. 定义基础图层 (包含 PSD 和 CSS 共用的几何属性)
export interface BaseLayer {
  id: string;          // 用于 React Key，可用 uuid 生成
  type: 'text' | 'image'; 
  name: string;        // 对应 PSD 的图层名 (Layer Panel Name)
  
  // 几何属性 (单位均为 px)
  x: number;           // 前端: left, 后端: left
  y: number;           // 前端: top, 后端: top
  width: number;       // 图片层需要，文本层由字号决定可为 0
  height: number;      
  
  rotation: number;    // 角度 0-360
  opacity: number;     // 透明度 0-1
}

// 2. 文本图层 (针对 ag-psd 优化的结构)
export interface TextLayer extends BaseLayer {
  type: 'text';
  content: string;     // 文本内容
  
  // 样式属性 (扁平化，方便 AI 生成)
  fontSize: number;    // px
  color: string;       // Hex 格式 "#333333" (后端需转 RGB)
  fontFamily: string;  // 关键！后端需注册同名字体 (如 "SimHei")
  textAlign: 'left' | 'center' | 'right'; 
  fontWeight: 'normal' | 'bold';
}

// 3. 图片图层
export interface ImageLayer extends BaseLayer {
  type: 'image';
  src: string;         // URL 或 Base64 (后端需下载转 Buffer)
}

// 4. 联合类型
export type Layer = TextLayer | ImageLayer;

// 5. 整个画布数据
export interface PosterData {
  canvas: {
    width: number;     // 通常 1080
    height: number;    // 通常 1920
    backgroundColor: string; // Hex
  };
  
  // 数组顺序即层级顺序：index 0 在最底下，index length-1 在最顶层
  layers: Layer[]; 
}