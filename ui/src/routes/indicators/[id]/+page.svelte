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

	/* local vars */

	let availableYears;
	let title;

	/* reactive vars */

	$: json = data.data;
	$: id = data.id;
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
	data={json}
	{id}
	{types}
/>
