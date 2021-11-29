<script>
	import ScreenSensor, {_screen}
		from '@svizzle/ui/src/sensors/screen/ScreenSensor.svelte';
	import LoadingView from '@svizzle/ui/src/LoadingView.svelte';
	import MultiBanner from '@svizzle/ui/src/MultiBanner.svelte';
	import NoScript from '@svizzle/ui/src/NoScript.svelte';
	import {onMount, beforeUpdate, tick} from 'svelte';

	import AccessibilityMenu from 'app/components/AccessibilityMenu.svelte';
	import ColorCorrection from 'app/components/ColorCorrection.svelte';
	import Nav from 'app/components/Nav.svelte';
	import Storage from 'app/components/Storage.svelte';
	import {
		_a11ySettings,
		_a11yColorStyles,
		_a11yTextStyles,
		_isA11yDirty,
		applyStyles,
		defaultA11ySettings
	} from 'app/stores/a11ySettings';
	import theme from 'app/theme';

	import Privacy from './_content/info/Privacy.svx';

	const bannerComponents = [
		Privacy
	];

	export let segment;

	let contentHeight;
	let headerHeight;
	let a11yHeight;
	let rootStyle;
	let showA11yMenu;
	let isLayoutUndefined = true;
	let scriptingActive = false;

	onMount(() => {
		const root = document.documentElement;
		rootStyle = root.style;

		scriptingActive = true;
		window.nesta_isLayoutUndefined = () => isLayoutUndefined;
	});
	beforeUpdate(async () => {
		if (isLayoutUndefined) {
			await tick();
		}
	});

	$: rootStyle && applyStyles(rootStyle, $_a11yTextStyles);
	$: rootStyle && applyStyles(rootStyle, $_a11yColorStyles);
	$: menuHeight = headerHeight + (showA11yMenu ? a11yHeight : 0);
	$: $_screen?.classes && (isLayoutUndefined = false);
</script>

<Storage
	_store={_a11ySettings}
	defaultValue={defaultA11ySettings}
	isReactive={true}
	key='a11ySettings'
	type='localStorage'
/>

<ScreenSensor />
<ColorCorrection />

<NoScript />

{#if scriptingActive}
	<MultiBanner
		{_screen}
		components={bannerComponents}
	/>
{/if}

{#if isLayoutUndefined}
	<LoadingView stroke={theme.colorMain} />
{/if}

<div
	class={$_screen?.classes}
	class:hidden={isLayoutUndefined}
	style='--menu-height: {menuHeight}px;'
	role='none'
>
	<header
		aria-label='Website header'
		bind:offsetHeight={headerHeight}
		role='banner'
	>
		<Nav
			{_screen}
			{contentHeight}
			{segment}
			bind:showA11yMenu
			isA11yDirty={$_isA11yDirty}
		/>
	</header>
	<main
		aria-label='Website content'
		bind:offsetHeight={contentHeight}
		role='main'
	>
		<slot></slot>
	</main>
	{#if showA11yMenu}
		<section
			bind:offsetHeight={a11yHeight}
			class='accessibility'
			role='region'
		>
			<AccessibilityMenu {_screen} />
		</section>
	{/if}
</div>

<style>
	div {
		display: grid;
		grid-template-areas:
			'content'
			'nav'
			'accessibility';
		grid-template-rows: calc(100% - var(--menu-height)) min-content min-content;
		height: 100%;
		overflow: hidden;
	}
	div.medium {
		grid-template-areas:
			'nav'
			'content'
			'accessibility';
		grid-template-rows: min-content 1fr min-content;
	}
	header {
		border-top: 1px solid var(--color-main-lighter);
		grid-area: nav;
		height: var(--dim-header-height);
		padding: 0 var(--dim-padding);
		width: 100%;
	}
	.medium header {
		border-bottom: 1px solid var(--color-main-lighter);
		border-top: none;
	}
	main {
		grid-area: content;
		height: 100%;
		overflow: hidden;
		position: relative;
		width: 100%;
	}
	.accessibility {
		grid-area: accessibility;
	}
	.hidden {
		display: none;
	}
</style>
