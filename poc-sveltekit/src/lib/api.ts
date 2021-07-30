import { results, metadata } from '$lib/store';

export function search(query: string): Any {
	const url = 'http://localhost:8088';
	const results_endpoint = `${url}/search?categories=general&format=json&q=${query}&language=fr-FR`;
	const metadata_endpoint = `${url}/search?engines=wikidata&format=json&q=${query}&language=fr-FR`;

	results.set({ results: new Array(0) });
	metadata.set({ infoboxes: new Array(0) });

	fetch(results_endpoint, {
		method: 'GET',
		headers: { 'Content-Type': 'application/json' }
	})
		.then((r) => {
			if (r.status === 404) {
				throw new Error(r.json.message);
			}
			return r.json();
		})
		.then((data) => {
			results.update((elt) => {
				return {
					results: elt.results.concat(data.results)
				};
			});
		})
		.catch((err) => {
			console.log(err.message);
		});

	fetch(metadata_endpoint, {
		method: 'GET',
		headers: { 'Content-Type': 'application/json' }
	})
		.then((r) => {
			if (r.status === 404) {
				throw new Error(r.json.message);
			}
			return r.json();
		})
		.then((data) => {
			metadata.update((elt) => {
				return {
					infoboxes: elt.infoboxes.concat(data.infoboxes)
				};
			});
		})
		.catch((err) => {
			console.log(err.message);
		});
}
