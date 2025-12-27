import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import type { PosterData } from '../types/PosterSchema';

interface Props {
  onGenerateSuccess: (data: PosterData) => void; 
}

export const PromptInput: React.FC<Props> = ({ onGenerateSuccess }) => {
  const [prompt, setPrompt] = useState("");
  const [fileA, setFileA] = useState<File | null>(null); // 人物图
  const [fileB, setFileB] = useState<File | null>(null); // 背景图
  const [isLoading, setIsLoading] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0); // 已用时间（秒）
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number | null>(null);

  // 计时器效果
  useEffect(() => {
    if (isLoading) {
      // 开始计时
      startTimeRef.current = Date.now();
      setElapsedTime(0);
      
      intervalRef.current = setInterval(() => {
        if (startTimeRef.current) {
          const elapsed = (Date.now() - startTimeRef.current) / 1000; // 转换为秒
          setElapsedTime(elapsed);
        }
      }, 100); // 每0.1秒更新一次
    } else {
      // 停止计时
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      startTimeRef.current = null;
      setElapsedTime(0);
    }
    
    // 清理函数
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isLoading]);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsLoading(true);
    try {
      // ⚠️ 关键变化：使用 FormData 发送多模态数据
      const formData = new FormData();
      formData.append('prompt', prompt);
      if (fileA) formData.append('image_person', fileA);
      if (fileB) formData.append('image_bg', fileB);

      // 发送到新的多模态接口
      const res = await axios.post('http://localhost:8000/api/generate_multimodal', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      onGenerateSuccess(res.data);
      
    } catch (error) {
      console.error("生成失败:", error);
      alert("生成失败，请检查后端");
    } finally {
      setIsLoading(false);
    }
  };
  
  // 格式化时间显示（精确到0.1秒）
  const formatTime = (seconds: number): string => {
    return seconds.toFixed(1);
  };

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 20 }}>
      
      {/* 文本输入 */}
      <div>
        <label style={{
          display: 'block', 
          marginBottom: 8, 
          fontWeight: 600, 
          color: '#111827',
          fontSize: '14px'
        }}>
          设计需求
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="例如: 把这个人放到海滩背景里，标题写'度假时光'..."
          style={{ 
            width: '100%', 
            height: 90, 
            padding: '12px', 
            borderRadius: 8, 
            border: '1px solid #D1D5DB',
            backgroundColor: '#FFFFFF',
            fontFamily: 'inherit',
            fontSize: '14px',
            color: '#111827',
            resize: 'vertical',
            transition: 'border-color 0.2s, box-shadow 0.2s',
            outline: 'none'
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = '#2563EB';
            e.currentTarget.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = '#D1D5DB';
            e.currentTarget.style.boxShadow = 'none';
          }}
        />
      </div>

      {/* 图片 A 上传 */}
      <div>
        <label style={{
          display: 'block', 
          marginBottom: 8, 
          fontSize: 14, 
          fontWeight: 600,
          color: '#374151'
        }}>
          👤 主体人物
        </label>
        <input 
          type="file" 
          accept="image/*"
          onChange={(e) => setFileA(e.target.files ? e.target.files[0] : null)}
          style={{
            width: '100%',
            fontSize: '13px',
            color: '#6B7280'
          }}
        />
        {fileA && (
          <div style={{
            marginTop: 6,
            fontSize: '12px',
            color: '#10B981',
            fontWeight: 500
          }}>
            ✓ {fileA.name}
          </div>
        )}
      </div>

      {/* 图片 B 上传 */}
      <div>
        <label style={{
          display: 'block', 
          marginBottom: 8, 
          fontSize: 14, 
          fontWeight: 600,
          color: '#374151'
        }}>
          🏞 背景场景
        </label>
        <input 
          type="file" 
          accept="image/*"
          onChange={(e) => setFileB(e.target.files ? e.target.files[0] : null)}
          style={{
            width: '100%',
            fontSize: '13px',
            color: '#6B7280'
          }}
        />
        {fileB && (
          <div style={{
            marginTop: 6,
            fontSize: '12px',
            color: '#10B981',
            fontWeight: 500
          }}>
            ✓ {fileB.name}
          </div>
        )}
      </div>

      <button
        onClick={handleGenerate}
        disabled={isLoading}
        style={{
          padding: '14px 20px', 
          backgroundColor: isLoading ? '#9CA3AF' : '#2563EB', 
          color: 'white', 
          border: 'none', 
          borderRadius: 8, 
          cursor: isLoading ? 'not-allowed' : 'pointer', 
          fontWeight: 600,
          fontSize: '15px',
          transition: 'all 0.2s ease',
          boxShadow: isLoading ? 'none' : '0 2px 8px rgba(37, 99, 235, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px'
        }}
        onMouseEnter={(e) => {
          if (!isLoading) {
            e.currentTarget.style.backgroundColor = '#1D4ED8';
            e.currentTarget.style.transform = 'translateY(-1px)';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(37, 99, 235, 0.4)';
          }
        }}
        onMouseLeave={(e) => {
          if (!isLoading) {
            e.currentTarget.style.backgroundColor = '#2563EB';
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 2px 8px rgba(37, 99, 235, 0.3)';
          }
        }}
      >
        {isLoading ? (
          <>
            <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⚙️</span>
            <span>AI 正在处理...</span>
            <span style={{ 
              marginLeft: '8px', 
              fontSize: '13px', 
              opacity: 0.9,
              fontFamily: 'monospace'
            }}>
              ({formatTime(elapsedTime)}s)
            </span>
          </>
        ) : (
          <>
            <span>✨</span>
            <span>开始融合生成</span>
          </>
        )}
      </button>
    </div>
  );
};