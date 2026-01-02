<script>
  export let message;

  $: isUser = message.type === 'task' || message.type === 'user';
</script>

{#if isUser}
  <div class="flex justify-end">
    <div class="max-w-[80%] px-4 py-2 bg-blue-600 rounded-2xl rounded-br-md">
      <p class="text-white">{message.content}</p>
    </div>
  </div>

{:else if message.type === 'plan_pending'}
  <div class="flex gap-3">
    <div class="w-8 h-8 bg-gray-800 rounded-lg shrink-0 flex items-center justify-center">
      <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <p class="text-gray-300 mb-3">{message.content}</p>
      {#if message.steps}
        <div class="bg-gray-800 rounded-lg p-3 space-y-2">
          {#each message.steps as step, idx}
            <div class="flex items-start gap-2 text-sm">
              <span class="text-gray-500 w-5 shrink-0">{idx + 1}.</span>
              <span class="text-gray-300">{step}</span>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>

{:else if message.type === 'complete'}
  <div class="flex gap-3">
    <div class="w-8 h-8 bg-green-900 rounded-lg shrink-0 flex items-center justify-center">
      <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="bg-green-900/30 border border-green-800 rounded-lg p-4">
        <p class="text-green-300 font-medium mb-1">Task Complete</p>
        <p class="text-gray-300 whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  </div>

{:else if message.type === 'error'}
  <div class="flex gap-3">
    <div class="w-8 h-8 bg-red-900 rounded-lg shrink-0 flex items-center justify-center">
      <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="bg-red-900/30 border border-red-800 rounded-lg p-4">
        <p class="text-red-300 font-medium mb-1">Error</p>
        <p class="text-gray-300">{message.content}</p>
      </div>
    </div>
  </div>

{:else if message.type === 'action'}
  <div class="flex gap-3">
    <div class="w-8 h-8 bg-gray-800 rounded-lg shrink-0 flex items-center justify-center">
      <svg class="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <code class="text-sm text-yellow-300 bg-gray-800 px-2 py-1 rounded break-all">{message.content}</code>
    </div>
  </div>

{:else if message.type === 'question'}
  <div class="flex gap-3">
    <div class="w-8 h-8 bg-orange-900 rounded-lg shrink-0 flex items-center justify-center">
      <svg class="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="bg-orange-900/30 border border-orange-800 rounded-lg p-4">
        <p class="text-orange-300 font-medium mb-1">Input Required</p>
        <p class="text-gray-300">{message.content}</p>
      </div>
    </div>
  </div>

{:else}
  <div class="flex gap-3">
    <div class="w-8 h-8 bg-gray-800 rounded-lg shrink-0 flex items-center justify-center">
      <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <p class="text-gray-300">{message.content}</p>
    </div>
  </div>
{/if}
