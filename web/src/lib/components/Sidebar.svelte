<script>
  import { isConnected, status } from '$lib/stores/websocket';

  export let isOpen = true;

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
    cancelled: 'Cancelled'
  };

  function getStatusColor(s) {
    if (['idle', 'complete'].includes(s)) return 'bg-green-500';
    if (['executing', 'starting', 'browser_ready'].includes(s)) return 'bg-blue-500';
    if (['planning', 'awaiting_confirmation', 'waiting_for_user'].includes(s)) return 'bg-yellow-500';
    return 'bg-gray-500';
  }
</script>

{#if isOpen}
  <aside class="w-64 bg-gray-950 border-r border-gray-800 flex flex-col shrink-0">
    <!-- Logo -->
    <div class="h-12 flex items-center px-4 border-b border-gray-800">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
          </svg>
        </div>
        <span class="font-semibold text-white">Manus</span>
      </div>
    </div>

    <!-- Status Section -->
    <div class="flex-1 overflow-y-auto px-3 py-4">
      <div class="text-xs text-gray-500 uppercase tracking-wider mb-3 px-2">Status</div>

      <!-- Connection Status -->
      <div class="flex items-center justify-between px-2 py-2 rounded-lg hover:bg-gray-800/50">
        <span class="text-sm text-gray-400">Connection</span>
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full {$isConnected ? 'bg-green-500' : 'bg-red-500'}"></div>
          <span class="text-sm">{$isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      <!-- Agent Status -->
      <div class="flex items-center justify-between px-2 py-2 rounded-lg hover:bg-gray-800/50">
        <span class="text-sm text-gray-400">Agent</span>
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full {getStatusColor($status)}"></div>
          <span class="text-sm">{statusMap[$status] || $status}</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="p-3 border-t border-gray-800">
      <div class="text-xs text-gray-500 text-center">
        Browser Automation Agent
      </div>
    </div>
  </aside>
{/if}
