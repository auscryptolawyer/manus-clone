<script>
  import '../app.css';
  import { onMount } from 'svelte';
  import { connect } from '$lib/stores/websocket.js';

  onMount(() => {
    connect();
  });
</script>

<slot />
