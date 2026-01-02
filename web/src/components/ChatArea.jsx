import { useState, useRef, useEffect } from 'react';

export function ChatArea({
  messages,
  status,
  pendingPlan,
  plan,
  currentStep,
  isConnected,
  onSendTask,
  onSendMessage,
  onConfirmPlan,
  onRejectPlan,
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || !isConnected) return;

    if (status === 'idle' || status === 'complete') {
      onSendTask(input.trim());
    } else if (status === 'waiting_for_user') {
      onSendMessage(input.trim());
    }

    setInput('');
  };

  const canSend = isConnected && (
    status === 'idle' ||
    status === 'complete' ||
    status === 'waiting_for_user'
  );

  const getPlaceholder = () => {
    if (!isConnected) return 'Connecting...';
    if (status === 'waiting_for_user') return 'Type your response...';
    if (status === 'awaiting_confirmation') return 'Review the plan above...';
    if (status === 'idle' || status === 'complete') return 'What would you like me to do?';
    return 'Task in progress...';
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-gray-900">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto py-6 px-4 space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-20">
              <div className="w-16 h-16 bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
              </div>
              <h2 className="text-xl font-medium text-gray-300 mb-2">Browser Agent</h2>
              <p className="text-gray-500 max-w-md mx-auto">
                Describe a web task and I'll browse the internet to complete it for you.
              </p>
              <div className="mt-6 flex flex-wrap justify-center gap-2">
                {['Search for news', 'Find weather', 'Look up information'].map((example) => (
                  <button
                    key={example}
                    onClick={() => setInput(example)}
                    className="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <MessageBubble key={idx} message={msg} />
          ))}

          {/* Plan Confirmation UI */}
          {pendingPlan && status === 'awaiting_confirmation' && (
            <PlanConfirmation
              plan={pendingPlan}
              onConfirm={onConfirmPlan}
              onReject={onRejectPlan}
            />
          )}

          {/* Progress indicator */}
          {plan.length > 0 && status === 'executing' && (
            <ProgressIndicator plan={plan} currentStep={currentStep} />
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-800 bg-gray-900">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto p-4">
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={getPlaceholder()}
              disabled={!canSend}
              className="w-full px-4 py-3 pr-12 bg-gray-800 border border-gray-700 rounded-xl focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-gray-100 placeholder-gray-500"
            />
            <button
              type="submit"
              disabled={!canSend || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function MessageBubble({ message }) {
  const { type, content, steps } = message;

  const isUser = type === 'task' || type === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] px-4 py-2 bg-blue-600 rounded-2xl rounded-br-md">
          <p className="text-white">{content}</p>
        </div>
      </div>
    );
  }

  if (type === 'plan_pending') {
    return (
      <div className="flex gap-3">
        <div className="w-8 h-8 bg-gray-800 rounded-lg flex-shrink-0 flex items-center justify-center">
          <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <div className="flex-1">
          <p className="text-gray-300 mb-3">{content}</p>
          <div className="bg-gray-800 rounded-lg p-3 space-y-2">
            {steps?.map((step, idx) => (
              <div key={idx} className="flex items-start gap-2 text-sm">
                <span className="text-gray-500 w-5">{idx + 1}.</span>
                <span className="text-gray-300">{step}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (type === 'complete') {
    return (
      <div className="flex gap-3">
        <div className="w-8 h-8 bg-green-900 rounded-lg flex-shrink-0 flex items-center justify-center">
          <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="bg-green-900/30 border border-green-800 rounded-lg p-4">
            <p className="text-green-300 font-medium mb-1">Task Complete</p>
            <p className="text-gray-300">{content}</p>
          </div>
        </div>
      </div>
    );
  }

  if (type === 'error') {
    return (
      <div className="flex gap-3">
        <div className="w-8 h-8 bg-red-900 rounded-lg flex-shrink-0 flex items-center justify-center">
          <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="bg-red-900/30 border border-red-800 rounded-lg p-4">
            <p className="text-red-300 font-medium mb-1">Error</p>
            <p className="text-gray-300">{content}</p>
          </div>
        </div>
      </div>
    );
  }

  if (type === 'action') {
    return (
      <div className="flex gap-3">
        <div className="w-8 h-8 bg-gray-800 rounded-lg flex-shrink-0 flex items-center justify-center">
          <svg className="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div className="flex-1">
          <code className="text-sm text-yellow-300 bg-gray-800 px-2 py-1 rounded">{content}</code>
        </div>
      </div>
    );
  }

  // Default assistant message
  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 bg-gray-800 rounded-lg flex-shrink-0 flex items-center justify-center">
        <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
      <div className="flex-1">
        <p className="text-gray-300">{content}</p>
      </div>
    </div>
  );
}

function PlanConfirmation({ plan, onConfirm, onReject }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
      <p className="text-gray-300 mb-4">Review the plan and confirm to start execution:</p>
      <div className="flex gap-3">
        <button
          onClick={onConfirm}
          className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
        >
          Confirm & Execute
        </button>
        <button
          onClick={onReject}
          className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

function ProgressIndicator({ plan, currentStep }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">Progress</span>
        <span className="text-sm text-gray-400">{currentStep} / {plan.length}</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2 mb-3">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${(currentStep / plan.length) * 100}%` }}
        />
      </div>
      {currentStep > 0 && currentStep <= plan.length && (
        <p className="text-sm text-gray-400">{plan[currentStep - 1]}</p>
      )}
    </div>
  );
}
