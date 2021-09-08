<script>
	import {_screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import {toolName} from 'app/config';

	import A11ymenu from './A11ymenu.svx';
</script>

<svelte:head>
	<title>Accessibility menu guide - {toolName}</title>
	<meta
		content='{toolName}: Accessibility menu guide'
		name='description'
	>
</svelte:head>

<A11ymenu/>
