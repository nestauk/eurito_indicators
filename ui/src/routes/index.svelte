<script>
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';
	import Home from './_content/Index.svx';
	import ResponsiveFlex from 'app/components/ResponsiveFlex.svelte';
	
	import {toolName} from 'app/config';
	import theme from 'app/theme';
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
				text='Read more about the methodology'
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
