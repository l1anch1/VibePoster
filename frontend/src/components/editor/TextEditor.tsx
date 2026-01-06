/**
 * 文本编辑器组件
 * 
 * 双击文本图层时显示，支持直接编辑
 */

import React, { useState, useRef, useEffect } from 'react';
import type { Layer } from '../../types/PosterSchema';
import { isTextLayer } from '../../utils/editorUtils';

interface TextEditorProps {
  layer: Layer;
  scale: number;
  onUpdate: (content: string) => void;
  onClose: () => void;
}

export const TextEditor: React.FC<TextEditorProps> = ({
  layer,
  scale,
  onUpdate,
  onClose,
}) => {
  // ✅ Hooks 必须在组件顶层调用（在任何条件判断之前）
  const isValidTextLayer = isTextLayer(layer) && layer.content;
  const [content, setContent] = useState(layer.content || '');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // 自动聚焦（仅在有效时）
    if (isValidTextLayer && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.select();
    }
  }, [isValidTextLayer]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      // Ctrl/Cmd + Enter 保存
      onUpdate(content);
      onClose();
    }
    // 阻止事件冒泡，避免触发其他快捷键
    e.stopPropagation();
  };

  const handleBlur = () => {
    // 失焦时保存
    if (content !== layer.content) {
      onUpdate(content);
    }
    onClose();
  };

  // ✅ 类型检查：返回 null 但 Hooks 已经调用完毕
  if (!isValidTextLayer) {
    console.warn('TextEditor: layer is not a valid text layer', layer);
    return null;
  }

  // 确保布局属性有效
  const safeX = Math.max(0, layer.x || 0);
  const safeY = Math.max(0, layer.y || 0);
  const safeWidth = Math.max(100, layer.width || 200);
  const safeHeight = Math.max(50, layer.height || 100);

  return (
    <div
      style={{
        position: 'absolute',
        left: `${safeX}px`,
        top: `${safeY}px`,
        width: `${safeWidth}px`,
        height: `${safeHeight}px`,
        zIndex: 10000,
        pointerEvents: 'all',
      }}
      onClick={(e) => e.stopPropagation()}
    >
      <textarea
        ref={textareaRef}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={handleBlur}
        style={{
          width: '100%',
          height: '100%',
          padding: '8px',
          fontSize: `${layer.fontSize || 16}px`,
          fontFamily: layer.fontFamily || 'Arial',
          fontWeight: layer.fontWeight || 'normal',
          color: layer.color || '#000000',
          textAlign: (layer.textAlign || 'left') as 'left' | 'center' | 'right',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          border: '2px solid #3B82F6',
          borderRadius: '4px',
          resize: 'none',
          outline: 'none',
          boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
          lineHeight: 1.4,
          boxSizing: 'border-box',
        }}
      />
    </div>
  );
};

