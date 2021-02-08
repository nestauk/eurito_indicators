<script>
	import {mq} from 'app/stores/mq';

	import Nav from 'app/components/Nav.svelte';

	export let segment;

	$: console.log($mq);
</script>

<header class={$mq.classNames}>
	<Nav {segment} media={$mq}/>
</header>

<main class={$mq.classNames}>
	<slot></slot>
</main>

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
	}
</style>
