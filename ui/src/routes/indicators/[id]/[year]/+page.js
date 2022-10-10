import {parseCSV} from '@svizzle/time_region_value/src/lib/utils/domain';

import {lookup} from '$lib/data/groups';

export function load ({fetch, params: {id, year}}) {
	return fetch(lookup[id].url)
		.then(r => r.text())
		.then(parseCSV(id))
		.then(data => ({data, id, year}))
}
