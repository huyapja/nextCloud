<template>
	<div class="p-5" v-if="deploy">
		<AlertAddressableError
			v-if="error"
			class="mb-5"
			:name="error.name"
			:title="error.title"
			@done="$resources.errors.reload()"
		/>
		<AlertBanner
			v-if="alertMessage && !error"
			:title="alertMessage"
			type="warning"
			class="mb-5"
		/>
		<Button :route="{ name: `${object.doctype} Detail Deploys` }">
			<template #prefix>
				<i-lucide-arrow-left class="inline-block h-4 w-4" />
			</template>
			All deploys
		</Button>

		<div class="mt-3">
			<div class="flex w-full items-center">
				<h2 class="text-lg font-medium text-gray-900">
					{{ deploy.deploy_candidate }}
				</h2>
				<Badge class="ml-2" :label="deploy.status" />
				<div class="ml-auto flex items-center space-x-2">
					<Button
						@click="$resources.deploy.reload()"
						:loading="$resources.deploy.get.loading"
					>
						<template #icon>
							<i-lucide-refresh-ccw class="h-4 w-4" />
						</template>
					</Button>
					<Dropdown v-if="dropdownOptions?.length" :options="dropdownOptions">
						<template v-slot="{ open }">
							<Button>
								<template #icon>
									<i-lucide-more-horizontal class="h-4 w-4" />
								</template>
							</Button>
						</template>
					</Dropdown>
				</div>
			</div>
			<div>
				<div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
					<div>
						<div class="text-sm font-medium text-gray-500">Creation</div>
						<div class="mt-2 text-sm text-gray-900">
							{{ $format.date(deploy.creation, 'lll') }}
						</div>
					</div>
					<div>
						<div class="text-sm font-medium text-gray-500">Creator</div>
						<div class="mt-2 text-sm text-gray-900">
							{{ deploy.owner }}
						</div>
					</div>
					<div>
						<div class="text-sm font-medium text-gray-500">Duration</div>
						<div class="mt-2 text-sm text-gray-900">
							{{
								deploy.build_end ? $format.duration(deploy.build_duration) : '-'
							}}
						</div>
					</div>
					<div>
						<div class="text-sm font-medium text-gray-500">Start</div>
						<div class="mt-2 text-sm text-gray-900">
							{{ $format.date(deploy.build_start, 'lll') }}
						</div>
					</div>
					<div>
						<div class="text-sm font-medium text-gray-500">End</div>
						<div class="mt-2 text-sm text-gray-900">
							{{
								deploy.build_end ? $format.date(deploy.build_end, 'lll') : '-'
							}}
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Build Steps -->
		<div :class="deploy.build_error ? 'mt-4' : 'mt-8'" class="space-y-4">
			<JobStep
				v-for="step in deploy.build_steps"
				:step="step"
				:key="step.name"
			/>
			<JobStep v-for="job in deploy.jobs" :step="job" :key="job.name" />
		</div>
	</div>
</template>
<script>
import { createResource, getCachedDocumentResource } from 'frappe-ui';
import { getObject } from '../objects';
import JobStep from '../components/JobStep.vue';
import AlertAddressableError from '../components/AlertAddressableError.vue';
import AlertBanner from '../components/AlertBanner.vue';
import dayjs from 'dayjs';
import { toast } from 'vue-sonner';

export default {
	name: 'DeployCandidate',
	props: ['id', 'objectType'],
	components: {
		JobStep,
		AlertBanner,
		AlertAddressableError,
	},
	resources: {
		deploy() {
			return {
				type: 'document',
				doctype: 'Deploy Candidate Build',
				name: this.id,
				transform: this.transformDeploy,
			};
		},
		errors() {
			return {
				type: 'list',
				cache: [
					'Press Notification',
					'Error',
					'Deploy Candidate Build',
					this.id,
				],
				doctype: 'Press Notification',
				auto: true,
				fields: ['title', 'name'],
				filters: {
					document_type: 'Deploy Candidate Build',
					document_name: this.id,
					is_actionable: true,
					class: 'Error',
				},
				limit: 1,
			};
		},
	},
	mounted() {
		this.$socket.emit('doc_subscribe', 'Deploy Candidate Build', this.id);
		this.$socket.on(`bench_deploy:${this.id}:steps`, (data) => {
			if (data.name === this.id && this.$resources.deploy.doc) {
				this.$resources.deploy.doc.build_steps = this.transformDeploy({
					build_steps: data.steps,
				})?.build_steps;
			}
		});
		this.$socket.on(`bench_deploy:${this.id}:finished`, () => {
			const rgDoc = getCachedDocumentResource(
				'Release Group',
				this.$resources.deploy.doc?.group,
			);
			if (rgDoc) rgDoc.reload();
			this.$resources.deploy.reload();
			this.$resources.errors.reload();
		});
	},
	beforeUnmount() {
		this.$socket.emit('doc_unsubscribe', 'Deploy Candidate Build', this.id);
		this.$socket.off(`bench_deploy:${this.id}:steps`);
	},
	computed: {
		deploy() {
			return this.$resources.deploy.doc;
		},
		object() {
			return getObject(this.objectType);
		},
		error() {
			return this.$resources.errors?.data?.[0] ?? null;
		},
		alertMessage() {
			if (!this.deploy) {
				return null;
			}

			if (this.deploy.retry_count > 0 && this.deploy.status === 'Scheduled') {
				return 'Previous deploy failed, re-deploy will be attempted soon';
			}
			return null;
		},
		dropdownOptions() {
			return [
				{
					label: 'View in Desk',
					icon: 'external-link',
					condition: () => this.$team?.doc?.is_desk_user,
					onClick: () => {
						window.open(
							`${window.location.protocol}//${window.location.host}/app/deploy-candidate-build/${this.id}`,
							'_blank',
						);
					},
				},
				{
					label: 'Fail and Redeploy',
					icon: 'repeat',
					condition: () => this.showFailAndRedeploy,
					onClick: () => this.failAndRedeploy(),
				},
			].filter((option) => option.condition?.() ?? true);
		},
		showFailAndRedeploy() {
			if (!this.deploy || this.deploy.status == 'Failure') {
				return false;
			}
			const from = ['Pending', 'Preparing'].includes(this.deploy.status)
				? this.deploy.creation
				: this.deploy.build_start;
			const now = dayjs(new Date());
			return now.diff(from, 'hours') > 2;
		},
	},
	methods: {
		transformDeploy(deploy) {
			for (let step of deploy.build_steps) {
				if (step.status === 'Running') {
					step.isOpen = true;
				} else {
					step.isOpen = this.$resources.deploy?.doc?.build_steps?.find(
						(s) => s.name === step.name,
					)?.isOpen;
				}
				step.title = `${step.stage} - ${step.step}`;
				step.output =
					step.command || step.output
						? `${step.command || ''}\n${step.output || ''}`.trim()
						: '';
				step.duration = ['Success', 'Failure'].includes(step.status)
					? step.cached
						? 'Cached'
						: `${step.duration}s`
					: null;
			}
			return deploy;
		},
		failAndRedeploy() {
			if (!this.deploy) {
				return;
			}

			const group = this.deploy.group;
			const onError = () => toast.error('Could not fail and redeploy');
			const router = this.$router;

			createResource({
				url: 'press.api.bench.fail_and_redeploy',
				params: { name: group, dc_name: this.deploy.name },
				onSuccess(name) {
					if (!name) {
						onError();
					} else {
						router.push(`/groups/${group}/deploys/${name}`);
					}
				},
				onError,
			}).fetch();
		},
	},
};
</script>
