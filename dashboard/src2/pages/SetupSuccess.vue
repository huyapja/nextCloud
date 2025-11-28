<template>
	<!-- Success Install Screen -->
<!-- Success Install Screen -->


<div class="min-h-screen w-screen flex items-start justify-center bg-white">
  <div class="w-full max-w-3xl px-6 text-center pt-16">

    <!-- Logo -->
    <div class="flex justify-center mb-6">
      <HNTLogo class="h-[64px] w-[160px]" />
    </div>

    <!-- Tagline (2 dòng, căn giữa) -->
    <p class="text-[18px] font-semibold text-gray-800 leading-snug">
      nextGRP - Tiên phong trong lĩnh vực công nghệ,<br>
      đồng hành với Chính phủ, doanh nghiệp trong công cuộc chuyển đổi số
    </p>

    <!-- Hàng trạng thái: ô vuông + tích + tiêu đề xanh -->
    <div class="mt-8 flex items-center justify-center gap-3">
      <span class="inline-flex h-10 w-10 items-center justify-center rounded-md
                   border border-green-500 bg-green-50">
        <!-- Check icon -->
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-600" fill="none"
             viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M5 13l4 4L19 7"/>
        </svg>
      </span>
      <span class="text-2xl font-bold text-blue-600">Hoàn tất cài đặt!</span>
    </div>

    <!-- Dòng mô tả 1: giữ 1 dòng từ md trở lên -->
    <p
      class="mt-8 text-[18px] font-semibold text-gray-800
             md:whitespace-nowrap md:block"
    >
      Hệ thống đã cài đặt xong toàn bộ ứng dụng cho tổ chức của bạn
      <span v-if="orgName">(<b>{{ orgName }}</b>)</span>
      và gửi thông tin đăng nhập qua email.
    </p>

    <!-- Dòng mô tả 2: icon nhỏ hồng + chữ, giữ 1 dòng từ md trở lên -->
    <div
      class="mt-4 flex items-center justify-center gap-2 text-[18px] font-semibold text-gray-800
             md:whitespace-nowrap pl-[150px]"
    >
      <!-- Mail icon hồng nhỏ -->
      <span class="inline-flex h-4 w-4 items-center justify-center rounded-[4px] bg-pink-100">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"
             class="h-3.5 w-3.5 text-pink-600 fill-current">
          <path d="M2.94 5.5h14.12c.52 0 .94.42.94.94v7.12a.94.94 0 0 1-.94.94H2.94a.94.94 0 0 1-.94-.94V6.44c0-.52.42-.94.94-.94zm.76 1.88 6.08 3.83c.14.08.3.08.44 0l6.08-3.83v-.32H3.7v.32z"/>
        </svg>
      </span>
      <span>
        Vui lòng kiểm tra hộp thư của bạn
        <template v-if="contactEmail"></template>
        để hoàn tất việc kích hoạt và bắt đầu sử dụng.
      </span>
    </div>

  </div>
</div>


</template>
<script>
import LoginBox from '../components/auth/LoginBox.vue';
import Spinner from '../components/Spinner.vue';
import { Progress } from 'frappe-ui';
import HNTLogo from '@/components/icons/HNTLogo.vue';
export default {
	name: 'SignupLoginToSite',
	props: ['productId'],
	components: {
		LoginBox,
		Progress,
		SignupSpinner: Spinner,
		HNTLogo,
	},
	data() {
		return {
			product_trial_request: this.$route.query.product_trial_request,
			progressCount: 0,
			currentBuildStep: 'Preparing for build',
			// Static data for UI demonstration
			siteStatus: 'Wait for Site', // Can be: 'Wait for Site', 'Site Created', 'Error'
			saasProduct: {
				title: 'Demo Product',
				logo: 'https://via.placeholder.com/38x38/3B82F6/FFFFFF?text=D'
			},
			siteDomain: 'demo-site.example.com'
		};
	},
	computed: {
		// Computed properties for UI logic
		isLoading() {
			return this.siteStatus !== 'Error';
		},
		isSiteCreated() {
			return this.siteStatus === 'Site Created';
		},
		isError() {
			return this.siteStatus === 'Error';
		}
	},
	mounted() {
		// Simulate progress for UI demonstration
		this.simulateProgress();
	},
	methods: {
		simulateProgress() {
			// Simulate progress increment for demo purposes
			const interval = setInterval(() => {
				if (this.progressCount < 100 && this.siteStatus !== 'Site Created') {
					this.progressCount += Math.random() * 10;
					if (this.progressCount >= 100) {
						this.progressCount = 100;
						this.siteStatus = 'Site Created';
						clearInterval(interval);
					}
				} else {
					clearInterval(interval);
				}
			}, 2000);
		},
		loginToSite() {
			// Simulate login action
			console.log('Logging to site:', this.siteDomain);
			// You can add actual login logic here if needed
		},
		// Method to change status for testing different UI states
		setStatus(status) {
			this.siteStatus = status;
		}
	},
};
</script>
