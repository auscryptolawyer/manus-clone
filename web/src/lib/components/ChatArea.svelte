<script>
  import { onMount, afterUpdate } from 'svelte';
  import {
    messages,
    status,
    pendingPlan,
    plan,
    currentStep,
    isConnected,
    canSendTask,
    awaitingConfirmation,
    startTask,
    confirmPlan,
    rejectPlan,
    sendUserMessage
  } from '$lib/stores/websocket';
  import Message from './Message.svelte';
  import PlanConfirmation from './PlanConfirmation.svelte';
  import ProgressIndicator from './ProgressIndicator.svelte';

  let input = '';
  let messagesContainer;

  $: canSend = $isConnected && ($status === 'idle' || $status === 'complete' || $status === 'waiting_for_user');

  $: placeholder = (() => {
    if (!$isConnected) return 'Connecting...';
    if ($status === 'waiting_for_user') return 'Type your response...';
    if ($status === 'awaiting_confirmation') return 'Review the plan above...';
    if ($status === 'idle' || $status === 'complete') return 'What would you like me to do?';
    return 'Task in progress...';
  })();

  function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim() || !canSend) return;

    if ($status === 'idle' || $status === 'complete') {
      startTask(input.trim());
    } else if ($status === 'waiting_for_user') {
      sendUserMessage(input.trim());
    }

    input = '';
  }

  function setExample(text) {
    input = text;
  }

  afterUpdate(() => {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  });
</script>

<div class="flex-1 flex flex-col min-w-0 bg-gray-900">
  <!-- Messages -->
  <div bind:this={messagesContainer} class="flex-1 overflow-y-auto">
    <div class="max-w-3xl mx-auto py-6 px-4 space-y-6">
      {#if $messages.length === 0}
        <!-- Welcome Screen -->
        <div class="text-center py-20">
          <div class="w-16 h-16 bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
          </div>
          <h2 class="text-xl font-medium text-gray-300 mb-2">Browser Agent</h2>
          <p class="text-gray-500 max-w-md mx-auto">
            Describe a web task and I'll browse the internet to complete it for you.
          </p>
          <div class="mt-6 flex flex-wrap justify-center gap-2">
            {#each ['Search for news', 'Find weather', 'Look up information'] as example}
              <button
                on:click={() => setExample(example)}
                class="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                {example}
              </button>
            {/each}
          </div>
        </div>
      {:else}
        {#each $messages as message}
          <Message {message} />
        {/each}

        <!-- Plan Confirmation -->
        {#if $pendingPlan && $awaitingConfirmation}
          <PlanConfirmation
            plan={$pendingPlan}
            on:confirm={confirmPlan}
            on:reject={rejectPlan}
          />
        {/if}

        <!-- Progress Indicator -->
        {#if $plan.length > 0 && $status === 'executing'}
          <ProgressIndicator plan={$plan} currentStep={$currentStep} />
        {/if}
      {/if}
    </div>
  </div>

  <!-- Input Area -->
  <div class="border-t border-gray-800 bg-gray-900">
    <form on:submit={handleSubmit} class="max-w-3xl mx-auto p-4">
      <div class="relative">
        <input
          type="text"
          bind:value={input}
          {placeholder}
          disabled={!canSend}
          class="w-full px-4 py-3 pr-12 bg-gray-800 border border-gray-700 rounded-xl focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-gray-100 placeholder-gray-500"
        />
        <button
          type="submit"
          disabled={!canSend || !input.trim()}
          class="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </form>
  </div>
</div>
