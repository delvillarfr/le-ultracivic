'use client';

import { useState, useEffect } from 'react';
import Head from 'next/head';
import Header from '@/components/Header';
import HeroSection from '@/components/HeroSection';
import ValueProps from '@/components/ValueProps';
import MessageSection from '@/components/MessageSection';
import Actions from '@/components/Actions';
import HistoryTable from '@/components/HistoryTable';
import Footer from '@/components/Footer';

export default function Home() {
  const [allowanceValue, setAllowanceValue] = useState(999);
  const [messageValue, setMessageValue] = useState('');
  const [priceCalc, setPriceCalc] = useState(23976);
  const [tokenCalc, setTokenCalc] = useState(999);
  const [impactCalc, setImpactCalc] = useState(229770);

  const updateCalculations = (allowance: number) => {
    const price = allowance * 24;
    const tokens = allowance;
    const impact = allowance * 230;
    
    setPriceCalc(price);
    setTokenCalc(tokens);
    setImpactCalc(impact);
  };

  const handleAllowanceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value) || 0;
    setAllowanceValue(value);
    updateCalculations(value);
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessageValue(e.target.value);
  };

  const handleDoItClick = () => {
    const allowance = allowanceValue;
    const message = messageValue.trim();
    
    if (allowance <= 0) {
      alert('Please enter a valid allowance amount.');
      return;
    }
    
    if (!message) {
      alert('Please enter a message for history.');
      return;
    }
    
    alert(`Starting payment flow for ${allowance} tons of CO2 allowances.\nMessage: "${message}"`);
    
    console.log('Payment flow initiated:', {
      allowance: allowance,
      price: allowance * 24,
      message: message
    });
  };

  const handleWhatClick = () => {
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
  };

  useEffect(() => {
    updateCalculations(allowanceValue);
  }, []);

  return (
    <>
      <Head>
        <title>Ultra Civic</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>
      
      <div className="container">
        <Header />
        <HeroSection 
          allowanceValue={allowanceValue}
          onAllowanceChange={handleAllowanceChange}
        />
        <ValueProps 
          priceCalc={priceCalc}
          tokenCalc={tokenCalc}
          impactCalc={impactCalc}
        />
        <MessageSection 
          messageValue={messageValue}
          onMessageChange={handleMessageChange}
        />
        <Actions 
          onDoItClick={handleDoItClick}
          onWhatClick={handleWhatClick}
        />
        <HistoryTable />
        <Footer />
      </div>
    </>
  );
}
