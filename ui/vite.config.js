import ViteYaml from '@modyfi/vite-plugin-yaml';
import {sveltekit} from '@sveltejs/kit/vite';


const config = {
	plugins: [
		ViteYaml(),
		sveltekit(),
	],
	server: {
		fs: {
			// Allow serving files from one level up to the project root
			allow: ['..']
		}
	}
};

export default config;
