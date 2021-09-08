<script>
	import CTA from 'app/components/CTA.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';

	import Home from './Index.svx';
	
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

		<CTA>
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
		</CTA>
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
