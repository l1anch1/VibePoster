/**
 * 编辑器类型定义
 * 
 * 定义在线编辑功能所需的所有类型
 */

import type { Layer, PosterData } from './PosterSchema';

/**
 * 编辑模式
 */
export type EditMode = 'select' | 'text-edit' | 'resize';

/**
 * 调整大小的方向
 */
export type ResizeDirection =
    | 'n' | 's' | 'e' | 'w'           // 上下左右
    | 'ne' | 'nw' | 'se' | 'sw'       // 四个角
    | null;

/**
 * 编辑器状态
 */
export interface EditorState {
    // 当前选中的图层 ID
    selectedLayerId: string | null;

    // 编辑模式
    editMode: EditMode;

    // 是否正在拖拽
    isDragging: boolean;

    // 是否正在调整大小
    isResizing: boolean;
    resizeDirection: ResizeDirection;

    // 是否显示图层面板
    showLayerPanel: boolean;

    // 是否显示属性面板
    showPropertyPanel: boolean;

    // 锁定的图层 ID 列表
    lockedLayerIds: Set<string>;

    // 隐藏的图层 ID 列表
    hiddenLayerIds: Set<string>;

    // 剪贴板（用于复制粘贴）
    clipboard: Layer | null;
}

/**
 * 历史记录项
 */
export interface HistoryEntry {
    data: PosterData;
    timestamp: number;
    description: string;
}

/**
 * 历史记录状态
 */
export interface HistoryState {
    past: HistoryEntry[];
    present: PosterData;
    future: HistoryEntry[];
    // 最大历史记录数
    maxHistory: number;
}

/**
 * 变换操作
 */
export interface Transform {
    x: number;
    y: number;
    width: number;
    height: number;
    rotation: number;
}

/**
 * 拖拽状态
 */
export interface DragState {
    isDragging: boolean;
    layerId: string | null;
    startX: number;
    startY: number;
    offsetX: number;
    offsetY: number;
}

/**
 * 调整大小状态
 */
export interface ResizeState {
    isResizing: boolean;
    layerId: string | null;
    direction: ResizeDirection;
    startX: number;
    startY: number;
    startWidth: number;
    startHeight: number;
    startLayerX: number;
    startLayerY: number;
}

/**
 * 选择框
 */
export interface SelectionBox {
    x: number;
    y: number;
    width: number;
    height: number;
}

/**
 * 键盘快捷键配置
 */
export interface KeyboardShortcuts {
    undo: string;           // Ctrl+Z / Cmd+Z
    redo: string;           // Ctrl+Shift+Z / Cmd+Shift+Z
    delete: string;         // Delete / Backspace
    copy: string;           // Ctrl+C / Cmd+C
    paste: string;          // Ctrl+V / Cmd+V
    selectAll: string;      // Ctrl+A / Cmd+A
    deselect: string;       // Escape
    duplicate: string;      // Ctrl+D / Cmd+D
}

/**
 * 属性更新参数（部分更新）
 */
export type LayerPropertyUpdate = Partial<{
    // 文本属性
    content: string;
    fontSize: number;
    color: string;
    fontFamily: string;
    textAlign: 'left' | 'center' | 'right';
    fontWeight: 'normal' | 'bold';

    // 通用属性
    x: number;
    y: number;
    width: number;
    height: number;
    rotation: number;
    opacity: number;

    // 图片属性
    src: string;
}>;

/**
 * 编辑器动作类型
 */
export type EditorAction =
    | { type: 'SELECT_LAYER'; layerId: string | null }
    | { type: 'SET_EDIT_MODE'; mode: EditMode }
    | { type: 'START_DRAG'; layerId: string; startX: number; startY: number }
    | { type: 'UPDATE_DRAG'; x: number; y: number }
    | { type: 'END_DRAG' }
    | { type: 'START_RESIZE'; layerId: string; direction: ResizeDirection; startX: number; startY: number }
    | { type: 'UPDATE_RESIZE'; x: number; y: number }
    | { type: 'END_RESIZE' }
    | { type: 'TOGGLE_LAYER_PANEL' }
    | { type: 'TOGGLE_PROPERTY_PANEL' }
    | { type: 'TOGGLE_LAYER_LOCK'; layerId: string }
    | { type: 'TOGGLE_LAYER_VISIBILITY'; layerId: string }
    | { type: 'COPY_LAYER' }
    | { type: 'PASTE_LAYER' }
    | { type: 'DELETE_LAYER'; layerId: string }
    | { type: 'DUPLICATE_LAYER'; layerId: string };

/**
 * 编辑器配置
 */
export interface EditorConfig {
    // 网格吸附
    snapToGrid: boolean;
    gridSize: number;

    // 显示辅助线
    showGuides: boolean;

    // 显示标尺
    showRuler: boolean;

    // 最小图层尺寸
    minLayerWidth: number;
    minLayerHeight: number;

    // 选中时的边框颜色
    selectionColor: string;

    // 调整大小手柄大小
    resizeHandleSize: number;
}

