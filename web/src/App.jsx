import { useState } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { BrowserPanel } from './components/BrowserPanel';

function App() {
  const {
    isConnected,
    status,
    plan,
    pendingPlan,
    currentStep,
    screenshot,
    elements,
    pageUrl,
    pageTitle,
    messages,
    result,
    error,
    startTask,
    confirmPlan,
    rejectPlan,
    cancelTask,
    sendUserMessage,
  } = useWebSocket();

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [browserPanelOpen, setBrowserPanelOpen] = useState(true);

  return (
    <div className="h-screen flex bg-gray-900 text-gray-100">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        isConnected={isConnected}
        status={status}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-12 border-b border-gray-700 flex items-center justify-between px-4 bg-gray-800">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="font-medium">Browser Agent</h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setBrowserPanelOpen(!browserPanelOpen)}
              className={`p-1.5 rounded-lg transition-colors ${browserPanelOpen ? 'bg-blue-600 text-white' : 'hover:bg-gray-700'}`}
              title="Toggle browser view"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </button>
            {status !== 'idle' && status !== 'complete' && status !== 'awaiting_confirmation' && (
              <button
                onClick={cancelTask}
                className="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
              >
                Cancel
              </button>
            )}
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Chat Area */}
          <ChatArea
            messages={messages}
            status={status}
            pendingPlan={pendingPlan}
            plan={plan}
            currentStep={currentStep}
            isConnected={isConnected}
            onSendTask={startTask}
            onSendMessage={sendUserMessage}
            onConfirmPlan={confirmPlan}
            onRejectPlan={rejectPlan}
          />

          {/* Browser Panel */}
          {browserPanelOpen && (
            <BrowserPanel
              screenshot={screenshot}
              pageUrl={pageUrl}
              pageTitle={pageTitle}
              elements={elements}
              status={status}
              onClose={() => setBrowserPanelOpen(false)}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
