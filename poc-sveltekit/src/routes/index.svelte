<script context="module" lang="ts">
	export const prerender = true;
</script>

<script lang="ts">
	import SearchBar from '$lib/SearchBar.svelte';
	import { results, metadata } from '$lib/store';
</script>

<svelte:head>
	<title>/e/ spot</title>
</svelte:head>

<section class="container mx-auto">
	{#if $results == null}
		<div class="flex flex-col justify-items-center place-items-center">
			<img
				src="https://spot.ecloud.global/static/themes/eelo/img/logo_searx_a.png"
				class="w-1/4 h-1/4 "
				alt="/e/ spot"
			/>
		</div>
	{/if}
	<SearchBar />
	<div class="h-6" />
	<div class="flex sm:flex-row-reverse flex-col">
		{#if $metadata != null}
			<div class="flex flex-col space-y-3">
				{#each $metadata.infoboxes as result}
					<div class="bg-white shadow overflow-hidden sm:rounded-lg">
						<div class="px-4 py-5 sm:px-6">
							<h3 class="text-lg leading-6 font-medium text-gray-900">{result.infobox}</h3>
							<p class="mt-1 max-w-2xl text-sm text-gray-500">{result.engine}</p>
						</div>
						<div class="px-4 py-5 sm:px-6 border-t border-gray-200">
							<img src={result.img_src} alt={result.infobox} />
						</div>
						<div class="border-t border-gray-200">
							<dl>
								{#each result.attributes as attr, idx}
									{#if idx % 2 == 0}
										<div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
											<dt class="text-sm font-medium text-gray-500">{attr.label}</dt>
											<dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{attr.value}</dd>
										</div>
									{:else}
										<div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
											<dt class="text-sm font-medium text-gray-500">{attr.label}</dt>
											<dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{attr.value}</dd>
										</div>
									{/if}
								{/each}
							</dl>
						</div>
						<div class="px-4 py-5 sm:px-6 grid grid-flow-col auto-rows-max gap-2">
							{#each result.urls as url, idx}
								<dl>
									<dd class="text-blue-500"><a href={url.url}>{url.title}</a></dd>
								</dl>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		{/if}
		{#if $results != null}
			<div class="flex flex-col space-y-3 px-2 m-2">
				{#each $results.results as result}
					<div class="">
						<h3 class="text-blue-700 text-bold hover:underline">
							<a href={result.url}>{result.title}</a>
						</h3>
						{#if result.content}
							<p>{result.content}</p>
						{/if}
						<a class="text-green-400 hover:underline" href={result.url}>{result.url}</a>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</section>
