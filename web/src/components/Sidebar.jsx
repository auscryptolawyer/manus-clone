export function Sidebar({ isOpen, onToggle, isConnected, status }) {
  if (!isOpen) return null;

  return (
    <aside className="w-64 bg-gray-950 border-r border-gray-800 flex flex-col">
      {/* Logo */}
      <div className="h-12 flex items-center px-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
          </div>
          <span className="font-semibold text-white">Manus</span>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button className="w-full flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Task
        </button>
      </div>

      {/* Status */}
      <div className="flex-1 overflow-y-auto px-3">
        <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 px-2">Status</div>
        <div className="space-y-1">
          <StatusItem
            label="Connection"
            value={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'green' : 'red'}
          />
          <StatusItem
            label="Agent"
            value={formatStatus(status)}
            color={getStatusColor(status)}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-800">
        <div className="text-xs text-gray-500 text-center">
          Browser Automation Agent
        </div>
      </div>
    </aside>
  );
}

function StatusItem({ label, value, color }) {
  const colorClasses = {
    green: 'bg-green-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    blue: 'bg-blue-500',
    gray: 'bg-gray-500',
  };

  return (
    <div className="flex items-center justify-between px-2 py-1.5 rounded-lg hover:bg-gray-800/50">
      <span className="text-sm text-gray-400">{label}</span>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${colorClasses[color] || colorClasses.gray}`} />
        <span className="text-sm">{value}</span>
      </div>
    </div>
  );
}

function formatStatus(status) {
  const statusMap = {
    idle: 'Ready',
    planning: 'Planning...',
    awaiting_confirmation: 'Awaiting Confirmation',
    starting: 'Starting...',
    browser_ready: 'Browser Ready',
    executing: 'Executing',
    waiting_for_user: 'Needs Input',
    complete: 'Complete',
    cancelling: 'Cancelling...',
    cancelled: 'Cancelled',
  };
  return statusMap[status] || status;
}

function getStatusColor(status) {
  if (['idle', 'complete'].includes(status)) return 'green';
  if (['executing', 'starting', 'browser_ready'].includes(status)) return 'blue';
  if (['planning', 'awaiting_confirmation', 'waiting_for_user'].includes(status)) return 'yellow';
  if (['cancelling', 'cancelled'].includes(status)) return 'gray';
  return 'gray';
}
