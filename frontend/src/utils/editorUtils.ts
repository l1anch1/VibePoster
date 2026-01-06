/**
 * 编辑器工具函数
 * 
 * 提供编辑器所需的各种工具函数
 */

import type { Layer, PosterData, TextLayer, ImageLayer } from '../types/PosterSchema';
import type { Transform, SelectionBox } from '../types/EditorTypes';

/**
 * 生成唯一 ID
 */
export function generateId(): string {
  return `layer_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 检查点是否在矩形内
 */
export function isPointInRect(
  px: number,
  py: number,
  rect: { x: number; y: number; width: number; height: number }
): boolean {
  return (
    px >= rect.x &&
    px <= rect.x + rect.width &&
    py >= rect.y &&
    py <= rect.y + rect.height
  );
}

/**
 * 获取鼠标相对于画布的位置
 */
export function getCanvasMousePosition(
  event: MouseEvent | React.MouseEvent,
  canvasElement: HTMLElement,
  scale: number
): { x: number; y: number } {
  const rect = canvasElement.getBoundingClientRect();
  const x = (event.clientX - rect.left) / scale;
  const y = (event.clientY - rect.top) / scale;
  return { x, y };
}

/**
 * 限制值在指定范围内
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

/**
 * 吸附到网格
 */
export function snapToGrid(value: number, gridSize: number): number {
  return Math.round(value / gridSize) * gridSize;
}

/**
 * 计算调整大小后的新尺寸和位置
 */
export function calculateResize(
  direction: string,
  deltaX: number,
  deltaY: number,
  originalTransform: Transform,
  minWidth: number = 20,
  minHeight: number = 20
): Transform {
  const result = { ...originalTransform };

  switch (direction) {
    case 'se': // 右下
      result.width = Math.max(minWidth, originalTransform.width + deltaX);
      result.height = Math.max(minHeight, originalTransform.height + deltaY);
      break;

    case 'sw': // 左下
      result.width = Math.max(minWidth, originalTransform.width - deltaX);
      result.height = Math.max(minHeight, originalTransform.height + deltaY);
      result.x = originalTransform.x + (originalTransform.width - result.width);
      break;

    case 'ne': // 右上
      result.width = Math.max(minWidth, originalTransform.width + deltaX);
      result.height = Math.max(minHeight, originalTransform.height - deltaY);
      result.y = originalTransform.y + (originalTransform.height - result.height);
      break;

    case 'nw': // 左上
      result.width = Math.max(minWidth, originalTransform.width - deltaX);
      result.height = Math.max(minHeight, originalTransform.height - deltaY);
      result.x = originalTransform.x + (originalTransform.width - result.width);
      result.y = originalTransform.y + (originalTransform.height - result.height);
      break;

    case 'e': // 右
      result.width = Math.max(minWidth, originalTransform.width + deltaX);
      break;

    case 'w': // 左
      result.width = Math.max(minWidth, originalTransform.width - deltaX);
      result.x = originalTransform.x + (originalTransform.width - result.width);
      break;

    case 'n': // 上
      result.height = Math.max(minHeight, originalTransform.height - deltaY);
      result.y = originalTransform.y + (originalTransform.height - result.height);
      break;

    case 's': // 下
      result.height = Math.max(minHeight, originalTransform.height + deltaY);
      break;
  }

  return result;
}

/**
 * 确保图层在画布范围内
 */
export function constrainToCanvas(
  layer: Layer,
  canvasWidth: number,
  canvasHeight: number
): Layer {
  const result = { ...layer };

  // 确保位置不为负
  result.x = Math.max(0, result.x);
  result.y = Math.max(0, result.y);

  // 确保不超出右边界
  if (result.x + result.width > canvasWidth) {
    result.x = Math.max(0, canvasWidth - result.width);
  }

  // 确保不超出下边界
  if (result.y + result.height > canvasHeight) {
    result.y = Math.max(0, canvasHeight - result.height);
  }

  return result;
}

/**
 * 查找指定位置的图层（从上到下）
 */
export function findLayerAtPosition(
  x: number,
  y: number,
  layers: Layer[],
  hiddenLayerIds: Set<string> = new Set()
): Layer | null {
  // 从上到下遍历（数组最后的图层在最上面）
  for (let i = layers.length - 1; i >= 0; i--) {
    const layer = layers[i];
    
    // 跳过隐藏的图层
    if (hiddenLayerIds.has(layer.id)) {
      continue;
    }

    if (isPointInRect(x, y, layer)) {
      return layer;
    }
  }

  return null;
}

/**
 * 获取图层的边界框
 */
export function getLayerBounds(layer: Layer): SelectionBox {
  return {
    x: layer.x,
    y: layer.y,
    width: layer.width,
    height: layer.height,
  };
}

/**
 * 复制图层
 */
export function duplicateLayer(layer: Layer, offsetX: number = 20, offsetY: number = 20): Layer {
  const newLayer = {
    ...layer,
    id: generateId(),
    name: `${layer.name} (copy)`,
    x: layer.x + offsetX,
    y: layer.y + offsetY,
  };

  return newLayer;
}

/**
 * 更新图层在数组中的顺序
 */
export function reorderLayer(
  layers: Layer[],
  layerId: string,
  direction: 'up' | 'down' | 'top' | 'bottom'
): Layer[] {
  const index = layers.findIndex((l) => l.id === layerId);
  if (index === -1) return layers;

  const newLayers = [...layers];
  const [layer] = newLayers.splice(index, 1);

  switch (direction) {
    case 'up':
      newLayers.splice(Math.min(index + 1, newLayers.length), 0, layer);
      break;
    case 'down':
      newLayers.splice(Math.max(index - 1, 0), 0, layer);
      break;
    case 'top':
      newLayers.push(layer);
      break;
    case 'bottom':
      newLayers.unshift(layer);
      break;
  }

  return newLayers;
}

/**
 * 获取图层索引
 */
export function getLayerIndex(layers: Layer[], layerId: string): number {
  return layers.findIndex((l) => l.id === layerId);
}

/**
 * 检查图层是否是文本图层
 */
export function isTextLayer(layer: Layer): layer is TextLayer {
  return layer.type === 'text';
}

/**
 * 检查图层是否是图片图层
 */
export function isImageLayer(layer: Layer): layer is ImageLayer {
  return layer.type === 'image';
}

/**
 * 计算两点之间的距离
 */
export function distance(x1: number, y1: number, x2: number, y2: number): number {
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${Math.round(bytes / Math.pow(k, i) * 100) / 100} ${sizes[i]}`;
}

/**
 * 深度克隆对象
 */
export function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * 验证海报数据
 */
export function validatePosterData(data: PosterData): boolean {
  if (!data || !data.canvas || !Array.isArray(data.layers)) {
    return false;
  }

  if (data.canvas.width <= 0 || data.canvas.height <= 0) {
    return false;
  }

  return true;
}

