<script>
	import Nav from 'app/components/Nav.svelte';
	import ScreenGauge, {screenGauge} from 'app/components/ScreenGauge.svelte';

	export let segment;
</script>

<ScreenGauge fontSize='1rem'/>
{#if $screenGauge?.display.large}
	<header>
		<Nav {segment} screen={$screenGauge}/>
	</header>
{/if}

<main>
	<slot></slot>
</main>

{#if $screenGauge?.display.small && $screenGauge?.orientation.portrait}
	<header class='small'>
		<Nav {segment} screen={$screenGauge}/>
	</header>
{/if}

<style>
	header {
		height: var(--dim-header-height);
		width: 100%;
		padding: 0 var(--dim-padding);
		border-bottom: 1px solid var(--color-main-lighter);
	}

	header.small {
		border-top: 1px solid var(--color-main-lighter);
		border-bottom: none;
	}

	main {
		height: var(--dim-main-height);
		width: 100%;
		overflow: hidden;
	}
</style>
