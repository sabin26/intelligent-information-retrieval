import React from 'react';
import { AppTab } from '../types';
import { SearchIcon, TagIcon } from './icons';

interface TabsProps {
  activeTab: AppTab;
  setActiveTab: (tab: AppTab) => void;
}

const Tabs: React.FC<TabsProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: AppTab.Search, label: 'Publication Search', icon: <SearchIcon className="w-5 h-5 mr-2" /> },
    { id: AppTab.Classifier, label: 'Document Classifier', icon: <TagIcon className="w-5 h-5 mr-2" /> },
  ];

  const getTabClass = (tabId: AppTab) => {
    const baseClasses = 'flex items-center justify-center w-full px-4 py-3 font-medium text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200';
    if (activeTab === tabId) {
      return `${baseClasses} bg-indigo-600 text-white shadow-md`;
    }
    return `${baseClasses} bg-white text-slate-600 hover:bg-slate-100`;
  };

  return (
    <div className="bg-slate-100 p-1.5 rounded-xl shadow-inner grid grid-cols-2 gap-2">
      {tabs.map(tab => (
        <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={getTabClass(tab.id)}>
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
};

export default Tabs;
