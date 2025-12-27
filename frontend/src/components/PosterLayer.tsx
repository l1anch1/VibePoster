import React from 'react';
import type { Layer } from '../types/PosterSchema';

interface PosterLayerProps {
  layer: Layer;
  canvasWidth?: number;
  canvasHeight?: number;
}

// 样式映射辅助函数
const getCommonStyle = (layer: Layer, canvasWidth?: number, canvasHeight?: number): React.CSSProperties => {
  // 计算实际位置，确保不超出画布
  let x = Math.max(0, layer.x);
  let y = Math.max(0, layer.y);
  
  if (canvasWidth !== undefined) {
    // 确保右边界不超出
    if (x + layer.width > canvasWidth) {
      x = Math.max(0, canvasWidth - layer.width);
    }
  }
  
  if (canvasHeight !== undefined) {
    // 确保下边界不超出
    if (y + layer.height > canvasHeight) {
      y = Math.max(0, canvasHeight - layer.height);
    }
  }
  
  return {
  position: 'absolute',
    left: `${x}px`,
    top: `${y}px`,
  width: `${layer.width}px`,
  height: `${layer.height}px`,
  transform: `rotate(${layer.rotation}deg)`,
  opacity: layer.opacity,
    zIndex: 1,
    border: '1px dashed rgba(0,0,0,0.1)',
  cursor: 'pointer'
  };
};

export const PosterLayer: React.FC<PosterLayerProps> = ({ layer, canvasWidth, canvasHeight }) => {
  const commonStyle = getCommonStyle(layer, canvasWidth, canvasHeight);

  if (layer.type === 'text') {
    return (
      <div 
	    id={layer.id}
	    style={{
        ...commonStyle,
        fontSize: `${layer.fontSize}px`,
        color: layer.color,
        fontFamily: layer.fontFamily,
        textAlign: layer.textAlign,
        fontWeight: layer.fontWeight,
        lineHeight: 1.2,
        whiteSpace: 'nowrap',
        overflow: 'hidden',           // 裁剪超出部分
        textOverflow: 'ellipsis',     // 超出显示省略号
        boxSizing: 'border-box',      // 确保宽度计算包含边框
        maxWidth: `${layer.width}px`, // 限制最大宽度
        maxHeight: `${layer.height}px`, // 限制最大高度
      }}>
        {layer.content}
      </div>
    );
  }

  if (layer.type === 'image') {
    return (
      <img 
		id={layer.id}
        src={layer.src} 
        alt={layer.name}
        style={{
          ...commonStyle,
          objectFit: 'cover' 
        }}
        draggable={false}
      />
    );
  }

  return null;
};