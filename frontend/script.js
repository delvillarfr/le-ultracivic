document.addEventListener('DOMContentLoaded', function() {
    const allowanceInput = document.getElementById('allowance-input');
    const priceCalc = document.getElementById('price-calc');
    const tokenCalc = document.getElementById('token-calc');
    const impactCalc = document.getElementById('impact-calc');
    const messageInput = document.getElementById('message-input');
    const doItBtn = document.getElementById('do-it-btn');
    const whatBtn = document.getElementById('what-btn');

    function updateCalculations() {
        const allowance = parseInt(allowanceInput.value) || 0;
        const price = allowance * 24;
        const tokens = allowance;
        const impact = allowance * 230;
        
        priceCalc.textContent = price.toLocaleString();
        tokenCalc.textContent = tokens.toLocaleString();
        impactCalc.textContent = impact.toLocaleString();
    }

    allowanceInput.addEventListener('input', updateCalculations);
    allowanceInput.addEventListener('change', updateCalculations);

    doItBtn.addEventListener('click', function() {
        const allowance = parseInt(allowanceInput.value) || 0;
        const message = messageInput.value.trim();
        
        if (allowance <= 0) {
            alert('Please enter a valid allowance amount.');
            return;
        }
        
        if (!message) {
            alert('Please enter a message for history.');
            return;
        }
        
        // Simulate payment flow
        alert(`Starting payment flow for ${allowance} tons of CO2 allowances.\nMessage: "${message}"`);
        
        // Here you would integrate with actual payment processing
        console.log('Payment flow initiated:', {
            allowance: allowance,
            price: allowance * 24,
            message: message
        });
    });

    whatBtn.addEventListener('click', function() {
        // Show modal with information about Ultra Civic
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; justify-content: center; align-items: center; z-index: 1000;">
                <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 20px;">
                    <h2 style="margin-bottom: 20px;">What is Ultra Civic?</h2>
                    <p style="margin-bottom: 15px;">Ultra Civic allows you to buy and retire polluters' legal rights to emit carbon dioxide, directly reducing global emissions.</p>
                    <p style="margin-bottom: 15px;">When you purchase CO2 allowances, you:</p>
                    <ul style="margin-bottom: 15px; padding-left: 20px;">
                        <li>Remove pollution rights from the market permanently</li>
                        <li>Earn PR tokens as proof of your environmental impact</li>
                        <li>Leave a message for history about your contribution</li>
                    </ul>
                    <p style="margin-bottom: 20px;">Each ton of CO2 allowances you retire makes a real difference in fighting climate change.</p>
                    <button onclick="this.parentElement.parentElement.remove()" style="padding: 10px 20px; background: #000; color: white; border: none; cursor: pointer;">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    });

    // Initialize calculations
    updateCalculations();
});