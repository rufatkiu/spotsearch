<script lang="ts">
	import { search } from '$lib/api';
	let query = '';

	function searchHandler() {
		search(query);
	}
</script>

<form on:submit|preventDefault={searchHandler}>
	<div class="flex flex-col place-items-center">
		<div class="mt-1 relative h-12 w-9/12">
			<div class="absolute inset-y-0 left-0 pl-3 flex items-center">
				<img
					src="https://spot.ecloud.global/static/themes/eelo/img/logo.png"
					class="h-5 w-5"
					alt="/e/ spot"
				/>
			</div>
			<input
				type="text"
				name="search"
				id="search"
				class="focus:outline-none border-2 border-gray-300 shadow-lg rounded-full focus:ring-1 focus:ring-blue-200 h-12 w-full pl-10 pr-12"
				bind:value={query}
				placeholder="Search"
			/>
			<div class="absolute inset-y-0 right-0 flex items-center">
				<button type="submit" class="text-gray-400 hover:text-gray-700 right-0 top-0 mt-0 mr-4">
					<svg
						class="h-5 w-5 fill-current"
						xmlns="http://www.w3.org/2000/svg"
						xmlns:xlink="http://www.w3.org/1999/xlink"
						version="1.1"
						id="Capa_1"
						x="0px"
						y="0px"
						viewBox="0 0 56.966 56.966"
						style="enable-background:new 0 0 56.966 56.966;"
						xml:space="preserve"
						width="512px"
						height="512px"
					>
						<path
							d="M55.146,51.887L41.588,37.786c3.486-4.144,5.396-9.358,5.396-14.786c0-12.682-10.318-23-23-23s-23,10.318-23,23  s10.318,23,23,23c4.761,0,9.298-1.436,13.177-4.162l13.661,14.208c0.571,0.593,1.339,0.92,2.162,0.92  c0.779,0,1.518-0.297,2.079-0.837C56.255,54.982,56.293,53.08,55.146,51.887z M23.984,6c9.374,0,17,7.626,17,17s-7.626,17-17,17  s-17-7.626-17-17S14.61,6,23.984,6z"
						/>
					</svg>
				</button>
			</div>
		</div>
	</div>
</form>
