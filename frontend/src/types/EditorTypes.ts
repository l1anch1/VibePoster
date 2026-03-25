/**
 * 编辑器类型定义
 */

export type ResizeDirection =
    | 'n' | 's' | 'e' | 'w'
    | 'ne' | 'nw' | 'se' | 'sw'
    | null;

export interface Transform {
    x: number;
    y: number;
    width: number;
    height: number;
    rotation: number;
}

