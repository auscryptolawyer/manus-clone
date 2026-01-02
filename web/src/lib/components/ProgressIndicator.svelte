<script>
  import { status } from '../stores/websocket.js';

  const statusConfig = {
    idle: { label: 'Ready', color: 'gray', pulse: false },
    planning: { label: 'Planning...', color: 'blue', pulse: true },
    plan_pending: { label: 'Awaiting Confirmation', color: 'yellow', pulse: true },
    executing: { label: 'Executing...', color: 'blue', pulse: true },
    waiting_user: { label: 'Waiting for Input', color: 'orange', pulse: true },
    complete: { label: 'Complete', color: 'green', pulse: false },
    error: { label: 'Error', color: 'red', pulse: false },
  };

  $: config = statusConfig[$status] || statusConfig.idle;
</script>

<div class="flex items-center gap-2">
  <span
    class="w-2 h-2 rounded-full {config.pulse ? 'animate-pulse-dot' : ''}"
    class:bg-gray-500={config.color === 'gray'}
    class:bg-blue-500={config.color === 'blue'}
    class:bg-yellow-500={config.color === 'yellow'}
    class:bg-orange-500={config.color === 'orange'}
    class:bg-green-500={config.color === 'green'}
    class:bg-red-500={config.color === 'red'}
  ></span>
  <span class="text-sm text-gray-400">{config.label}</span>
</div>
