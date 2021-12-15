<script context='module'>
	import {parseCSV} from '@svizzle/time_region_value/src/node_modules/utils/domain';

	import {lookup} from 'app/data/groups';

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

	import {toolName} from 'app/config';
	import types from 'app/data/types';
	import {_lookup} from 'app/stores/data';
	import {
		_availableYears,
		resetSelectedYear,
	} from 'app/stores/selection';

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
