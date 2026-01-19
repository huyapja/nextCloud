<template>
	<CardWithDetails :title="title" :subtitle="subtitle" :showDetails="jobName">
		<template #actions>
			<Button
				variant="outline"
				:loading="$resources.fixStuckJobs?.loading"
				@click="$resources.fixStuckJobs.submit()"
				label="Polling Server"
			/>
		</template>
		<div>
			<router-link
				v-for="job in $resources.jobs.data"
				class="block cursor-pointer rounded-md px-2.5"
				:class="jobName === job.name ? 'bg-gray-100' : 'hover:bg-gray-50'"
				:key="job.name"
				:to="jobRoute(job)"
			>
				<ListItem :title="job.job_type" :description="formatDate(job.creation)">
					<template v-slot:actions>
						<Badge
							class="whitespace-nowrap"
							v-if="
								runningJob &&
								runningJob.id == job.name &&
								runningJob.status !== 'Success'
							"
							:label="runningJob.status"
						/>
						<Badge
							class="whitespace-nowrap"
							v-else-if="job.status != 'Success'"
							:label="job.status"
						/>
					</template>
				</ListItem>
				<div class="border-b"></div>
			</router-link>
			<div class="py-3" v-if="$resources.jobs.hasNextPage">
				<Button
					:loading="$resources.jobs.list.loading"
					loadingText="Loading..."
					@click="$resources.jobs.next()"
				>
					Load more
				</Button>
			</div>
		</div>
		<template #details>
			<JobsDetail :jobName="jobName" />
		</template>
	</CardWithDetails>
</template>
<script>
import CardWithDetails from '@/components/CardWithDetails.vue';
import JobsDetail from './JobsDetail.vue';
import { toast } from 'vue-sonner';
export default {
	name: 'AgentJobs',
	props: ['title', 'subtitle', 'resource', 'jobName', 'jobRoute'],
	components: { JobsDetail, CardWithDetails },
	data() {
		return {
			runningJob: null
		};
	},
	resources: {
		jobs() {
			return this.resource();
		},
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
					// Reload jobs list
					this.$resources.jobs.reload();
				},
				onError: (error) => {
					toast.error(error.messages?.join('\n') || 'Có lỗi xảy ra khi fix stuck jobs');
				}
			};
		}
	},
	mounted() {
		this.$socket.on('agent_job_update', this.onAgentJobUpdate);
	},
	unmounted() {
		this.$socket.off('agent_job_update', this.onAgentJobUpdate);
	},
	methods: {
		onAgentJobUpdate(data) {
			if (data.id === this.jobName) {
				this.runningJob = data;
				if (this.runningJob.status === 'Success') {
					setTimeout(() => {
						// calling reload immediately does not fetch the latest status
						// so adding 1 sec delay
						this.$resources.jobs.reset();
						this.$resources.jobs.reload();
					}, 1000);
				}
			}
		}
	}
};
</script>
