<script>
	import {Download,_screen} from '@svizzle/ui';

	import {toolName} from '$lib/config';

	import Methodology from '$lib/_content/Methodology.svx';
</script>

<svelte:head>
	<title>Methodology - {toolName}</title>
	<meta
		content='{toolName}: methodology used to produce these indicators'
		name='description'
	>
</svelte:head>

<main class='_layout methodology {$_screen?.classes}'>
	<div>
		<Methodology/>
	</div>
</main>

<style>
	main {
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
