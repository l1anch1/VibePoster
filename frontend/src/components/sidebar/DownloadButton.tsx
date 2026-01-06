// frontend/src/components/DownloadButton.tsx
import React, { useState } from 'react';
import axios from 'axios';
import type { PosterData } from '../../types/PosterSchema';

interface Props {
  data: PosterData;
}

type DownloadFormat = 'psd' | 'png' | 'jpg';

export const DownloadButton: React.FC<Props> = ({ data }) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<DownloadFormat>('png');
  const [showDropdown, setShowDropdown] = useState(false);

  const formatInfo = {
    psd: { label: 'PSD 源文件', icon: '📐', desc: '可编辑的源文件' },
    png: { label: 'PNG 图片', icon: '🖼️', desc: '高质量透明图片' },
    jpg: { label: 'JPG 图片', icon: '📷', desc: '通用图片格式' },
  };

  const handleDownload = async (format: DownloadFormat) => {
    setIsDownloading(true);
    setShowDropdown(false);

    try {
      console.log(`📤 准备下载 ${format.toUpperCase()} 格式...`);

      let response;
      let filename;

      if (format === 'psd') {
        // PSD 下载（返回 ZIP 包）
        response = await axios.post('http://localhost:3000/api/render/psd', data, {
          responseType: 'blob',
        });
        filename = 'poster_with_fonts.zip';
      } else {
        // PNG/JPG 下载
        response = await axios.post(
          `http://localhost:3000/api/render/image?format=${format}&quality=95`,
          data,
          {
            responseType: 'blob',
          }
        );
        filename = `poster.${format}`;
      }

      console.log(`📥 下载文件名: ${filename}`);

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log(`✅ ${format.toUpperCase()} 下载成功`);
    } catch (error) {
      console.error('❌ 下载失败:', error);
      alert(`下载 ${format.toUpperCase()} 失败，请重试`);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      {/* 主下载按钮 */}
      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={() => handleDownload(selectedFormat)}
          disabled={isDownloading}
          style={{
            flex: 1,
            padding: '14px 20px',
            backgroundColor: isDownloading ? '#9CA3AF' : '#10B981',
            color: 'white',
            border: 'none',
            borderRadius: '12px 0 0 12px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: isDownloading ? 'not-allowed' : 'pointer',
            boxShadow: isDownloading
              ? 'none'
              : '0 4px 16px rgba(16, 185, 129, 0.4)',
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
          }}
          onMouseEnter={(e) => {
            if (!isDownloading) {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.5)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isDownloading) {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(16, 185, 129, 0.4)';
            }
          }}
        >
          <span>{formatInfo[selectedFormat].icon}</span>
          {isDownloading ? '下载中...' : `下载 ${selectedFormat.toUpperCase()}`}
        </button>

        {/* 格式选择按钮 */}
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          disabled={isDownloading}
          style={{
            padding: '14px 16px',
            backgroundColor: isDownloading ? '#9CA3AF' : '#10B981',
            color: 'white',
            border: 'none',
            borderRadius: '0 12px 12px 0',
            fontSize: '15px',
            fontWeight: 600,
            cursor: isDownloading ? 'not-allowed' : 'pointer',
            boxShadow: isDownloading
              ? 'none'
              : '0 4px 16px rgba(16, 185, 129, 0.4)',
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onMouseEnter={(e) => {
            if (!isDownloading) {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.5)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isDownloading) {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(16, 185, 129, 0.4)';
            }
          }}
        >
          ▼
        </button>
      </div>

      {/* 格式选择下拉菜单 */}
      {showDropdown && !isDownloading && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 8px)',
            left: 0,
            right: 0,
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
            zIndex: 1000,
            overflow: 'hidden',
            border: '1px solid #E5E7EB',
          }}
        >
          {(Object.keys(formatInfo) as DownloadFormat[]).map((format) => (
            <button
              key={format}
              onClick={() => {
                setSelectedFormat(format);
                setShowDropdown(false);
              }}
              style={{
                width: '100%',
                padding: '14px 16px',
                backgroundColor: selectedFormat === format ? '#F0FDF4' : '#FFFFFF',
                border: 'none',
                borderBottom: '1px solid #F3F4F6',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'background-color 0.15s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
              }}
              onMouseEnter={(e) => {
                if (selectedFormat !== format) {
                  e.currentTarget.style.backgroundColor = '#F9FAFB';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedFormat !== format) {
                  e.currentTarget.style.backgroundColor = '#FFFFFF';
                }
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '18px' }}>{formatInfo[format].icon}</span>
                <span style={{ fontSize: '15px', fontWeight: 600, color: '#1F2937' }}>
                  {formatInfo[format].label}
                </span>
                {selectedFormat === format && (
                  <span style={{ marginLeft: 'auto', color: '#10B981', fontSize: '18px' }}>✓</span>
                )}
              </div>
              <div style={{ fontSize: '13px', color: '#6B7280', paddingLeft: '28px' }}>
                {formatInfo[format].desc}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* 点击外部关闭下拉菜单 */}
      {showDropdown && (
        <div
          onClick={() => setShowDropdown(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 999,
          }}
        />
      )}
    </div>
  );
};