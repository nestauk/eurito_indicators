<script>
	import watchMedia from "svelte-media";
	import Nav from 'app/components/Nav.svelte';

	export let segment;

	const mediaqueries = {
		mobile: "(max-width: 639px)",
		tablet: "(min-width: 640px) and (max-width: 1023px)",
		desktop: "(min-width: 1024px)",
		landscape: "(orientation: landscape)"
	};
	const media = watchMedia(mediaqueries);

	$: console.log($media);
</script>

<header class={$media.classNames}>
	<Nav {segment} media={$media}/>
</header>

<main class={$media.classNames}>
	<slot></slot>
</main>

<style>
	header {
		height: var(--dim-header-height);
		width: 100%;
		padding: 0 var(--dim-padding);
		border-bottom: 1px solid var(--color-main-lighter);
	}

	main {
		height: var(--dim-main-height);
		width: 100%;
	}
</style>
