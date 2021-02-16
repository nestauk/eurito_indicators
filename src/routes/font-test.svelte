<script>
	import TextRuler from 'app/components/TextRuler.svelte';

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
	let dim;

	function updateDim (e) {
		dim = e.detail;
	}
</script>
<TextRuler on:resize={updateDim} fontSize={sizeMultiplier+'rem'}/>
<main>
	<div class="square"> </div>
	<section style={`--size-mult: ${sizeMultiplier}`}>
		<p class='info'>
			DPPR: {dim?.pixelRatio.toPrecision(4)} W: {dim?.pixelWidth} H: {dim?.pixelHeight} CHARS: {dim?.charsPerLine.toFixed(0)}x{dim?.linesPerPage.toFixed(0)}
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
	.square {
		position: fixed;
		width: 50vw;
		height: 50vh;
		font-size: 3vmin;
		background: #ffff0088;
		z-index: -1;
		top: 25vh;
		left: 25vw;
	}

</style>