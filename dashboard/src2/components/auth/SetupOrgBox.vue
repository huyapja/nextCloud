<template>
	<div class="relative h-full">
		<div class="relative z-10 mx-auto pb-8 sm:max-w-4xl sm:w-full sm:pb-24">
			<div class="flex flex-col px-4 py-2" @dblclick="redirectForFrappeioAuth">
				<slot name="logo"> 
					<div class="flex flex-col items-center"> 
						<div class="flex flex-col items-center">  
							<HNTLogo class="inline-block h-[90px] w-[200px] rounded-sm" />
						</div> 
					</div>
				</slot>
			</div>
			<div class="mx-auto w-full bg-white px-6  max-w-3xl sm:rounded-2xl">
				<div class="mb-2 text-center" v-if="title">
					<span
					class="text-2xl font-bold leading-5 tracking-tight text-gray-900"
					>
							{{ title }}  
					</span> 
				</div>
				<!-- <p
					class="mb-6 break-words text-base font-normal leading-[21px] text-gray-700"
					v-if="subtitle"
				>
					{{ subtitle }}  
				</p> -->
				<slot></slot>
			</div>
			<slot name="footer"></slot>
		</div>
	</div>
</template>

<script>
import { toast } from 'vue-sonner';
import FCLogo from '@/components/icons/FCLogo.vue';
import HNTLogo from '@/components/icons/HNTLogo.vue';
export default {
	name: 'LoginBox',
	props: ['title', 'logo', 'subtitle'],
	components: {
		FCLogo,HNTLogo,
	},
	mounted() {
		const params = new URLSearchParams(window.location.search);

		if (params.get('showRemoteLoginError')) {
			toast.error('Token Invalid or Expired');
		}
	},
	methods: {
		redirectForFrappeioAuth() {
			window.location = '/f-login';
		},
	},
};
</script>
