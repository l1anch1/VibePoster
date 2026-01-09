/**
 * 编辑器画布组件
 * 
 * 集成所有编辑功能
 */

import React, { useRef, useCallback, useState } from 'react';
import type { PosterData, Layer } from '../../types/PosterSchema';
import type { ResizeDirection } from '../../types/EditorTypes';
import { EditableLayer } from './EditableLayer';
import { TextEditor } from './TextEditor';
import {
  constrainToCanvas,
  calculateResize,
  isTextLayer,
} from '../../utils/editorUtils';

interface EditorCanvasProps {
  data: PosterData;
  scale: number;
  onDataChange?: (data: PosterData) => void;  // Optional: used for batch updates
  isEditMode?: boolean;
  // 编辑状态（从外部传入）
  selectedLayerId?: string | null;
  lockedLayerIds?: Set<string>;
  hiddenLayerIds?: Set<string>;
  onSelectLayer?: (layerId: string) => void;
  isLayerLocked?: (layerId: string) => boolean;
  onUpdateLayer?: (layerId: string, updates: Partial<Layer>) => void;
  // 文本编辑
  editingLayerId?: string | null;
  onStartEditing?: (layerId: string) => void;
  onStopEditing?: () => void;
}

export const EditorCanvas: React.FC<EditorCanvasProps> = ({
  data,
  scale,
  isEditMode = false,
  selectedLayerId = null,
  hiddenLayerIds = new Set(),
  onSelectLayer = () => {},
  isLayerLocked = () => false,
  onUpdateLayer = () => {},
  editingLayerId = null,
  onStartEditing = () => {},
  onStopEditing = () => {},
}) => {
  const canvasRef = useRef<HTMLDivElement>(null);

  // 拖拽状态
  const [dragState, setDragState] = useState<{
    layerId: string | null;
    startX: number;
    startY: number;
  }>({ layerId: null, startX: 0, startY: 0 });

  // 调整大小状态
  const [resizeState, setResizeState] = useState<{
    layerId: string | null;
    direction: ResizeDirection;
    originalLayer: Layer | null;
  }>({ layerId: null, direction: null, originalLayer: null });

  // 拖拽开始
  const handleDragStart = useCallback(
    (layerId: string, startX: number, startY: number) => {
      if (isLayerLocked(layerId)) return;
      setDragState({ layerId, startX, startY });
    },
    [isLayerLocked]
  );

  // 拖拽中
  const handleDrag = useCallback(
    (deltaX: number, deltaY: number) => {
      if (!dragState.layerId) return;

      const layer = data.layers.find((l) => l.id === dragState.layerId);
      if (!layer) return;

      const newX = layer.x + deltaX;
      const newY = layer.y + deltaY;
      
      const constrainedLayer = constrainToCanvas(
        { ...layer, x: newX, y: newY },
        data.canvas.width,
        data.canvas.height
      );

      onUpdateLayer(layer.id, {
        x: constrainedLayer.x,
        y: constrainedLayer.y,
      });
    },
    [dragState, data, onUpdateLayer]
  );

  // 拖拽结束
  const handleDragEnd = useCallback(() => {
    setDragState({ layerId: null, startX: 0, startY: 0 });
  }, []);

  // 调整大小开始
  const handleResizeStart = useCallback(
    (layerId: string, direction: ResizeDirection) => {
      if (isLayerLocked(layerId)) return;

      const layer = data.layers.find((l) => l.id === layerId);
      if (!layer) return;

      setResizeState({
        layerId,
        direction,
        originalLayer: layer,
      });
    },
    [data.layers, isLayerLocked]
  );

  // 调整大小中
  const handleResize = useCallback(
    (deltaX: number, deltaY: number) => {
      if (!resizeState.layerId || !resizeState.originalLayer || !resizeState.direction) return;

      const newTransform = calculateResize(
        resizeState.direction,
        deltaX,
        deltaY,
        {
          x: resizeState.originalLayer.x,
          y: resizeState.originalLayer.y,
          width: resizeState.originalLayer.width,
          height: resizeState.originalLayer.height,
          rotation: resizeState.originalLayer.rotation,
        },
        20,
        20
      );

      const constrainedLayer = constrainToCanvas(
        { ...resizeState.originalLayer, ...newTransform },
        data.canvas.width,
        data.canvas.height
      );

      onUpdateLayer(resizeState.layerId, {
        x: constrainedLayer.x,
        y: constrainedLayer.y,
        width: constrainedLayer.width,
        height: constrainedLayer.height,
      });
    },
    [resizeState, data.canvas, onUpdateLayer]
  );

  // 调整大小结束
  const handleResizeEnd = useCallback(() => {
    setResizeState({ layerId: null, direction: null, originalLayer: null });
  }, []);

  // 清空选择
  const clearSelection = useCallback(() => {
    onSelectLayer('');
  }, [onSelectLayer]);

  // 双击图层（文本图层进入编辑模式）
  const handleDoubleClick = useCallback(
    (layerId: string) => {
      const layer = data.layers.find((l) => l.id === layerId);
      if (layer && isTextLayer(layer)) {
        onStartEditing(layerId);
      }
    },
    [data.layers, onStartEditing]
  );

  // 更新编辑中的文本内容
  const handleUpdateText = useCallback(
    (layerId: string, content: string) => {
      onUpdateLayer(layerId, { content });
    },
    [onUpdateLayer]
  );

  // 获取正在编辑的图层
  const editingLayer = editingLayerId
    ? data.layers.find((l) => l.id === editingLayerId) || null
    : null;

  // 计算缩放后的尺寸
  const scaledWidth = data.canvas.width * scale;
  const scaledHeight = data.canvas.height * scale;

  return (
    <div
      style={{
        width: `${scaledWidth}px`,
        height: `${scaledHeight}px`,
        position: 'relative',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
        width: `${data.canvas.width}px`,
        height: `${data.canvas.height}px`,
        backgroundColor: data.canvas.backgroundColor,
        transform: `scale(${scale})`,
          transformOrigin: 'top left',
          boxShadow: '0 25px 50px rgba(0,0,0,0.15), 0 0 0 1px rgba(0,0,0,0.08)',
        boxSizing: 'border-box',
        overflow: 'hidden',
          borderRadius: '4px',
      }}
      ref={canvasRef}
      onClick={(e) => {
        if (e.target === canvasRef.current) {
          clearSelection();
        }
      }}
    >
      {/* 渲染所有图层 */}
      {data.layers.map((layer) => (
        <EditableLayer
          key={layer.id}
          layer={layer}
          isSelected={layer.id === selectedLayerId}
          isLocked={isLayerLocked(layer.id)}
          isHidden={hiddenLayerIds.has(layer.id) || layer.id === editingLayerId}
          scale={scale}
          onSelect={onSelectLayer}
          onDragStart={handleDragStart}
          onDrag={handleDrag}
          onDragEnd={handleDragEnd}
          onResizeStart={handleResizeStart}
          onResize={handleResize}
          onResizeEnd={handleResizeEnd}
          onDoubleClick={handleDoubleClick}
        />
      ))}

      {/* 文本编辑器（编辑模式） */}
      {editingLayer && isTextLayer(editingLayer) && (
        <TextEditor
          layer={editingLayer}
          scale={scale}
          onUpdate={(content) => handleUpdateText(editingLayer.id, content)}
          onClose={onStopEditing}
        />
      )}

      {/* 编辑模式：无浮动面板（由外部 EditorSidebar 处理） */}
      {/* 非编辑模式：显示简单的工具提示 */}
      {!isEditMode && (
        <div
          style={{
            position: 'fixed',
            bottom: '24px',
            left: '50%',
            transform: `translateX(-50%)`,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            color: '#FFFFFF',
            padding: '12px 20px',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 500,
            zIndex: 1000,
            pointerEvents: 'none',
            backdropFilter: 'blur(8px)',
          }}
        >
          💡 切换到编辑模式以修改海报
        </div>
      )}
      </div>
    </div>
  );
};

