<template>
	<PlansCards v-model="currentPlan" :plans="plans" />
</template>

<script>
import PlansCards from './PlansCards.vue';
import { getPlans } from '../data/plans';

export default {
	name: 'SitePlansCards',
	props: [
		'modelValue',
		'isPrivateBenchSite',
		'isDedicatedServerSite',
		'selectedCluster',
		'selectedApps',
		'selectedVersion',
		'hideRestrictedPlans',
	],
	emits: ['update:modelValue'],
	components: {
		PlansCards,
	},
	computed: {
		currentPlan: {
			get() {
				return this.modelValue;
			},
			set(value) {
				this.$emit('update:modelValue', value);
			},
		},
		plans() {
			let plans = getPlans();
			console.log("plans", plans);
			if (this.isPrivateBenchSite) {
				console.log("1");
				plans = plans.filter((plan) => plan.private_benches);
			}
			if (this.isPrivateBenchSite && this.isDedicatedServerSite) {
				console.log("2");
				plans = plans.filter((plan) => plan.dedicated_server_plan);
			} else {
				console.log("3");
				plans = plans.filter((plan) => !plan.dedicated_server_plan);
				console.log("3plans", plans);
			}
			if (this.selectedCluster) {
				console.log("4");
				plans = plans.map((plan) => {
					return {
						...plan,
						disabled:
							plan.disabled ||
							(plan.clusters.length == 0
								? false
								: !plan.clusters.includes(this.selectedCluster)),
					};
				});
			}
			if (this.selectedApps) {
				console.log("5");
				plans = plans.map((plan) => {
					return {
						...plan,
						disabled:
							plan.disabled ||
							(plan.allowed_apps.length == 0
								? false
								: !this.selectedApps.every((app) =>
										plan.allowed_apps.includes(app.app),
									)),
					};
				});
			}
			if (this.selectedVersion) {
				console.log("6");
				plans = plans.map((plan) => {
					return {
						...plan,
						disabled:
							plan.disabled ||
							(plan.bench_versions.length == 0
								? false
								: !plan.bench_versions.includes(this.selectedVersion)),
					};
				});
			}
			if (this.hideRestrictedPlans) {
				console.log("7");
				plans = plans.filter((plan) => !plan.restricted_plan);
			}
			console.log("8");
			return plans.map((plan) => {
				return {
					...plan,
					features: [
						{
							label: `${this.$format.plural(
								plan.cpu_time_per_day,
								'compute hour',
								'compute hours',
							)} / day`,
							condition: !plan.name.includes('Unlimited'),
							value: plan.cpu_time_per_day,
						},
						{
							label: 'Database',
							condition: !plan.name.includes('Unlimited'),
							value: this.$format.bytes(plan.max_database_usage, 1, 2),
						},
						{
							label: 'Disk',
							condition: !plan.name.includes('Unlimited'),
							value: this.$format.bytes(plan.max_storage_usage, 1, 2),
						},
						{
							value: plan.name.includes('Unlimited - Low')
								? 'Allocate fewer resources here (more for other benches)'
								: '',
						},
						{
							value: plan.support_included ? 'Product Warranty' : '',
						},
						{
							value: plan.database_access ? 'Database Access' : '',
						},
						{
							value: plan.offsite_backups ? 'Offsite Backups' : '',
						},
						{
							value: plan.monitor_access ? 'Advanced Monitoring' : '',
						},
					].filter((feature) => feature.condition ?? true),
				};
			});
		},
	},
};
</script>
