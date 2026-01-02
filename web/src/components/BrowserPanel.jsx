export function BrowserPanel({ screenshot, pageUrl, pageTitle, elements, status, onClose }) {
  const isExecuting = ['executing', 'starting', 'browser_ready'].includes(status);

  return (
    <aside className="w-[500px] border-l border-gray-800 bg-gray-950 flex flex-col">
      {/* Header */}
      <div className="h-12 flex items-center justify-between px-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <span className="text-sm font-medium">Browser View</span>
          {isExecuting && (
            <span className="flex items-center gap-1 px-2 py-0.5 bg-blue-600/20 text-blue-400 text-xs rounded-full">
              <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
              Live
            </span>
          )}
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-800 rounded transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Browser Chrome */}
      {screenshot ? (
        <>
          {/* URL Bar */}
          <div className="px-3 py-2 bg-gray-900 border-b border-gray-800">
            <div className="flex items-center gap-2">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/70" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                <div className="w-3 h-3 rounded-full bg-green-500/70" />
              </div>
              <div className="flex-1 px-3 py-1 bg-gray-800 rounded text-xs text-gray-400 truncate">
                {pageUrl || 'about:blank'}
              </div>
            </div>
            {pageTitle && (
              <div className="mt-1 text-xs text-gray-500 truncate">{pageTitle}</div>
            )}
          </div>

          {/* Screenshot */}
          <div className="flex-1 overflow-auto bg-white">
            <img
              src={`data:image/jpeg;base64,${screenshot}`}
              alt="Browser screenshot"
              className="w-full h-auto"
            />
          </div>

          {/* Footer */}
          <div className="px-3 py-2 bg-gray-900 border-t border-gray-800 text-xs text-gray-500">
            {elements.length} interactive elements detected
          </div>
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center bg-gray-900">
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <p className="text-gray-500 mb-1">No browser session</p>
            <p className="text-gray-600 text-sm">Start a task to see the browser</p>
          </div>
        </div>
      )}
    </aside>
  );
}
