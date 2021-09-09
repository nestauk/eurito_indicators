import visit from 'unist-util-visit';

const entites = [
	[/&#123;/g, '{' ],
	[/&#125;/g, '}' ],
];

export function unescape_code() { 
	return function (tree) {
		visit(tree, 'inlineCode', unescape);

		function unescape(node) {
			for (let i = 0; i < entites.length; i += 1) {
				node.value = node.value.replace(entites[i][0], entites[i][1]);
			}
		}
	};
}
