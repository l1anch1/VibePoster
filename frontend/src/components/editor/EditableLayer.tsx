/**
 * 可编辑图层组件
 * 
 * 支持选中、拖拽、调整大小等交互功能
 */

import React, { useState, useRef, useCallback, type CSSProperties } from 'react';
import type { Layer } from '../../types/PosterSchema';
import type { ResizeDirection } from '../../types/EditorTypes';

interface EditableLayerProps {
  layer: Layer;
  isSelected: boolean;
  isLocked: boolean;
  isHidden: boolean;
  scale: number;
  onSelect: (layerId: string) => void;
  onDragStart: (layerId: string, startX: number, startY: number) => void;
  onDrag: (deltaX: number, deltaY: number) => void;
  onDragEnd: () => void;
  onResizeStart: (layerId: string, direction: ResizeDirection, startX: number, startY: number) => void;
  onResize: (deltaX: number, deltaY: number) => void;
  onResizeEnd: () => void;
  onDoubleClick?: (layerId: string) => void;
}

// 调整大小手柄的位置定义
const RESIZE_HANDLES: Array<{ direction: ResizeDirection; cursor: string; style: CSSProperties }> = [
  { direction: 'nw', cursor: 'nw-resize', style: { top: -4, left: -4 } },
  { direction: 'n', cursor: 'n-resize', style: { top: -4, left: '50%', transform: 'translateX(-50%)' } },
  { direction: 'ne', cursor: 'ne-resize', style: { top: -4, right: -4 } },
  { direction: 'e', cursor: 'e-resize', style: { top: '50%', right: -4, transform: 'translateY(-50%)' } },
  { direction: 'se', cursor: 'se-resize', style: { bottom: -4, right: -4 } },
  { direction: 's', cursor: 's-resize', style: { bottom: -4, left: '50%', transform: 'translateX(-50%)' } },
  { direction: 'sw', cursor: 'sw-resize', style: { bottom: -4, left: -4 } },
  { direction: 'w', cursor: 'w-resize', style: { top: '50%', left: -4, transform: 'translateY(-50%)' } },
];

export const EditableLayer: React.FC<EditableLayerProps> = ({
  layer,
  isSelected,
  isLocked,
  isHidden,
  scale,
  onSelect,
  onDragStart,
  onDrag,
  onDragEnd,
  onResizeStart,
  onResize,
  onResizeEnd,
  onDoubleClick,
}) => {
  // ✅ 所有 Hooks 必须在组件顶部，任何条件返回之前
  const layerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef({ x: 0, y: 0 });
  const resizeStartPos = useRef({ x: 0, y: 0 });

  /**
   * 处理鼠标按下（拖拽开始）
   */
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (isLocked) return;

      // 如果点击的是调整大小手柄，不处理拖拽
      if ((e.target as HTMLElement).classList.contains('resize-handle')) {
        return;
      }

      e.stopPropagation();
      onSelect(layer.id);

      setIsDragging(true);
      dragStartPos.current = { x: e.clientX, y: e.clientY };
      onDragStart(layer.id, e.clientX, e.clientY);

      // 添加全局鼠标移动和释放事件
      const handleMouseMove = (moveEvent: MouseEvent) => {
        const deltaX = (moveEvent.clientX - dragStartPos.current.x) / scale;
        const deltaY = (moveEvent.clientY - dragStartPos.current.y) / scale;
        onDrag(deltaX, deltaY);
        dragStartPos.current = { x: moveEvent.clientX, y: moveEvent.clientY };
      };

      const handleMouseUp = () => {
        setIsDragging(false);
        onDragEnd();
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };

      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    },
    [isLocked, layer.id, scale, onSelect, onDragStart, onDrag, onDragEnd]
  );

  /**
   * 处理调整大小手柄鼠标按下
   */
  const handleResizeMouseDown = useCallback(
    (direction: ResizeDirection, e: React.MouseEvent) => {
      if (isLocked) return;

      e.stopPropagation();
      resizeStartPos.current = { x: e.clientX, y: e.clientY };
      onResizeStart(layer.id, direction, e.clientX, e.clientY);

      // 添加全局鼠标移动和释放事件
      const handleMouseMove = (moveEvent: MouseEvent) => {
        const deltaX = (moveEvent.clientX - resizeStartPos.current.x) / scale;
        const deltaY = (moveEvent.clientY - resizeStartPos.current.y) / scale;
        onResize(deltaX, deltaY);
        resizeStartPos.current = { x: moveEvent.clientX, y: moveEvent.clientY };
      };

      const handleMouseUp = () => {
        onResizeEnd();
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };

      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    },
    [isLocked, layer.id, scale, onResizeStart, onResize, onResizeEnd]
  );

  /**
   * 处理双击
   */
  const handleDoubleClick = useCallback(
    (e: React.MouseEvent) => {
      if (isLocked) return;
      e.stopPropagation();
      onDoubleClick?.(layer.id);
    },
    [isLocked, layer.id, onDoubleClick]
  );

  // ✅ 所有 Hooks 调用完毕后，再做条件返回
  if (isHidden) {
    return null;
  }

  // 通用样式
  const commonStyle: CSSProperties = {
    position: 'absolute',
    left: `${layer.x}px`,
    top: `${layer.y}px`,
    width: `${layer.width}px`,
    height: `${layer.height}px`,
    transform: `rotate(${layer.rotation}deg)`,
    opacity: layer.opacity,
    cursor: isDragging ? 'grabbing' : isLocked ? 'not-allowed' : 'grab',
    userSelect: 'none',
    pointerEvents: isLocked ? 'none' : 'auto',
  };

  // 选中边框样式
  const selectionStyle: CSSProperties = isSelected
    ? {
        outline: '2px solid #3B82F6',
        outlineOffset: '0px',
      }
    : {};

  // 渲染图层内容
  const renderLayerContent = () => {
    if (layer.type === 'text') {
      const textStyle: CSSProperties = {
        fontSize: `${layer.fontSize}px`,
        color: layer.color,
        fontFamily: layer.fontFamily,
        textAlign: layer.textAlign,
        fontWeight: layer.fontWeight,
        lineHeight: 1.2,
        whiteSpace: 'normal',
        wordWrap: 'break-word',
        wordBreak: 'break-word',
        overflowWrap: 'break-word',
        overflow: 'hidden',
        boxSizing: 'border-box',
        width: '100%',
        height: '100%',
        display: 'block',
      };

      return <div style={textStyle}>{layer.content}</div>;
    }

    if (layer.type === 'image') {
      return (
        <img
          src={layer.src}
          alt={layer.name}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
          draggable={false}
        />
      );
    }

    return null;
  };

  return (
    <div
      ref={layerRef}
      style={{ ...commonStyle, ...selectionStyle }}
      onMouseDown={handleMouseDown}
      onDoubleClick={handleDoubleClick}
      className="editable-layer"
    >
      {renderLayerContent()}

      {/* 调整大小手柄（只在选中且未锁定时显示） */}
      {isSelected && !isLocked && (
        <>
          {RESIZE_HANDLES.map((handle) => (
            <div
              key={handle.direction}
              className="resize-handle"
              style={{
                position: 'absolute',
                width: '8px',
                height: '8px',
                backgroundColor: '#3B82F6',
                border: '1px solid #FFFFFF',
                borderRadius: '50%',
                cursor: handle.cursor,
                zIndex: 1000,
                ...handle.style,
              }}
              onMouseDown={(e) => handleResizeMouseDown(handle.direction, e)}
            />
          ))}
        </>
      )}
    </div>
  );
};

