import regionSpecs from '@svizzle/atlas/src/specs';
import {getFamilies} from "@svizzle/ui/src/drivers/fonts/utils";

export const toolName = 'EURITO';
export const toolLongName = 'EURITO spatial data tool';
export const contactEmail = 'dataanalytics@nesta.org.uk';

/* navigation */

export const hrefBase = '/indicators';
export const userTestingUrl = 'https://docs.google.com/forms/d/e/1FAIpQLSfmQKIwocPmaI_Sdte0QLMhRODCYPnuYNJreehE61xDig3nAA/viewform?embedded=true';

/* flags */

export const flags = {
	showPOIs: false
}

/* regional selection */

const regionType = 'NUTS';
const nutsLevels = regionSpecs[regionType].levels;
const [rootLevel,] = nutsLevels;

export const regionSettings = {
	canSelectLevels: true,
	filterableLevel: 0,
	ignoredRegions: [

		// IDEA: use atlas sub-type instead (`overseas`, etc)
		// IDEA: define these in atlas' dist/

		/* ES */

		// Canarias
		68,		// ES7
		248,	// ES70
		1114,	// ES701
		1115,	// ES702
		1936,	// ES703
		1937,	// ES704
		1938,	// ES705
		1939,	// ES706
		1940,	// ES707
		1941,	// ES708
		1942,	// ES709

		/* FR */

		// French Guyene
		79,		// FR9
		278,	// FR93
		1234, // FR930, FRY30

		// Guadeloupe

		2111,	// FRA10, FRY10
		2084,	// FRY1
		1232,	// FR910
		276,	// FR91

		// Guyane

		1234,	// FRA30, FRY30
		278,	// FRY3

		// La Réunion

		1235,	// FRA40, FRY40
		279,	// FRY4

		// Martinique

		1233,	// FRA20, FRY20
		277,	// FRY2

		// Mayotte

		2112,	// FRA50, FRY50
		2085,	// FRY5

		// RÉGIONS ULTRAPÉRIPHÉRIQUES FRANÇAISES

		2083,	// FRY

		/* PT */

		112,	// PT2
		372,	// PT20
		1592,	// PT200

		113,	// PT3
		373,	// PT30
		1593,	// PT300

		/* IS */

		// 16,	// IS
		// 89,	// IS0
		// 305,	// IS00
		// 1336,	// IS000
		// 1945,	// IS001
		// 1946,	// IS002
	],
	key: 'NUTS_ID',
	initialLevel: rootLevel,
	levels: nutsLevels,
	objectId: 'NUTS',
	resolution: '10M',
	rootIds: undefined, // all roots
	type: regionType,
}

/* testing */

export const urlBases = {
    development: 'http://localhost:3000',
    preview: 'https://eurito-indicators-ui-dev.netlify.app',
    // production: '',
};

export const lighthouseUrls = {
	Home: '/',
	Methodology: '/methodology',
	Guide: '/guide',
	Indicators: '/indicators',
	Trends: '/indicators/area_university_site',
	Geo: '/indicators/area_university_site/2015',
};

/*
There's a bug in Lighthouse 7.4.0 which causes the audit on the following
pages to fail when running in mobile display emulation. Commenting them
for now as tests are being run in desktop mode only pending the fix.
Ref.: https://github.com/GoogleChrome/lighthouse/issues/12039
*/
export const failingA11yAudit = [
//    'Trends',
//    'Geo'
];

export const isDev = process.env.NODE_ENV === 'development';

export const fontsInfo = [
	{
		family: 'Avenir Next Variable',
		faces: [
			{
				src: 'url(/font/AvenirNext/Variable.ttf) format("truetype")'
			}
		]
	},
	{
		family: 'Archivo',
		faces: [
			{
				src: 'url(/font/Archivo/VariableFont_wdth,wght.ttf) format("truetype")',
				descriptors: {
					style: 'normal'
				}
			},
			{
				src: 'url(/font/Archivo/Italic-VariableFont_wdth,wght.ttf) format("truetype")',
				descriptors: {
					style: 'italic'
				}
			},
		]
	},
	{
		family: 'Noboto Flex',
		faces: [
			{
				src: 'url(/font/NobotoFlex/Variable.woff2)',
				descriptors: {
					weight: 140
				}
			}
		]
	},
	{
		family: 'Courier New'
	},
	{
		family: 'Open Dyslexia',
		faces: [
			{
				src: 'url(/font/OpenDyslexic/Regular.otf) format("opentype")',
				descriptors: {
					weight: 400,
					style: 'normal'
				}
			},
			{
				src: 'url(/font/OpenDyslexic/Italic.otf) format("opentype")',
				descriptors: {
					weight: 400,
					style: 'italic'
				}
			},
			{
				src: 'url(/font/OpenDyslexic/Bold.otf) format("opentype")',
				descriptors: {
					weight: 700,
					style: 'normal'
				}
			},
			{
				src: 'url(/font/OpenDyslexic/BoldItalic.otf) format("opentype")',
				descriptors: {
					weight: 700,
					style: 'italic'
				}
			}
		]
	}
];

export const a11yFontFamilies = getFamilies(fontsInfo);
