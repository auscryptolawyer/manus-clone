export function Controls({ status, isConnected, plan, currentStep, onCancel }) {
  const getStatusColor = () => {
    switch (status) {
      case 'idle':
        return 'bg-gray-500';
      case 'starting':
      case 'browser_ready':
      case 'planning':
        return 'bg-yellow-500';
      case 'executing':
        return 'bg-blue-500 animate-pulse';
      case 'waiting_for_user':
        return 'bg-orange-500 animate-pulse';
      case 'complete':
        return 'bg-green-500';
      case 'cancelling':
      case 'cancelled':
        return 'bg-gray-500';
      default:
        return 'bg-red-500';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'idle':
        return 'Ready';
      case 'starting':
        return 'Starting...';
      case 'browser_ready':
        return 'Browser ready';
      case 'planning':
        return 'Planning task...';
      case 'executing':
        return 'Executing...';
      case 'waiting_for_user':
        return 'Waiting for input';
      case 'complete':
        return 'Complete';
      case 'cancelling':
        return 'Cancelling...';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  };

  const isRunning = ['starting', 'browser_ready', 'planning', 'executing', 'waiting_for_user'].includes(status);

  return (
    <div className="p-4 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between">
        {/* Status */}
        <div className="flex items-center gap-3">
          {/* Connection indicator */}
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-gray-500">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Status badge */}
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor()}`} />
            <span className="text-sm font-medium text-gray-700">
              {getStatusText()}
            </span>
          </div>
        </div>

        {/* Cancel button */}
        {isRunning && (
          <button
            onClick={onCancel}
            className="px-4 py-1.5 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Progress */}
      {plan.length > 0 && (
        <div className="mt-3">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Progress</span>
            <span>{Math.min(currentStep, plan.length)} / {plan.length} steps</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / plan.length) * 100}%` }}
            />
          </div>

          {/* Current step description */}
          {currentStep > 0 && currentStep <= plan.length && (
            <p className="mt-2 text-sm text-gray-600 truncate">
              {plan[currentStep - 1]}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
