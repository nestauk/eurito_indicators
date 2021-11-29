<script>
	import ScreenSensor, {_screen}
		from '@svizzle/ui/src/sensors/screen/ScreenSensor.svelte';
	import LoadingView from '@svizzle/ui/src/LoadingView.svelte';
	import A11yMenu
		from '@svizzle/ui/src/a11y/menu/A11yMenu.svelte';
	import A11yMenuDriver
		from '@svizzle/ui/src/a11y/menu/A11yMenuDriver.svelte';
	import {_isA11yDirty} from '@svizzle/ui/src/a11y/menu/settings';
	import MultiBanner from '@svizzle/ui/src/MultiBanner.svelte';
	import NoScript from '@svizzle/ui/src/NoScript.svelte';
	import {onMount, beforeUpdate, tick} from 'svelte';

	import Nav from 'app/components/Nav.svelte';
	import theme from 'app/theme';

	import Privacy from './_content/info/Privacy.svx';

	const bannerComponents = [
		Privacy
	];

	export let segment;

	let contentHeight;
	let headerHeight;
	let a11yHeight;
	let showA11yMenu;
	let isLayoutUndefined = true;
	let scriptingActive = false;

	onMount(() => {
		scriptingActive = true;
		window.nesta_isLayoutUndefined = () => isLayoutUndefined;
	});

	beforeUpdate(async () => {
		if (isLayoutUndefined) {
			await tick();
		}
	});

	$: menuHeight = headerHeight + (showA11yMenu ? a11yHeight : 0);
	$: $_screen?.classes && (isLayoutUndefined = false);
</script>

<A11yMenuDriver
	defaults={{
		typeface: {
			defaultValue: 'Avenir Next Variable',
			values: [
				'Avenir Next Variable',
				'Archivo',
				'Noboto Flex',
				'Courier New',
				'Open Dyslexia'
			],
		}
	}}
/>

<ScreenSensor />

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
			<A11yMenu {_screen} />
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
	.medium .accessibility {
		bottom: 150px;
		left: 50%;
		margin-left: -240px;
		position: fixed;
		width: 480px;
	}
	.hidden {
		display: none;
	}
</style>
