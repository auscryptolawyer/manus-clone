import { useState, useEffect, useCallback, useRef } from 'react';

// Determine WebSocket URL based on environment
function getWebSocketUrl() {
  const host = window.location.host;
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

  // GitHub Codespaces: frontend is on port 5173, backend on 8000
  if (host.includes('app.github.dev')) {
    const backendHost = host.replace('-5173.', '-8000.');
    return `${protocol}//${backendHost}/ws`;
  }

  // Local development
  if (import.meta.env.DEV) {
    return 'ws://localhost:8000/ws';
  }

  // Production: same host
  return `${protocol}//${host}/ws`;
}

const WS_URL = getWebSocketUrl();

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [status, setStatus] = useState('idle');
  const [plan, setPlan] = useState([]);
  const [pendingPlan, setPendingPlan] = useState(null); // For confirmation
  const [currentStep, setCurrentStep] = useState(0);
  const [screenshot, setScreenshot] = useState(null);
  const [elements, setElements] = useState([]);
  const [pageUrl, setPageUrl] = useState('');
  const [pageTitle, setPageTitle] = useState('');
  const [messages, setMessages] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const addMessage = useCallback((type, content, extra = {}) => {
    setMessages(prev => [...prev, { type, content, timestamp: Date.now(), ...extra }]);
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
      console.log('WebSocket connected');
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');

      // Auto-reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    ws.onerror = (e) => {
      console.error('WebSocket error:', e);
      setError('Connection error');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleMessage(data);
    };

    wsRef.current = ws;
  }, []);

  const handleMessage = useCallback((data) => {
    const { type, ...payload } = data;

    switch (type) {
      case 'status':
        setStatus(payload.status);
        break;

      case 'plan_pending':
        // Plan needs confirmation
        setPendingPlan({
          task: payload.task,
          steps: payload.steps,
          message: payload.message
        });
        addMessage('plan_pending', payload.message, { steps: payload.steps });
        break;

      case 'plan_rejected':
        setPendingPlan(null);
        addMessage('system', payload.message);
        break;

      case 'plan':
        setPlan(payload.steps);
        setCurrentStep(0);
        setPendingPlan(null);
        addMessage('plan', `Executing plan with ${payload.steps.length} steps`);
        break;

      case 'step_start':
        setCurrentStep(payload.step);
        addMessage('step', `Step ${payload.step}: ${payload.description}`);
        break;

      case 'observation':
        setScreenshot(payload.screenshot);
        setElements(payload.elements || []);
        setPageUrl(payload.url);
        setPageTitle(payload.title);
        break;

      case 'action':
        addMessage('action', `${payload.tool}(${JSON.stringify(payload.params)})`);
        break;

      case 'step_complete':
        addMessage('step', `Step ${payload.step} complete`);
        break;

      case 'complete':
        setResult(payload.result);
        setStatus('complete');
        addMessage('complete', payload.result);
        break;

      case 'error':
        setError(payload.message);
        addMessage('error', payload.message);
        break;

      case 'ask_user':
        addMessage('question', payload.question);
        setStatus('waiting_for_user');
        break;

      default:
        console.log('Unknown message type:', type, payload);
    }
  }, [addMessage]);

  const startTask = useCallback((task) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      setMessages([]);
      setResult(null);
      setError(null);
      setPlan([]);
      setPendingPlan(null);
      setScreenshot(null);
      addMessage('task', task);
      wsRef.current.send(JSON.stringify({ type: 'start_task', task }));
    }
  }, [addMessage]);

  const confirmPlan = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      addMessage('system', 'Plan confirmed. Starting execution...');
      wsRef.current.send(JSON.stringify({ type: 'confirm_plan' }));
    }
  }, [addMessage]);

  const rejectPlan = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'reject_plan' }));
    }
  }, []);

  const cancelTask = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'cancel' }));
    }
  }, []);

  const sendUserMessage = useCallback((content) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      addMessage('user', content);
      wsRef.current.send(JSON.stringify({ type: 'user_message', content }));
    }
  }, [addMessage]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
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
  };
}
