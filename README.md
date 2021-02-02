# EURITO indicators UI

EURITO indicators UI.

## Setup

Please take the following steps within the same dir:
- svizzle:
	- clone [the Svizzle repo](https://github.com/nestauk/svizzle)
	- `cd svizzle`
	- `git checkout dev` (or another branch depending on what we're currently working on)
	- `npm install`
	- `npm run lernacleanboot --legacy-peer-deps`
	- press yes when it asks
	- linking:
		- in `svizzle/packages/components/time_region_value`, run `npm link`
		- in `svizzle/packages/components/ui`, run `npm link`
		- with `npm list -g`, you should see 2 lines like:
			- `@svizzle/time_region_value@0.0.1 -> /path/to/svizzle/packages/components/time_region_value`
			- `@svizzle/ui@0.1.0 -> /path/to/svizzle/packages/components/ui`
		- in general, you need to `npm link` all packages that end up being modified by `173_time_region_value`
- app:
	- clone [this repo](https://github.com/nestauk/eurito_indicators_ui)
	- `cd eurito_indicators_ui`
	- `git checkout dev` (or another branch depending on what we're currently working on)
	- linking:
		- `npm link @svizzle/time_region_value`
		- `npm link @svizzle/ui`
		- in general, you need to `npm link` all `svizzle` packages that end up being modified by `173_time_region_value`
	- `npm install`
	- `npm run makedata`
	- `npm run dev`
