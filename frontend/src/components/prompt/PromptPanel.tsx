/**
 * 左侧问答面板组件
 * 
 * 包含：快速开始卡片、输入框、生成按钮
 */

import React, { useState } from 'react';

interface PromptPanelProps {
  onGenerate: (prompt: string, imageFile?: File | null) => void;
  isGenerating: boolean;
}

const QUICK_START_PROMPTS = [
  {
    icon: '💼',
    title: '商务海报',
    prompt: '创建一张简约大气的商务发布会海报，包含"新品发布"大标题和日期时间',
  },
  {
    icon: '🎉',
    title: '活动宣传',
    prompt: '设计一张热烈醒目的音乐节海报，标题"夏日音乐节"，包含时间地点信息',
  },
  {
    icon: '🛍️',
    title: '产品推广',
    prompt: '制作一张时尚精致的新品上市海报，突出产品特点和优惠信息',
  },
  {
    icon: '🎓',
    title: '校园活动',
    prompt: '设计一张充满活力的社团招新海报，吸引大学新生加入',
  },
];

export const PromptPanel: React.FC<PromptPanelProps> = ({ onGenerate, isGenerating }) => {
  const [prompt, setPrompt] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  // 处理图片上传
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // 清除图片
  const handleRemoveImage = () => {
    setImageFile(null);
    setImagePreview(null);
  };

  // 处理生成
  const handleSubmit = () => {
    if (prompt.trim() || imageFile) {
      onGenerate(prompt.trim(), imageFile);
    }
  };

  // 使用快速开始提示
  const handleQuickStart = (quickPrompt: string) => {
    setPrompt(quickPrompt);
  };

  return (
    <div
      style={{
        width: '380px',
        height: '100%',
        backgroundColor: '#FAFBFC',
        borderRight: '1px solid #E5E7EB',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* 顶部标题 */}
      <div
        style={{
          padding: '24px 24px 16px',
          borderBottom: '1px solid #E5E7EB',
        }}
      >
        <h2
          style={{
            fontSize: '18px',
            fontWeight: 700,
            color: '#1F2937',
            margin: 0,
            marginBottom: '6px',
          }}
        >
          ✨ AI 海报生成
        </h2>
        <p
          style={{
            fontSize: '13px',
            color: '#6B7280',
            margin: 0,
            lineHeight: 1.5,
          }}
        >
          描述你想要的海报内容，或上传参考图片
        </p>
      </div>

      {/* 快速开始卡片 */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px',
        }}
      >
        <div style={{ marginBottom: '16px' }}>
          <h3
            style={{
              fontSize: '13px',
              fontWeight: 600,
              color: '#6B7280',
              margin: '0 0 12px 0',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            快速开始
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {QUICK_START_PROMPTS.map((item, index) => (
              <button
                key={index}
                onClick={() => handleQuickStart(item.prompt)}
                disabled={isGenerating}
                style={{
                  padding: '14px 16px',
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #E5E7EB',
                  borderRadius: '10px',
                  textAlign: 'left',
                  cursor: isGenerating ? 'not-allowed' : 'pointer',
                  transition: 'all 0.15s ease',
                  opacity: isGenerating ? 0.6 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!isGenerating) {
                    e.currentTarget.style.backgroundColor = '#F9FAFB';
                    e.currentTarget.style.borderColor = '#D1D5DB';
                    e.currentTarget.style.transform = 'translateX(2px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isGenerating) {
                    e.currentTarget.style.backgroundColor = '#FFFFFF';
                    e.currentTarget.style.borderColor = '#E5E7EB';
                    e.currentTarget.style.transform = 'translateX(0)';
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '20px' }}>{item.icon}</span>
                  <span style={{ fontSize: '14px', fontWeight: 600, color: '#374151' }}>
                    {item.title}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* 图片预览 */}
        {imagePreview && (
          <div
            style={{
              marginTop: '16px',
              padding: '12px',
              backgroundColor: '#FFFFFF',
              borderRadius: '10px',
              border: '1px solid #E5E7EB',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px',
              }}
            >
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>
                📎 参考图片
              </span>
              <button
                onClick={handleRemoveImage}
                style={{
                  padding: '4px 8px',
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '12px',
                  color: '#EF4444',
                  fontWeight: 500,
                }}
              >
                移除
              </button>
            </div>
            <img
              src={imagePreview}
              alt="Preview"
              style={{
                width: '100%',
                borderRadius: '8px',
                border: '1px solid #E5E7EB',
              }}
            />
          </div>
        )}
      </div>

      {/* 底部输入区域 */}
      <div
        style={{
          padding: '20px',
          backgroundColor: '#FFFFFF',
          borderTop: '1px solid #E5E7EB',
        }}
      >
        {/* 文本输入框 */}
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="描述你想要的海报内容，例如：创建一张活动宣传海报..."
          disabled={isGenerating}
          style={{
            width: '100%',
            minHeight: '120px',
            padding: '14px 16px',
            fontSize: '14px',
            lineHeight: 1.6,
            color: '#1F2937',
            backgroundColor: '#F9FAFB',
            border: '1px solid #E5E7EB',
            borderRadius: '10px',
            resize: 'vertical',
            fontFamily: 'inherit',
            outline: 'none',
            transition: 'all 0.15s ease',
            opacity: isGenerating ? 0.6 : 1,
            marginBottom: '12px',
          }}
          onFocus={(e) => {
            e.currentTarget.style.backgroundColor = '#FFFFFF';
            e.currentTarget.style.borderColor = '#6366F1';
          }}
          onBlur={(e) => {
            e.currentTarget.style.backgroundColor = '#F9FAFB';
            e.currentTarget.style.borderColor = '#E5E7EB';
          }}
        />

        {/* 操作按钮 */}
        <div style={{ display: 'flex', gap: '10px' }}>
          {/* 上传图片按钮 */}
          <label
            style={{
              flex: 1,
              padding: '12px 16px',
              backgroundColor: '#F9FAFB',
              border: '1px solid #E5E7EB',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 600,
              color: '#374151',
              cursor: isGenerating ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.15s ease',
              opacity: isGenerating ? 0.6 : 1,
            }}
            onMouseEnter={(e) => {
              if (!isGenerating) {
                e.currentTarget.style.backgroundColor = '#F3F4F6';
                e.currentTarget.style.borderColor = '#D1D5DB';
              }
            }}
            onMouseLeave={(e) => {
              if (!isGenerating) {
                e.currentTarget.style.backgroundColor = '#F9FAFB';
                e.currentTarget.style.borderColor = '#E5E7EB';
              }
            }}
          >
            <span>🖼️</span>
            <span>上传图片</span>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              disabled={isGenerating}
              style={{ display: 'none' }}
            />
          </label>

          {/* 生成按钮 */}
          <button
            onClick={handleSubmit}
            disabled={isGenerating || (!prompt.trim() && !imageFile)}
            style={{
              flex: 2,
              padding: '12px 20px',
              backgroundColor:
                isGenerating || (!prompt.trim() && !imageFile) ? '#9CA3AF' : '#6366F1',
              border: 'none',
              borderRadius: '10px',
              fontSize: '15px',
              fontWeight: 700,
              color: '#FFFFFF',
              cursor:
                isGenerating || (!prompt.trim() && !imageFile) ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.15s ease',
              boxShadow:
                isGenerating || (!prompt.trim() && !imageFile)
                  ? 'none'
                  : '0 4px 12px rgba(99, 102, 241, 0.3)',
            }}
            onMouseEnter={(e) => {
              if (!isGenerating && (prompt.trim() || imageFile)) {
                e.currentTarget.style.backgroundColor = '#4F46E5';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 6px 16px rgba(99, 102, 241, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isGenerating && (prompt.trim() || imageFile)) {
                e.currentTarget.style.backgroundColor = '#6366F1';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(99, 102, 241, 0.3)';
              }
            }}
          >
            {isGenerating ? (
              <>
                <div
                  style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid #FFFFFF',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 0.6s linear infinite',
                  }}
                />
                <span>生成中...</span>
              </>
            ) : (
              <>
                <span>🚀</span>
                <span>生成海报</span>
              </>
            )}
          </button>
        </div>

        {/* 提示文字 */}
        <div
          style={{
            marginTop: '12px',
            fontSize: '12px',
            color: '#9CA3AF',
            textAlign: 'center',
          }}
        >
          按 {navigator.platform.includes('Mac') ? 'Cmd' : 'Ctrl'} + Enter 快速生成
        </div>
      </div>

      {/* CSS动画 */}
      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

