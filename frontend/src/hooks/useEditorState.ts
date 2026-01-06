/**
 * 编辑器状态 Hook
 * 
 * 管理编辑器的核心状态（选中、锁定、隐藏等）
 */

import { useState, useCallback } from 'react';
import type { Layer } from '../types/PosterSchema';
import type { EditMode } from '../types/EditorTypes';

export function useEditorState() {
    const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null);
    const [editMode, setEditMode] = useState<EditMode>('select');
    const [lockedLayerIds, setLockedLayerIds] = useState<Set<string>>(new Set());
    const [hiddenLayerIds, setHiddenLayerIds] = useState<Set<string>>(new Set());
    const [showLayerPanel, setShowLayerPanel] = useState(true);
    const [showPropertyPanel, setShowPropertyPanel] = useState(true);
    const [clipboard, setClipboard] = useState<Layer | null>(null);

    /**
     * 选中图层
     */
    const selectLayer = useCallback((layerId: string | null) => {
        setSelectedLayerId(layerId);
        if (layerId) {
            setEditMode('select');
        }
    }, []);

    /**
     * 切换图层锁定状态
     */
    const toggleLayerLock = useCallback((layerId: string) => {
        setLockedLayerIds((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(layerId)) {
                newSet.delete(layerId);
            } else {
                newSet.add(layerId);
            }
            return newSet;
        });
    }, []);

    /**
     * 切换图层可见性
     */
    const toggleLayerVisibility = useCallback((layerId: string) => {
        setHiddenLayerIds((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(layerId)) {
                newSet.delete(layerId);
            } else {
                newSet.add(layerId);
            }
            return newSet;
        });
    }, []);

    /**
     * 检查图层是否被锁定
     */
    const isLayerLocked = useCallback(
        (layerId: string) => {
            return lockedLayerIds.has(layerId);
        },
        [lockedLayerIds]
    );

    /**
     * 检查图层是否隐藏
     */
    const isLayerHidden = useCallback(
        (layerId: string) => {
            return hiddenLayerIds.has(layerId);
        },
        [hiddenLayerIds]
    );

    /**
     * 复制图层到剪贴板
     */
    const copyLayer = useCallback((layer: Layer | null) => {
        setClipboard(layer);
    }, []);

    /**
     * 清空选择
     */
    const clearSelection = useCallback(() => {
        setSelectedLayerId(null);
        setEditMode('select');
    }, []);

    /**
     * 重置编辑器状态
     */
    const resetEditorState = useCallback(() => {
        setSelectedLayerId(null);
        setEditMode('select');
        setLockedLayerIds(new Set());
        setHiddenLayerIds(new Set());
        setClipboard(null);
    }, []);

    return {
        // 状态
        selectedLayerId,
        editMode,
        lockedLayerIds,
        hiddenLayerIds,
        showLayerPanel,
        showPropertyPanel,
        clipboard,

        // 方法
        selectLayer,
        setEditMode,
        toggleLayerLock,
        toggleLayerVisibility,
        isLayerLocked,
        isLayerHidden,
        copyLayer,
        clearSelection,
        resetEditorState,
        setShowLayerPanel,
        setShowPropertyPanel,
    };
}

