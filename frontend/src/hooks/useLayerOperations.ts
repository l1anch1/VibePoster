/**
 * 图层操作 Hook
 * 
 * 抽取图层相关的业务逻辑，减轻 EditorCanvas 负担
 */

import { useCallback } from 'react';
import type { PosterData, Layer } from '../types/PosterSchema';
import {
  constrainToCanvas,
  duplicateLayer,
  reorderLayer,
} from '../utils/editorUtils';

interface UseLayerOperationsProps {
  data: PosterData;
  updateData: (newData: PosterData, description?: string) => void;
  selectLayer: (layerId: string | null) => void;
  clearSelection: () => void;
  selectedLayerId: string | null;
}

export function useLayerOperations({
  data,
  updateData,
  selectLayer,
  clearSelection,
  selectedLayerId,
}: UseLayerOperationsProps) {
  /**
   * 更新单个图层属性
   */
  const updateLayer = useCallback(
    (layerId: string, updates: Partial<Layer>) => {
      const newLayers = data.layers.map((layer) =>
        layer.id === layerId ? { ...layer, ...updates } : layer
      );
      const newData = { ...data, layers: newLayers };
      updateData(newData, 'Update layer');
    },
    [data, updateData]
  );

  /**
   * 移动图层位置（带画布约束）
   */
  const moveLayer = useCallback(
    (layerId: string, deltaX: number, deltaY: number) => {
      const layer = data.layers.find((l) => l.id === layerId);
      if (!layer) return;

      const newX = layer.x + deltaX;
      const newY = layer.y + deltaY;

      const constrainedLayer = constrainToCanvas(
        { ...layer, x: newX, y: newY },
        data.canvas.width,
        data.canvas.height
      );

      updateLayer(layerId, {
        x: constrainedLayer.x,
        y: constrainedLayer.y,
      });
    },
    [data, updateLayer]
  );

  /**
   * 删除图层
   */
  const deleteLayer = useCallback(
    (layerId: string) => {
      const newLayers = data.layers.filter((l) => l.id !== layerId);
      const newData = { ...data, layers: newLayers };
      updateData(newData, 'Delete layer');
      if (selectedLayerId === layerId) {
        clearSelection();
      }
    },
    [data, selectedLayerId, updateData, clearSelection]
  );

  /**
   * 复制图层
   */
  const duplicateLayerById = useCallback(
    (layerId: string) => {
      const layer = data.layers.find((l) => l.id === layerId);
      if (!layer) return;

      const newLayer = duplicateLayer(layer);
      const newLayers = [...data.layers, newLayer];
      const newData = { ...data, layers: newLayers };
      updateData(newData, 'Duplicate layer');
      selectLayer(newLayer.id);
    },
    [data, updateData, selectLayer]
  );

  /**
   * 调整图层顺序
   */
  const reorderLayerById = useCallback(
    (layerId: string, direction: 'up' | 'down') => {
      const newLayers = reorderLayer(data.layers, layerId, direction);
      const newData = { ...data, layers: newLayers };
      updateData(newData, 'Reorder layer');
    },
    [data, updateData]
  );

  /**
   * 获取图层
   */
  const getLayer = useCallback(
    (layerId: string): Layer | undefined => {
      return data.layers.find((l) => l.id === layerId);
    },
    [data.layers]
  );

  return {
    updateLayer,
    moveLayer,
    deleteLayer,
    duplicateLayerById,
    reorderLayerById,
    getLayer,
  };
}

