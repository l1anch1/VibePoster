/**
 * useKeyboardShortcuts — 编辑器全局快捷键
 *
 * 当前支持：
 * - Escape: 退出文本编辑 / 取消图层选择 / 关闭导出面板
 * - Delete / Backspace: 删除选中图层（焦点不在 input/textarea 时）
 */

import { useEffect } from 'react';

interface ShortcutHandlers {
  selectedLayerId: string | null;
  editingLayerId: string | null;
  onClearEditing: () => void;
  onClearSelection: () => void;
  onCloseExport: () => void;
  onDeleteLayer: (layerId: string) => void;
}

export function useKeyboardShortcuts({
  selectedLayerId,
  editingLayerId,
  onClearEditing,
  onClearSelection,
  onCloseExport,
  onDeleteLayer,
}: ShortcutHandlers): void {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (editingLayerId) {
          onClearEditing();
        } else if (selectedLayerId) {
          onClearSelection();
        }
        onCloseExport();
      }

      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedLayerId) {
        const tag = document.activeElement?.tagName;
        if (tag !== 'INPUT' && tag !== 'TEXTAREA') {
          onDeleteLayer(selectedLayerId);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedLayerId, editingLayerId, onClearEditing, onClearSelection, onCloseExport, onDeleteLayer]);
}
