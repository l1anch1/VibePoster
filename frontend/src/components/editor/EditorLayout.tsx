/**
 * 编辑器布局组件
 * 
 * 组合画布和右侧编辑面板，管理编辑状态
 */

import React, { useCallback, useState, useEffect, useRef } from 'react';
import type { PosterData, Layer } from '../../types/PosterSchema';
import { EditorCanvas } from './EditorCanvas';
import { EditorSidebar } from './EditorSidebar';
import { useEditorState } from '../../hooks/useEditorState';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import {
  reorderLayer,
  duplicateLayer,
} from '../../utils/editorUtils';

interface EditorLayoutProps {
  data: PosterData;
  scale: number;
  onDataChange: (data: PosterData) => void;
}

export const EditorLayout: React.FC<EditorLayoutProps> = ({
  data,
  scale,
  onDataChange,
}) => {
  // 编辑器状态
  const {
    selectedLayerId,
    lockedLayerIds,
    hiddenLayerIds,
    clipboard,
    selectLayer,
    toggleLayerLock,
    toggleLayerVisibility,
    isLayerLocked,
    copyLayer,
    clearSelection,
  } = useEditorState();

  // 文本编辑状态
  const [editingLayerId, setEditingLayerId] = useState<string | null>(null);

  // 保存初始状态（刚生成时的海报）
  const initialDataRef = useRef<PosterData>(data);
  const initialDataJsonRef = useRef(JSON.stringify(data));

  // 当前编辑状态（用于撤销功能）
  const [currentData, setCurrentData] = useState<PosterData>(data);
  const [history, setHistory] = useState<PosterData[]>([]);

  // 检测新海报的签名
  const getDataSignature = (d: PosterData) => {
    const firstLayerId = d.layers[0]?.id || 'empty';
    return `${d.canvas.width}x${d.canvas.height}-${firstLayerId}`;
  };
  const lastDataSignatureRef = useRef(getDataSignature(data));

  // 检测新海报，重置初始状态
  useEffect(() => {
    const currentSignature = getDataSignature(data);
    if (currentSignature !== lastDataSignatureRef.current) {
      console.log('[EditorLayout] 🎨 新海报，保存初始状态');
      initialDataRef.current = data;
      initialDataJsonRef.current = JSON.stringify(data);
      setCurrentData(data);
      setHistory([]);
      lastDataSignatureRef.current = currentSignature;
    }
  }, [data]);

  // 撤销：回到上一步
  const handleUndo = useCallback(() => {
    setHistory((prevHistory) => {
      if (prevHistory.length === 0) return prevHistory;
      const previousData = prevHistory[prevHistory.length - 1];
      setCurrentData(previousData);
      onDataChange(previousData);
      console.log('[EditorLayout] ⏮️  撤销到上一步');
      return prevHistory.slice(0, -1);
    });
  }, [onDataChange]);

  // 重做：回到初始状态
  const handleRedo = useCallback(() => {
    const initial = initialDataRef.current;
    setCurrentData(initial);
    setHistory([]);
    onDataChange(initial);
    console.log('[EditorLayout] 🔄 重做，恢复到初始状态');
  }, [onDataChange]);

  // 判断是否可以撤销/重做
  const canUndo = history.length > 0;
  const canRedo = JSON.stringify(currentData) !== initialDataJsonRef.current;

  // 更新图层
  const updateLayer = useCallback(
    (layerId: string, updates: Partial<Layer>) => {
      setCurrentData((prevData) => {
        const newLayers = prevData.layers.map((layer) =>
          layer.id === layerId ? { ...layer, ...updates } : layer
        );
        const newData = { ...prevData, layers: newLayers };
        // 保存当前状态到历史
        setHistory((prevHistory) => [...prevHistory, prevData]);
        // 同步到父组件
        onDataChange(newData);
        console.log('[EditorLayout] ✏️  Update layer');
        return newData;
      });
    },
    [onDataChange]
  );

  // 删除图层
  const handleDeleteLayer = useCallback(
    (layerId: string) => {
      setCurrentData((prevData) => {
        const newLayers = prevData.layers.filter((l) => l.id !== layerId);
        const newData = { ...prevData, layers: newLayers };
        // 保存当前状态到历史
        setHistory((prevHistory) => [...prevHistory, prevData]);
        // 同步到父组件
        onDataChange(newData);
        console.log('[EditorLayout] ✏️  Delete layer');
        return newData;
      });
      if (selectedLayerId === layerId) {
        clearSelection();
      }
    },
    [selectedLayerId, onDataChange, clearSelection]
  );

  // 复制图层
  const handleDuplicateLayer = useCallback(
    (layerId: string) => {
      setCurrentData((prevData) => {
        const layer = prevData.layers.find((l) => l.id === layerId);
        if (!layer) return prevData;

        const newLayer = duplicateLayer(layer);
        const newLayers = [...prevData.layers, newLayer];
        const newData = { ...prevData, layers: newLayers };
        // 保存当前状态到历史
        setHistory((prevHistory) => [...prevHistory, prevData]);
        // 同步到父组件
        onDataChange(newData);
        console.log('[EditorLayout] ✏️  Duplicate layer');
        selectLayer(newLayer.id);
        return newData;
      });
    },
    [onDataChange, selectLayer]
  );

  // 调整图层顺序
  const handleReorderLayer = useCallback(
    (layerId: string, direction: 'up' | 'down') => {
      setCurrentData((prevData) => {
        const newLayers = reorderLayer(prevData.layers, layerId, direction);
        const newData = { ...prevData, layers: newLayers };
        // 保存当前状态到历史
        setHistory((prevHistory) => [...prevHistory, prevData]);
        // 同步到父组件
        onDataChange(newData);
        console.log('[EditorLayout] ✏️  Reorder layer');
        return newData;
      });
    },
    [onDataChange]
  );

  // 更新属性
  const handleUpdateProperty = useCallback(
    (layerId: string, property: string, value: any) => {
      updateLayer(layerId, { [property]: value });
    },
    [updateLayer]
  );

  // 键盘快捷键
  useKeyboardShortcuts(
    {
      onUndo: canUndo ? handleUndo : undefined,
      onRedo: canRedo ? handleRedo : undefined,
      onDelete: selectedLayerId ? () => handleDeleteLayer(selectedLayerId) : undefined,
      onCopy: selectedLayerId
        ? () => {
            const layer = currentData.layers.find((l) => l.id === selectedLayerId);
            copyLayer(layer || null);
          }
        : undefined,
      onPaste: clipboard ? () => handleDuplicateLayer(clipboard.id) : undefined,
      onDeselect: clearSelection,
      onDuplicate: selectedLayerId ? () => handleDuplicateLayer(selectedLayerId) : undefined,
    },
    true
  );

  // 获取选中的图层
  const selectedLayer = selectedLayerId
    ? currentData.layers.find((l) => l.id === selectedLayerId) || null
    : null;

  return (
    <div style={{ display: 'flex', height: '100%', width: '100%' }}>
      {/* 画布区域 */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#1F2937',
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)
          `,
          backgroundSize: '24px 24px',
          overflow: 'hidden',
        }}
      >
        {/* 画布包装器：用于隔离 scale 的影响，确保画布居中 */}
        <div
          style={{
            position: 'relative',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <EditorCanvas
            data={currentData}
            scale={scale}
            onDataChange={onDataChange}
            isEditMode={true}
            selectedLayerId={selectedLayerId}
            lockedLayerIds={lockedLayerIds}
            hiddenLayerIds={hiddenLayerIds}
            onSelectLayer={selectLayer}
            isLayerLocked={isLayerLocked}
            onUpdateLayer={updateLayer}
            editingLayerId={editingLayerId}
            onStartEditing={setEditingLayerId}
            onStopEditing={() => setEditingLayerId(null)}
          />
        </div>
      </div>

      {/* 右侧编辑面板 */}
      <EditorSidebar
        canUndo={canUndo}
        canRedo={canRedo}
        onUndo={handleUndo}
        onRedo={handleRedo}
        layers={currentData.layers}
        selectedLayerId={selectedLayerId}
        lockedLayerIds={lockedLayerIds}
        hiddenLayerIds={hiddenLayerIds}
        onSelectLayer={selectLayer}
        onToggleLock={toggleLayerLock}
        onToggleVisibility={toggleLayerVisibility}
        onDeleteLayer={handleDeleteLayer}
        onReorderLayer={handleReorderLayer}
        selectedLayer={selectedLayer}
        onUpdateProperty={handleUpdateProperty}
      />
    </div>
  );
};

