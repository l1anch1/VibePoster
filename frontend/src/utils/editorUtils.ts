/**
 * 编辑器工具函数
 */

import type { Layer, PosterData, TextLayer } from '../types/PosterSchema';
import type { Transform } from '../types/EditorTypes';

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
    case 'se':
      result.width = Math.max(minWidth, originalTransform.width + deltaX);
      result.height = Math.max(minHeight, originalTransform.height + deltaY);
      break;

    case 'sw':
      result.width = Math.max(minWidth, originalTransform.width - deltaX);
      result.height = Math.max(minHeight, originalTransform.height + deltaY);
      result.x = originalTransform.x + (originalTransform.width - result.width);
      break;

    case 'ne':
      result.width = Math.max(minWidth, originalTransform.width + deltaX);
      result.height = Math.max(minHeight, originalTransform.height - deltaY);
      result.y = originalTransform.y + (originalTransform.height - result.height);
      break;

    case 'nw':
      result.width = Math.max(minWidth, originalTransform.width - deltaX);
      result.height = Math.max(minHeight, originalTransform.height - deltaY);
      result.x = originalTransform.x + (originalTransform.width - result.width);
      result.y = originalTransform.y + (originalTransform.height - result.height);
      break;

    case 'e':
      result.width = Math.max(minWidth, originalTransform.width + deltaX);
      break;

    case 'w':
      result.width = Math.max(minWidth, originalTransform.width - deltaX);
      result.x = originalTransform.x + (originalTransform.width - result.width);
      break;

    case 'n':
      result.height = Math.max(minHeight, originalTransform.height - deltaY);
      result.y = originalTransform.y + (originalTransform.height - result.height);
      break;

    case 's':
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

  result.x = Math.max(0, result.x);
  result.y = Math.max(0, result.y);

  if (result.x + result.width > canvasWidth) {
    result.x = Math.max(0, canvasWidth - result.width);
  }

  if (result.y + result.height > canvasHeight) {
    result.y = Math.max(0, canvasHeight - result.height);
  }

  return result;
}

/**
 * 检查图层是否是文本图层
 */
export function isTextLayer(layer: Layer): layer is TextLayer {
  return layer.type === 'text';
}

/**
 * 等比缩放图层列表，用于画布尺寸变更时保持排版
 */
export function rescaleLayers(layers: Layer[], scaleX: number, scaleY: number): Layer[] {
  const fontScale = (scaleX + scaleY) / 2;

  return layers.map((layer) => {
    const scaled: Layer = {
      ...layer,
      x: Math.round(layer.x * scaleX),
      y: Math.round(layer.y * scaleY),
      width: Math.max(1, Math.round(layer.width * scaleX)),
      height: Math.max(1, Math.round(layer.height * scaleY)),
    };

    if (isTextLayer(layer) && isTextLayer(scaled)) {
      scaled.fontSize = Math.max(12, Math.round(layer.fontSize * fontScale));
    }

    return scaled;
  });
}
