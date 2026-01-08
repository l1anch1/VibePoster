/**
 * 编辑器右侧面板组件
 *
 * 功能：图层列表、属性编辑（类似 PS）
 * 风格：iOS 液态玻璃
 */

import React from 'react';
import type { Layer, TextLayer, PosterData } from '../../types/PosterSchema';
import { isTextLayer } from '../../utils/editorUtils';

interface EditorRightPanelProps {
  data: PosterData;
  selectedLayerId: string | null;
  onSelectLayer: (id: string | null) => void;
  onUpdateLayer: (id: string, updates: Partial<Layer>) => void;
  onDeleteLayer: (id: string) => void;
}

export const EditorRightPanel: React.FC<EditorRightPanelProps> = ({
  data,
  selectedLayerId,
  onSelectLayer,
  onUpdateLayer,
  onDeleteLayer,
}) => {
  const selectedLayer = selectedLayerId
    ? data.layers.find((l) => l.id === selectedLayerId) || null
    : null;

  return (
    <aside
      className="w-64 flex flex-col shrink-0 m-3 ml-0 rounded-3xl overflow-hidden"
      style={{
        background: 'rgba(255,255,255,0.85)',
        backdropFilter: 'blur(20px) saturate(180%)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.1), inset 0 0 0 1px rgba(255,255,255,0.6)',
        border: '1px solid rgba(0,0,0,0.08)',
      }}
    >
      {/* 属性面板 */}
      <div className="flex-1 overflow-y-auto">
        {selectedLayer ? (
          <PropertyEditor
            layer={selectedLayer}
            onUpdate={onUpdateLayer}
            onDelete={onDeleteLayer}
          />
        ) : (
          <EmptyState />
        )}
      </div>

      {/* 图层列表 */}
      <LayerList
        layers={data.layers}
        selectedLayerId={selectedLayerId}
        onSelectLayer={onSelectLayer}
      />
    </aside>
  );
};

// ============================================================================
// 属性编辑器
// ============================================================================

interface PropertyEditorProps {
  layer: Layer;
  onUpdate: (id: string, updates: Partial<Layer>) => void;
  onDelete: (id: string) => void;
}

const PropertyEditor: React.FC<PropertyEditorProps> = ({ layer, onUpdate, onDelete }) => (
  <div className="p-4">
    {/* 图层信息 */}
    <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-md shadow-violet-500/20">
        <span className="text-lg">{layer.type === 'text' ? '📝' : '🖼️'}</span>
      </div>
      <div className="flex-1 min-w-0">
        <input
          type="text"
          value={layer.name}
          onChange={(e) => onUpdate(layer.id, { name: e.target.value })}
          className="w-full px-2 py-1.5 bg-white text-base font-semibold text-gray-900 border border-gray-300 rounded-lg focus:border-violet-500 focus:outline-none truncate shadow-sm"
        />
        <div className="text-sm text-gray-500 capitalize mt-1">{layer.type} Layer</div>
      </div>
    </div>

    {/* Transform */}
    <div className="py-4 border-b border-gray-200">
      <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
        Transform
      </h4>
      <div className="grid grid-cols-2 gap-2">
        {[
          { key: 'x', label: 'X' },
          { key: 'y', label: 'Y' },
          { key: 'width', label: 'W' },
          { key: 'height', label: 'H' },
        ].map(({ key, label }) => (
          <div key={key} className="relative">
            <label className="absolute left-2.5 top-1/2 -translate-y-1/2 text-sm text-gray-500 font-medium">
              {label}
            </label>
            <input
              type="number"
              value={Math.round(layer[key as keyof typeof layer] as number)}
              onChange={(e) => onUpdate(layer.id, { [key]: Number(e.target.value) })}
              className="w-full pl-8 pr-2 py-2.5 text-base bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none transition-all text-gray-900 shadow-sm"
            />
          </div>
        ))}
      </div>
    </div>

    {/* 文本属性 */}
    {isTextLayer(layer) && <TextProperties layer={layer} onUpdate={onUpdate} />}

    {/* 删除按钮 */}
    <div className="pt-4">
      <button
        onClick={() => onDelete(layer.id)}
        className="w-full py-3 text-base font-medium text-red-600 bg-red-50 hover:bg-red-100 border border-red-200 rounded-xl transition-colors flex items-center justify-center gap-2 shadow-sm"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
        Delete Layer
      </button>
    </div>
  </div>
);

// ============================================================================
// 文本属性编辑
// ============================================================================

interface TextPropertiesProps {
  layer: TextLayer;
  onUpdate: (id: string, updates: Partial<TextLayer>) => void;
}

const TextProperties: React.FC<TextPropertiesProps> = ({ layer, onUpdate }) => (
  <div className="py-4 border-b border-gray-200">
    <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
      Typography
    </h4>

    {/* 文本内容 */}
    <textarea
      value={layer.content}
      onChange={(e) => onUpdate(layer.id, { content: e.target.value })}
      rows={2}
      className="w-full px-3 py-2.5 text-base bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none resize-none mb-3 transition-all text-gray-900 shadow-sm"
      placeholder="Enter text..."
    />

    {/* 字号和颜色 */}
    <div className="grid grid-cols-2 gap-2 mb-3">
      <div className="relative">
        <label className="absolute left-2.5 top-1/2 -translate-y-1/2 text-sm text-gray-500">
          Size
        </label>
        <input
          type="number"
          value={layer.fontSize}
          onChange={(e) => onUpdate(layer.id, { fontSize: Number(e.target.value) })}
          className="w-full pl-11 pr-2 py-2.5 text-base bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none transition-all text-gray-900 shadow-sm"
        />
      </div>
      <div className="relative">
        <input
          type="color"
          value={layer.color}
          onChange={(e) => onUpdate(layer.id, { color: e.target.value })}
          className="absolute inset-0 opacity-0 cursor-pointer"
        />
        <div className="flex items-center gap-2 px-2.5 py-2.5 bg-white border border-gray-300 rounded-xl cursor-pointer shadow-sm hover:border-violet-400 transition-colors">
          <div
            className="w-5 h-5 rounded-md border border-gray-300 shadow-inner"
            style={{ backgroundColor: layer.color }}
          />
          <span className="text-sm text-gray-600 font-mono truncate">{layer.color}</span>
        </div>
      </div>
    </div>

    {/* 对齐方式 */}
    <div className="flex gap-1">
      {(['left', 'center', 'right'] as const).map((align) => (
        <button
          key={align}
          onClick={() => onUpdate(layer.id, { textAlign: align })}
          className={`flex-1 py-2.5 rounded-xl transition-all text-base font-medium ${layer.textAlign === align
            ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-md shadow-violet-500/30'
            : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-300 shadow-sm'
            }`}
        >
          {align === 'left' ? '◀' : align === 'center' ? '●' : '▶'}
        </button>
      ))}
    </div>
  </div>
);

// ============================================================================
// 空状态
// ============================================================================

const EmptyState: React.FC = () => (
  <div className="flex-1 flex items-center justify-center p-6 text-center">
    <div>
      <div className="w-14 h-14 mx-auto mb-3 rounded-xl bg-gray-100 border border-gray-200 flex items-center justify-center shadow-sm">
        <svg className="w-7 h-7 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"
          />
        </svg>
      </div>
      <p className="text-base text-gray-600 font-medium">Select a layer to edit</p>
      <p className="text-sm text-gray-400 mt-1">or click on canvas</p>
    </div>
  </div>
);

// ============================================================================
// 图层列表
// ============================================================================

interface LayerListProps {
  layers: Layer[];
  selectedLayerId: string | null;
  onSelectLayer: (id: string | null) => void;
}

const LayerList: React.FC<LayerListProps> = ({ layers, selectedLayerId, onSelectLayer }) => (
  <div className="border-t border-gray-200">
    <div className="h-11 px-4 flex items-center justify-between bg-gray-50/80">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Layers</h3>
      <span className="text-sm text-gray-600 bg-white px-2 py-0.5 rounded-md border border-gray-200 shadow-sm">
        {layers.length}
      </span>
    </div>
    <div className="max-h-48 overflow-y-auto p-2">
      {layers.length === 0 ? (
        <div className="text-center py-6 text-sm text-gray-400">No layers yet</div>
      ) : (
        [...layers].reverse().map((layer, i) => (
          <button
            key={layer.id}
            onClick={() => onSelectLayer(layer.id)}
            className={`flex items-center gap-2 w-full px-3 py-2.5 rounded-xl mb-1 text-left transition-all ${selectedLayerId === layer.id
              ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-md shadow-violet-500/20'
              : 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 shadow-sm'
              }`}
          >
            <span className="text-base">{layer.type === 'text' ? '📝' : '🖼️'}</span>
            <span className="text-base font-medium truncate flex-1">{layer.name}</span>
            <span
              className={`text-sm ${selectedLayerId === layer.id ? 'text-white/70' : 'text-gray-400'
                }`}
            >
              {layers.length - i}
            </span>
          </button>
        ))
      )}
    </div>
  </div>
);
