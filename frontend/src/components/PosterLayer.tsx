import React from 'react';
import type { Layer } from '../types/PosterSchema';

// 样式映射辅助函数
const getCommonStyle = (layer: Layer): React.CSSProperties => ({
  position: 'absolute',
  left: `${layer.x}px`,      // 核心验证点：数字变像素
  top: `${layer.y}px`,       // 核心验证点
  width: `${layer.width}px`,
  height: `${layer.height}px`,
  transform: `rotate(${layer.rotation}deg)`,
  opacity: layer.opacity,
  zIndex: 1, // 暂时写死，实际可以用 index
  border: '1px dashed rgba(0,0,0,0.1)', // 加个虚线框方便你看清楚范围
  cursor: 'pointer'
});

export const PosterLayer: React.FC<{ layer: Layer }> = ({ layer }) => {
  const commonStyle = getCommonStyle(layer);

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
        whiteSpace: 'nowrap'
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