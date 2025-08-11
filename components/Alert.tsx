import React from 'react';

interface AlertProps {
  message: string;
}

const Alert: React.FC<AlertProps> = ({ message }) => {
  return (
    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg" role="alert">
      <p className="font-medium text-sm">Error</p>
      <p className="text-sm">{message}</p>
    </div>
  );
};

export default Alert;
