// frontend/src/components/PromptInput.tsx
import React, { useState } from 'react';
import axios from 'axios';
import type { PosterData } from '../types/PosterSchema';

interface Props {
  onGenerateSuccess: (data: PosterData) => void; 
}

export const PromptInput: React.FC<Props> = ({ onGenerateSuccess }) => {
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setIsLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/generate', null, {
        params: { prompt: prompt } 
      });
      onGenerateSuccess(res.data);
    } catch (error) {
      console.error("生成失败:", error);
      alert("后端连接失败");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      // ⚠️ 修改点：删除了 position: fixed, left, top, zIndex
      width: '100%', // 占满 Sidebar 宽度
      display: 'flex',
      flexDirection: 'column',
      gap: 10
    }}>
      
      <label style={{ fontSize: '14px', fontWeight: 'bold', color: '#555' }}>
        描述你的需求：
      </label>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="例如: 科技风招聘，蓝黑色调..."
        style={{
          width: '100%',
          height: 120, //稍微高一点
          padding: 12,
          borderRadius: 8,
          border: '1px solid #ddd',
          resize: 'none',
          boxSizing: 'border-box',
          fontSize: '14px',
          lineHeight: '1.5',
          outline: 'none',
          transition: 'border 0.2s'
        }}
      />

      <button
        onClick={handleGenerate}
        disabled={isLoading}
        style={{
          width: '100%',
          padding: '12px 0',
          backgroundColor: isLoading ? '#9CA3AF' : '#2563EB',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          cursor: isLoading ? 'not-allowed' : 'pointer',
          fontWeight: 'bold',
          fontSize: '15px',
          transition: 'background-color 0.2s'
        }}
      >
        {isLoading ? '🤖 正在思考与设计...' : '✨ 开始生成'}
      </button>
    </div>
  );
};