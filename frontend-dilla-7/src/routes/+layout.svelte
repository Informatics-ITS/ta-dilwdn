<script>
	import '../css/app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	onMount(() => {
		// Only redirect on homepage
		if ($page.url.pathname === '/') {
			const user = localStorage.getItem('user');
			if (user) {
				try {
					const userData = JSON.parse(user);
					// Redirect to pages that have proper design
					if (userData.role === 'guru' || userData.role === 'admin') {
						goto('/dashboard'); // Dashboard already has complete design
					} else if (userData.role === 'siswa') {
						goto('/siswa'); // Will auto-redirect to siswa/[id] which has design
					}
				} catch (error) {
					console.error('Error parsing user data:', error);
					localStorage.removeItem('user');
				}
			}
		}
	});
</script>

<div class="font-roboto">
	<slot />
</div>
