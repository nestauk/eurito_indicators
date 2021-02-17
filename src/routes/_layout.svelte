<script>
	import {onMount} from 'svelte';
	import {fontScaling} from 'app/stores/fontScaling';

	import Nav from 'app/components/Nav.svelte';
	import ScreenGauge, {screenGauge} from 'app/components/ScreenGauge.svelte';

	export let segment;
	let rootStyle;

	onMount(() => {
		rootStyle = document.documentElement.style;
	})

	// set document root element font size so that `rem` units work
	$: rootStyle && ( rootStyle.fontSize = `${$fontScaling * 16}px`);
</script>

{#if !$screenGauge?.size.small}
	<header>
		<Nav {segment} screen={$screenGauge}/>
	</header>
{/if}

<main>
	<ScreenGauge bands={[60, 82, 100, 120]} />
	<slot></slot>
</main>

{#if $screenGauge?.size.small}
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
