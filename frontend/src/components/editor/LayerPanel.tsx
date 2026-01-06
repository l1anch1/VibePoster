/**
 * 图层管理面板
 * 
 * 显示所有图层，支持选择、显示/隐藏、锁定、删除、排序等操作
 */

import React from 'react';
import type { Layer } from '../../types/PosterSchema';

interface LayerPanelProps {
  layers: Layer[];
  selectedLayerId: string | null;
  lockedLayerIds: Set<string>;
  hiddenLayerIds: Set<string>;
  onSelectLayer: (layerId: string) => void;
  onToggleLock: (layerId: string) => void;
  onToggleVisibility: (layerId: string) => void;
  onDeleteLayer: (layerId: string) => void;
  onReorderLayer: (layerId: string, direction: 'up' | 'down') => void;
  onClose?: () => void;
  isInSidebar?: boolean;
}

export const LayerPanel: React.FC<LayerPanelProps> = ({
  layers,
  selectedLayerId,
  lockedLayerIds,
  hiddenLayerIds,
  onSelectLayer,
  onToggleLock,
  onToggleVisibility,
  onDeleteLayer,
  onReorderLayer,
  onClose,
  isInSidebar = false,
}) => {
  // 反转图层顺序（数组最后的在最上面）
  const displayLayers = [...layers].reverse();

  // 侧边栏模式样式
  const containerStyle = isInSidebar
    ? {
        width: '100%',
        height: '100%',
        backgroundColor: '#FFFFFF',
        display: 'flex' as const,
        flexDirection: 'column' as const,
        overflow: 'hidden' as const,
      }
    : {
        position: 'absolute' as const,
        right: '24px',
        top: '24px',
        width: '280px',
        maxHeight: 'calc(100vh - 48px)',
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        boxShadow: '0 10px 40px rgba(0,0,0,0.15), 0 0 0 1px rgba(0,0,0,0.05)',
        display: 'flex' as const,
        flexDirection: 'column' as const,
        overflow: 'hidden' as const,
        zIndex: 100,
      };

  return (
    <div style={containerStyle}>
      {/* 标题栏 */}
      <div
        style={{
          padding: isInSidebar ? '16px 20px' : '18px 20px',
          borderBottom: '1px solid #E5E7EB',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: isInSidebar ? '#F9FAFB' : '#FAFBFC',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {!isInSidebar && (
            <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor">
              <path d="M2 4h12v2H2V4zm0 4h12v2H2V8zm0 4h12v2H2v-2z" />
            </svg>
          )}
          <h3
            style={{
              margin: 0,
              fontSize: isInSidebar ? '13px' : '15px',
              fontWeight: 600,
              color: isInSidebar ? '#6B7280' : '#111827',
              textTransform: isInSidebar ? 'uppercase' : 'none',
              letterSpacing: isInSidebar ? '0.5px' : '0',
            }}
          >
            图层列表
          </h3>
          <span
            style={{
              fontSize: '12px',
              color: '#6B7280',
              backgroundColor: '#F3F4F6',
              padding: '2px 8px',
              borderRadius: '4px',
            }}
          >
            {layers.length}
          </span>
        </div>
        {!isInSidebar && onClose && (
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '6px',
              color: '#6B7280',
              display: 'flex',
              alignItems: 'center',
              borderRadius: '4px',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F3F4F6';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor">
              <path d="M4.293 4.293a1 1 0 011.414 0L8 6.586l2.293-2.293a1 1 0 111.414 1.414L9.414 8l2.293 2.293a1 1 0 01-1.414 1.414L8 9.414l-2.293 2.293a1 1 0 01-1.414-1.414L6.586 8 4.293 5.707a1 1 0 010-1.414z" />
            </svg>
          </button>
        )}
      </div>

      {/* 图层列表 */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '8px',
        }}
      >
        {displayLayers.length === 0 ? (
          <div
            style={{
              padding: '40px 20px',
              textAlign: 'center',
              color: '#9CA3AF',
              fontSize: '13px',
            }}
          >
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              style={{ margin: '0 auto 12px' }}
            >
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M3 9h18M9 21V9" />
            </svg>
            <div>暂无图层</div>
            <div style={{ fontSize: '11px', marginTop: '4px' }}>
              生成海报后将显示图层
            </div>
          </div>
        ) : (
          displayLayers.map((layer, index) => {
            const isSelected = layer.id === selectedLayerId;
            const isLocked = lockedLayerIds.has(layer.id);
            const isHidden = hiddenLayerIds.has(layer.id);
            const actualIndex = layers.length - 1 - index;

            return (
              <div
                key={layer.id}
                onClick={() => onSelectLayer(layer.id)}
                style={{
                  padding: '10px 12px',
                  marginBottom: '4px',
                  backgroundColor: isSelected ? '#EFF6FF' : '#FFFFFF',
                  border: isSelected ? '2px solid #3B82F6' : '1px solid #E5E7EB',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = '#F9FAFB';
                    e.currentTarget.style.borderColor = '#D1D5DB';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = '#FFFFFF';
                    e.currentTarget.style.borderColor = '#E5E7EB';
                  }
                }}
              >
                {/* 图层图标 */}
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    backgroundColor: '#F3F4F6',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    color: layer.type === 'text' ? '#3B82F6' : '#10B981',
                  }}
                >
                  {layer.type === 'text' ? (
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M3 2h10v2H9v10H7V4H3V2z" />
                    </svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                      <rect x="2" y="2" width="12" height="12" rx="2" />
                      <circle cx="6" cy="6" r="1" fill="#FFFFFF" />
                      <path d="M2 11l3-3 2 2 3-4 4 5v1a2 2 0 01-2 2H4a2 2 0 01-2-2v-1z" fill="#FFFFFF" />
                    </svg>
                  )}
                </div>

                {/* 图层信息 */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: '13px',
                      fontWeight: 500,
                      color: '#111827',
                      marginBottom: '2px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      opacity: isHidden ? 0.5 : 1,
                    }}
                  >
                    {layer.name}
                  </div>
                  <div
                    style={{
                      fontSize: '11px',
                      color: '#6B7280',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {layer.type === 'text'
                      ? layer.content.substring(0, 20) + (layer.content.length > 20 ? '...' : '')
                      : `${Math.round(layer.width)} × ${Math.round(layer.height)}`}
                  </div>
                </div>

                {/* 操作按钮组 */}
                <div
                  style={{
                    display: 'flex',
                    gap: '4px',
                    flexShrink: 0,
                  }}
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* 显示/隐藏按钮 */}
                  <button
                    onClick={() => onToggleVisibility(layer.id)}
                    title={isHidden ? '显示' : '隐藏'}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '4px',
                      color: isHidden ? '#9CA3AF' : '#6B7280',
                      display: 'flex',
                      borderRadius: '4px',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#F3F4F6';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    {isHidden ? (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 00-2.79.588l.77.771A5.944 5.944 0 018 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0114.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z" />
                        <path d="M11.297 9.176a3.5 3.5 0 00-4.474-4.474l.823.823a2.5 2.5 0 012.829 2.829l.822.822zm-2.943 1.299l.822.822a3.5 3.5 0 01-4.474-4.474l.823.823a2.5 2.5 0 002.829 2.829z" />
                        <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 001.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 018 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884l-12-12 .708-.708 12 12-.708.708z" />
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0114.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 011.172 8c.058-.087.122-.183.195-.288.335-.48.83-1.12 1.465-1.755C4.121 4.668 5.881 3.5 8 3.5zM0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8zm8 3.5a3.5 3.5 0 100-7 3.5 3.5 0 000 7zm0-1a2.5 2.5 0 110-5 2.5 2.5 0 010 5z" />
                      </svg>
                    )}
                  </button>

                  {/* 锁定/解锁按钮 */}
                  <button
                    onClick={() => onToggleLock(layer.id)}
                    title={isLocked ? '解锁' : '锁定'}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '4px',
                      color: isLocked ? '#EF4444' : '#6B7280',
                      display: 'flex',
                      borderRadius: '4px',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#F3F4F6';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    {isLocked ? (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 1a2 2 0 012 2v4H6V3a2 2 0 012-2zm3 6V3a3 3 0 00-6 0v4a2 2 0 00-2 2v5a2 2 0 002 2h6a2 2 0 002-2V9a2 2 0 00-2-2z" />
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 1a2 2 0 012 2v4H6V3a2 2 0 012-2zm3 6V3a3 3 0 00-6 0v4a2 2 0 00-2 2v5a2 2 0 002 2h6a2 2 0 002-2V9a2 2 0 00-2-2zM5 8h6a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1V9a1 1 0 011-1z" />
                      </svg>
                    )}
                  </button>

                  {/* 上移按钮 */}
                  <button
                    onClick={() => onReorderLayer(layer.id, 'up')}
                    disabled={actualIndex === layers.length - 1}
                    title="上移"
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: actualIndex === layers.length - 1 ? 'not-allowed' : 'pointer',
                      padding: '4px',
                      color: actualIndex === layers.length - 1 ? '#D1D5DB' : '#6B7280',
                      display: 'flex',
                      borderRadius: '4px',
                      opacity: actualIndex === layers.length - 1 ? 0.5 : 1,
                    }}
                    onMouseEnter={(e) => {
                      if (actualIndex !== layers.length - 1) {
                        e.currentTarget.style.backgroundColor = '#F3F4F6';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M8 3.293l4.146 4.147-.707.707L8 4.707 4.561 8.147l-.707-.707L8 3.293z" />
                      <path d="M8 9.293l4.146 4.147-.707.707L8 10.707l-3.439 3.44-.707-.707L8 9.293z" />
                    </svg>
                  </button>

                  {/* 下移按钮 */}
                  <button
                    onClick={() => onReorderLayer(layer.id, 'down')}
                    disabled={actualIndex === 0}
                    title="下移"
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: actualIndex === 0 ? 'not-allowed' : 'pointer',
                      padding: '4px',
                      color: actualIndex === 0 ? '#D1D5DB' : '#6B7280',
                      display: 'flex',
                      borderRadius: '4px',
                      opacity: actualIndex === 0 ? 0.5 : 1,
                    }}
                    onMouseEnter={(e) => {
                      if (actualIndex !== 0) {
                        e.currentTarget.style.backgroundColor = '#F3F4F6';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" transform="rotate(180)">
                      <path d="M8 3.293l4.146 4.147-.707.707L8 4.707 4.561 8.147l-.707-.707L8 3.293z" />
                      <path d="M8 9.293l4.146 4.147-.707.707L8 10.707l-3.439 3.44-.707-.707L8 9.293z" />
                    </svg>
                  </button>

                  {/* 删除按钮 */}
                  <button
                    onClick={() => {
                      if (window.confirm(`确定要删除图层"${layer.name}"吗？`)) {
                        onDeleteLayer(layer.id);
                      }
                    }}
                    title="删除"
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '4px',
                      color: '#EF4444',
                      display: 'flex',
                      borderRadius: '4px',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#FEE2E2';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M5.5 5.5A.5.5 0 016 6v6a.5.5 0 01-1 0V6a.5.5 0 01.5-.5zm2.5 0a.5.5 0 01.5.5v6a.5.5 0 01-1 0V6a.5.5 0 01.5-.5zm3 .5a.5.5 0 00-1 0v6a.5.5 0 001 0V6z" />
                      <path fillRule="evenodd" d="M14.5 3a1 1 0 01-1 1H13v9a2 2 0 01-2 2H5a2 2 0 01-2-2V4h-.5a1 1 0 01-1-1V2a1 1 0 011-1H6a1 1 0 011-1h2a1 1 0 011 1h3.5a1 1 0 011 1v1zM4.118 4L4 4.059V13a1 1 0 001 1h6a1 1 0 001-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z" />
                    </svg>
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

