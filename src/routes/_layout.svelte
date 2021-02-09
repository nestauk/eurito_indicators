<script>
	import {mq} from 'app/stores/mq';

	import Nav from 'app/components/Nav.svelte';

	export let segment;
</script>

{#if !$mq.mobile}
	<header>
		<Nav {segment} media={$mq}/>
	</header>
{/if}

<main>
	<slot></slot>
</main>

{#if $mq.mobile}
	<header class='mobile'>
		<Nav {segment} media={$mq}/>
	</header>
{/if}

<style>
	header {
		height: var(--dim-header-height);
		width: 100%;
		padding: 0 var(--dim-padding);
		border-bottom: 1px solid var(--color-main-lighter);
	}

	main {
		height: var(--dim-main-height);
		width: 100%;
		overflow: hidden;
	}

	header.mobile {
		border-top: 1px solid var(--color-main-lighter);
		border-bottom: none;
	}
</style>
