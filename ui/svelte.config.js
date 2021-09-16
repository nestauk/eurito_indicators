import { mdsvex } from "mdsvex";
/** @type {import('@sveltejs/kit').Config} */
const config = {
	extensions: ['.svelte', '.svx'],
	kit: {
	},
	preprocess: [mdsvex()]
};

export default config;
