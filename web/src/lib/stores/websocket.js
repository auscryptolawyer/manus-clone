import { writable, derived } from 'svelte/store';

// WebSocket URL determination
function getWebSocketUrl() {
  if (typeof window === 'undefined') return '';

  const host = window.location.host;
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

  // GitHub Codespaces
  if (host.includes('app.github.dev')) {
    const backendHost = host.replace('-5173.', '-8000.');
    return `${protocol}//${backendHost}/ws`;
  }

  // Local development
  if (host.includes('localhost') || host.includes('127.0.0.1')) {
    return 'ws://localhost:8000/ws';
  }

  // Production
  return `${protocol}//${host}/ws`;
}

// Core state stores
export const isConnected = writable(false);
export const status = writable('idle');
export const messages = writable([]);
export const pendingPlan = writable(null);
export const plan = writable([]);
export const currentStep = writable(0);
export const screenshot = writable(null);
export const elements = writable([]);
export const pageUrl = writable('');
export const pageTitle = writable('');
export const error = writable(null);

// Derived stores
export const isExecuting = derived(status, $status =>
  ['executing', 'starting', 'browser_ready'].includes($status)
);

export const canSendTask = derived([isConnected, status], ([$isConnected, $status]) =>
  $isConnected && ['idle', 'complete'].includes($status)
);

export const awaitingConfirmation = derived(status, $status =>
  $status === 'awaiting_confirmation'
);

// WebSocket connection
let ws = null;
let reconnectTimeout = null;

export function connect() {
  if (typeof window === 'undefined') return;
  if (ws?.readyState === WebSocket.OPEN) return;

  const url = getWebSocketUrl();
  ws = new WebSocket(url);

  ws.onopen = () => {
    isConnected.set(true);
    error.set(null);
    console.log('WebSocket connected');
  };

  ws.onclose = () => {
    isConnected.set(false);
    console.log('WebSocket disconnected');

    // Auto-reconnect
    reconnectTimeout = setTimeout(() => {
      connect();
    }, 3000);
  };

  ws.onerror = (e) => {
    console.error('WebSocket error:', e);
    error.set('Connection error');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleMessage(data);
  };
}

export function disconnect() {
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }
  if (ws) {
    ws.close();
    ws = null;
  }
}

function handleMessage(data) {
  const { type, ...payload } = data;

  switch (type) {
    case 'status':
      status.set(payload.status);
      break;

    case 'plan_pending':
      pendingPlan.set({
        task: payload.task,
        steps: payload.steps,
        message: payload.message
      });
      addMessage('plan_pending', payload.message, { steps: payload.steps });
      break;

    case 'plan_rejected':
      pendingPlan.set(null);
      addMessage('system', payload.message);
      break;

    case 'plan':
      plan.set(payload.steps);
      currentStep.set(0);
      pendingPlan.set(null);
      addMessage('plan', `Executing plan with ${payload.steps.length} steps`);
      break;

    case 'observation':
      screenshot.set(payload.screenshot);
      elements.set(payload.elements || []);
      pageUrl.set(payload.url);
      pageTitle.set(payload.title);
      break;

    case 'action':
      addMessage('action', `${payload.tool}(${JSON.stringify(payload.params)})`);
      break;

    case 'complete':
      status.set('complete');
      addMessage('complete', payload.result);
      break;

    case 'error':
      error.set(payload.message);
      addMessage('error', payload.message);
      break;

    case 'ask_user':
      addMessage('question', payload.question);
      status.set('waiting_for_user');
      break;

    default:
      console.log('Unknown message type:', type, payload);
  }
}

function addMessage(type, content, extra = {}) {
  messages.update(msgs => [...msgs, {
    type,
    content,
    timestamp: Date.now(),
    ...extra
  }]);
}

export function startTask(task) {
  if (ws?.readyState !== WebSocket.OPEN) return;

  // Reset state
  messages.set([]);
  error.set(null);
  plan.set([]);
  pendingPlan.set(null);
  screenshot.set(null);

  addMessage('task', task);
  ws.send(JSON.stringify({ type: 'start_task', task }));
}

export function confirmPlan() {
  if (ws?.readyState !== WebSocket.OPEN) return;
  addMessage('system', 'Plan confirmed. Starting execution...');
  ws.send(JSON.stringify({ type: 'confirm_plan' }));
}

export function rejectPlan() {
  if (ws?.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({ type: 'reject_plan' }));
}

export function cancelTask() {
  if (ws?.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({ type: 'cancel' }));
}

export function sendUserMessage(content) {
  if (ws?.readyState !== WebSocket.OPEN) return;
  addMessage('user', content);
  ws.send(JSON.stringify({ type: 'user_message', content }));
}
