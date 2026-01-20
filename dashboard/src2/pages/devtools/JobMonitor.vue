<template>
	<Header class="sticky top-0 z-10 bg-white">
		<div
			class="flex w-full flex-col gap-2 md:flex-row md:items-center md:justify-between"
		>
			<div class="flex flex-row items-center gap-2">
				<Breadcrumbs
					:items="[
						{ label: 'Dev Tools', route: '/job-monitor' },
						{ label: 'Job Monitor', route: '/job-monitor' },
					]"
				/>
			</div>
			<div class="flex flex-row gap-2">
				<Button
					variant="outline"
					:loading="$resources.fixStuckJobs?.loading"
					@click="$resources.fixStuckJobs.submit()"
					iconLeft="refresh-cw"
				>
					Poll All Servers
				</Button>
			</div>
		</div>
	</Header>
	<div class="m-5">
		<div class="space-y-6">
			<!-- Summary Cards -->
			<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
				<div class="rounded-lg border bg-white p-4 shadow-sm">
					<div class="text-sm font-medium text-gray-600">Pending Jobs</div>
					<div class="mt-2 text-2xl font-semibold text-gray-900">
						{{ summary.pending || 0 }}
					</div>
				</div>
				<div class="rounded-lg border bg-white p-4 shadow-sm">
					<div class="text-sm font-medium text-gray-600">Running Jobs</div>
					<div class="mt-2 text-2xl font-semibold text-gray-900">
						{{ summary.running || 0 }}
					</div>
				</div>
				<div class="rounded-lg border bg-white p-4 shadow-sm">
					<div class="text-sm font-medium text-gray-600">Servers</div>
					<div class="mt-2 text-2xl font-semibold text-gray-900">
						{{ summary.servers || 0 }}
					</div>
				</div>
			</div>

			<!-- Jobs by Type -->
			<div class="rounded-lg border bg-white shadow-sm">
				<div class="p-4">
					<h3 class="mb-4 text-lg font-medium text-gray-900">Jobs by Type</h3>
					<div
						v-if="jobsByType.length === 0"
						class="py-8 text-center text-gray-500"
					>
						No stuck jobs found
					</div>
					<div v-else class="space-y-2">
						<div
							v-for="item in jobsByType"
							:key="item.job_type"
							class="flex items-center justify-between rounded border p-3"
						>
							<div>
								<div class="font-medium text-gray-900">{{ item.job_type }}</div>
								<div class="text-sm text-gray-500">
									Pending: {{ item.pending }}, Running: {{ item.running }}
								</div>
							</div>
							<Badge
								:label="`${item.total} total`"
								:theme="item.total > 10 ? 'red' : 'gray'"
							/>
						</div>
					</div>
				</div>
			</div>

			<!-- Jobs by Server -->
			<div class="rounded-lg border bg-white shadow-sm">
				<div class="p-4">
					<h3 class="mb-4 text-lg font-medium text-gray-900">Jobs by Server</h3>
					<div
						v-if="jobsByServer.length === 0"
						class="py-8 text-center text-gray-500"
					>
						No stuck jobs found
					</div>
					<div v-else class="space-y-2">
						<div
							v-for="item in jobsByServer"
							:key="item.server"
							class="flex items-center justify-between rounded border p-3"
						>
							<div>
								<div class="font-medium text-gray-900">{{ item.server }}</div>
								<div class="text-sm text-gray-500">
									Pending: {{ item.pending }}, Running: {{ item.running }}
								</div>
							</div>
							<Badge
								:label="`${item.total} total`"
								:theme="item.total > 10 ? 'red' : 'gray'"
							/>
						</div>
					</div>
				</div>
			</div>

			<!-- Long Running Jobs -->
			<div
				v-if="longRunningJobs.length > 0"
				class="rounded-lg border bg-white shadow-sm"
			>
				<div class="p-4">
					<h3 class="mb-4 text-lg font-medium text-gray-900">
						Long Running Jobs (>1 hour)
					</h3>
					<div class="space-y-2">
						<div
							v-for="job in longRunningJobs"
							:key="job.name"
							class="flex items-center justify-between rounded border border-yellow-200 bg-yellow-50 p-3"
						>
							<div>
								<div class="font-medium text-gray-900">
									{{ job.job_type }}: {{ job.name }}
								</div>
								<div class="text-sm text-gray-500">
									Server: {{ job.server }} | Duration:
									{{ formatDuration(job.duration) }}
								</div>
							</div>
							<Badge
								:label="job.status"
								:theme="job.status === 'Running' ? 'yellow' : 'gray'"
							/>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { toast } from 'vue-sonner';
import Header from '../../components/Header.vue';

export default {
	name: 'JobMonitor',
	components: {
		Header,
	},
	data() {
		return {
			summary: {
				pending: 0,
				running: 0,
				servers: 0,
			},
			jobsByType: [],
			jobsByServer: [],
			longRunningJobs: [],
			pollInterval: null,
		};
	},
	computed: {
		hasActiveJobs() {
			return (this.summary.pending || 0) + (this.summary.running || 0) > 0;
		},
	},
	resources: {
		fixStuckJobs() {
			return {
				url: 'press.utils.job_monitor.quick_fix_all_stuck_jobs',
				auto: false,
				onSuccess: (data) => {
					if (data.message) {
						toast.success(data.message);
					} else {
						toast.success(
							`Đã poll ${data.servers_polled} server(s) với ${data.total_servers} server(s) tổng cộng`
						);
					}
					// Reload data
					this.$resources.loadJobs.reload();
				},
				onError: (error) => {
					toast.error(
						error.messages?.join('\n') || 'Có lỗi xảy ra khi polling servers'
					);
				},
			};
		},
		loadJobs() {
			return {
				url: 'press.utils.job_monitor.get_stuck_jobs_summary',
				auto: true,
				onSuccess: (data) => {
					this.summary = data.summary || {};
					this.jobsByType = data.jobs_by_type || [];
					this.jobsByServer = data.jobs_by_server || [];
					this.longRunningJobs = data.long_running_jobs || [];
					this.checkAndManagePolling();
				},
			};
		},
	},
	mounted() {
		this.checkAndManagePolling();
	},
	unmounted() {
		this.stopAutoPoll();
	},
	methods: {
		formatDuration(hours) {
			if (hours < 1) {
				return `${Math.round(hours * 60)} phút`;
			}
			return `${hours.toFixed(1)} giờ`;
		},
		startAutoPoll() {
			this.stopAutoPoll();

			this.pollInterval = setInterval(() => {
				if (!this.$resources.fixStuckJobs?.loading) {
					this.$resources.fixStuckJobs.submit();
				}
			}, 30000);
		},
		stopAutoPoll() {
			if (this.pollInterval) {
				clearInterval(this.pollInterval);
				this.pollInterval = null;
			}
		},
		checkAndManagePolling() {
			if (this.hasActiveJobs) {
				this.startAutoPoll();
			} else {
				// Không còn jobs, dừng auto-poll
				this.stopAutoPoll();
			}
		},
	},
};
</script>
