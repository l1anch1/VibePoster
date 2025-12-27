// frontend/src/components/DownloadButton.tsx
import React, { useState } from 'react';
import axios from 'axios';
import type { PosterData } from '../types/PosterSchema';

interface Props {
  data: PosterData;
}

export const DownloadButton: React.FC<Props> = ({ data }) => {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      // 调试：打印要发送的数据
      console.log('📤 准备发送数据到后端:', {
        canvas: data.canvas,
        layersCount: data.layers.length,
        textLayers: data.layers.filter(l => l.type === 'text').map(l => ({
          id: l.id,
          name: l.name,
          content: l.content,
          x: l.x,
          y: l.y,
          width: l.width,
          height: l.height,
          fontSize: l.type === 'text' ? l.fontSize : undefined,
          fontFamily: l.type === 'text' ? l.fontFamily : undefined,
          color: l.type === 'text' ? l.color : undefined,
        }))
      });
      
      const response = await axios.post('http://localhost:3000/api/render/psd', data, {
        responseType: 'blob', 
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'design_poster.psd');
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert("下载失败");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <button
      onClick={handleDownload}
      disabled={isDownloading}
      style={{
        width: '100%', // 全宽按钮，与生成按钮保持一致
        padding: '14px 20px',
        backgroundColor: isDownloading ? '#9CA3AF' : '#10B981', 
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '15px',
        fontWeight: 600,
        cursor: isDownloading ? 'not-allowed' : 'pointer',
        boxShadow: isDownloading 
          ? 'none' 
          : '0 4px 16px rgba(16, 185, 129, 0.4), 0 0 0 1px rgba(255,255,255,0.1)',
        transition: 'all 0.2s ease',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        backdropFilter: 'blur(10px)',
      }}
      onMouseEnter={(e) => {
        if (!isDownloading) {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.5), 0 0 0 1px rgba(255,255,255,0.1)';
        }
      }}
      onMouseLeave={(e) => {
        if (!isDownloading) {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 4px 16px rgba(16, 185, 129, 0.4), 0 0 0 1px rgba(255,255,255,0.1)';
        }
      }}
    >
      <span>📥</span>
      {isDownloading ? '打包中...' : '下载 PSD 源文件'}
    </button>
  );
};