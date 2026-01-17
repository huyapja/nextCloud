<template>
<div
		class="flex h-screen overflow-hidden"
	>
		<div class="w-full overflow-auto">
			<SetupOrgBox
				:title="invitedBy ? 'Invitation to join' :  `Thiết lập thông tin tổ chức của bạn`"
				:subtitle="invitedBy ? `Invitation by ${invitedBy}` :''"
			>
				<!-- <template v-slot:logo>
					<div class="flex flex-col items-center">
						<div class="flex flex-col items-center">
						<img
							class="inline-block h-[150px] w-[150px] rounded-sm"
							:src="saasProduct?.logo"
							/>
					</div>
					</div>
				</template> -->
				<form class="mt-6 flex flex-col" @submit.prevent="createSite">
					<template v-if="is2FA">
						<FormControl
							label="2FA Code from your Authenticator App"
							placeholder="123456"
							v-model="twoFactorCode"
							required
						/>
						<Button
							class="mt-4"
							:loading="$resources.verify2FA?.loading"
							variant="solid"
							@click="
								$resources.verify2FA.submit({
									user: email,
									totp_code: twoFactorCode,
								})
							"
						>
							Verify
						</Button>
						<ErrorMessage class="mt-2" :message="$resources.verify2FA.error" />
					</template>
					<template v-else>
						<div class="space-y-4">
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div>
									<labeL class="block text-xs text-ink-gray-5 pb-[6px]">Mã Cơ quan</labeL>
									<Autocomplete
									v-model="selectedOrg"
									:options="baseOrgOptions"
									placeholder="Chọn cơ quan..."
								/>
								</div>
									<FormControl
										label="Tên Cơ Quan"
										type="text"
										v-model="agencyName"
										name="agencyName"
										autocomplete="family-name"
										variant="outline"
										disabled
									/>
								</div>

								<!-- loai co quan cap  -->
								 <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<FormControl
										label="Loại Cơ Quan"
										type="text"
										v-model="agencyType"
										name="agencyType"
										autocomplete="given-name"
										variant="outline"
										disabled
									/>
									<FormControl
										label="Cấp"
										type="text"
										v-model="agencyLevel"
										name="agencyLevel"
										autocomplete="family-name"
										variant="outline"
									disabled
									/>
								</div>

								<!-- tinh/thanh pho , xa/phuong -->
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<FormControl
										label="Tỉnh/Thành phố"
										type="text"
										v-model="province"
										name="province"
										autocomplete="given-name"
										variant="outline"
									disabled
									/>
									<FormControl
										label="Xã/Phường"
										type="text"
										v-model="commune"
										name="commune"
										autocomplete="family-name"
										variant="outline"
										disabled
									/>
								</div>

								<!-- ten domain , email dang nhap  -->
								 <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<FormControl
										label="Tên domain"
										type="text"
										v-model="domain_rq"
										name="domain_rq"
										autocomplete="given-name"
										variant="outline"
										required
										disabled
									/>
									<FormControl
										label="Email"
										type="text"
										:modelValue="email"
										variant="outline"
										v-model="email"
										required
									/>
								</div>
								<!-- so dtien thoa -->

								 <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<FormControl
										label="Số điện thoại"
										type="text"
										v-model="phone"
										name="phone"
										autocomplete="given-name"
										variant="outline"
										required

									/>
								</div>

							<!-- <FormControl
								type="select"
								:options="countries"
								v-if="!isInvitation"
								label="Country"
								v-model="country"
								variant="outline"
								required
							/> -->
						</div>
						<!-- <ErrorMessage
							class="mt-4"
							:message="$resources.setupAccount?.error || ''"
						/> -->
						<div class="mt-4 flex justify-center">
							<!-- <Button
							class="mt-4 p-4 pr-8 pl-8"
							variant="solid"
							:loading="$resources.setupAccount?.loading"
							theme="blue"
						>
							{{
								is2FA ? 'Verify' : isInvitation ? 'Accept' : 'Tạo tổ chức'
							}}
						</Button> -->
						<Button
												class="mt-4 p-4 pr-8 pl-8"
												variant="solid"
												label="Tạo tổ chức"
												:loading="findingClosestServer ||$resources.createSite?.loading"
												:loadingText="'Đang khởi tạo tổ chức...'"
												theme="blue"
											/>
						</div>
					</template>
				</form>
				<!-- <div class="mt-4" v-if="!is2FA && !isInvitation">
					<span class="text-base font-normal text-gray-600">
						{{ 'By signing up, you agree to our ' }}
					</span>
					<a
						class="text-base font-normal text-gray-900 underline hover:text-gray-700"
						href="https://frappecloud.com/policies"
					>
						Terms & Policies
					</a>
				</div> -->
			</SetupOrgBox>
		</div>
	</div>
</template>
<script>
import SetupOrgBox from '../../components/auth/SetupOrgBox.vue';
import Link from '@/components/Link.vue';
import Form from '@/components/Form.vue';
import { DashboardError } from '../../utils/error';
import { toRaw, isProxy } from 'vue';
import {toast} from 'vue-sonner';

export default {
	name: 'SignupSetup',
	props: ['productId'],
	components: {
		SetupOrgBox,
		Link,
		Form,
	},
	data() {
		return {
			email: null,
			firstName: null,
			lastName: null,
			errorMessage: null,
			userExists: null,
			twoFactorCode: null,
			progressErrorCount: 0,
			findingClosestServer: false,
			closestCluster: null,
			subdomain: '',
			oauthDomain: false,
			country: null,
			invitedBy: null,
			invitedByParentTeam: false,
			countries: [],
			signupValues: {},
			baseOrgOptions:[],
			selectedOrg: null,
			orgMap: {},
			phone: null,
			domain_rq: null,
		};
	},
	resources: {
		siteRequest() {
			return {
				url: 'press.api.product_trial.get_request',
				params: {
					product: this.productId,
					account_request: this.$team.doc.account_request,
				},
				auto: !!this.saasProduct,
				initialData: {},
				onSuccess: (data) => {
					if (data?.status !== 'Pending') {
						this.$router.push({
							name: 'SignupLoginToSite',
							params: { productId: this.productId },
							query: {
								product_trial_request: data.name,
							},
						});
					}
				},
				onError(error) {
					toast.error(error.messages.join('\n'));
				},
			};
		},
		createSite() {
			return {
				url: 'press.api.client.run_doc_method',
				makeParams: () => {
					return {
						dt: 'Product Trial Request',
						dn: this.$resources.siteRequest.data.name ,
						method: 'create_site_hnt',
						args: {
							subdomain: this.subdomain,
							cluster: this.closestCluster ?? 'Default',
							email: this.email,
							phone: this.phone,
							base_org:this.selectedOrg.value,
						},
					};
				},
				auto: false,
				onSuccess: (data) => {
					this.$router.push({
						name: 'SignupLoginToSite',
						params: { productId: this.productId },
						query: {
							product_trial_request: this.$resources.siteRequest.data.name,
						},
					});
				},
				onError: (error) => {
					if (error?.exc_type !== 'ValidationError') {
						return;
					}
					let errorMessage = '';
					if ((error?.messages ?? []).length) {
						errorMessage = error?.messages?.[0];
						toast.error(errorMessage);
					}
				}
			};
		},
		saasProduct() {
			return {
				type: 'document',
				doctype: 'Product Trial',
				name: this.productId,
				auto: true,
			};
		},
		getBaseOrg()
		{
			return{

					url: 'nextgrp.nextgrp.doctype.organization.organization_press.get_org',
					auto: true,
					cache:true,
					onSuccess(res) {
						if (res) {
							const list = Array.isArray(res) ? res : (res?.message || []);
							this.baseOrgOptions = list.map(o => {
								this.orgMap[o.name] = o;
							return {
										label: o.organization_code,
										value: o.name,
									};
							});
							// res.forEach(element => {

								// this.baseOrgOptions.push(
								// 	{
								// 		label: element.organization_code,
								// 		value: element.name,
								// 		...element
								// 	}
								// )
							// });
						}
					},
			}
		},
	},
	computed: {
		saasProduct() {
			return this.$resources.saasProduct?.doc;
		},
		domain() {
			return this.saasProduct?.domain;
		},
	},
	methods: {
		async createSite() {
			await this.getClosestCluster();
			return this.$resources.createSite.submit();
		},
		async getClosestCluster() {
			if (this.closestCluster) return this.closestCluster;
			let proxyServers = Object.keys(this.saasProduct.proxy_servers);
			if (proxyServers.length > 0) {
				this.findingClosestServer = true;
				let promises = proxyServers.map((server) => this.getPingTime(server));
				let results = await Promise.allSettled(promises);
				let fastestServer = results.reduce((a, b) =>
					a.value.pingTime < b.value.pingTime ? a : b,
				);
				let closestServer = fastestServer.value.server;
				let closestCluster = this.saasProduct.proxy_servers[closestServer];
				if (!this.closestCluster) {
					this.closestCluster = closestCluster;
				}
				this.findingClosestServer = false;
			}
			return this.closestCluster;
		},
		async getPingTime(server) {
			let pingTime = 999999;
			try {
				let t1 = new Date().getTime();
				await fetch(`https://${server}`);
				let t2 = new Date().getTime();
				pingTime = t2 - t1;
			} catch (error) {
				console.warn(error);
			}
			return { server, pingTime };
		},
	},
	watch: {
  selectedOrg(code) {
	const rawMap = isProxy(this.orgMap) ? toRaw(this.orgMap) : this.orgMap;
	const org = this.orgMap[code.value];
	if (!org) return;
	this.agencyCode  = org.organization_code || '';
	this.agencyName  = org.organization_name || '';
	this.agencyType  = org.type || '';
	this.agencyLevel = org.level || '';
	this.province    = org.province || '';
	this.commune     = org.commune || '';
	this.domain_rq      = org.name_domain || '';
  },
},
};
</script>
