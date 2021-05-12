<script>
	import {screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';

	// import {fontScaling} from 'app/stores/font';

	const sizes = {
		rem: '1rem',
		pt: '12pt',
		px: '16px',
		cm: '.423cm',
		vw: '2vw',
		vh: '2vh',
		vmin: '2vmin',
		vmax: '2vmax',
	}
	const units = Object.keys(sizes);

	let sizeMultiplier = 1.0;

	// $: fontScaling.set(sizeMultiplier);
</script>

<main>
	<div class="quarter-screen-ref"> </div>
	<section style={`--size-mult: ${sizeMultiplier}`}>
		<pre id='info'>{JSON.stringify($screen) || {}}</pre>
		<p class='info'>
			DPPR: {$screen?.display.pixelRatio.toPrecision(4)}
			W: {$screen?.display.width}
			H: {$screen?.display.height}
			CHARS: {$screen?.text.maxChars}
			x {$screen?.text.maxLines}
			size: {$screen?.classes}
		</p>
		{#each units as unit}
			<div style={`--font-size: ${sizes[unit]}`}>
				<header>
					{`font-size: calc(${sizes[unit]} * ${sizeMultiplier})`}
				</header>
				<p>
					Fmxg.
				</p>
				<p class='unused'>
					mmmmm mmmmm mmmmm mmmmm mmmmm mmmmm mmmmm
				</p>
				<p class='unused'>
					xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx xxxxx
				</p>
			</div>
			<hr />
		{/each}
	</section>
	<input type='range' bind:value={sizeMultiplier} min={0.2} max={3} step={0.01}/>
</main>

<style>
	main {
		display: grid;
		grid-template-rows: 1fr min-content;
		height: 100%;
		overflow: hidden;
	}
	section {
		height: 100%;
		overflow-y: auto;
	}

	input {
		width:100%;
	}

	header {
		color: maroon;
	}
	.info {
		background: maroon;
		color: white;
	}
	div p {
		font-size: calc(var(--font-size) * var(--size-mult))
	}
	.unused {
		display: none;
	}
	hr {
		margin: 4px;
	}
	.quarter-screen-ref {
		background: #ffff0088;
		font-size: 3vmin;
		height: 50vh;
		left: 25vw;
		position: fixed;
		top: 25vh;
		width: 50vw;
		z-index: -1;
	}
	pre {
		display: none;
	}
</style>
