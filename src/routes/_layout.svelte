<script>
	import {onMount} from 'svelte';

	import Nav from 'app/components/Nav.svelte';
	import ScreenGauge, {screenGauge} from 'app/components/ScreenGauge.svelte';
	import AccessibilityMenu from 'app/components/AccessibilityMenu.svelte';
	import {fontFamily, fontScaling, fontVariation} from 'app/stores/fontScaling';

	const dev = process.env.NODE_ENV === 'development';

	export let segment;
	let rootStyle;
	let defaultFontSize;

	onMount(() => {
		const root = document.documentElement;
		defaultFontSize = window.getComputedStyle(root).fontSize;
		rootStyle = root.style;
	})

	// set document root element font size so that `rem` units work
	$: rootStyle
		&& (rootStyle.fontFamily = $fontFamily);
	$: rootStyle
		&& (rootStyle.fontSize = `calc(${defaultFontSize} * ${$fontScaling})`);
	$: rootStyle
		&& (rootStyle.variation = $fontVariation);
</script>

<ScreenGauge bands={[60, 82, 100, 120]} devMode={dev} />

{#if $screenGauge?.size.medium}
	<header>
		<Nav {segment} screen={$screenGauge}/>
		<AccessibilityMenu/>
	</header>
{/if}

<main>
	<slot></slot>
</main>

{#if !$screenGauge?.size.medium}
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
