<script>
  import { pendingPlan, confirmPlan, rejectPlan } from '../stores/websocket.js';
</script>

{#if $pendingPlan}
  <div class="flex gap-3">
    <div class="w-8 h-8 bg-blue-900 rounded-lg shrink-0 flex items-center justify-center">
      <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <p class="text-blue-400 font-medium mb-3">Proposed Plan</p>

        {#if $pendingPlan.steps && $pendingPlan.steps.length > 0}
          <div class="space-y-2 mb-4">
            {#each $pendingPlan.steps as step, idx}
              <div class="flex items-start gap-3">
                <span class="w-6 h-6 bg-gray-700 rounded-full flex items-center justify-center text-xs text-gray-400 shrink-0">
                  {idx + 1}
                </span>
                <span class="text-gray-300 text-sm">{step.description || step}</span>
              </div>
            {/each}
          </div>
        {/if}

        <div class="flex gap-2 pt-2 border-t border-gray-700">
          <button
            on:click={confirmPlan}
            class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Confirm & Start
          </button>
          <button
            on:click={rejectPlan}
            class="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg text-sm font-medium transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
