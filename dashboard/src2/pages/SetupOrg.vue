<template>
	<div
		class="flex h-screen overflow-hidden"
		v-if="!$resources.validateRequestKey?.loading && email"
	>
		<div class="w-full overflow-auto">
			<SetupOrgBox
				:title="invitedBy ? 'Invitation to join' : 'Thiết lập thông tin tổ chức của bạn'"
				:subtitle="invitedBy ? `Invitation by ${invitedBy}` : ''"
			>
				<template v-slot:logo v-if="saasProduct">
					<div class="flex flex-col items-center">
						<img
							class="inline-block h-[150px] w-[150px] rounded-sm"
							:src="saasProduct?.logo"
						/>
					</div>
				</template>
				<form class="mt-6 flex flex-col" @submit.prevent="submitForm">
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
							<template v-if="!userExists">
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
										v-model="domain"
										name="domain"
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
										disabled
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
							</template>
							
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
							<Button
							class="mt-4 p-4 pr-8 pl-8"
							variant="solid"
							:loading="$resources.setupAccount?.loading"
							theme="blue"
						>
							{{
								is2FA ? 'Verify' : isInvitation ? 'Accept' : 'Tạo tổ chức'
							}}
						</Button>
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
	<div
		class="mt-20 px-6 text-center"
		v-else-if="!$resources.validateRequestKey?.loading && !email"
	>
		Verification link is invalid or expired.
		<Link to="/signup">Sign up</Link>
		for a new account.
	</div>
	<div v-else></div>
</template>

<script>
import SetupOrgBox from '../components/auth/SetupOrgBox.vue';
import Link from '@/components/Link.vue';
import Form from '@/components/Form.vue';
import { DashboardError } from '../utils/error';
import { toRaw, isProxy } from 'vue';
import {toast} from 'vue-sonner';
export default {
	name: 'SetupAccount',
	components: {
		SetupOrgBox,
		Link,
		Form,
	},
	props: ['requestKey', 'joinRequest'],
	data() {
		return {
			email: null,
			firstName: null,
			lastName: null,
			errorMessage: null,
			userExists: null,
			twoFactorCode: null,
			invitationToTeam: null,
			isInvitation: null,
			oauthSignup: 0,
			oauthDomain: false,
			country: null,
			invitedBy: null,
			invitedByParentTeam: false,
			countries: [],
			saasProduct: null,
			signupValues: {},
			baseOrgOptions:[],
			selectedOrg: null,
			orgMap: {}, 
			phone: null,
		};
	},
	resources: {
		validateRequestKey() {
				return {
					url: 'press.api.account.validate_request_key',
					params: {
						key: this.requestKey,
						timezone: window.Intl
							? Intl.DateTimeFormat().resolvedOptions().timeZone
							: null,
					},
					auto: true,
					onSuccess(res) {
						if (res && res.email) {
							this.email = res.email;
							this.firstName = res.first_name;
							this.lastName = res.last_name;
							this.country = res.country;
							this.userExists = res.user_exists;
							this.invitationToTeam = res.team;
							this.invitedBy = res.invited_by;
							this.isInvitation = res.is_invitation;
							this.invitedByParentTeam = res.invited_by_parent_team;
							this.oauthSignup = res.oauth_signup;
							this.oauthDomain = res.oauth_domain;
							this.countries = res.countries;
							this.saasProduct = res.product_trial;
						}
					},
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
		setupAccount() {
			return {
				url: 'press.api.account.setup_account',
				params: {
					key: this.requestKey,
					first_name: this.email,
					last_name: this.email,
					country: this.country,
					is_invitation: this.isInvitation,
					user_exists: this.userExists,
					invited_by_parent_team: this.invitedByParentTeam,
					oauth_signup: this.oauthSignup,
					oauth_domain: this.oauthDomain,
					base_org:this.selectedOrg.value,
					phone: this.phone
				},
				onSuccess(message) {
					console.log(message)
					let path =  `/dashboard/create-site/${this.saasProduct.name}/login-to-site?product_trial_request=${message.message.rq_name}`;
					// if (this.saasProduct) {
					// 	path = `/dashboard/create-site/${this.saasProduct.name}/setup`;
					// }
					// if (this.isInvitation) {
					// 	path = '/dashboard/sites';
					// }
					console.log("redirect to "+path)
					window.location.href = path;
				},
				 onError: (error) => {
					let errorMessage = '';
					if ((error?.messages ?? []).length) {
						errorMessage = error?.messages?.[0];
						toast.error(errorMessage)
						return
					}
					toast.error( "Tổ chức đã được sử dụng");  
				}
			};
		},
		is2FAEnabled() {
			return {
				url: 'press.api.account.is_2fa_enabled',
			};
		},
		verify2FA() {
			return {
				url: 'press.api.account.verify_2fa',
				onSuccess() {
					this.$resources.setupAccount.submit();
				},
			};
		},
	},
	computed: {
		is2FA() {
			return (
				this.$route.name === 'Setup Account' && this.$route.query.two_factor
			);
		},
	},
	methods: {
		submitForm() {
			if (this.invitedBy) {
				this.$resources.is2FAEnabled.submit(
					{
						user: this.email,
					},
					{
						onSuccess: (two_factor_enabled) => {
							if (two_factor_enabled) {
								this.$router.push({
									name: 'Setup Account',
									query: {
										...this.$route.query,
										two_factor: 1,
									},
								});
							} else {
								this.$resources.setupAccount.submit();
							}
						},
					},
				);
			} else {
				this.$resources.setupAccount.submit();
			}
		},
	},
	watch: {
  selectedOrg(code) {
	console.log("code" + code.value)
	const rawMap = isProxy(this.orgMap) ? toRaw(this.orgMap) : this.orgMap;
// console.log('orgMap =', rawMap);         
// console.dir(rawMap);
// console.log('%o', rawMap);
    const org = this.orgMap[code.value];
	console.log("debug-=-- "+org);
    if (!org) return;
    this.agencyCode  = org.organization_code || '';
    this.agencyName  = org.organization_name || '';
    this.agencyType  = org.type || '';
    this.agencyLevel = org.level || '';
    this.province    = org.province || '';
    this.commune     = org.commune || '';
    this.domain      = org.name_domain || '';
  },
},
};
</script>
