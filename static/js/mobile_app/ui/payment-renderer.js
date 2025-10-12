class PaymentRenderer {
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) {
            return '방금 전';
        } else if (diff < 3600000) {
            return `${Math.floor(diff / 60000)}분 전`;
        } else if (diff < 86400000) {
            return `${Math.floor(diff / 3600000)}시간 전`;
        } else {
            return date.toLocaleDateString('ko-KR');
        }
    }

    updatePaymentList(paymentData) {
        const paymentList = document.getElementById('recentPaymentsList');
        if (!paymentList) return;

        paymentList.innerHTML = '';

        (paymentData.slice(0, 5) || []).forEach(payment => {
            const paymentItem = document.createElement('div');
            paymentItem.className = 'payment-item';
            paymentItem.innerHTML = `
                <div class="payment-info">
                    <div class="payment-method">${payment.method}</div>
                    <div class="payment-time">${this.formatTime(payment.timestamp)}</div>
                </div>
                <div class="payment-amount">₩${payment.amount.toLocaleString()}</div>
            `;
            paymentList.appendChild(paymentItem);
        });
    }
}

export default PaymentRenderer;