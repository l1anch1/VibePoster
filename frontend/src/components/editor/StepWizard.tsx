/**
 * 分步生成向导 — 全屏横向卡片布局
 *
 * 三步人机协作流程：
 * Step 1: 意图理解 — 展示/编辑设计简报
 * Step 2: 素材选择 — 展示候选背景图（匹配画布比例）
 * Step 3: 版式选择 — 展示候选版式方案（真实画布预览）
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import type { PosterData } from '../../types/PosterSchema';
import type { DesignBrief } from '../../services/api';
import { stepPlan, stepAssets, stepLayouts, stepFinalize } from '../../services/api';
import { EditorCanvas } from './canvas';

// ============================================================================
// 类型
// ============================================================================

type WizardStep = 'idle' | 'plan-loading' | 'plan-review' | 'assets-loading' | 'assets-review' | 'layouts-loading' | 'layouts-review' | 'finalizing';

export interface WizardConfig {
  prompt: string;
  canvasWidth: number;
  canvasHeight: number;
  imageBg?: File | null;
  imageSubject?: File | null;
}

interface StepWizardProps {
  config: WizardConfig;
  onComplete: (posterData: PosterData, analysisData?: { palette: string[]; styles: string[] } | null) => void;
  onCancel: () => void;
}

// ============================================================================
// 子组件
// ============================================================================

const StepIndicator: React.FC<{ current: number; labels: string[] }> = ({ current, labels }) => (
  <div className="flex items-center gap-2 px-6 py-4">
    {labels.map((label, i) => {
      const isActive = i === current;
      const isDone = i < current;
      return (
        <React.Fragment key={label}>
          {i > 0 && <div className={`flex-1 h-px max-w-16 ${isDone ? 'bg-violet-400' : 'bg-gray-200'}`} />}
          <div className="flex items-center gap-2">
            <div
              className={`w-7 h-7 rounded-full text-xs font-bold flex items-center justify-center transition-all ${
                isActive
                  ? 'bg-violet-500 text-white shadow-lg shadow-violet-500/30'
                  : isDone
                    ? 'bg-violet-400 text-white'
                    : 'bg-gray-200 text-gray-400'
              }`}
            >
              {isDone ? '✓' : i + 1}
            </div>
            <span className={`text-sm font-medium ${isActive ? 'text-violet-600' : isDone ? 'text-violet-400' : 'text-gray-400'}`}>
              {label}
            </span>
          </div>
        </React.Fragment>
      );
    })}
  </div>
);

const LOADING_MESSAGES: Record<string, string[]> = {
  'plan-loading': ['Analyzing your intent...', 'Understanding design requirements...', 'Crafting your design brief...'],
  'assets-loading': ['Searching for assets...', 'Finding the perfect images...', 'Matching your style...'],
  'layouts-loading': ['Generating layout candidates...', 'Arranging text elements...', 'Optimizing composition...', 'Running quality review...'],
  'finalizing': ['Finalizing poster...', 'Polishing details...', 'Almost there...'],
};

const Spinner: React.FC<{ text: string; step?: string }> = ({ text, step }) => {
  const [msgIdx, setMsgIdx] = useState(0);
  const messages = step ? LOADING_MESSAGES[step] || [text] : [text];

  useEffect(() => {
    setMsgIdx(0);
    const timer = setInterval(() => setMsgIdx((i) => (i + 1) % messages.length), 3000);
    return () => clearInterval(timer);
  }, [step, messages.length]);

  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8">
      <div className="w-10 h-10 border-3 border-violet-200 border-t-violet-500 rounded-full animate-spin" />
      <p className="text-sm text-gray-500 transition-opacity duration-300">{messages[msgIdx]}</p>
    </div>
  );
};

const ErrorBanner: React.FC<{ message: string; onRetry: () => void }> = ({ message, onRetry }) => (
  <div className="mx-6 my-3 p-4 rounded-2xl bg-red-50 border border-red-200 text-sm text-red-600">
    <p>{message}</p>
    <button onClick={onRetry} className="mt-2 text-xs font-medium text-red-500 hover:text-red-700 underline">
      Retry
    </button>
  </div>
);

const ActionBar: React.FC<{
  onBack: () => void;
  onNext: () => void;
  nextLabel: string;
  nextDisabled?: boolean;
  backLabel?: string;
}> = ({ onBack, onNext, nextLabel, nextDisabled, backLabel = 'Back' }) => (
  <div className="px-6 py-4 border-t border-gray-200/60 flex justify-between items-center">
    <button
      onClick={onBack}
      className="px-5 py-2.5 text-sm font-medium text-gray-500 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors"
    >
      {backLabel}
    </button>
    <button
      onClick={onNext}
      disabled={nextDisabled}
      className={`px-6 py-2.5 text-sm font-semibold rounded-xl transition-all ${
        nextDisabled
          ? 'text-gray-400 bg-gray-200 cursor-not-allowed'
          : 'text-white bg-gradient-to-r from-violet-500 to-fuchsia-500 shadow-lg shadow-violet-500/20 hover:shadow-xl hover:-translate-y-0.5'
      }`}
    >
      {nextLabel}
    </button>
  </div>
);

// ============================================================================
// Step 1: 设计简报审阅
// ============================================================================

const BriefEditor: React.FC<{
  brief: DesignBrief;
  onChange: (b: DesignBrief) => void;
  onConfirm: () => void;
  onBack: () => void;
}> = ({ brief, onChange, onConfirm, onBack }) => {
  const update = (key: string, value: unknown) => onChange({ ...brief, [key]: value });

  return (
    <>
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="max-w-xl mx-auto space-y-4">
          <label className="block">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Title</span>
            <input
              value={brief.title || ''}
              onChange={(e) => update('title', e.target.value)}
              className="mt-1.5 w-full px-4 py-2.5 text-sm bg-white border border-gray-300 rounded-xl focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            />
          </label>

          <label className="block">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Subtitle</span>
            <input
              value={brief.subtitle || ''}
              onChange={(e) => update('subtitle', e.target.value)}
              className="mt-1.5 w-full px-4 py-2.5 text-sm bg-white border border-gray-300 rounded-xl focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
            />
          </label>

          <div className="grid grid-cols-2 gap-4">
            <label className="block">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Main Color</span>
              <div className="mt-1.5 flex items-center gap-3 px-3 py-2 bg-white border border-gray-300 rounded-xl">
                <input
                  type="color"
                  value={brief.main_color || '#000000'}
                  onChange={(e) => update('main_color', e.target.value)}
                  className="w-8 h-8 rounded-lg border-0 cursor-pointer"
                />
                <span className="text-xs font-mono text-gray-400">{brief.main_color}</span>
              </div>
            </label>
            <label className="block">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Background</span>
              <div className="mt-1.5 flex items-center gap-3 px-3 py-2 bg-white border border-gray-300 rounded-xl">
                <input
                  type="color"
                  value={brief.background_color || '#FFFFFF'}
                  onChange={(e) => update('background_color', e.target.value)}
                  className="w-8 h-8 rounded-lg border-0 cursor-pointer"
                />
                <span className="text-xs font-mono text-gray-400">{brief.background_color}</span>
              </div>
            </label>
          </div>

          <label className="block">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Style Keywords</span>
            <input
              value={(brief.style_keywords || []).join(', ')}
              onChange={(e) => update('style_keywords', e.target.value.split(',').map((s) => s.trim()).filter(Boolean))}
              className="mt-1.5 w-full px-4 py-2.5 text-sm bg-white border border-gray-300 rounded-xl focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none"
              placeholder="e.g. modern, gradient, bold"
            />
          </label>

          {(brief.industry || brief.vibe) && (
            <div className="pt-2 space-y-2">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">AI Detected</p>
              <div className="flex flex-wrap gap-2">
                {brief.industry && (
                  <span className="px-3 py-1 text-xs rounded-full bg-blue-50 text-blue-600 border border-blue-200/60">
                    {brief.industry}
                  </span>
                )}
                {brief.vibe && (
                  <span className="px-3 py-1 text-xs rounded-full bg-purple-50 text-purple-600 border border-purple-200/60">
                    {brief.vibe}
                  </span>
                )}
                {brief.intent && (
                  <span className="px-3 py-1 text-xs rounded-full bg-green-50 text-green-600 border border-green-200/60">
                    {brief.intent}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
      <ActionBar onBack={onBack} onNext={onConfirm} nextLabel="Next: Search Assets" backLabel="Cancel" />
    </>
  );
};

// ============================================================================
// Step 2: 素材选择 — 横向 3 列，匹配画布比例
// ============================================================================

const AssetPicker: React.FC<{
  candidates: string[];
  selectedIndex: number | null;
  canvasWidth: number;
  canvasHeight: number;
  keywordsUsed?: string[];
  onSelect: (i: number) => void;
  onConfirm: () => void;
  onBack: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}> = ({ candidates, selectedIndex, canvasWidth, canvasHeight, keywordsUsed, onSelect, onConfirm, onBack, onRefresh, isRefreshing }) => (
  <>
    <div className="flex-1 overflow-y-auto px-6 py-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-sm font-medium text-gray-600">Choose a background image</p>
          {keywordsUsed && keywordsUsed.length > 0 && (
            <p className="text-xs text-gray-400 mt-0.5">Keywords: {keywordsUsed.join(', ')}</p>
          )}
        </div>
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 text-xs text-violet-500 hover:text-violet-700 font-medium disabled:opacity-50 transition-colors"
        >
          <svg className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {isRefreshing ? 'Searching...' : 'Refresh'}
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {candidates.map((src, i) => (
          <button
            key={i}
            onClick={() => onSelect(i)}
            className={`group relative rounded-2xl overflow-hidden border-2 transition-all ${
              selectedIndex === i
                ? 'border-violet-500 shadow-lg shadow-violet-500/20 ring-4 ring-violet-500/10'
                : 'border-gray-200 hover:border-violet-300 hover:shadow-md'
            }`}
          >
            <div className="w-full bg-gray-100" style={{ height: 'clamp(160px, calc(100vh - 340px), 460px)' }}>
              <img src={src} alt={`Candidate ${i + 1}`} className="w-full h-full object-cover" />
            </div>
            {selectedIndex === i && (
              <div className="absolute top-3 right-3 w-7 h-7 bg-violet-500 rounded-full flex items-center justify-center shadow-lg">
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors" />
          </button>
        ))}
      </div>

      {candidates.length === 0 && !isRefreshing && (
        <div className="text-center py-12 text-gray-400 text-sm">
          No candidates found. Try refreshing.
        </div>
      )}
    </div>
    <ActionBar onBack={onBack} onNext={onConfirm} nextLabel="Next: Generate Layouts" nextDisabled={selectedIndex === null} />
  </>
);

// ============================================================================
// Step 3: 版式选择 — 横向 3 列，真实画布缩放预览
// ============================================================================

const LayoutPreviewCard: React.FC<{
  poster: PosterData;
  label: string;
  isSelected: boolean;
  onSelect: () => void;
}> = ({ poster, label, isSelected, onSelect }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dims, setDims] = useState({ w: 300, h: 400 });

  const cw = poster.canvas?.width || 1080;
  const ch = poster.canvas?.height || 1920;

  useEffect(() => {
    if (!containerRef.current) return;
    const obs = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      if (width > 0 && height > 0) setDims({ w: width, h: height });
    });
    obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  const scale = Math.min(dims.w / cw, dims.h / ch);
  const offsetX = (dims.w - cw * scale) / 2;
  const offsetY = (dims.h - ch * scale) / 2;

  return (
    <button
      onClick={onSelect}
      className={`group w-full rounded-2xl overflow-hidden border-2 transition-all ${
        isSelected
          ? 'border-violet-500 shadow-lg shadow-violet-500/20 ring-4 ring-violet-500/10'
          : 'border-gray-200 hover:border-violet-300 hover:shadow-md'
      }`}
    >
      <div
        ref={containerRef}
        className="relative bg-gray-50 overflow-hidden w-full"
        style={{ height: 'clamp(200px, calc(100vh - 340px), 520px)' }}
      >
        <div
          className="absolute origin-top-left pointer-events-none"
          style={{
            transform: `scale(${scale})`,
            width: cw,
            height: ch,
            left: offsetX,
            top: offsetY,
          }}
        >
          <EditorCanvas data={poster} scale={1} />
        </div>
        {isSelected && (
          <div className="absolute top-2 right-2 w-6 h-6 bg-violet-500 rounded-full flex items-center justify-center shadow-lg z-10">
            <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors z-[1]" />
      </div>
      <div className="px-2 py-1.5 bg-white text-xs text-gray-500 text-center font-medium truncate">
        {label}
      </div>
    </button>
  );
};

const LayoutPicker: React.FC<{
  layouts: PosterData[];
  selectedIndex: number | null;
  onSelect: (i: number) => void;
  onConfirm: () => void;
  onBack: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}> = ({ layouts, selectedIndex, onSelect, onConfirm, onBack, onRefresh, isRefreshing }) => {
  const getLabel = (poster: PosterData, idx: number) => {
    const style = (poster as any).layout_style as string | undefined;
    return style || `Layout ${idx + 1}`;
  };

  return (
    <>
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-medium text-gray-600">
            Choose a layout
            <span className="ml-2 text-xs text-gray-400 font-normal">
              {layouts.length} styles
            </span>
          </p>
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 text-xs text-violet-500 hover:text-violet-700 font-medium disabled:opacity-50 transition-colors"
          >
            <svg className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {isRefreshing ? 'Generating...' : 'Regenerate All'}
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {layouts.map((poster, i) => (
            <LayoutPreviewCard
              key={i}
              poster={poster}
              label={getLabel(poster, i)}
              isSelected={selectedIndex === i}
              onSelect={() => onSelect(i)}
            />
          ))}
        </div>

        {layouts.length === 0 && !isRefreshing && (
          <div className="text-center py-12 text-gray-400 text-sm">
            No layouts generated. Try refreshing.
          </div>
        )}
      </div>
      <ActionBar onBack={onBack} onNext={onConfirm} nextLabel="Finalize Poster" nextDisabled={selectedIndex === null} />
    </>
  );
};

// ============================================================================
// 主组件 — 全屏卡片
// ============================================================================

export const StepWizard: React.FC<StepWizardProps> = ({ config, onComplete, onCancel }) => {
  const [step, setStep] = useState<WizardStep>('plan-loading');
  const [error, setError] = useState<string | null>(null);

  // Step 1
  const [designBrief, setDesignBrief] = useState<DesignBrief>({});

  // Step 2
  const [assetCandidates, setAssetCandidates] = useState<string[]>([]);
  const [selectedAssetIdx, setSelectedAssetIdx] = useState<number | null>(null);
  const [isRefreshingAssets, setIsRefreshingAssets] = useState(false);
  const [subjectUrl, setSubjectUrl] = useState<string | null>(null);
  const [subjectDims, setSubjectDims] = useState<{ w: number; h: number } | null>(null);
  const [imageAnalyses, setImageAnalyses] = useState<Record<string, unknown>[] | null>(null);
  const [colorSuggestions, setColorSuggestions] = useState<Record<string, unknown> | null>(null);
  const [keywordsUsed, setKeywordsUsed] = useState<string[]>([]);

  // Step 3
  const [layoutCandidates, setLayoutCandidates] = useState<PosterData[]>([]);
  const [selectedLayoutIdx, setSelectedLayoutIdx] = useState<number | null>(null);
  const [isRefreshingLayouts, setIsRefreshingLayouts] = useState(false);

  const didInit = useRef(false);

  // ----- Step 1: Plan -----
  const doPlan = useCallback(async () => {
    setStep('plan-loading');
    setError(null);
    try {
      const res = await stepPlan({
        prompt: config.prompt,
        canvasWidth: config.canvasWidth,
        canvasHeight: config.canvasHeight,
      });
      setDesignBrief(res.design_brief);
      setStep('plan-review');
    } catch (e: any) {
      setError(e?.message || 'Plan failed');
      setStep('plan-review');
    }
  }, [config]);

  useEffect(() => {
    if (didInit.current) return;
    didInit.current = true;
    doPlan();
  }, [doPlan]);

  // ----- Step 2: Assets -----
  const doAssets = useCallback(async () => {
    setStep('assets-loading');
    setError(null);
    try {
      const res = await stepAssets({
        designBrief,
        canvasWidth: config.canvasWidth,
        canvasHeight: config.canvasHeight,
        count: 3,
        imageBg: config.imageBg,
        imageSubject: config.imageSubject,
      });
      setAssetCandidates(res.candidates);
      if (res.design_brief) setDesignBrief(prev => ({ ...prev, ...res.design_brief }));
      setSubjectUrl(res.subject_url || null);
      setSubjectDims(res.subject_width && res.subject_height ? { w: res.subject_width, h: res.subject_height } : null);
      setImageAnalyses(res.image_analyses || null);
      setColorSuggestions(res.color_suggestions || null);
      setKeywordsUsed(res.keywords_used || []);
      setSelectedAssetIdx(null);
      setStep('assets-review');
    } catch (e: any) {
      setError(e?.message || 'Asset search failed');
      setStep('assets-review');
    }
  }, [designBrief, config]);

  const refreshAssets = useCallback(async () => {
    setIsRefreshingAssets(true);
    try {
      const res = await stepAssets({
        designBrief,
        canvasWidth: config.canvasWidth,
        canvasHeight: config.canvasHeight,
        count: 3,
        imageBg: config.imageBg,
        imageSubject: config.imageSubject,
      });
      setAssetCandidates(res.candidates);
      if (res.design_brief) setDesignBrief(prev => ({ ...prev, ...res.design_brief }));
      setSubjectUrl(res.subject_url || null);
      setSubjectDims(res.subject_width && res.subject_height ? { w: res.subject_width, h: res.subject_height } : null);
      setImageAnalyses(res.image_analyses || null);
      setColorSuggestions(res.color_suggestions || null);
      setKeywordsUsed(res.keywords_used || []);
      setSelectedAssetIdx(null);
    } catch (e: any) {
      setError(e?.message || 'Refresh failed');
    }
    setIsRefreshingAssets(false);
  }, [designBrief, config]);

  // ----- Step 3: Layouts — 并行生成多个自由版式 -----
  const doLayouts = useCallback(async () => {
    if (selectedAssetIdx === null) return;
    setStep('layouts-loading');
    setError(null);
    try {
      const res = await stepLayouts({
        designBrief,
        selectedAssetUrl: assetCandidates[selectedAssetIdx],
        subjectAssetUrl: subjectUrl,
        subjectWidth: subjectDims?.w,
        subjectHeight: subjectDims?.h,
        canvasWidth: config.canvasWidth,
        canvasHeight: config.canvasHeight,
        count: 3,
        imageAnalyses: imageAnalyses,
        colorSuggestions: colorSuggestions,
      });
      setLayoutCandidates(res.layouts);
      setSelectedLayoutIdx(null);
      setStep('layouts-review');
    } catch (e: any) {
      setError(e?.message || 'Layout generation failed');
      setStep('layouts-review');
    }
  }, [designBrief, assetCandidates, selectedAssetIdx, subjectUrl, subjectDims, config, imageAnalyses, colorSuggestions]);

  const refreshLayouts = useCallback(async () => {
    if (selectedAssetIdx === null) return;
    setIsRefreshingLayouts(true);
    try {
      const res = await stepLayouts({
        designBrief,
        selectedAssetUrl: assetCandidates[selectedAssetIdx],
        subjectAssetUrl: subjectUrl,
        subjectWidth: subjectDims?.w,
        subjectHeight: subjectDims?.h,
        canvasWidth: config.canvasWidth,
        canvasHeight: config.canvasHeight,
        count: 3,
        imageAnalyses: imageAnalyses,
        colorSuggestions: colorSuggestions,
      });
      setLayoutCandidates(res.layouts);
      setSelectedLayoutIdx(null);
    } catch (e: any) {
      setError(e?.message || 'Refresh failed');
    }
    setIsRefreshingLayouts(false);
  }, [designBrief, assetCandidates, selectedAssetIdx, subjectUrl, subjectDims, config, imageAnalyses, colorSuggestions]);

  // ----- Step 4: Finalize (layouts already reviewed in Step 3) -----
  const doFinalize = useCallback(async () => {
    if (selectedLayoutIdx === null) return;
    setStep('finalizing');
    setError(null);
    try {
      const res = await stepFinalize({
        posterData: layoutCandidates[selectedLayoutIdx],
      });
      // Extract analysis data for the dashboard
      const extractedAnalysis = {
        palette: [
          ...(colorSuggestions?.palette as string[] || []),
          designBrief?.main_color,
          designBrief?.background_color,
        ].filter((c): c is string => !!c && typeof c === 'string'),
        styles: designBrief?.style_keywords as string[] || [],
      };
      onComplete(res.poster, extractedAnalysis);
    } catch (e: any) {
      setError(e?.message || 'Finalize failed');
      setStep('layouts-review');
    }
  }, [layoutCandidates, selectedLayoutIdx, onComplete, colorSuggestions, designBrief]);

  // ----- 当前步骤序号 -----
  const currentStepNum =
    step.startsWith('plan') ? 0 :
    step.startsWith('assets') ? 1 :
    step.startsWith('layouts') || step === 'finalizing' ? 2 : 0;

  // ----- Render -----
  return (
    <div
      className="flex-1 flex flex-col m-3 rounded-3xl overflow-hidden"
      style={{
        background: 'rgba(255,255,255,0.88)',
        backdropFilter: 'blur(24px) saturate(180%)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.08), inset 0 0 0 1px rgba(255,255,255,0.6)',
        border: '1px solid rgba(0,0,0,0.06)',
      }}
    >
      {/* 头部：标题 + 步骤指示器 */}
      <div className="border-b border-gray-200/60">
        <div className="flex items-center justify-between px-6 pt-4 pb-0">
          <h2 className="text-base font-semibold text-gray-800">Design Wizard</h2>
          <button
            onClick={onCancel}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-400 hover:text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            Cancel
          </button>
        </div>
        <StepIndicator current={currentStepNum} labels={['Design Brief', 'Assets', 'Layout']} />
      </div>

      {/* 错误提示 */}
      {error && <ErrorBanner message={error} onRetry={
        step.startsWith('plan') ? doPlan :
        step.startsWith('assets') ? doAssets :
        doLayouts
      } />}

      {/* Step 内容 */}
      {step === 'plan-loading' && <Spinner text="Analyzing your intent..." step="plan-loading" />}
      {step === 'plan-review' && !error && (
        <BriefEditor
          brief={designBrief}
          onChange={setDesignBrief}
          onConfirm={doAssets}
          onBack={onCancel}
        />
      )}

      {step === 'assets-loading' && <Spinner text="Searching for assets..." step="assets-loading" />}
      {step === 'assets-review' && !error && (
        <AssetPicker
          candidates={assetCandidates}
          selectedIndex={selectedAssetIdx}
          canvasWidth={config.canvasWidth}
          canvasHeight={config.canvasHeight}
          keywordsUsed={keywordsUsed}
          onSelect={setSelectedAssetIdx}
          onConfirm={doLayouts}
          onBack={() => setStep('plan-review')}
          onRefresh={refreshAssets}
          isRefreshing={isRefreshingAssets}
        />
      )}

      {step === 'layouts-loading' && <Spinner text="Generating layouts..." step="layouts-loading" />}
      {step === 'layouts-review' && !error && (
        <LayoutPicker
          layouts={layoutCandidates}
          selectedIndex={selectedLayoutIdx}
          onSelect={setSelectedLayoutIdx}
          onConfirm={doFinalize}
          onBack={() => setStep('assets-review')}
          onRefresh={refreshLayouts}
          isRefreshing={isRefreshingLayouts}
        />
      )}

      {step === 'finalizing' && <Spinner text="Finalizing poster..." step="finalizing" />}
    </div>
  );
};
