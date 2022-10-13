<script>
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';
	import ResponsiveFlex from '@svizzle/ui/src/ResponsiveFlex.svelte';

	import {toolName} from '$lib/config';
	import {_currThemeVars} from '$lib/stores/theme';

	import Content from '$lib/_content/Index.svx';
</script>

<svelte:head>
	<title>Home - {toolName}</title>
	<meta
		content='{toolName}: homepage'
		name='description'
	>
</svelte:head>

<main class='home'>
	<div>
		<Content />

		<ResponsiveFlex>
			<LinkButton
				href='/methodology'
				text='Our methodology'
				theme={{backgroundColor: $_currThemeVars['--colorLink']}}
			/>
			<LinkButton
				href='/indicators'
				text='Explore the indicators'
				theme={{backgroundColor: $_currThemeVars['--colorLink']}}
			/>
		</ResponsiveFlex>
	</div>
</main>

<style>
	.home {
		background-color: var(--colorPageBackground);
		display: flex;
		font-weight: 200;
		height: 100%;
		justify-content: space-around;
		width: 100%;
	}

	div {
		background-color: var(--colorBackground);
		max-width: 900px;
		overflow-y: auto;
		padding: 2rem;
	}
</style>
