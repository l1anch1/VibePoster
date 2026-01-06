/**
 * 历史记录 Hook
 * 
 * 管理撤销/重做功能
 */

import { useState, useCallback, useRef } from 'react';
import type { PosterData } from '../types/PosterSchema';
import type { HistoryEntry } from '../types/EditorTypes';
import { deepClone } from '../utils/editorUtils';

interface UseHistoryOptions {
    maxHistory?: number;
}

export function useHistory(initialData: PosterData, options: UseHistoryOptions = {}) {
    const { maxHistory = 50 } = options;

    const [past, setPast] = useState<HistoryEntry[]>([]);
    const [present, setPresent] = useState<PosterData>(initialData);
    const [future, setFuture] = useState<HistoryEntry[]>([]);

    // 使用 ref 跟踪是否由 undo/redo 触发，避免重复记录
    const isUndoRedoRef = useRef(false);

    /**
     * 记录新的历史状态
     */
    const pushHistory = useCallback(
        (newData: PosterData, description: string = 'Edit') => {
            // 如果是 undo/redo 操作，不记录历史
            if (isUndoRedoRef.current) {
                isUndoRedoRef.current = false;
                return;
            }

            setPast((prev) => {
                const newPast = [
                    ...prev,
                    {
                        data: deepClone(present),
                        timestamp: Date.now(),
                        description,
                    },
                ];

                // 限制历史记录数量
                if (newPast.length > maxHistory) {
                    return newPast.slice(newPast.length - maxHistory);
                }

                return newPast;
            });

            setPresent(newData);
            setFuture([]); // 清空 future（新操作后无法重做之前的内容）
        },
        [present, maxHistory]
    );

    /**
     * 撤销
     */
    const undo = useCallback(() => {
        if (past.length === 0) return;

        isUndoRedoRef.current = true;

        const previous = past[past.length - 1];
        const newPast = past.slice(0, past.length - 1);

        setPast(newPast);
        setFuture((prev) => [
            ...prev,
            {
                data: deepClone(present),
                timestamp: Date.now(),
                description: 'Redo point',
            },
        ]);
        setPresent(previous.data);
    }, [past, present]);

    /**
     * 重做
     */
    const redo = useCallback(() => {
        if (future.length === 0) return;

        isUndoRedoRef.current = true;

        const next = future[future.length - 1];
        const newFuture = future.slice(0, future.length - 1);

        setFuture(newFuture);
        setPast((prev) => [
            ...prev,
            {
                data: deepClone(present),
                timestamp: Date.now(),
                description: 'Undo point',
            },
        ]);
        setPresent(next.data);
    }, [future, present]);

    /**
     * 清空历史
     */
    const clearHistory = useCallback(() => {
        setPast([]);
        setFuture([]);
    }, []);

    /**
     * 重置到初始状态
     */
    const reset = useCallback((newData: PosterData) => {
        setPast([]);
        setPresent(newData);
        setFuture([]);
    }, []);

    return {
        present,
        past,
        future,
        canUndo: past.length > 0,
        canRedo: future.length > 0,
        pushHistory,
        undo,
        redo,
        clearHistory,
        reset,
    };
}

