/**
 * 工具栏按钮组件
 */

import React from 'react';

interface ToolButtonProps {
    onClick: () => void;
    disabled?: boolean;
    active?: boolean;
    title?: string;
    children: React.ReactNode;
}

export const ToolButton: React.FC<ToolButtonProps> = ({
  onClick,
  disabled = false,
  active = false,
  title,
  children,
}) => (
  <button
    onClick={onClick}
    disabled={disabled}
    title={title}
    style={{
      background: active ? '#EFF6FF' : disabled ? '#F3F4F6' : '#FFFFFF',
      border: active ? '2px solid #3B82F6' : '2px solid #E5E7EB',
      borderRadius: '8px',
      padding: '10px 16px',
      cursor: disabled ? 'not-allowed' : 'pointer',
      color: disabled ? '#9CA3AF' : active ? '#3B82F6' : '#111827',
      fontSize: '15px',
      fontWeight: 600,
      opacity: disabled ? 0.5 : 1,
      transition: 'all 0.2s ease',
      display: 'flex',
      alignItems: 'center',
      gap: '6px',
      minHeight: '44px',
      flex: 1,
    }}
    onMouseEnter={(e) => {
      if (!disabled && !active) {
        e.currentTarget.style.backgroundColor = '#F9FAFB';
        e.currentTarget.style.borderColor = '#D1D5DB';
        e.currentTarget.style.transform = 'translateY(-1px)';
      }
    }}
    onMouseLeave={(e) => {
      if (!disabled && !active) {
        e.currentTarget.style.backgroundColor = '#FFFFFF';
        e.currentTarget.style.borderColor = '#E5E7EB';
        e.currentTarget.style.transform = 'translateY(0)';
      }
    }}
  >
    {children}
  </button>
);

