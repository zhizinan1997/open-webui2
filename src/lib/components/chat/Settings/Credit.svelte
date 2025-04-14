<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { user } from '$lib/stores';
	import { createTradeTicket, listCreditLog } from '$lib/apis/credit';
	import { toast } from 'svelte-sonner';
	import { getSessionUser } from '$lib/apis/auths';

	const i18n = getContext('i18n');

	type Model = {
		id: string;
		name: string;
	};
	type APIParams = {
		model: Model;
	};
	type LogDetail = {
		desc: string;
		api_params: APIParams;
	};
	type Log = {
		id: string;
		credit: string;
		detail: LogDetail;
		created_at: number;
	};
	let page = 1;
	let hasMore = true;
	let logs: Array<Log> = [];
	const loadLogs = async (append: boolean) => {
		const data = await listCreditLog(localStorage.token, page).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		if (data.length === 0) {
			hasMore = false;
		}
		if (append) {
			logs = [...logs, ...data];
		} else {
			logs = data;
		}
	};
	const nextLogs = async () => {
		page++;
		await loadLogs(true);
	};

	let credit = 0;
	let payType = 'wxpay';
	let payTypes = [
		{
			code: 'wxpay',
			title: $i18n.t('WXPay')
		},
		{
			code: 'alipay',
			title: $i18n.t('Alipay')
		}
	];
	let amount = 10;

	let tradeInfo = {
		detail: {
			code: -1,
			msg: '',
			payurl: '',
			qrcode: '',
			urlscheme: ''
		}
	};

	const handleAddCreditClick = async () => {
		const res = await createTradeTicket(localStorage.token, payType, amount).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		if (res) {
			tradeInfo = res;
			if (tradeInfo.detail === undefined) {
				toast.error('init payment failed');
				return;
			}

			const detail = tradeInfo.detail;
			if (detail?.code !== 1) {
				toast.error(tradeInfo?.detail?.msg);
				return;
			}

			if (detail?.payurl) {
				open(detail.payurl);
			}

			if (detail?.urlscheme) {
				window.location.href = detail.urlscheme;
			}

			if (detail?.qrcode) {
				document.getElementById('trade-qrcode').innerHTML = '';
				new QRCode(document.getElementById('qrcode'), {
					text: detail.qrcode,
					width: 128,
					height: 128,
					colorDark: '#000000',
					colorLight: '#ffffff',
					correctLevel: QRCode.CorrectLevel.H
				});
			}
		}
	};

	const handleWeChatClick = async () => {
		payType = 'wxpay';
		await handleAddCreditClick();
	};

	const handleAlipayClick = async () => {
		payType = 'alipay';
		await handleAddCreditClick();
	};

	function formatDate(t: number) {
		return new Date(t * 1000).toLocaleString();
	}

	onMount(async () => {
		const sessionUser = await getSessionUser(localStorage.token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		await user.set(sessionUser);

		credit = $user?.credit ? $user?.credit : 0;

		await loadLogs(false);
	});
</script>

<div class="flex flex-col h-full justify-between text-sm">
	<div class=" space-y-3 lg:max-h-full">
		<div class="space-y-1">
			<div class="pt-0.5">
				<div class="flex flex-col w-full">
					<div class="mb-1 text-base font-medium">{$i18n.t('Credit')}</div>
					<div class="flex-1">{credit}</div>
				</div>
			</div>

			<hr class=" border-gray-100 dark:border-gray-700/10 my-2.5 w-full" />

			<div class="pt-0.5">
				<div class="flex flex-col w-full">
					<div class="mb-1 text-base font-medium">{$i18n.t('Add Credit')}</div>

					<div class="flex w-full justify-between">
						<div class=" self-center text-xs font-medium">{$i18n.t('Pay Type')}</div>
						<div class="flex items-center relative">
							<select
								class=" dark:bg-gray-900 w-fit pr-8 rounded-sm py-2 px-2 text-xs bg-transparent outline-hidden text-right"
								bind:value={payType}
								placeholder="Select a pay type"
							>
								{#each payTypes as payType}
									<option value={payType['code']}>{payType['title']}</option>
								{/each}
							</select>
						</div>
					</div>

					<div class="flex w-full justify-between">
						<div class=" self-center text-xs font-medium">{$i18n.t('Amount')}</div>
						<div class="flex items-center relative">
							<input
								class="w-full text-sm bg-transparent placeholder:text-gray-300 dark:placeholder:text-gray-700 outline-hidden text-end"
								type="number"
								bind:value={amount}
								autocomplete="off"
								required
							/>
						</div>
					</div>

					<div class="flex w-full justify-end mt-6">
						<button
							class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full flex flex-row space-x-1 items-center"
							type="button"
							on:click={() => {
								handleAddCreditClick();
							}}
						>
							{$i18n.t('Submit')}
						</button>
					</div>
				</div>
			</div>

			<div id="trade-qrcode"></div>

			<hr class=" border-gray-100 dark:border-gray-700/10 my-2.5 w-full" />

			<div class="pt-0.5">
				<div class="flex flex-col w-full">
					<div class="mb-1 text-base font-medium">{$i18n.t('Credit Log')}</div>
					<div class="overflow-y-scroll max-h-[15rem] flex flex-col">
						{#if logs.length > 0}
							<table class="w-full text-center table-auto border-collapse border border-gray-400">
								<thead>
									<tr>
										<th class="border border-gray-300 bg-stone-100">{$i18n.t('Date')}</th>
										<th class="border border-gray-300 bg-stone-100">{$i18n.t('Credit')}</th>
										<th class="border border-gray-300 bg-stone-100">{$i18n.t('Model')}</th>
										<th class="border border-gray-300 bg-stone-100">{$i18n.t('Desc')}</th>
									</tr>
								</thead>
								<tbody>
									{#each logs as log}
										<tr>
											<td class="border border-gray-300">{formatDate(log.created_at)}</td>
											<td class="border border-gray-300">{parseFloat(log.credit).toFixed(6)}</td>
											<td class="border border-gray-300"
												>{log.detail?.api_params?.model?.name ||
													log.detail?.api_params?.model?.id ||
													'- -'}</td
											>
											<td class="border border-gray-300">{log.detail.desc}</td>
										</tr>
									{/each}
								</tbody>
							</table>
							{#if hasMore}
								<button
									type="button"
									on:click={() => {
										nextLogs(true);
									}}
								>
									{$i18n.t('Load More')}
								</button>
							{/if}
						{:else}
							<div>{$i18n.t('No Log')}</div>
						{/if}
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
