<script>
  import { screenshot, pageUrl } from '../stores/websocket.js';
</script>

<div class="h-full flex flex-col bg-gray-900">
  <!-- URL Bar -->
  <div class="p-3 border-b border-gray-800">
    <div class="flex items-center gap-2 bg-gray-800 rounded-lg px-3 py-2">
      <svg class="w-4 h-4 text-gray-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
      <span class="text-sm text-gray-400 truncate flex-1">
        {$pageUrl || 'No page loaded'}
      </span>
    </div>
  </div>

  <!-- Screenshot View -->
  <div class="flex-1 overflow-auto p-3">
    {#if $screenshot}
      <div class="relative rounded-lg overflow-hidden border border-gray-800">
        <img
          src="data:image/jpeg;base64,{$screenshot}"
          alt="Browser view"
          class="w-full h-auto"
        />
      </div>
    {:else}
      <div class="h-full flex items-center justify-center">
        <div class="text-center">
          <svg class="w-16 h-16 text-gray-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <p class="text-gray-500">Browser view will appear here</p>
          <p class="text-gray-600 text-sm mt-1">Start a task to see live screenshots</p>
        </div>
      </div>
    {/if}
  </div>
</div>
