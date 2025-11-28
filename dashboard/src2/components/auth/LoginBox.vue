<template>
	<div class="relative h-full">
		<div class="relative z-10 mx-auto py-12 sm:w-max sm:py-26">
			<div class="flex flex-col px-4" @dblclick="redirectForFrappeioAuth">
				<slot name="logo">
					<div class="flex flex-col items-center">
						<!-- <HNTLogo class="inline-block h-[38px] w-[38px]" /> -->
					 
					<div class="flex flex-col items-center">
						<!-- <img
							class="inline-block h-[150px] w-[150px] rounded-sm"
							src="https://admin.nextgrp.vn/files/ChatGPT%20Image%20Aug%2014,%202025,%2010_55_54%20AM.png"
						/> -->
							<HNTLogo   class="inline-block h-[90px] w-[150px] rounded-sm"/>
					</div>
					</div>
				</slot>
			</div>
			<div class="mx-auto w-full bg-white px-6  max-w-xl sm:rounded-lg py-2">
				<!-- <div class="mb-2" v-if="title">
					<span
						class="text-2xl font-bold leading-5 tracking-tight text-gray-900"
					>
						{{ title }}
					</span>
				</div>
				<p
					class="mb-6 break-words text-base font-normal leading-[21px] text-gray-700"
					v-if="subtitle"
				>
					{{ subtitle }}
				</p> -->
				  <p class="font-semibold text-lg leading-snug text-center pb-2">
					<span class="whitespace-nowrap">
						nextGRP – Tiên phong trong lĩnh vực công nghệ,
					</span><br>
					<span class="whitespace-nowrap">
						đồng hành với Chính phủ, doanh nghiệp trong công cuộc chuyển đổi số
					</span>
				</p>

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
		FCLogo,
		HNTLogo
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
