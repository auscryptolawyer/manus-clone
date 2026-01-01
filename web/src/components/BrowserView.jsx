export function BrowserView({ screenshot, pageUrl, pageTitle, elements }) {
  if (!screenshot) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-100 text-gray-400">
        <div className="text-center">
          <svg
            className="w-16 h-16 mx-auto mb-4 opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
          <p>Browser view will appear here</p>
          <p className="text-sm mt-2">Start a task to see the browser</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* URL Bar */}
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-800 text-white">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
        </div>
        <div className="flex-1 px-3 py-1 bg-gray-700 rounded text-sm text-gray-300 truncate">
          {pageUrl || 'about:blank'}
        </div>
      </div>

      {/* Page Title */}
      {pageTitle && (
        <div className="px-3 py-1 bg-gray-700 text-gray-300 text-xs truncate">
          {pageTitle}
        </div>
      )}

      {/* Screenshot */}
      <div className="flex-1 overflow-auto bg-white">
        <img
          src={`data:image/jpeg;base64,${screenshot}`}
          alt="Browser screenshot"
          className="w-full h-auto"
        />
      </div>

      {/* Element Count */}
      <div className="px-3 py-1 bg-gray-800 text-gray-400 text-xs">
        {elements.length} interactive elements detected
      </div>
    </div>
  );
}
