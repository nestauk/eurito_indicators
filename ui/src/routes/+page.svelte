<script>
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';
	import ResponsiveFlex from '@svizzle/ui/src/ResponsiveFlex.svelte';

	import {toolName} from '$lib/config';
	import theme from '$lib/theme';

	import Home from '$lib/_content/Index.svx';
</script>

<svelte:head>
	<title>Home - {toolName}</title>
	<meta
		content='{toolName}: homepage'
		name='description'
	>
</svelte:head>

<main>
	<div>
		<Home />

		<ResponsiveFlex>
			<LinkButton
				href='/methodology'
				text='Our methodology'
				theme={{backgroundColor: theme.colorLink}}
			/>
			<LinkButton
				href='/indicators'
				text='Explore the indicators'
				theme={{backgroundColor: theme.colorLink}}
			/>
		</ResponsiveFlex>
	</div>
</main>

<style>
	main {
		background-color: var(--color-background);
		display: flex;
		font-weight: 200;
		height: 100%;
		justify-content: space-around;
		width: 100%;
	}

	div {
		background-color: white;
		max-width: 900px;
		overflow-y: auto;
		padding: 2rem;
	}
</style>
