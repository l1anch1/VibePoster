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
        // ⚠️ 修改点：删除了 position: fixed, top, right
        // 现在它只负责长得像个按钮，位置由 App.tsx 里的父容器决定
        padding: '12px 24px',
        backgroundColor: isDownloading ? '#9CA3AF' : '#10B981', 
        color: 'white',
        border: 'none',
        borderRadius: '50px', // 变成圆角矩形更好看
        fontSize: '16px',
        fontWeight: 'bold',
        cursor: isDownloading ? 'not-allowed' : 'pointer',
        boxShadow: '0 4px 15px rgba(16, 185, 129, 0.4)', // 加个绿色光晕
        transition: 'transform 0.2s, box-shadow 0.2s',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}
      onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
      onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
    >
      <span>📥</span>
      {isDownloading ? '打包中...' : '下载 PSD 源文件'}
    </button>
  );
};