<script>
	import { getContext, onMount } from 'svelte';
	import { getCreditStats } from '$lib/apis/credit';
	import { toast } from 'svelte-sonner';
	import * as echarts from 'echarts';

	let modelTokenPie;
	let modelTokenPieOption = {};
	let modelTokenPieChart;

	let modelCostPie;
	let modelCostPieOption = {};
	let modelCostPieChart;

	let userTokenPie;
	let userTokenPieOption = {};
	let userTokenPieChart;

	let userCostPie;
	let userCostPieOption = {};
	let userCostPieChart;

	const i18n = getContext('i18n');

	let period = 7;

	let endTime = new Date();
	let startTime = new Date();

	const onChangePeriod = async (p) => {
		period = p;
		await doQuery();
	};

	const doQuery = async () => {
		endTime = new Date();
		startTime = new Date();
		startTime.setDate(endTime.getDate() - period);

		const data = await getCreditStats(localStorage.token, {
			start_time: Math.round(startTime.getTime() / 1000),
			end_time: Math.round(endTime.getTime() / 1000)
		}).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (data) {
			drawChart(data);
		}
	};

	const drawChart = (data) => {
		if (!modelTokenPieChart) {
			modelTokenPieChart = echarts.init(modelTokenPie);
		}
		modelTokenPieOption = {
			title: {
				text: $i18n.t('Model Tokens Cost'),
				textStyle: {
					fontSize: 14,
					fontWeight: '400'
				}
			},
			legend: {
				type: 'scroll',
				orient: 'vertical',
				right: '10px',
				top: '10px',
				bottom: '10px'
			},
			tooltip: {
				show: true
			},
			series: [
				{
					type: 'pie',
					data: data.model_token_pie,
					radius: ['50%', '70%']
				}
			]
		};
		modelTokenPieChart.setOption(modelTokenPieOption);

		if (!modelCostPieChart) {
			modelCostPieChart = echarts.init(modelCostPie);
		}
		modelCostPieOption = {
			title: {
				text: $i18n.t('Model Credit Cost'),
				textStyle: {
					fontSize: 14,
					fontWeight: '400'
				}
			},
			legend: {
				type: 'scroll',
				orient: 'vertical',
				right: '10px',
				top: '10px',
				bottom: '10px'
			},
			tooltip: {
				show: true
			},
			series: [
				{
					type: 'pie',
					data: data.model_cost_pie,
					radius: ['50%', '70%']
				}
			]
		};
		modelCostPieChart.setOption(modelCostPieOption);

		if (!userTokenPieChart) {
			userTokenPieChart = echarts.init(userTokenPie);
		}
		userTokenPieOption = {
			title: {
				text: $i18n.t('User Tokens Cost'),
				textStyle: {
					fontSize: 14,
					fontWeight: '400'
				}
			},
			legend: {
				type: 'scroll',
				orient: 'vertical',
				right: '10px',
				top: '10px',
				bottom: '10px'
			},
			tooltip: {
				show: true
			},
			series: [
				{
					type: 'pie',
					data: data.user_token_pie,
					radius: ['50%', '70%']
				}
			]
		};
		userTokenPieChart.setOption(userTokenPieOption);

		if (!userCostPieChart) {
			userCostPieChart = echarts.init(userCostPie);
		}
		userCostPieOption = {
			title: {
				text: $i18n.t('User Credit Cost'),
				textStyle: {
					fontSize: 14,
					fontWeight: '400'
				}
			},
			legend: {
				type: 'scroll',
				orient: 'vertical',
				right: '10px',
				top: '10px',
				bottom: '10px'
			},
			tooltip: {
				show: true
			},
			series: [
				{
					type: 'pie',
					data: data.user_cost_pie,
					radius: ['50%', '70%']
				}
			]
		};
		userCostPieChart.setOption(userCostPieOption);
	};

	onMount(async () => {
		await doQuery();
	});
</script>

<div class="mt-0.5 mb-2">
	<div class="flex md:self-center text-lg font-medium px-0.5">
		{$i18n.t('Credit Statistics')}
	</div>

	<div class="mt-2 flex justify-around h-[36px] white">
		<button
			class="bg-gray-50 w-full mr-2 rounded-md"
			on:click={async () => {
				await onChangePeriod(30);
			}}
		>
			{$i18n.t('Last 30 Days')}
		</button>
		<button
			class="bg-gray-50 w-full mr-2 rounded-md"
			on:click={async () => {
				await onChangePeriod(14);
			}}
		>
			{$i18n.t('Last 14 Days')}
		</button>
		<button
			class="bg-gray-50 w-full mr-2 rounded-md"
			on:click={async () => {
				await onChangePeriod(7);
			}}
		>
			{$i18n.t('Last 7 Days')}
		</button>
		<button
			class="bg-gray-50 w-full rounded-md"
			on:click={async () => {
				await onChangePeriod(1);
			}}
		>
			{$i18n.t('Today')}
		</button>
	</div>

	<div
		class="mt-2 bg-gray-50 rounded-md"
		bind:this={modelTokenPie}
		style="width: 100%; height: 300px;"
	></div>
	<div
		class="mt-2 bg-gray-50 rounded-md"
		bind:this={modelCostPie}
		style="width: 100%; height: 300px;"
	></div>
	<div
		class="mt-2 bg-gray-50 rounded-md"
		bind:this={userTokenPie}
		style="width: 100%; height: 300px;"
	></div>
	<div
		class="mt-2 bg-gray-50 rounded-md"
		bind:this={userCostPie}
		style="width: 100%; height: 300px;"
	></div>
</div>
