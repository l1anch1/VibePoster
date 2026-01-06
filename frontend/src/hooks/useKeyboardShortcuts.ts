/**
 * 键盘快捷键 Hook
 * 
 * 处理编辑器的键盘快捷键
 */

import { useEffect, useCallback } from 'react';

export interface KeyboardShortcutHandlers {
  onUndo?: () => void;
  onRedo?: () => void;
  onDelete?: () => void;
  onCopy?: () => void;
  onPaste?: () => void;
  onSelectAll?: () => void;
  onDeselect?: () => void;
  onDuplicate?: () => void;
  onSave?: () => void;
}

export function useKeyboardShortcuts(handlers: KeyboardShortcutHandlers, enabled: boolean = true) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const cmdOrCtrl = isMac ? event.metaKey : event.ctrlKey;

      // 阻止某些默认行为
      const shouldPreventDefault = () => {
        // Ctrl/Cmd + Z (撤销)
        if (cmdOrCtrl && event.key.toLowerCase() === 'z' && !event.shiftKey) {
          return true;
        }
        // Ctrl/Cmd + Shift + Z (重做)
        if (cmdOrCtrl && event.shiftKey && event.key.toLowerCase() === 'z') {
          return true;
        }
        // Ctrl/Cmd + C (复制)
        if (cmdOrCtrl && event.key.toLowerCase() === 'c') {
          return true;
        }
        // Ctrl/Cmd + V (粘贴)
        if (cmdOrCtrl && event.key.toLowerCase() === 'v') {
          return true;
        }
        // Ctrl/Cmd + D (复制)
        if (cmdOrCtrl && event.key.toLowerCase() === 'd') {
          return true;
        }
        // Ctrl/Cmd + S (保存)
        if (cmdOrCtrl && event.key.toLowerCase() === 's') {
          return true;
        }
        return false;
      };

      if (shouldPreventDefault()) {
        event.preventDefault();
      }

      // Ctrl/Cmd + Z (撤销)
      if (cmdOrCtrl && event.key.toLowerCase() === 'z' && !event.shiftKey) {
        handlers.onUndo?.();
        return;
      }

      // Ctrl/Cmd + Shift + Z 或 Ctrl/Cmd + Y (重做)
      if (
        (cmdOrCtrl && event.shiftKey && event.key.toLowerCase() === 'z') ||
        (cmdOrCtrl && event.key.toLowerCase() === 'y')
      ) {
        handlers.onRedo?.();
        return;
      }

      // Delete 或 Backspace (删除)
      if (event.key === 'Delete' || event.key === 'Backspace') {
        // 检查是否在输入框中
        const target = event.target as HTMLElement;
        if (
          target.tagName === 'INPUT' ||
          target.tagName === 'TEXTAREA' ||
          target.isContentEditable
        ) {
          return; // 在输入框中时不删除图层
        }
        handlers.onDelete?.();
        return;
      }

      // Ctrl/Cmd + C (复制)
      if (cmdOrCtrl && event.key.toLowerCase() === 'c') {
        handlers.onCopy?.();
        return;
      }

      // Ctrl/Cmd + V (粘贴)
      if (cmdOrCtrl && event.key.toLowerCase() === 'v') {
        handlers.onPaste?.();
        return;
      }

      // Ctrl/Cmd + A (全选)
      if (cmdOrCtrl && event.key.toLowerCase() === 'a') {
        event.preventDefault();
        handlers.onSelectAll?.();
        return;
      }

      // Escape (取消选择)
      if (event.key === 'Escape') {
        handlers.onDeselect?.();
        return;
      }

      // Ctrl/Cmd + D (复制)
      if (cmdOrCtrl && event.key.toLowerCase() === 'd') {
        handlers.onDuplicate?.();
        return;
      }

      // Ctrl/Cmd + S (保存)
      if (cmdOrCtrl && event.key.toLowerCase() === 's') {
        handlers.onSave?.();
        return;
      }
    },
    [handlers, enabled]
  );

  useEffect(() => {
    if (!enabled) return;

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown, enabled]);
}

