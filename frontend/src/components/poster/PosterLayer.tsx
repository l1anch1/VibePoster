import React from 'react';
import type { Layer } from '../../types/PosterSchema';

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
    const lineHeight = 1.2;
    
    // 为文本图层创建独立的样式
    // 注意：文本样式必须在 commonStyle 之后，确保覆盖所有可能阻止换行的属性
    const textStyle: React.CSSProperties = {
      // 先应用 commonStyle（位置、边框等基础样式）
      position: commonStyle.position,
      left: commonStyle.left,
      top: commonStyle.top,
      transform: commonStyle.transform,
      opacity: commonStyle.opacity,
      zIndex: commonStyle.zIndex,
      border: commonStyle.border,
      cursor: commonStyle.cursor,
      // 文本特定样式
      fontSize: `${layer.fontSize}px`,
      color: layer.color,
      fontFamily: layer.fontFamily,
      textAlign: layer.textAlign,
      fontWeight: layer.fontWeight,
      lineHeight: lineHeight,
      // 文本换行设置 - 关键属性必须在最后，确保优先级
      whiteSpace: 'normal',         // 允许换行（关键！必须覆盖任何 nowrap）
      wordWrap: 'break-word',       // 长单词自动换行
      wordBreak: 'break-word',      // 支持中文和英文换行
      overflowWrap: 'break-word',   // 额外的换行支持
      overflow: 'hidden',           // 隐藏超出部分（关键！防止超出高度）
      boxSizing: 'border-box',      // 确保宽度计算包含边框
      width: `${layer.width}px`,     // 固定宽度（必须设置，否则无法换行）
      minWidth: `${layer.width}px`,  // 确保最小宽度
      maxWidth: `${layer.width}px`,  // 限制最大宽度
      // 高度限制：使用固定高度，确保不会超出并遮挡其他图层
      height: `${layer.height}px`,   // 固定高度（防止超出并遮挡其他图层）
      minHeight: `${layer.fontSize * lineHeight}px`, // 至少一行的高度
      maxHeight: `${layer.height}px`, // 限制最大高度（双重保险）
      // 使用标准 block 布局，确保文本可以换行
      display: 'block',
    };
    
    return (
      <div 
	    id={layer.id}
	    style={textStyle}>
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