/**
 * useKeyboardShortcuts — 编辑器全局快捷键
 *
 * 支持：
 * - Escape: 退出文本编辑 / 取消图层选择 / 关闭导出面板
 * - Delete / Backspace: 删除选中图层（焦点不在 input/textarea 时）
 * - Cmd+Z / Ctrl+Z: 撤销
 * - Cmd+Shift+Z / Ctrl+Shift+Z: 重做
 */

import { useEffect } from 'react';

interface ShortcutHandlers {
  selectedLayerId: string | null;
  editingLayerId: string | null;
  onClearEditing: () => void;
  onClearSelection: () => void;
  onCloseExport: () => void;
  onDeleteLayer: (layerId: string) => void;
  onUndo: () => void;
  onRedo: () => void;
}

export function useKeyboardShortcuts({
  selectedLayerId,
  editingLayerId,
  onClearEditing,
  onClearSelection,
  onCloseExport,
  onDeleteLayer,
  onUndo,
  onRedo,
}: ShortcutHandlers): void {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const tag = document.activeElement?.tagName;
      const isEditing = tag === 'INPUT' || tag === 'TEXTAREA';

      // Undo / Redo (works even when editing text inputs)
      if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
        e.preventDefault();
        if (e.shiftKey) {
          onRedo();
        } else {
          onUndo();
        }
        return;
      }

      if (e.key === 'Escape') {
        if (editingLayerId) {
          onClearEditing();
        } else if (selectedLayerId) {
          onClearSelection();
        }
        onCloseExport();
      }

      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedLayerId && !isEditing) {
        onDeleteLayer(selectedLayerId);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedLayerId, editingLayerId, onClearEditing, onClearSelection, onCloseExport, onDeleteLayer, onUndo, onRedo]);
}
