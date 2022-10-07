<script context='module'>
	import {parseCSV} from '@svizzle/time_region_value/src/lib/utils/domain';

	import {lookup} from '$lib/data/groups';

	export function preload ({params: {id}}) {
		return this.fetch(lookup[id].url)
		.then(r => r.text())
		.then(parseCSV(id))
		.then(data => ({data, id}))
	}
</script>

<script>
	import IdIndex from '@svizzle/time_region_value/src/routes/[id]/index.svelte';
	import * as _ from 'lamb';

	/* local deps */

	import {toolName} from '$lib/config';
	import types from '$lib/data/types';
	import {_lookup} from '$lib/stores/data';
	import {
		_availableYears,
		resetSelectedYear,
	} from '$lib/stores/selection';

	/* props */

	export let data;
	export let id;

	/* local vars */

	let availableYears;
	let title;

	/* reactive vars */

	$: id && resetSelectedYear();
	$: ({availableYears, title} = $_lookup[id] || {});
	$: $_availableYears = availableYears;
</script>

<svelte:head>
	<title>{title} - {toolName}</title>
	<meta
		content='{toolName}: temporal trends for each available NUTS2 region for the indicator: {title}'
		name='description'
	>
</svelte:head>

<IdIndex
	{data}
	{id}
	{types}
/>
