import { WEBUI_API_BASE_URL } from '$lib/constants';

export const createTradeTicket = async (token: string, payType: string, amount: number) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/credit/tickets`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			pay_type: payType,
			amount: amount
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const listCreditLog = async (token: string, page: number) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/credit/logs?page=${page}`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.log(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
