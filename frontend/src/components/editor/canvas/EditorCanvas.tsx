/**
 * 编辑器画布组件
 *
 * 集成拖拽、缩放、对齐辅助线、Undo batch
 */

import React, { useRef, useCallback, useState } from 'react';
import type { PosterData, Layer } from '../../../types/PosterSchema';
import type { ResizeDirection } from '../../../types/EditorTypes';
import { EditableLayer } from './EditableLayer';
import { TextEditor } from './TextEditor';
import {
  constrainToCanvas,
  calculateResize,
  isTextLayer,
} from '../../../utils/editorUtils';

// ============================================================================
// 对齐辅助线
// ============================================================================

interface Guide {
  orientation: 'h' | 'v';
  position: number;
}

const SNAP_THRESHOLD = 5; // canvas pixels

function calculateGuides(
  movingLayer: { x: number; y: number; width: number; height: number },
  allLayers: Layer[],
  canvasWidth: number,
  canvasHeight: number,
): { guides: Guide[]; snapX: number | null; snapY: number | null } {
  const guides: Guide[] = [];
  let snapX: number | null = null;
  let snapY: number | null = null;

  const mx = movingLayer.x;
  const my = movingLayer.y;
  const mw = movingLayer.width;
  const mh = movingLayer.height;
  const mCx = mx + mw / 2;
  const mCy = my + mh / 2;

  // reference points: canvas center + other layers' edges/centers
  const vRefs: number[] = [canvasWidth / 2]; // vertical reference X positions
  const hRefs: number[] = [canvasHeight / 2]; // horizontal reference Y positions

  for (const l of allLayers) {
    vRefs.push(l.x, l.x + l.width / 2, l.x + l.width);
    hRefs.push(l.y, l.y + l.height / 2, l.y + l.height);
  }

  // Check vertical snapping (X axis)
  const xEdges = [
    { pos: mx, label: 'left' },           // left edge
    { pos: mCx, label: 'center' },        // center
    { pos: mx + mw, label: 'right' },     // right edge
  ];
  for (const edge of xEdges) {
    for (const ref of vRefs) {
      if (Math.abs(edge.pos - ref) <= SNAP_THRESHOLD) {
        snapX = mx + (ref - edge.pos);
        guides.push({ orientation: 'v', position: ref });
        break;
      }
    }
    if (snapX !== null) break;
  }

  // Check horizontal snapping (Y axis)
  const yEdges = [
    { pos: my, label: 'top' },
    { pos: mCy, label: 'center' },
    { pos: my + mh, label: 'bottom' },
  ];
  for (const edge of yEdges) {
    for (const ref of hRefs) {
      if (Math.abs(edge.pos - ref) <= SNAP_THRESHOLD) {
        snapY = my + (ref - edge.pos);
        guides.push({ orientation: 'h', position: ref });
        break;
      }
    }
    if (snapY !== null) break;
  }

  return { guides, snapX, snapY };
}

// ============================================================================
// EditorCanvas
// ============================================================================

interface EditorCanvasProps {
  data: PosterData;
  scale: number;
  isEditMode?: boolean;
  selectedLayerId?: string | null;
  hiddenLayerIds?: Set<string>;
  onSelectLayer?: (layerId: string) => void;
  isLayerLocked?: (layerId: string) => boolean;
  onUpdateLayer?: (layerId: string, updates: Partial<Layer>) => void;
  editingLayerId?: string | null;
  onStartEditing?: (layerId: string) => void;
  onStopEditing?: () => void;
  onBeginBatch?: () => void;
  onEndBatch?: () => void;
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
  onBeginBatch = () => {},
  onEndBatch = () => {},
}) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [guides, setGuides] = useState<Guide[]>([]);

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
      onBeginBatch();
      setDragState({ layerId, startX, startY });
    },
    [isLayerLocked, onBeginBatch]
  );

  // 拖拽中（含吸附）
  const handleDrag = useCallback(
    (deltaX: number, deltaY: number) => {
      if (!dragState.layerId) return;

      const layer = data.layers.find((l) => l.id === dragState.layerId);
      if (!layer) return;

      let newX = layer.x + deltaX;
      let newY = layer.y + deltaY;

      // 计算对齐辅助线
      const otherLayers = data.layers.filter((l) => l.id !== dragState.layerId);
      const { guides: newGuides, snapX, snapY } = calculateGuides(
        { x: newX, y: newY, width: layer.width, height: layer.height },
        otherLayers,
        data.canvas.width,
        data.canvas.height,
      );
      if (snapX !== null) newX = snapX;
      if (snapY !== null) newY = snapY;
      setGuides(newGuides);

      const constrained = constrainToCanvas(
        { ...layer, x: newX, y: newY },
        data.canvas.width,
        data.canvas.height
      );

      onUpdateLayer(layer.id, { x: constrained.x, y: constrained.y });
    },
    [dragState, data, onUpdateLayer]
  );

  // 拖拽结束
  const handleDragEnd = useCallback(() => {
    setDragState({ layerId: null, startX: 0, startY: 0 });
    setGuides([]);
    onEndBatch();
  }, [onEndBatch]);

  // 调整大小开始
  const handleResizeStart = useCallback(
    (layerId: string, direction: ResizeDirection) => {
      if (isLayerLocked(layerId)) return;
      const layer = data.layers.find((l) => l.id === layerId);
      if (!layer) return;
      onBeginBatch();
      setResizeState({ layerId, direction, originalLayer: layer });
    },
    [data.layers, isLayerLocked, onBeginBatch]
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

      const constrained = constrainToCanvas(
        { ...resizeState.originalLayer, ...newTransform },
        data.canvas.width,
        data.canvas.height
      );

      onUpdateLayer(resizeState.layerId, {
        x: constrained.x,
        y: constrained.y,
        width: constrained.width,
        height: constrained.height,
      });
    },
    [resizeState, data.canvas, onUpdateLayer]
  );

  // 调整大小结束
  const handleResizeEnd = useCallback(() => {
    setResizeState({ layerId: null, direction: null, originalLayer: null });
    onEndBatch();
  }, [onEndBatch]);

  // 清空选择
  const clearSelection = useCallback(() => {
    onSelectLayer('');
  }, [onSelectLayer]);

  // 双击图层
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

  const editingLayer = editingLayerId
    ? data.layers.find((l) => l.id === editingLayerId) || null
    : null;

  const scaledWidth = data.canvas.width * scale;
  const scaledHeight = data.canvas.height * scale;

  return (
    <div style={{ width: `${scaledWidth}px`, height: `${scaledHeight}px`, position: 'relative' }}>
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
          boxShadow: '0 25px 50px rgba(0,0,0,0.12), 0 0 0 1px rgba(0,0,0,0.06)',
          boxSizing: 'border-box',
          overflow: 'hidden',
          borderRadius: '8px',
          transition: 'transform 0.2s ease',
        }}
        ref={canvasRef}
        onClick={(e) => {
          if (e.target === canvasRef.current) clearSelection();
        }}
      >
        {/* 图层 */}
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

        {/* 对齐辅助线 */}
        {guides.map((g, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              [g.orientation === 'v' ? 'left' : 'top']: `${g.position}px`,
              [g.orientation === 'v' ? 'top' : 'left']: 0,
              [g.orientation === 'v' ? 'width' : 'height']: '1px',
              [g.orientation === 'v' ? 'height' : 'width']: '100%',
              backgroundColor: '#8b5cf6',
              pointerEvents: 'none',
              zIndex: 9999,
              opacity: 0.6,
            }}
          />
        ))}

        {/* 文本编辑器 */}
        {editingLayer && isTextLayer(editingLayer) && (
          <TextEditor
            layer={editingLayer}
            onUpdate={(content) => handleUpdateText(editingLayer.id, content)}
            onClose={onStopEditing}
          />
        )}

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
            Switch to edit mode to modify the poster
          </div>
        )}
      </div>
    </div>
  );
};
