<script>
  import Sidebar from '$lib/components/Sidebar.svelte';
  import ChatArea from '$lib/components/ChatArea.svelte';
  import BrowserPanel from '$lib/components/BrowserPanel.svelte';

  let showBrowser = false;
</script>

<svelte:head>
  <title>Manus Clone - Browser Automation Agent</title>
</svelte:head>

<div class="h-screen flex bg-gray-950 text-white">
  <!-- Sidebar -->
  <Sidebar />

  <!-- Main Content -->
  <div class="flex-1 flex">
    <!-- Chat Panel -->
    <div class="flex-1 {showBrowser ? 'w-1/2' : 'w-full'}">
      <ChatArea />
    </div>

    <!-- Browser Panel (toggleable) -->
    {#if showBrowser}
      <div class="w-1/2 border-l border-gray-800">
        <BrowserPanel />
      </div>
    {/if}
  </div>

  <!-- Toggle Browser Button -->
  <button
    on:click={() => showBrowser = !showBrowser}
    class="fixed bottom-4 right-4 p-3 bg-gray-800 hover:bg-gray-700 rounded-full shadow-lg transition-colors z-10"
    title={showBrowser ? 'Hide browser' : 'Show browser'}
  >
    <svg class="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      {#if showBrowser}
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      {:else}
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      {/if}
    </svg>
  </button>
</div>
