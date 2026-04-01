/**
 * useEditorState — 海报数据 + 图层 CRUD + 画布预设 + 重置
 *
 * 使用 useReducer 集中管理状态，保持对外接口不变。
 */

import { useReducer, useCallback, useMemo } from 'react';
import type { PosterData, Layer } from '../types/PosterSchema';
import type { UploadedImages } from '../components/editor/panels/EditorLeftPanel';
import type { WizardConfig } from '../components/editor/StepWizard';
import {
  CANVAS_PRESETS,
  DEFAULT_POSTER_DATA,
  type CanvasPreset,
} from '../config/constants';
import { rescaleLayers } from '../utils/editorUtils';

// ============================================================================
// 公开接口（保持不变）
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
  hasLayers: boolean;
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
  handleReset: () => void;

  handleGenerate: () => void;
  handleWizardComplete: (posterData: PosterData) => void;
  handleWizardCancel: () => void;
}

// ============================================================================
// Reducer 实现
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
  | { type: 'START_WIZARD'; config: WizardConfig }
  | { type: 'WIZARD_COMPLETE'; posterData: PosterData }
  | { type: 'WIZARD_CANCEL' }
  | { type: 'RESET' };

const initialState: StateData = {
  data: DEFAULT_POSTER_DATA,
  prompt: '',
  uploadedImages: { imageBg: null, imageSubject: null },
  selectedLayerId: null,
  editingLayerId: null,
  selectedPreset: CANVAS_PRESETS[0],
  showExport: false,
  wizardConfig: null,
};

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

    case 'START_WIZARD':
      return { ...state, wizardConfig: action.config };

    case 'WIZARD_COMPLETE':
      return { ...state, data: action.posterData, prompt: '', selectedLayerId: null, wizardConfig: null };

    case 'WIZARD_CANCEL':
      return { ...state, wizardConfig: null };

    case 'RESET':
      return { ...initialState };

    default:
      return state;
  }
}

// ============================================================================
// Hook
// ============================================================================

export function useEditorState(): EditorState & EditorActions {
  const [state, dispatch] = useReducer(editorReducer, initialState);
  const hasLayers = state.data.layers.length > 0;

  // setState-compatible dispatchers（保持与旧接口兼容）
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
    (posterData: PosterData) => dispatch({ type: 'WIZARD_COMPLETE', posterData }), []
  );
  const handleWizardCancel = useCallback(
    () => dispatch({ type: 'WIZARD_CANCEL' }), []
  );

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
    hasLayers,
    // Setters
    setData, setPrompt, setUploadedImages, setShowExport, setEditingLayerId,
    // Handlers
    handlePresetChange, handleSelectLayer, handleUpdateLayer, handleDeleteLayer,
    handleReset, handleGenerate, handleWizardComplete, handleWizardCancel,
  }), [
    state, hasLayers,
    setData, setPrompt, setUploadedImages, setShowExport, setEditingLayerId,
    handlePresetChange, handleSelectLayer, handleUpdateLayer, handleDeleteLayer,
    handleReset, handleGenerate, handleWizardComplete, handleWizardCancel,
  ]);
}
