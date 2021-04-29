<script>
	// import Accessibility from './accessibility.svelte';
	import {onMount} from 'svelte';
	import ScreenGauge, {screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';

	import Nav from 'app/components/Nav.svelte';
	import AccessibilityMenu, {a11yStyles, applyStyles} from 'app/components/AccessibilityMenu.svelte';
	/*
	import {
		fontFamily, 
		fontScaling, 
		fontVariationSettings,
		letterSpacing,
		wordSpacing,
		lineHeight
	} from 'app/stores/font';
	import {
		colorCorrection,
		a11ySettings
	} from 'app/stores/color';
	*/

	const dev = process.env.NODE_ENV === 'development';

	export let segment;

	let contentHeight;

	let rootStyle;
	let showA11y;

	onMount(() => {
		rootStyle = document.documentElement.style;
	});

	$: rootStyle && applyStyles(rootStyle, $a11yStyles);
</script>

<ScreenGauge devMode={dev} />

<section class={'usercontent ' + $screen?.classes} style={`--content-height: ${contentHeight}px`}>
	<header>
		<Nav {segment} screen={$screen} bind:showA11y />
	</header>
	<main bind:offsetHeight={contentHeight}>
		<slot></slot>
	</main>
	{#if showA11y}
		<div class='accessibility'>
			<AccessibilityMenu/>
		</div>
	{/if}
</section>

<style>
	.usercontent {
		display: grid;
		grid-template-areas:
			"content"
			"nav"
			"accessibility";
			grid-template-rows: 1fr min-content min-content;
			height: 100%;
			overflow: hidden;
	}
	.medium.usercontent {
		grid-template-areas:
			"nav"
			"content"
			"accessibility";
		grid-template-rows: min-content 1fr min-content;
	}

	header {
		height: var(--dim-header-height);
		width: 100%;
		padding: 0 var(--dim-padding);
		border-top: 1px solid var(--color-main-lighter);
		grid-area: nav;
	}
	header.medium {
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
