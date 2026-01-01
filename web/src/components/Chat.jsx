import { useState, useRef, useEffect } from 'react';

export function Chat({ messages, onSendMessage, onSendTask, status, isConnected }) {
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

  const getMessageStyle = (type) => {
    const baseStyle = 'px-3 py-2 rounded-lg max-w-[85%] break-words';
    switch (type) {
      case 'task':
        return `${baseStyle} bg-blue-600 text-white ml-auto`;
      case 'user':
        return `${baseStyle} bg-blue-500 text-white ml-auto`;
      case 'plan':
        return `${baseStyle} bg-purple-100 text-purple-800`;
      case 'step':
        return `${baseStyle} bg-gray-100 text-gray-700`;
      case 'action':
        return `${baseStyle} bg-yellow-50 text-yellow-800 font-mono text-sm`;
      case 'complete':
        return `${baseStyle} bg-green-100 text-green-800`;
      case 'error':
        return `${baseStyle} bg-red-100 text-red-800`;
      case 'question':
        return `${baseStyle} bg-orange-100 text-orange-800`;
      default:
        return `${baseStyle} bg-gray-100 text-gray-700`;
    }
  };

  const canSend = isConnected && (
    status === 'idle' ||
    status === 'complete' ||
    status === 'waiting_for_user'
  );

  const getPlaceholder = () => {
    if (!isConnected) return 'Connecting...';
    if (status === 'waiting_for_user') return 'Type your response...';
    if (status === 'idle' || status === 'complete') return 'Describe a task...';
    return 'Task in progress...';
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p className="text-lg mb-2">Welcome to Manus Clone</p>
            <p className="text-sm">Describe a web task and I'll complete it for you.</p>
            <p className="text-sm mt-4 text-gray-500">
              Example: "Find the weather in Brisbane"
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.type === 'task' || msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={getMessageStyle(msg.type)}>
              {msg.type === 'action' ? (
                <code>{msg.content}</code>
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={getPlaceholder()}
            disabled={!canSend}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-400"
          />
          <button
            type="submit"
            disabled={!canSend || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
