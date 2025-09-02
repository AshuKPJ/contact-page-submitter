// src/components/AlertMessage.jsx
import React from 'react';
import { AlertCircle, CheckCircle, X } from 'lucide-react';

const AlertMessage = ({ type = 'error', title, message, onClose }) => {
  const styles = {
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: 'text-red-600'
    },
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icon: 'text-green-600'
    }
  };

  const style = styles[type];
  const Icon = type === 'error' ? AlertCircle : CheckCircle;

  return (
    <div className={`${style.bg} ${style.border} border rounded-lg p-4 mb-4`}>
      <div className="flex items-start">
        <Icon className={`w-5 h-5 ${style.icon} mt-0.5 mr-3`} />
        <div className="flex-1">
          <h3 className={`font-semibold ${style.text}`}>{title}</h3>
          <p className={`text-sm mt-1 ${style.text} opacity-90`}>{message}</p>
        </div>
        {onClose && (
          <button onClick={onClose} className={`${style.text} hover:opacity-70`}>
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default AlertMessage;