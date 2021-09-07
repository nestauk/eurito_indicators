<script>
	import Home from 'app/components/content/Home.svx';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';
	import theme from 'app/theme';

	import {toolName} from 'app/config';
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

		<div class='cta'>
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
		</div>
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
	.cta {
		align-content: center;
		display: flex;
		flex-direction: column;
		justify-content: space-around;
		margin: 2rem 0 3rem 0;
		row-gap: 1em;
	}

	:global(.medium) .cta {
		flex-direction: row;
		row-gap: 0;
	}
</style>
