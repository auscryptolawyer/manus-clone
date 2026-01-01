import { useState } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { Chat } from './components/Chat';
import { BrowserView } from './components/BrowserView';
import { Controls } from './components/Controls';

function App() {
  const {
    isConnected,
    status,
    plan,
    currentStep,
    screenshot,
    elements,
    pageUrl,
    pageTitle,
    messages,
    result,
    error,
    startTask,
    cancelTask,
    sendUserMessage,
  } = useWebSocket();

  const [showBrowser, setShowBrowser] = useState(true);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <h1 className="text-xl font-semibold text-gray-800">
            Manus Clone
          </h1>
          <button
            onClick={() => setShowBrowser(!showBrowser)}
            className="md:hidden px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg"
          >
            {showBrowser ? 'Show Chat' : 'Show Browser'}
          </button>
        </div>
      </header>

      {/* Controls */}
      <Controls
        status={status}
        isConnected={isConnected}
        plan={plan}
        currentStep={currentStep}
        onCancel={cancelTask}
      />

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Desktop: Side by side */}
        {/* Mobile: Toggle between views */}

        {/* Browser View */}
        <div
          className={`
            w-full md:w-1/2 lg:w-3/5 h-full border-r border-gray-200
            ${showBrowser ? 'block' : 'hidden md:block'}
          `}
        >
          <BrowserView
            screenshot={screenshot}
            pageUrl={pageUrl}
            pageTitle={pageTitle}
            elements={elements}
          />
        </div>

        {/* Chat */}
        <div
          className={`
            w-full md:w-1/2 lg:w-2/5 h-full bg-white
            ${showBrowser ? 'hidden md:block' : 'block'}
          `}
        >
          <Chat
            messages={messages}
            onSendMessage={sendUserMessage}
            onSendTask={startTask}
            status={status}
            isConnected={isConnected}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
