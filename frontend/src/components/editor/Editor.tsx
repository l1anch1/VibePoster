/**
 * 编辑器主组件
 *
 * 布局：
 * - 上：顶部参数栏（画布尺寸、导出）
 * - 左：输入面板（提示词、图片上传）
 * - 中：画布区域（白色海报）
 * - 右：属性面板（图层列表、属性编辑，类似 PS）
 *
 * 风格：iOS 液态玻璃
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import type { ExportFormat } from '../../config/constants';
import { exportAndDownloadPoster } from '../../services/api';
import { useEditorState } from '../../hooks/useEditorState';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import { useToast } from '../ui/Toast';

import { EditorTopBar } from './toolbar';
import { EditorLeftPanel } from './panels';
import { EditorRightPanel } from './panels';
import { EditorCanvas } from './canvas';
import { StepWizard } from './StepWizard';

// ============================================================================
// Props
// ============================================================================

interface EditorProps {
  onBack?: () => void;
}

// ============================================================================
// Editor 组件
// ============================================================================

export const Editor: React.FC<EditorProps> = ({ onBack }) => {
  const { addToast } = useToast();
  const [isExporting, setIsExporting] = useState(false);
  const state = useEditorState();
  const {
    data, prompt, selectedLayerId, editingLayerId,
    selectedPreset, showExport, wizardConfig, hasLayers,
    setPrompt, setUploadedImages, setShowExport, setEditingLayerId,
    handlePresetChange, handleSelectLayer, handleUpdateLayer, handleDeleteLayer,
    handleReset, handleGenerate, handleWizardComplete, handleWizardCancel,
  } = state;

  // ========== 画布缩放 ==========
  const canvasContainerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0.4);

  useEffect(() => {
    const calculateScale = () => {
      if (!canvasContainerRef.current) return;
      const container = canvasContainerRef.current.getBoundingClientRect();
      const padding = 80;
      const scaleX = (container.width - padding) / data.canvas.width;
      const scaleY = (container.height - padding) / data.canvas.height;
      const isLandscape = data.canvas.width > data.canvas.height;
      const maxScale = isLandscape ? 0.45 : 0.55;
      setScale(Math.min(scaleX, scaleY, maxScale));
    };
    calculateScale();
    window.addEventListener('resize', calculateScale);
    return () => window.removeEventListener('resize', calculateScale);
  }, [data.canvas.width, data.canvas.height]);

  // ========== 快捷键 ==========
  useKeyboardShortcuts({
    selectedLayerId,
    editingLayerId,
    onClearEditing: useCallback(() => setEditingLayerId(null), [setEditingLayerId]),
    onClearSelection: useCallback(() => handleSelectLayer(null), [handleSelectLayer]),
    onCloseExport: useCallback(() => setShowExport(false), [setShowExport]),
    onDeleteLayer: handleDeleteLayer,
  });

  // ========== 导出 ==========
  const handleExport = useCallback(
    async (format: ExportFormat['format']) => {
      setIsExporting(true);
      try {
        await exportAndDownloadPoster(data, format);
        setShowExport(false);
        addToast('Export successful', 'success');
      } catch (error: unknown) {
        const msg = (error as { userMessage?: string })?.userMessage || 'Export failed';
        addToast(msg, 'error');
      } finally {
        setIsExporting(false);
      }
    },
    [data, setShowExport, addToast]
  );

  // ========== Render ==========
  return (
    <div
      className="h-screen flex flex-col overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #e0e7ff 0%, #fae8ff 50%, #fef3c7 100%)' }}
    >
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-blue-300/30 to-purple-300/30 blur-3xl" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[400px] h-[400px] rounded-full bg-gradient-to-br from-pink-300/30 to-orange-200/30 blur-3xl" />
      </div>

      <EditorTopBar
        onBack={onBack}
        selectedPreset={selectedPreset}
        onPresetChange={handlePresetChange}
        hasLayers={hasLayers}
        showExport={showExport}
        onToggleExport={() => setShowExport(!showExport)}
        onExport={handleExport}
        onReset={handleReset}
        isLocked={!!wizardConfig}
      />

      <div className="flex-1 flex overflow-hidden relative z-10">
        {wizardConfig ? (
          <StepWizard
            config={wizardConfig}
            onComplete={handleWizardComplete}
            onCancel={handleWizardCancel}
          />
        ) : (
          <>
            <EditorLeftPanel
              prompt={prompt}
              onPromptChange={setPrompt}
              isGenerating={false}
              onGenerate={handleGenerate}
              onImagesChange={setUploadedImages}
            />

            <main
              ref={canvasContainerRef}
              className="flex-1 flex items-center justify-center relative"
              onClick={() => { handleSelectLayer(null); setShowExport(false); }}
            >
              <div onClick={(e) => e.stopPropagation()}>
                <EditorCanvas
                  data={data}
                  scale={scale}
                  isEditMode={true}
                  selectedLayerId={selectedLayerId}
                  onSelectLayer={handleSelectLayer}
                  isLayerLocked={() => false}
                  onUpdateLayer={handleUpdateLayer}
                  editingLayerId={editingLayerId}
                  onStartEditing={setEditingLayerId}
                  onStopEditing={() => setEditingLayerId(null)}
                />
              </div>
              <div
                className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3 px-4 py-2 rounded-full text-xs font-medium text-gray-600"
                style={{ background: 'rgba(255,255,255,0.7)', backdropFilter: 'blur(10px)' }}
              >
                <span>{data.canvas.width} × {data.canvas.height}</span>
                <span className="w-1 h-1 rounded-full bg-gray-400" />
                <span>{Math.round(scale * 100)}%</span>
              </div>
            </main>

            {hasLayers && (
              <EditorRightPanel
                data={data}
                selectedLayerId={selectedLayerId}
                onSelectLayer={handleSelectLayer}
                onUpdateLayer={handleUpdateLayer}
                onDeleteLayer={handleDeleteLayer}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
};
