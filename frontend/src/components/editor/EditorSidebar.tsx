/**
 * 编辑器右侧面板
 * 
 * 包含工具栏、图层面板、属性面板
 */

import React from 'react';
import type { Layer } from '../../types/PosterSchema';
import { LayerPanel } from './LayerPanel';
import { PropertyPanel } from './PropertyPanel';
import { ToolButton } from './ToolButton';

interface EditorSidebarProps {
  // 历史操作
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;

  // 图层相关
  layers: Layer[];
  selectedLayerId: string | null;
  lockedLayerIds: Set<string>;
  hiddenLayerIds: Set<string>;
  onSelectLayer: (layerId: string) => void;
  onToggleLock: (layerId: string) => void;
  onToggleVisibility: (layerId: string) => void;
  onDeleteLayer: (layerId: string) => void;
  onReorderLayer: (layerId: string, direction: 'up' | 'down') => void;

  // 属性编辑
  selectedLayer: Layer | null;
  onUpdateProperty: (layerId: string, property: string, value: any) => void;
}

export const EditorSidebar: React.FC<EditorSidebarProps> = ({
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  layers,
  selectedLayerId,
  lockedLayerIds,
  hiddenLayerIds,
  onSelectLayer,
  onToggleLock,
  onToggleVisibility,
  onDeleteLayer,
  onReorderLayer,
  selectedLayer,
  onUpdateProperty,
}) => {
  return (
    <div
      style={{
        width: '340px',
        height: '100%',
        backgroundColor: '#FFFFFF',
        borderLeft: '1px solid #E5E7EB',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* 工具栏 */}
      <div
        style={{
          padding: '20px',
          borderBottom: '1px solid #E5E7EB',
          backgroundColor: '#FAFBFC',
        }}
      >
        <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
          <ToolButton onClick={onUndo} disabled={!canUndo} title="撤销 (Ctrl+Z)">
            <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z" />
              <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z" />
            </svg>
            <span>撤销</span>
          </ToolButton>
          <ToolButton onClick={onRedo} disabled={!canRedo} title="重做 (Ctrl+Shift+Z)">
            <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 3a5 5 0 1 1-4.546 2.914.5.5 0 0 0-.908-.417A6 6 0 1 0 8 2v1z" />
              <path d="M8 4.466V.534a.25.25 0 0 0-.41-.192L5.23 2.308a.25.25 0 0 0 0 .384l2.36 1.966A.25.25 0 0 0 8 4.466z" />
            </svg>
            <span>重做</span>
          </ToolButton>
        </div>

      </div>

      {/* 属性面板（选中时显示） */}
      {selectedLayer && (
        <div style={{ flex: '0 0 auto', borderBottom: '1px solid #E5E7EB', maxHeight: '40vh', overflowY: 'auto' }}>
          <PropertyPanel
            layer={selectedLayer}
            onUpdateProperty={onUpdateProperty}
            isInSidebar={true}
          />
        </div>
      )}

      {/* 图层面板 */}
      <div style={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
        <LayerPanel
          layers={layers}
          selectedLayerId={selectedLayerId}
          lockedLayerIds={lockedLayerIds}
          hiddenLayerIds={hiddenLayerIds}
          onSelectLayer={onSelectLayer}
          onToggleLock={onToggleLock}
          onToggleVisibility={onToggleVisibility}
          onDeleteLayer={onDeleteLayer}
          onReorderLayer={onReorderLayer}
          isInSidebar={true}
        />
      </div>
    </div>
  );
};

