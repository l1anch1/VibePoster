/**
 * useEditorState — 海报数据 + 图层 CRUD + 画布预设 + Undo/Redo + 图层排序
 *
 * 使用 useReducer + 历史栈包装实现撤销/重做。
 * 拖拽/缩放操作通过 BEGIN_BATCH / END_BATCH 合并为单次 undo 步骤。
 */

import { useReducer, useCallback, useMemo } from 'react';
import type { PosterData, Layer } from '../types/PosterSchema';
import type { ExtractedData } from '../types/EditorTypes';
import type { UploadedImages } from '../components/editor/panels/EditorLeftPanel';
import type { WizardConfig } from '../components/editor/StepWizard';
import {
  CANVAS_PRESETS,
  DEFAULT_POSTER_DATA,
  type CanvasPreset,
} from '../config/constants';
import { rescaleLayers } from '../utils/editorUtils';

// ============================================================================
// 公开接口
// ============================================================================

export interface EditorState {
  data: PosterData;
  prompt: string;
  uploadedImages: UploadedImages;
  selectedLayerId: string | null;
  editingLayerId: string | null;
  selectedPreset: CanvasPreset;
  showExport: boolean;
  wizardConfig: WizardConfig | null;
  analysisData: ExtractedData | null;
  hasLayers: boolean;
  canUndo: boolean;
  canRedo: boolean;
}

export interface EditorActions {
  setData: React.Dispatch<React.SetStateAction<PosterData>>;
  setPrompt: React.Dispatch<React.SetStateAction<string>>;
  setUploadedImages: React.Dispatch<React.SetStateAction<UploadedImages>>;
  setShowExport: React.Dispatch<React.SetStateAction<boolean>>;
  setEditingLayerId: React.Dispatch<React.SetStateAction<string | null>>;

  handlePresetChange: (preset: CanvasPreset) => void;
  handleSelectLayer: (id: string | null) => void;
  handleUpdateLayer: (layerId: string, updates: Partial<Layer>) => void;
  handleDeleteLayer: (layerId: string) => void;
  handleReorderLayer: (layerId: string, direction: 'up' | 'down') => void;
  handleReset: () => void;

  handleGenerate: () => void;
  handleWizardComplete: (posterData: PosterData, analysisData?: ExtractedData | null) => void;
  handleWizardCancel: () => void;

  handleUndo: () => void;
  handleRedo: () => void;
  handleBeginBatch: () => void;
  handleEndBatch: () => void;
}

// ============================================================================
// 内部状态
// ============================================================================

interface StateData {
  data: PosterData;
  prompt: string;
  uploadedImages: UploadedImages;
  selectedLayerId: string | null;
  editingLayerId: string | null;
  selectedPreset: CanvasPreset;
  showExport: boolean;
  wizardConfig: WizardConfig | null;
  analysisData: ExtractedData | null;
}

type Action =
  | { type: 'SET_DATA'; payload: PosterData | ((prev: PosterData) => PosterData) }
  | { type: 'SET_PROMPT'; payload: string | ((prev: string) => string) }
  | { type: 'SET_UPLOADED_IMAGES'; payload: UploadedImages | ((prev: UploadedImages) => UploadedImages) }
  | { type: 'SET_SHOW_EXPORT'; payload: boolean | ((prev: boolean) => boolean) }
  | { type: 'SET_EDITING_LAYER'; payload: string | null | ((prev: string | null) => string | null) }
  | { type: 'CHANGE_PRESET'; payload: CanvasPreset }
  | { type: 'SELECT_LAYER'; payload: string | null }
  | { type: 'UPDATE_LAYER'; layerId: string; updates: Partial<Layer> }
  | { type: 'DELETE_LAYER'; layerId: string }
  | { type: 'REORDER_LAYER'; layerId: string; direction: 'up' | 'down' }
  | { type: 'START_WIZARD'; config: WizardConfig }
  | { type: 'WIZARD_COMPLETE'; posterData: PosterData; analysisData?: ExtractedData | null }
  | { type: 'WIZARD_CANCEL' }
  | { type: 'RESET' }
  | { type: 'UNDO' }
  | { type: 'REDO' }
  | { type: 'BEGIN_BATCH' }
  | { type: 'END_BATCH' };

const initialState: StateData = {
  data: DEFAULT_POSTER_DATA,
  prompt: '',
  uploadedImages: { imageBg: null, imageSubject: null },
  selectedLayerId: null,
  editingLayerId: null,
  selectedPreset: CANVAS_PRESETS[0],
  showExport: false,
  wizardConfig: null,
  analysisData: null,
};

// ============================================================================
// 内部 reducer（纯状态转换，无历史逻辑）
// ============================================================================

function resolve<T>(payload: T | ((prev: T) => T), prev: T): T {
  return typeof payload === 'function' ? (payload as (p: T) => T)(prev) : payload;
}

function editorReducer(state: StateData, action: Action): StateData {
  switch (action.type) {
    case 'SET_DATA':
      return { ...state, data: resolve(action.payload, state.data) };

    case 'SET_PROMPT':
      return { ...state, prompt: resolve(action.payload, state.prompt) };

    case 'SET_UPLOADED_IMAGES':
      return { ...state, uploadedImages: resolve(action.payload, state.uploadedImages) };

    case 'SET_SHOW_EXPORT':
      return { ...state, showExport: resolve(action.payload, state.showExport) };

    case 'SET_EDITING_LAYER':
      return { ...state, editingLayerId: resolve(action.payload, state.editingLayerId) };

    case 'CHANGE_PRESET': {
      const preset = action.payload;
      const { data } = state;
      const oldW = data.canvas.width;
      const oldH = data.canvas.height;
      const newW = preset.width;
      const newH = preset.height;
      const needsRescale = data.layers.length > 0 && (oldW !== newW || oldH !== newH);
      const layers = needsRescale
        ? rescaleLayers(data.layers, newW / oldW, newH / oldH)
        : data.layers;
      return {
        ...state,
        selectedPreset: preset,
        data: { ...data, canvas: { ...data.canvas, width: newW, height: newH }, layers },
      };
    }

    case 'SELECT_LAYER':
      return { ...state, selectedLayerId: action.payload, editingLayerId: null };

    case 'UPDATE_LAYER':
      return {
        ...state,
        data: {
          ...state.data,
          layers: state.data.layers.map((l) =>
            l.id === action.layerId ? ({ ...l, ...action.updates } as Layer) : l
          ),
        },
      };

    case 'DELETE_LAYER':
      return {
        ...state,
        data: { ...state.data, layers: state.data.layers.filter((l) => l.id !== action.layerId) },
        selectedLayerId: null,
        editingLayerId: null,
      };

    case 'REORDER_LAYER': {
      const layers = [...state.data.layers];
      const idx = layers.findIndex((l) => l.id === action.layerId);
      if (idx === -1) return state;
      // up = toward top = increase index; down = toward bottom = decrease index
      const targetIdx = action.direction === 'up' ? idx + 1 : idx - 1;
      if (targetIdx < 0 || targetIdx >= layers.length) return state;
      [layers[idx], layers[targetIdx]] = [layers[targetIdx], layers[idx]];
      return { ...state, data: { ...state.data, layers } };
    }

    case 'START_WIZARD':
      return { ...state, wizardConfig: action.config };

    case 'WIZARD_COMPLETE':
      return { ...state, data: action.posterData, prompt: '', selectedLayerId: null, wizardConfig: null, analysisData: action.analysisData || null };

    case 'WIZARD_CANCEL':
      return { ...state, wizardConfig: null };

    case 'RESET':
      return { ...initialState };

    default:
      return state;
  }
}

// ============================================================================
// 历史栈包装
// ============================================================================

const MAX_HISTORY = 50;

// 会记入 undo 历史的 action 类型
const DATA_MUTATING_ACTIONS = new Set([
  'SET_DATA', 'CHANGE_PRESET', 'UPDATE_LAYER', 'DELETE_LAYER',
  'REORDER_LAYER', 'RESET',
]);

interface HistoryState {
  past: StateData[];
  present: StateData;
  future: StateData[];
  batching: boolean; // BEGIN_BATCH 已调用但尚未 END_BATCH
  batchSnapshot: StateData | null; // batch 开始时的快照
}

const initialHistoryState: HistoryState = {
  past: [],
  present: initialState,
  future: [],
  batching: false,
  batchSnapshot: null,
};

function historyReducer(history: HistoryState, action: Action): HistoryState {
  const { past, present, future, batching, batchSnapshot } = history;

  switch (action.type) {
    case 'UNDO': {
      if (past.length === 0) return history;
      const prev = past[past.length - 1];
      return {
        past: past.slice(0, -1),
        present: prev,
        future: [present, ...future],
        batching: false,
        batchSnapshot: null,
      };
    }

    case 'REDO': {
      if (future.length === 0) return history;
      const next = future[0];
      return {
        past: [...past, present],
        present: next,
        future: future.slice(1),
        batching: false,
        batchSnapshot: null,
      };
    }

    case 'BEGIN_BATCH':
      return {
        ...history,
        batching: true,
        batchSnapshot: batchSnapshot ?? present, // 只在没有现有快照时保存
      };

    case 'END_BATCH': {
      if (!batching) return history;
      // 如果 batch 期间有实际改动，将快照推入 past
      if (batchSnapshot && batchSnapshot !== present) {
        return {
          past: [...past, batchSnapshot].slice(-MAX_HISTORY),
          present,
          future: [],
          batching: false,
          batchSnapshot: null,
        };
      }
      return { ...history, batching: false, batchSnapshot: null };
    }

    case 'WIZARD_COMPLETE': {
      const newPresent = editorReducer(present, action);
      return {
        past: [],
        present: newPresent,
        future: [],
        batching: false,
        batchSnapshot: null,
      };
    }

    default: {
      const newPresent = editorReducer(present, action);
      if (newPresent === present) return history;

      // 非数据变更 action：不影响历史
      if (!DATA_MUTATING_ACTIONS.has(action.type)) {
        return { ...history, present: newPresent };
      }

      // 在 batch 中：只更新 present，不推入 past（快照已保存）
      if (batching) {
        return { ...history, present: newPresent };
      }

      // 正常数据变更：推入历史
      return {
        past: [...past, present].slice(-MAX_HISTORY),
        present: newPresent,
        future: [],
        batching: false,
        batchSnapshot: null,
      };
    }
  }
}

// ============================================================================
// Hook
// ============================================================================

export function useEditorState(): EditorState & EditorActions {
  const [history, dispatch] = useReducer(historyReducer, initialHistoryState);
  const state = history.present;
  const hasLayers = state.data.layers.length > 0;
  const canUndo = history.past.length > 0;
  const canRedo = history.future.length > 0;

  // setState-compatible dispatchers
  const setData: React.Dispatch<React.SetStateAction<PosterData>> = useCallback(
    (v) => dispatch({ type: 'SET_DATA', payload: v }), []
  );
  const setPrompt: React.Dispatch<React.SetStateAction<string>> = useCallback(
    (v) => dispatch({ type: 'SET_PROMPT', payload: v }), []
  );
  const setUploadedImages: React.Dispatch<React.SetStateAction<UploadedImages>> = useCallback(
    (v) => dispatch({ type: 'SET_UPLOADED_IMAGES', payload: v }), []
  );
  const setShowExport: React.Dispatch<React.SetStateAction<boolean>> = useCallback(
    (v) => dispatch({ type: 'SET_SHOW_EXPORT', payload: v }), []
  );
  const setEditingLayerId: React.Dispatch<React.SetStateAction<string | null>> = useCallback(
    (v) => dispatch({ type: 'SET_EDITING_LAYER', payload: v }), []
  );

  const handlePresetChange = useCallback(
    (preset: CanvasPreset) => dispatch({ type: 'CHANGE_PRESET', payload: preset }), []
  );
  const handleSelectLayer = useCallback(
    (id: string | null) => dispatch({ type: 'SELECT_LAYER', payload: id }), []
  );
  const handleUpdateLayer = useCallback(
    (layerId: string, updates: Partial<Layer>) => dispatch({ type: 'UPDATE_LAYER', layerId, updates }), []
  );
  const handleDeleteLayer = useCallback(
    (layerId: string) => dispatch({ type: 'DELETE_LAYER', layerId }), []
  );
  const handleReorderLayer = useCallback(
    (layerId: string, direction: 'up' | 'down') => dispatch({ type: 'REORDER_LAYER', layerId, direction }), []
  );
  const handleReset = useCallback(() => dispatch({ type: 'RESET' }), []);

  const handleGenerate = useCallback(() => {
    if (!state.prompt.trim() || state.wizardConfig) return;
    dispatch({
      type: 'START_WIZARD',
      config: {
        prompt: state.prompt,
        canvasWidth: state.data.canvas.width,
        canvasHeight: state.data.canvas.height,
        imageBg: state.uploadedImages.imageBg,
        imageSubject: state.uploadedImages.imageSubject,
      },
    });
  }, [state.prompt, state.wizardConfig, state.data.canvas.width, state.data.canvas.height, state.uploadedImages]);

  const handleWizardComplete = useCallback(
    (posterData: PosterData, analysisData?: ExtractedData | null) => dispatch({ type: 'WIZARD_COMPLETE', posterData, analysisData }), []
  );
  const handleWizardCancel = useCallback(
    () => dispatch({ type: 'WIZARD_CANCEL' }), []
  );

  const handleUndo = useCallback(() => dispatch({ type: 'UNDO' }), []);
  const handleRedo = useCallback(() => dispatch({ type: 'REDO' }), []);
  const handleBeginBatch = useCallback(() => dispatch({ type: 'BEGIN_BATCH' }), []);
  const handleEndBatch = useCallback(() => dispatch({ type: 'END_BATCH' }), []);

  return useMemo(() => ({
    // State
    data: state.data,
    prompt: state.prompt,
    uploadedImages: state.uploadedImages,
    selectedLayerId: state.selectedLayerId,
    editingLayerId: state.editingLayerId,
    selectedPreset: state.selectedPreset,
    showExport: state.showExport,
    wizardConfig: state.wizardConfig,
    analysisData: state.analysisData,
    hasLayers,
    canUndo,
    canRedo,
    // Setters
    setData, setPrompt, setUploadedImages, setShowExport, setEditingLayerId,
    // Handlers
    handlePresetChange, handleSelectLayer, handleUpdateLayer, handleDeleteLayer,
    handleReorderLayer,
    handleReset, handleGenerate, handleWizardComplete, handleWizardCancel,
    handleUndo, handleRedo, handleBeginBatch, handleEndBatch,
  }), [
    state, hasLayers, canUndo, canRedo,
    setData, setPrompt, setUploadedImages, setShowExport, setEditingLayerId,
    handlePresetChange, handleSelectLayer, handleUpdateLayer, handleDeleteLayer,
    handleReorderLayer,
    handleReset, handleGenerate, handleWizardComplete, handleWizardCancel,
    handleUndo, handleRedo, handleBeginBatch, handleEndBatch,
  ]);
}
