<script context="module">
	import Link from '@svizzle/ui/src/Link.svelte';
	import {availableDownloadIds, basename} from 'app/utils/assets';

	const maxIndex = availableDownloadIds.length - 1;

	export async function preload({params: {id}}) {
		if (availableDownloadIds.includes(id)) {
			return this.redirect(302, `/data/${basename}_${id}.csv`);
		}
	}
</script>

<section class='layout'>
	<h2>Sorry, the file you're looking for is not available.</h2>
	<p>Please try one of
		{#each availableDownloadIds as availableId, index}
			<Link
				download={availableId}
				href='/download/{availableId}'
			>
				{availableId}
			</Link>
			{#if index < maxIndex},{/if}
		{/each}
		or find the collection of all indicators 
		<Link
			download={basename}
			href='/download'
		>
			here
		</Link>.
	</p>
</section>

<style>
	.layout {
		padding: 1rem;
	}
</style>
