/**
 * 属性编辑面板
 * 
 * 编辑选中图层的属性（颜色、字体、大小等）
 */

import React from 'react';
import type { Layer } from '../../types/PosterSchema';
import { isTextLayer } from '../../utils/editorUtils';

interface PropertyPanelProps {
    layer: Layer | null;
    onUpdateProperty: (layerId: string, property: string, value: any) => void;
    onClose?: () => void;
    isInSidebar?: boolean;
}

export const PropertyPanel: React.FC<PropertyPanelProps> = ({
    layer,
    onUpdateProperty,
    onClose,
    isInSidebar = false,
}) => {
    if (!layer) {
        return null;
    }

    const handleChange = (property: string, value: any) => {
        onUpdateProperty(layer.id, property, value);
    };

    // 侧边栏模式样式
    const containerStyle = isInSidebar
        ? {
              width: '100%',
              backgroundColor: '#FFFFFF',
              display: 'flex' as const,
              flexDirection: 'column' as const,
              overflow: 'hidden' as const,
          }
        : {
              position: 'absolute' as const,
              right: '320px',
              top: '24px',
              width: '260px',
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
            {/* 标题栏（非侧边栏模式） */}
            {!isInSidebar && onClose && (
                <div
                    style={{
                        padding: '18px 20px',
                        borderBottom: '1px solid #E5E7EB',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        backgroundColor: '#FAFBFC',
                    }}
                >
                    <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 600, color: '#111827' }}>
                        属性
                    </h3>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: '6px',
                            color: '#6B7280',
                            display: 'flex',
                            borderRadius: '4px',
                        }}
                    >
                        <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M4.293 4.293a1 1 0 011.414 0L8 6.586l2.293-2.293a1 1 0 111.414 1.414L9.414 8l2.293 2.293a1 1 0 01-1.414 1.414L8 9.414l-2.293 2.293a1 1 0 01-1.414-1.414L6.586 8 4.293 5.707a1 1 0 010-1.414z" />
                        </svg>
                    </button>
                </div>
            )}

            {/* 标题栏（侧边栏模式） */}
            {isInSidebar && (
                <div
                    style={{
                        padding: '16px 20px',
                        borderBottom: '1px solid #E5E7EB',
                        backgroundColor: '#F9FAFB',
                    }}
                >
                    <h3
                        style={{
                            margin: 0,
                            fontSize: '13px',
                            fontWeight: 600,
                            color: '#6B7280',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                        }}
                    >
                        属性编辑
                    </h3>
                </div>
            )}

            {/* 属性列表 */}
            <div
                style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: isInSidebar ? '20px' : '16px',
                }}
            >
                {/* 通用属性 */}
                <PropertySection title="位置和大小">
                    <PropertyRow label="X">
                        <input
                            type="number"
                            value={Math.round(layer.x)}
                            onChange={(e) => handleChange('x', parseFloat(e.target.value) || 0)}
                            style={inputStyle}
                        />
                    </PropertyRow>
                    <PropertyRow label="Y">
                        <input
                            type="number"
                            value={Math.round(layer.y)}
                            onChange={(e) => handleChange('y', parseFloat(e.target.value) || 0)}
                            style={inputStyle}
                        />
                    </PropertyRow>
                    <PropertyRow label="宽度">
                        <input
                            type="number"
                            value={Math.round(layer.width)}
                            onChange={(e) => handleChange('width', parseFloat(e.target.value) || 1)}
                            style={inputStyle}
                        />
                    </PropertyRow>
                    <PropertyRow label="高度">
                        <input
                            type="number"
                            value={Math.round(layer.height)}
                            onChange={(e) => handleChange('height', parseFloat(e.target.value) || 1)}
                            style={inputStyle}
                        />
                    </PropertyRow>
                </PropertySection>

                <PropertySection title="外观">
                    <PropertyRow label="旋转">
                        <input
                            type="number"
                            value={layer.rotation}
                            onChange={(e) => handleChange('rotation', parseFloat(e.target.value) || 0)}
                            style={inputStyle}
                            min="0"
                            max="360"
                        />
                    </PropertyRow>
                    <PropertyRow label="透明度">
                        <input
                            type="range"
                            value={layer.opacity}
                            onChange={(e) => handleChange('opacity', parseFloat(e.target.value))}
                            style={{ width: '100%' }}
                            min="0"
                            max="1"
                            step="0.01"
                        />
                        <span style={{ fontSize: '12px', color: '#6B7280' }}>
                            {Math.round(layer.opacity * 100)}%
                        </span>
                    </PropertyRow>
                </PropertySection>

                {/* 文本专属属性 */}
                {isTextLayer(layer) && (
                    <>
                        <PropertySection title="文本">
                            <PropertyRow label="内容">
                                <textarea
                                    value={layer.content}
                                    onChange={(e) => handleChange('content', e.target.value)}
                                    style={{
                                        ...inputStyle,
                                        minHeight: '60px',
                                        resize: 'vertical',
                                        fontFamily: 'inherit',
                                    }}
                                />
                            </PropertyRow>
                        </PropertySection>

                        <PropertySection title="字体">
                            <PropertyRow label="字号">
                                <input
                                    type="number"
                                    value={layer.fontSize}
                                    onChange={(e) => handleChange('fontSize', parseFloat(e.target.value) || 12)}
                                    style={inputStyle}
                                    min="8"
                                    max="200"
                                />
                            </PropertyRow>
                            <PropertyRow label="颜色">
                                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                    <input
                                        type="color"
                                        value={layer.color}
                                        onChange={(e) => handleChange('color', e.target.value)}
                                        style={{ width: '40px', height: '30px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
                                    />
                                    <input
                                        type="text"
                                        value={layer.color}
                                        onChange={(e) => handleChange('color', e.target.value)}
                                        style={{ ...inputStyle, flex: 1 }}
                                    />
                                </div>
                            </PropertyRow>
                            <PropertyRow label="对齐">
                                <select
                                    value={layer.textAlign}
                                    onChange={(e) => handleChange('textAlign', e.target.value)}
                                    style={inputStyle}
                                >
                                    <option value="left">左对齐</option>
                                    <option value="center">居中</option>
                                    <option value="right">右对齐</option>
                                </select>
                            </PropertyRow>
                            <PropertyRow label="粗细">
                                <select
                                    value={layer.fontWeight}
                                    onChange={(e) => handleChange('fontWeight', e.target.value)}
                                    style={inputStyle}
                                >
                                    <option value="normal">正常</option>
                                    <option value="bold">加粗</option>
                                </select>
                            </PropertyRow>
                        </PropertySection>
                    </>
                )}
            </div>
        </div>
    );
};

// 属性区块组件
const PropertySection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
    <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '12px', fontWeight: 600, color: '#6B7280', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            {title}
        </div>
        {children}
    </div>
);

// 属性行组件
const PropertyRow: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
    <div style={{ marginBottom: '12px' }}>
        <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '6px' }}>{label}</div>
        {children}
    </div>
);

// 通用输入框样式
const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '8px 10px',
    border: '1px solid #E5E7EB',
    borderRadius: '6px',
    fontSize: '13px',
    color: '#111827',
    backgroundColor: '#FFFFFF',
    boxSizing: 'border-box',
};

