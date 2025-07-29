export { matchers } from './matchers.js';

export const nodes = [
	() => import('./nodes/0'),
	() => import('./nodes/1'),
	() => import('./nodes/2'),
	() => import('./nodes/3'),
	() => import('./nodes/4'),
	() => import('./nodes/5'),
	() => import('./nodes/6'),
	() => import('./nodes/7'),
	() => import('./nodes/8'),
	() => import('./nodes/9'),
	() => import('./nodes/10'),
	() => import('./nodes/11'),
	() => import('./nodes/12'),
	() => import('./nodes/13'),
	() => import('./nodes/14'),
	() => import('./nodes/15'),
	() => import('./nodes/16'),
	() => import('./nodes/17'),
	() => import('./nodes/18'),
	() => import('./nodes/19'),
	() => import('./nodes/20'),
	() => import('./nodes/21'),
	() => import('./nodes/22'),
	() => import('./nodes/23'),
	() => import('./nodes/24')
];

export const server_loads = [];

export const dictionary = {
		"/": [4],
		"/dashboard": [5,[2]],
		"/dashboard/analisis": [6,[2]],
		"/dashboard/analisis/comparison-demo": [7,[2]],
		"/dashboard/analisis/[id]": [8,[2]],
		"/dashboard/kelas": [9,[2]],
		"/dashboard/kelas/[id]": [10,[2]],
		"/dashboard/laporan": [11,[2]],
		"/dashboard/laporan/ujian-siswa": [12,[2]],
		"/dashboard/laporan/ujian-siswa/[id]": [~13,[2]],
		"/dashboard/laporan/[id]": [14,[2]],
		"/dashboard/ujian": [15,[2]],
		"/dashboard/ujian/[id]": [16,[2]],
		"/dashboard/ujian/[id]/jawaban": [17,[2]],
		"/login": [18],
		"/register": [19],
		"/siswa": [20,[3]],
		"/siswa/nilai": [21,[3]],
		"/siswa/[id]": [22,[3]],
		"/siswa/[id]/[ujian]": [23,[3]],
		"/siswa/[id]/[ujian]/[result]": [24,[3]]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
	
	reroute: (() => {}),
	transport: {}
};

export const decoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.decode]));

export const hash = false;

export const decode = (type, value) => decoders[type](value);

export { default as root } from '../root.js';