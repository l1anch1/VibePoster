/**
 * useEditorState — 海报数据 + 图层 CRUD + 画布预设 + 重置
 *
 * 从 Editor 组件中提取的核心状态管理逻辑。
 */

import { useState, useCallback } from 'react';
import type { PosterData, Layer } from '../types/PosterSchema';
import type { UploadedImages } from '../components/editor/EditorLeftPanel';
import type { WizardConfig } from '../components/editor/StepWizard';
import {
  CANVAS_PRESETS,
  DEFAULT_POSTER_DATA,
  type CanvasPreset,
} from '../config/constants';
import { rescaleLayers } from '../utils/editorUtils';

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

export function useEditorState(): EditorState & EditorActions {
  const [data, setData] = useState<PosterData>(DEFAULT_POSTER_DATA);
  const [prompt, setPrompt] = useState('');
  const [uploadedImages, setUploadedImages] = useState<UploadedImages>({ imageBg: null, imageSubject: null });
  const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null);
  const [editingLayerId, setEditingLayerId] = useState<string | null>(null);
  const [selectedPreset, setSelectedPreset] = useState<CanvasPreset>(CANVAS_PRESETS[0]);
  const [showExport, setShowExport] = useState(false);
  const [wizardConfig, setWizardConfig] = useState<WizardConfig | null>(null);

  const hasLayers = data.layers.length > 0;

  // ---- 画布预设 ----
  const handlePresetChange = useCallback((preset: CanvasPreset) => {
    setSelectedPreset(preset);
    setData((prev) => {
      const oldW = prev.canvas.width;
      const oldH = prev.canvas.height;
      const newW = preset.width;
      const newH = preset.height;

      const needsRescale = prev.layers.length > 0 && (oldW !== newW || oldH !== newH);
      const layers = needsRescale
        ? rescaleLayers(prev.layers, newW / oldW, newH / oldH)
        : prev.layers;

      return {
        ...prev,
        canvas: { ...prev.canvas, width: newW, height: newH },
        layers,
      };
    });
  }, []);

  // ---- 图层 CRUD ----
  const handleSelectLayer = useCallback((id: string | null) => {
    setSelectedLayerId(id);
    setEditingLayerId(null);
  }, []);

  const handleUpdateLayer = useCallback((layerId: string, updates: Partial<Layer>) => {
    setData((prev) => ({
      ...prev,
      layers: prev.layers.map((l) => (l.id === layerId ? ({ ...l, ...updates } as Layer) : l)),
    }));
  }, []);

  const handleDeleteLayer = useCallback((layerId: string) => {
    setData((prev) => ({ ...prev, layers: prev.layers.filter((l) => l.id !== layerId) }));
    setSelectedLayerId(null);
    setEditingLayerId(null);
  }, []);

  // ---- 向导 ----
  const handleGenerate = useCallback(() => {
    if (!prompt.trim() || wizardConfig) return;
    setWizardConfig({
      prompt,
      canvasWidth: data.canvas.width,
      canvasHeight: data.canvas.height,
      imageBg: uploadedImages.imageBg,
      imageSubject: uploadedImages.imageSubject,
    });
  }, [prompt, wizardConfig, data.canvas.width, data.canvas.height, uploadedImages]);

  const handleWizardComplete = useCallback((posterData: PosterData) => {
    setData(posterData);
    setPrompt('');
    setSelectedLayerId(null);
    setWizardConfig(null);
  }, []);

  const handleWizardCancel = useCallback(() => {
    setWizardConfig(null);
  }, []);

  // ---- 重置 ----
  const handleReset = useCallback(() => {
    setData(DEFAULT_POSTER_DATA);
    setPrompt('');
    setSelectedLayerId(null);
    setEditingLayerId(null);
    setUploadedImages({ imageBg: null, imageSubject: null });
    setShowExport(false);
    setWizardConfig(null);
  }, []);

  return {
    data, prompt, uploadedImages, selectedLayerId, editingLayerId,
    selectedPreset, showExport, wizardConfig, hasLayers,

    setData, setPrompt, setUploadedImages, setShowExport, setEditingLayerId,

    handlePresetChange, handleSelectLayer, handleUpdateLayer, handleDeleteLayer,
    handleReset, handleGenerate, handleWizardComplete, handleWizardCancel,
  };
}
