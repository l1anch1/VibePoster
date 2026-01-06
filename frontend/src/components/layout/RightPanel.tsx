/**
 * 右侧面板组件
 * 
 * 包含：画布展示区 + 编辑面板（编辑模式）
 */

import React from 'react';
import type { PosterData } from '../../types/PosterSchema';
import { EditorLayout } from '../editor/EditorLayout';
import { PosterLayer } from '../poster/PosterLayer';

interface RightPanelProps {
  data: PosterData;
  scale: number;
  isEditMode: boolean;
  onDataChange: (data: PosterData) => void;
}

export const RightPanel: React.FC<RightPanelProps> = ({
  data,
  scale,
  isEditMode,
  onDataChange,
}) => {
  return (
    <div
      style={{
        flex: 1,
        height: '100%',
        backgroundColor: '#F9FAFB',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {isEditMode ? (
        /* 编辑模式：使用 EditorLayout */
        <EditorLayout data={data} scale={scale} onDataChange={onDataChange} />
      ) : (
        /* 查看模式：画布居中显示 + 编辑按钮 */
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
            position: 'relative',
            overflow: 'hidden', // 防止画布超出
          }}
        >
          {/* 画布包装器：用于隔离 scale 的影响 */}
          <div
            style={{
              position: 'relative',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            {/* 画布 */}
            <div
              style={{
                position: 'relative',
                width: `${data.canvas.width}px`,
                height: `${data.canvas.height}px`,
                backgroundColor: data.canvas.backgroundColor,
                transform: `scale(${scale})`,
                transformOrigin: 'center center',
                boxShadow:
                  '0 25px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.05)',
                transition: 'transform 0.3s ease',
                boxSizing: 'border-box',
                overflow: 'hidden',
                borderRadius: '2px',
              }}
            >
              {/* 渲染所有图层 */}
              {data.layers.map((layer) => (
                <PosterLayer key={layer.id} layer={layer} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

