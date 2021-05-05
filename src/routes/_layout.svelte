<script>
	import {onMount} from 'svelte';
	import ScreenGauge, {screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';

	import ColorCorrection from 'app/components/ColorCorrection.svelte';
	import Nav from 'app/components/Nav.svelte';
	import AccessibilityMenu from 'app/components/AccessibilityMenu.svelte';
	import DevAccessibilityMenu from 'app/components/DevAccessibilityMenu.svelte';
	import {
		fontFamily, 
		fontScaling, 
		fontVariationSettings,
		letterSpacing,
		wordSpacing,
		lineHeight
	} from 'app/stores/font';
	import {
		colorCorrectionOptions,
		colorCorrection,
		cvdSimulation
	} from 'app/stores/color';

	const dev = process.env.NODE_ENV === 'development';

	export let segment;

	let contentHeight;
	let rootStyle;
	let defaultFontSize;
	let showA11y;

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
		&& (rootStyle.letterSpacing = $letterSpacing);
	$: rootStyle
		&& (rootStyle.wordSpacing = $wordSpacing);
	$: rootStyle
		&& (rootStyle.lineHeight = $lineHeight);
	$: rootStyle
		&& (rootStyle.fontVariationSettings = $fontVariationSettings);
	$: rootStyle
		&& rootStyle.setProperty(...$colorCorrection);
	$: rootStyle
		&& rootStyle.setProperty(...$cvdSimulation);
</script>

<ScreenGauge devMode={dev} />
<ColorCorrection options={$colorCorrectionOptions} />

<section class={$screen?.classes}>
	<header>
		<Nav {segment} screen={$screen} {contentHeight} bind:showA11y />
	</header>
	<main bind:offsetHeight={contentHeight}>
		<slot></slot>
		<DevAccessibilityMenu/>
	</main>
	{#if showA11y}
		<div class='accessibility'>
			<AccessibilityMenu screen={$screen} />
		</div>
	{/if}
</section>

<style>
	section {
		display: grid;
		height: 100%;
		overflow: hidden;
		grid-template-areas:
			'content'
			'nav'
			'accessibility';
		grid-template-rows: 1fr min-content min-content;
	}
	section.medium {
		grid-template-areas:
			'nav'
			'content'
			'accessibility';
		grid-template-rows: min-content 1fr min-content;
	}
	header {
		height: var(--dim-header-height);
		width: 100%;
		padding: 0 var(--dim-padding);
		border-top: 1px solid var(--color-main-lighter);
		grid-area: nav;
	}
	.medium header {
		border-top: none;
		border-bottom: 1px solid var(--color-main-lighter);
	}
	main {
		height: 100%;
		width: 100%;
		overflow: hidden;
		position: relative;
		grid-area: content;
	}
	.accessibility {
		grid-area: accessibility;
	}
</style>
